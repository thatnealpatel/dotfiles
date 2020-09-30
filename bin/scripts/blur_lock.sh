#!/bin/bash

img=$(mktemp $HOME/tmp/XXXXXXXXXX.png)

import -window root $img 

# Pixelate the screenshot
convert $img -scale 5% -scale 2000% $img

i3lock -u -i $img

rm $img