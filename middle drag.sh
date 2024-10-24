#!/usr/bin/env bash
# This script maps middle mouse button to a key

xdotool mousedown 2
while :; do
	# Run <xinput list> for a list of device names (IDs change so use names)
	# Get button current state
	state1=$(xinput query-state 'Virtual core XTEST pointer' | awk 'NR==3{print $1}')
	state2="button[1]=down"
	# If button is pressed then lift it
	if [ "$state1" = "$state2" ]; then
		xdotool mouseup 2
		break
	fi
done
