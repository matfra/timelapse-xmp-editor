# timelapse-xmp-editor (WIP, not ready for use)
This tool allows you to generate xmp files with gradual development settings to a set of pictures in order to make beautiful timelapses with varying lighting conditions (typically during sunrise and sunset)

## Requirements
- python3
- Photoshop and Camera Raw
- Optionally : ffmpeg

## How to use
Select all the RAW pictures you need to make your timelapse and put them into an empty working directory
Edit the first one in Photoshop Camera raw. 
- Make the cropping and alignment adjustments
- Adjust all the settings to your liking
Click the Done button and an .xmp file should appear next to the RAW/ARW file
Now go and do the same with the last picture. This time only adjust the lighting settings.
Cropping, alignment, lens distortion or any other metadata will be duplicated from the first picture


Run this script by passing it the working directory path and the extension of your RAW pictures
./generate-xmps.py /path/to/directory ARW

This should generate all the xmp files for all the pictures. You can open one RAW picture randomly with Photoshop Camera Raw and you should see the interpolated settings appear


In Photoshop, file Script, Image processor
and give it the directory

It will automatically open pictures one by one apply the settings in the xmp and save the picture (typically jpeg)

## How does it work
It's pretty simple really
First the script will look at at the difference between your 2 xmp files
Entries that are present only in the first file will be applied to all files (croping, alignement, lens distortion)
Settings that are present in both files but have differentvalues will be applied, gradually, to the entire set of files. Using basic linear interpolation.

Example:
Given a set of 200 pictures.
Exposure setting on the first picture: -1
Exposure setting on the last picture : +1
Exposure setting for the 120th picture: 0.2

## TO-DO
- Support interval settings
- Add log or exp function support instead of just linear
- Support other Dark table so we don't need photoshop at all. (Need proper XML and XMP parsing)
- Proper logging
- Support more complex fields than just crs float values



## How to create the timelapse

I usually use the following command:

ffmpeg -framerate 30 -pattern_type glob -i "*.jpg" -c:v libx264 -preset veryslow -crf 21 -s 3840x2160 -vf format=yuv420p timelapse.mp4