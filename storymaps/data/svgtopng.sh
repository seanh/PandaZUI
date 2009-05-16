for i in *.svg; do inkscape -f "$i" -e "$i-64.png"; -w 64; done
for i in *.svg; do inkscape -f "$i" -e "$i-128.png" -w 128; done
for i in *.svg; do inkscape -f "$i" -e "$i-256.png"; -w 256; done
for i in *.svg; do inkscape -f "$i" -e "$i-512.png" -w 512; done