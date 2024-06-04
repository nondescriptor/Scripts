#!/usr/bin/env bash
# This script fixes, converts, and imports android music playlists into rhythmbox

set -euo pipefail
trap 'printf "Error: Line $LINENO\nExit code: $?\n"' ERR

function fix() {
	# Fix playlist errors and convert to simplified android format
	# Delete strings containing / up to the last instance
	sed -i 's/^.*\([/]\)//' $1
	# Prepend relative path to lines starting with letters or numbers
	sed -i '/^[A-Z,a-z,0-9]/ s|^|./../Music/|' $1
	# Append .mp3 to lines starting with #EXTINF
	sed -i '/^#EXTINF/s/$/.mp3/' $1
	# Delete lines starting with [commas are simply for readability] but not lines ending with .mp3
	sed -i '/^[A-Z,a-z,0-9,.,:,#]/ {/\.mp3$/!d;}' $1
	# Insert #EXTM3U as first line
	sed -i '1s/^/#EXTM3U\n/' $1
	# Delete string between : and , in lines starting with #
	# Songs with commas in their name get messed up but it doesn't affect functionality
	sed -i 's/\(:\).*\(,\)/\1\2/' $1
	# Delete all duplicate lines
	# This command should be run in a loop to treat each file independently (opposed to /*)
	# This is because awk's seen array will fill up with duplicate lines from all files passed to it
	awk -i inplace '!seen[$0]++' $1
	# Delete empty lines
	sed -i '/^$/d' $1
	# Pass playlist to delete function
	delete $1
}

function delete() {
	# Delete entries of songs that have been renamed or no longer exist
	while read song; do
		# In order to grep song from music library we have to account for [] in the name
		local song_original=$song
		local playlist_length=$(sed -e 's/^.*\([/]\)//' $1 | sed -e '/^#/d' | wc -l)
		set +e; echo "$song" | grep '\[[^]]*\]' > /dev/null 2>&1; result1=$?

		if [ $result1 -eq 0 ]; then
			# Insert \ before every [] so grep can interpret it
			local song=$(echo "$song" | sed -e 's/\[/\\\[/g' | sed -e 's/\]/\\\]/g')
		fi

		# Search for song in music library
		ls ~/Music/'All music' | grep -x "$song" > /dev/null 2>&1

		# If song exists in library, do nothing. Otherwise, delete it.
		if [ $? -eq 0 ]; then
			:
		else
			# In order to delete playlist entries, we have to account for [] and & in the name
			local song=$song_original #restore version without backslashes
			# Check if song contains &
			echo "$song" | grep '&' > /dev/null 2>&1; result2=$?; set -e

			if [ $result1 -eq 0 ]; then
				# Replace brackets with brackets enclosed in brackets so sed can interpret it
				# Replace right-most bracket first since sed works from left to right and will
				# only replace first instace (no g flag)
				local song=$(echo "$song" | sed -e 's/[]]/[]]/' | sed -e 's/[[]/[[]/')
			elif [ $result2 -eq 0 ]; then
				# Replace & with [&] so sed can interpret it
				# You only have to escape the special character in the search section of sed
				# You can escape it with \ or enclose it in []
				local song=$(echo "$song" | sed -e 's/[&]/[&]/g')
			fi

			# Delete entry (all lines containing the song)
			sed -i '/'"$song"'/d' $1
			local playlist_length_new=$(sed -e 's/^.*\([/]\)//' $1 | sed -e '/^#/d' | wc -l)
			local song=$song_original

			# Even if sed fails, it will return a 0
			# This is because it's not checking for successful substitutions
			# but rather whether the command managed to run at all
			# So instead, check if song has really been deleted by comparing number of songs
			if [ $playlist_length -eq $playlist_length_new ]; then
				echo -e "$song could not be deleted from $playlist \nexiting"
				echo "$song could not be deleted from $playlist" >> "$path"errors.log
				exit 1
			else
				echo "$song has been deleted from $playlist"
				echo "$song has been deleted from $playlist" >> "$path"errors.log
			fi
		fi
	done < <(sed -e 's/^.*\([/]\)//' $1 | sed -e '/^#/d')
}

