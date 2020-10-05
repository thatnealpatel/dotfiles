#!/bin/bash

img=$(mktemp $HOME/tmp/XXXXXXXXXX.png)

import -window root $img 

# Pixelate the screenshot
convert $img -scale 10% -scale 1000% $img

i3lock -u -i $img

rm $img