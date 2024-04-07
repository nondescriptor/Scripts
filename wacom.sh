#!/bin/bash
# This script toggles easystroke scrolling on and off for applications that do not support wacom driver

set -euxo pipefail
trap 'printf "Error: Line $LINENO\nExit code: $?\n"' ERR

# Get current scrolling button value
state1=$(xsetwacom --get "Wacom Intuos PT S 2 Pen stylus" Button 2 | awk 'NR==1{print $1}')

wacom () {
	xsetwacom --set "Wacom Intuos PT S 2 Pad pad" Button 1 key "ctrl i"
	xsetwacom --set "Wacom Intuos PT S 2 Pen stylus" Button 2 "pan"
	xsetwacom --set "Wacom Intuos PT S 2 Pen stylus" "PanScrollThreshold" 200
	xsetwacom --set "Wacom Intuos PT S 2 Pad pad" Button 3 key "super e"
	xsetwacom --set "Wacom Intuos PT S 2 Pad pad" Button 8 key "super d"
	xsetwacom --set "Wacom Intuos PT S 2 Pad pad" Button 9 key "super t"
}

if [ 'button' = "$state1" ]; then
	wacom
	# Easystroke commands return exit code of 1 even though they work
	! firejail easystroke disable
	# Enable middle click system-wide
	xmodmap -e "pointer = 1 2 3 4 5 6 7 8 9" > /dev/null 2>&1
	notify-send -t 3000 --icon=/usr/share/icons/Yaru/cursors/pencil.cur 'Wacom scrolling enabled'
else
	# Reset wacom variable to defaults so easystroke can override it
	xsetwacom --set "Wacom Intuos PT S 2 Pen stylus" Button 2 "button +2"
	! firejail easystroke enable
	# Disable middle click system-wide to avoid issues
	xmodmap -e "pointer = 1 25 3 4 5 6 7 8 9" > /dev/null 2>&1
	notify-send -t 3000 --icon=/usr/share/icons/hicolor/scalable/apps/easystroke.svg 'Easystroke scrolling enabled'
fitest