function XML_convert() {
	# XML conversion
	# I know it's considered bad to write XML files this way but this was a pretty simple case
	echo 2 converting to XML
	for temp_playlist in "${temp_list[@]}"; do
		# Echo name of current playlist in console
		# Remove path from filename
		local var=$(echo $temp_playlist | sed -e 's/^.*\([/]\)//')
		# Remove everything after <-> using bash parameter expansion
		echo "- converting ${var%%-*}"
		# Delete lines beginning with #
		sed -i '/^#/d' $temp_playlist
		# Delete the parts of strings containing / up to the last instance
		sed -i 's/^.*\([/]\)//' $temp_playlist
		# Prepend path to all lines
		sed -i 's|^|/home/<user>/Music/All music/|' $temp_playlist
		# Prepend <location>file:// and append </location> and to all lines
		sed -i 's|^|<location>file://|;s|$|</location>|' $temp_playlist
		# Replace all whitespaces with %20
		sed -i "s/\s\{1,\}/%20/g" $temp_playlist
		# Replace all & with &amp;
		sed -i 's/[&]/&amp;/g' $temp_playlist
		# Replace [] with %5B and %5D respectively
		sed -i 's/[[]/%5B/;s/[]]/%5D/' $temp_playlist
		# Prepend 4 whitespaces (1 tab) to all lines
		sed -i 's|^|    |' $temp_playlist
		# Insert playlist header (remove extension from filename)
		local playlist_name=$(echo ${var%%-*} | sed 's/\.[^.]*$//')
		sed -i '1s/^/  <playlist name="'$playlist_name'" show-browser="true" browser-position="180" search-type="search-match" type="static">\n/' $temp_playlist
		# Insert playlist footer
		# The -n stops echo from inserting a blank line at the end
		echo -n "  </playlist>" >> $temp_playlist
	done
}

function import() {
	echo 3 importing playlists
	! killall rhythmbox & > /dev/null 2>&1
	# Type each playlist in a new line one after the other to be copied as one
	local var=$(for temp_playlist in "${temp_list[@]}"; do
	      			cat $temp_playlist
					echo
		 	    done)
	# Reset playlists.xml file
	cp -af "$path"playlists_clean.xml ~/.local/share/rhythmbox/playlists.xml &&
	# Import playlists at line 33
	awk -i inplace -v x="$var" 'NR==33{print x}1' ~/.local/share/rhythmbox/playlists.xml > /dev/null 2>&1
	cp -af ~/.local/share/rhythmbox/playlists.xml "$path"playlists_before_import.xml
}

function verify_playlists() {
	echo 4 verifying playlists
	rhythmbox &
	sleep 2
	# Check playlist files are the same in case rhythmbox changed something
	hash1=$(sha256sum ~/.local/share/rhythmbox/playlists.xml | awk 'NR==1{print $1}')
	hash2=$(sha256sum "$path"playlists_before_import.xml | awk 'NR==1{print $1}')
	if [ "$hash1" = "$hash2" ]; then
		rm "$path"playlists_before_import.xml
		echo "- playlists match"
	else
		cp -af ~/.local/share/rhythmbox/playlists.xml "$path"playlists_after_import.xml
		echo "Playlists differ after import" >> "$path"errors.log
		echo "Playlists differ after import"
		exit 1
	fi
}

