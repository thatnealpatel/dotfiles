#!/usr/bin/env bash

# Terminate already running bar instances
killall -q polybar
# If all your bars have ipc enabled, you can also use 
# polybar-msg cmd quit


echo "---" | tee -a /tmp/polybar1.log

echo "launching polybar..."

#for m in $(polybar --list-monitors | cut -d":" -f1); do
#MONITOR=$m polybar --reload sysbar >> /tmp/polybar1.log 2>&1 &
#done

polybar -r i3custombar >> /tmp/polybar1.log 2>&1 & disown

echo "setting background..."
feh --bg-fill ~/usr/img/wallpapers/newyork_21_9.jpeg


# neofetch
