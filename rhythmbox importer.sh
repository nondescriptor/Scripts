#!/bin/bash
# This script fixes, converts, and imports android music playlists into rhythmbox

set -euxo pipefail
trap 'printf "Error: Line $LINENO\nExit code: $?\n"' ERR

android_convert() {
	# Sync playlists
	rsync -avth --delete --exclude=playlists.xml --exclude=playlists_clean.xml --exclude=log.txt \
	~/Music/Playlists/ "$path" >/dev/null &&

	# Create list of all playlists
	list=$(ls "$path" | egrep '\.m3u$')

	# Delete previous log file if it exists
	! trash "$path"log.txt

	# Check if playlist has been fixed already
	for item in $list; do
		if grep "#EXTENC" "$path"$item >/dev/null; then
			fix
		else
			:
		fi
	done

	# Copy fixed playlists back before converting to XML
	rsync -avth --delete --exclude=playlists.xml --exclude=playlists_clean.xml --exclude=log.txt \
	"$path" ~/Music/Playlists/ >/dev/null
}

fix() {
	# Fix playlist errors and convert to simplified android format
	# Delete strings containing / up to the last instance
	sed -i 's/^.*\([/]\)//' "$path"$item
	# Prepend relative path to lines starting with letters or numbers
	sed -i '/^[A-Z,a-z,0-9]/ s|^|./../Music/|' "$path"$item
	# Append .mp3 to lines starting with #EXTINF
	sed -i '/^#EXTINF/s/$/.mp3/' "$path"$item
	# Delete lines starting with [commas are simply for readability] but not lines ending with .mp3
	sed -i '/^[A-Z,a-z,0-9,.,:,#]/ {/\.mp3$/!d;}' "$path"$item
	# Insert #EXTM3U as first line
	sed -i '1s/^/#EXTM3U\n/' "$path"$item
	# Delete string between : and , in lines starting with #
	# Songs with commas in their name get messed up but it doesn't affect functionality
	sed -i 's/\(:\).*\(,\)/\1\2/' "$path"$item
	# Delete all duplicate lines
	awk -i inplace '!seen[$0]++' "$path"$item
	# Delete empty lines
	sed -i '/^$/d' "$path"$item
	delete
}

delete() {
	# Delete entries of songs that have been renamed or no longer exist
	local x=0
	while read song; do
		# Check is song name contains []
		if echo "$song" | grep -oP '\[' && echo "$song" | grep -oP '\]'; then
			# Insert \ before every [] so grep can interpret it
			song_new=$(echo "$song" | sed -e 's/\[/\\\[/g' | sed -e 's/\]/\\\]/g')
		fi

		if ls ~/Music/'All music' | grep -x "$song" >/dev/null; then
			:
		elif ls ~/Music/'All music' | grep -x "$song_new" >/dev/null; then
			:
		else
			# Delete entry if not found in library
			sed -i '/'"$song"'/d' "$path"$item
			# Search if song still exists in playlist
			if grep "$song" "$path"$item || grep "$song_new" "$path"$item; then
				echo "$song could not be deleted from $item" >> "$path"log.txt
				notify-send -t 3000 'Error occurred'
				paplay --volume=50000 /usr/share/sounds/freedesktop/stereo/complete.oga
				exit
			else
				echo "$song has been deleted from $item" >> "$path"log.txt
				x=$((x+1))
			fi
		fi
	done < <(sed -e 's/^.*\([/]\)//' "$path"$item | sed -e '/^#/d')

	if ((x>0)); then
		echo "$x songs have been deleted" >> "$path"log.txt
	fi
}

XML_convert() {
	# XML conversion
	for item in $list; do
		# Delete lines beginning with #
		sed -i '/^#/d' "$path"$item
		# Delete the parts of strings containing / up to the last instance
		sed -i 's/^.*\([/]\)//' "$path"$item
		# Prepend path to all lines
		sed -i 's|^|/home/<user>/Music/All music/|' "$path"$item
		# Prepend <location>file:// and append </location> and to all lines
		sed -i 's|^|<location>file://|;s|$|</location>|' "$path"$item
		# Replace whitespaces with %20
		sed -i "s/\s\{1,\}/%20/g" "$path"$item
		# Replace [] with %5B and %5D respectively
		sed -i 's/[[]/%5B/;s/[]]/%5D/' "$path"$item
		# Prepend 4 whitespaces (1 tab) to all lines
		sed -i 's|^|    |' "$path"$item
		# Insert playlist header (remove extension from filename)
		name=$(echo $item | sed 's/\.[^.]*$//')
		sed -i '1s/^/  <playlist name="'$name'" show-browser="true" browser-position="180" search-type="search-match" type="static">\n/' "$path"$item
		# Insert playlist footer
		echo -n "  </playlist>" >> "$path"$item
	done
}

import() {
	# Type each playlist in a new line one after the other to be copied as one
	var=$(for item in $list; do
	      	cat "$path"$item
			echo
		  done)
	# Reset playlists.xml file
	cp -af "$path"playlists_clean.xml ~/.local/share/rhythmbox/playlists.xml &&
	# Import playlists at line 33
	awk -i inplace -v x="$var" 'NR==33{print x}1' ~/.local/share/rhythmbox/playlists.xml > /dev/null 2>&1
	cp -af ~/.local/share/rhythmbox/playlists.xml "$path"playlists.xml
}

verify() {
	# Check playlist files are the same in case rhythmbox changed something
	hash1=$(sha256sum ~/.local/share/rhythmbox/playlists.xml | awk 'NR==1{print $1}')
	hash2=$(sha256sum "$path"playlists.xml | awk 'NR==1{print $1}')
	if [ "$hash1" = "$hash2" ]; then
		:
	else
		echo "Playlists differ" >> "$path"log.txt
		notify-send -t 3000 'Error occurred'
		cp -af ~/.local/share/rhythmbox/playlists.xml "$path"playlists_rhythmbox.xml
		paplay --volume=50000 /usr/share/sounds/freedesktop/stereo/complete.oga
		exit
	fi

	# Check music library file
	app_library=$(cat ~/.local/share/rhythmbox/rhythmdb.xml |
	sed -e '/^    <title>/!d;s/<\/title>//;s/<title>//;s/    //;/^$/d;s/\.[^.]*$//' |
	awk '!seen[$0]++' | sort)
	# Compare every song in music library to rhythmbox library
	while read song; do
		if $app_library | grep -x "$song"; then
			:
		else
			# Reset entire music library
			killall rhythmbox &
			trash ~/.local/share/rhythmbox/rhythmdb.xml
			echo "$song was missing from rhythmbox music library" >> "$path"log.txt
			echo "rhythmbox music library has been reset" >> "$path"log.txt
			xdg-open '/home/<user>/Music/All music/example.mp3'
			break
		fi
	done < <(ls ~/Music/'All music' | sed 's/\.[^.]*$//')
}

notify() {
	# Check if log file was created
	if [ -e "$path"log.txt ]; then
		notify-send -t 3000 "Log created"
		paplay --volume=50000 /usr/share/sounds/freedesktop/stereo/complete.oga
	else
		:
	fi
}

#===============================================================================================================
# Declare path variable
path=~/Music/'Playlists rhythmbox'/

android_convert
XML_convert
! killall rhythmbox &
import
rhythmbox &
verify
notify