function verify_library() {
	echo 5 verifying rhythmbox music library
	# Delete all lines not starting with <title>
	# Delete </title> and <title> from all lines (substitute it with whitespace)
	# Delete tabs (replace 4 whitespaces with nothing)
	# Delete all empty lines
	# Delete duplicate entries
	# Sort entries alphabetically
	# Count number of lines
	rhythmbox_library=$(cat ~/.local/share/rhythmbox/rhythmdb.xml |
						sed -e '/^    <title>/!d;s/<\/title>//;s/<title>//;s/    //;/^$/d' |
						awk '!seen[$0]++' | sort | wc -l)
	music_library=$(ls ~/Music/'All music' | wc -l)

	# Compare number of songs
	if [ $music_library -eq $rhythmbox_library ]; then
		echo "- libraries match"
	else
		zenity --question --title="Warning" \
		--text="Number of songs don't match. \
		        \nWould you like to reset rhythmbox music library?"
		if [ $? -eq 0 ]; then
			# Reset entire music library
			echo resetting library
			killall rhythmbox &
			trash ~/.local/share/rhythmbox/rhythmdb.xml
			sleep 2
			echo "number of songs was mismatched" >> "$path"errors.log
			echo "rhythmbox music library has been reset" >> "$path"errors.log
			xdg-open '/home/<user>/Music/All music/<sample song>.mp3'
		fi
	fi
}

function notify() {
	# Check if log file was created
	echo 6 notify
	if [ -e "$path"errors.log ]; then
		notify-send -t 3000 "Log created"
		paplay --volume=50000 /usr/share/sounds/freedesktop/stereo/complete.oga
	fi
}

function confirm() {
	# Ask user for confimation before overwriting original playlists
	echo "7 confirm"
	read -p "Overwrite original playlists? (y/n) " yn
	case $yn in
		[yY])
			for ((i=0;i<${#temp_fixed_list[@]};i++)); do
				cat ${temp_fixed_list[$i]} > ${original_list[$i]}
			done
			exit 0
			;;
		[nN])
			exit 1
			;;
		*)
			echo "invalid response"; exit 1;;
	esac
}

function main() {
	# Path to playlists
	declare -rg path=~/Music/'Playlists'/

	# Create temp directory and delete it when script exits anywhere
	dir=$(mktemp -d)
	trap "rm -r $dir" EXIT

	# Delete old log file if it exists
	! trash "$path"errors.log > /dev/null 2>&1

	# Declare arrays
	list=($(ls "$path" | egrep '\.m3u$'))	# Original playlists
	temp_list=()
	temp_fixed_list=()

	local number_of_playlists=${#list[@]}
	local x=0

	# Check if playlist has been fixed already
	echo "1. Cleaning playlists"
	for playlist in ${list[@]}; do
		# If playlist contains string then it has not been fixed yet
		if grep "#EXTENC" "$path"$playlist > /dev/null 2>&1; then
			echo "   - fixing $playlist"

			# Create copy of original for manipulation, and add it to array
			temp_playlist=$(mktemp --tmpdir=/$dir $playlist-XXXXX)
			cat "$path"$playlist > $temp_playlist
			fix $temp_playlist
			delete $temp_playlist
			temp_list+=($temp_playlist)

			# Create copy of copy and add it to array
			# Will be used to overwrite original upon user confirmation
			temp_fixed_playlist=$(mktemp --tmpdir=/$dir "$playlist"_fixed-XXXXX)
			cat $temp_playlist > $temp_fixed_playlist
			temp_fixed_list+=($temp_fixed_playlist)
		else
			echo "   - no fixing required for $playlist"

			# Even if playlist has been fixed already, check for deprecated entries again
			# Add it to same array
			temp_playlist=$(mktemp --tmpdir=/$dir $playlist-XXXXX)
			cat "$path"$playlist > $temp_playlist
			delete $temp_playlist
			temp_list+=($temp_playlist)

			# Create copy of copy and add it to array
			# Will be used to overwrite original upon user confirmation
			temp_fixed_playlist=$(mktemp --tmpdir=/$dir "$playlist"_fixed-XXXXX)
			cat $temp_playlist > $temp_fixed_playlist
			temp_fixed_list+=($temp_fixed_playlist)

			((x++))
		fi
	done

	# Exit script if all playlists were skipped and no songs were deleted
	if [ $x -eq $number_of_playlists ] && [ ! -e "$path"errors.log ]; then
		echo -e "   No changes have been made to playlists\n   Exiting now"
		exit 0
	else
	# If any changes were made, convert all playlists again
		XML_convert
		import
		verify_playlists
		verify_library
		notify
		confirm
	fi
}
#===============================================================================================================
main
