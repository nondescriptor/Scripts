#!/bin/bash
# This script maps key to middle mouse button because my mouse does not have one

xdotool mousedown 2
while :; do
	#xinput list (use names because IDs change)
	state1=$(xinput query-state 'Virtual core XTEST pointer' | awk 'NR==3{print $1}')
	state2="button[1]=down"
	if [ "$state1" = "$state2" ]; then
		xdotool mouseup 2
		# Break from while loop
		break
	fi
done
