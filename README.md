# Minbay Pixel Artboard Image Converter

A small tool to convert .PIX files from a [Minbay Pixel Artboard](https://minbay.com/product.html) 
into usable image files.

The Artboard stores images as .PIX files in a *bizarre* proprietary format where the data is
interleaved across multiple bytes (these are *not* Alias .pix files), with a corresponding .DAT 
file that stores undo data for the image.  This script only deals with the .PIX files that contain 
the actual pixel data.

## Requirements

Python 3, and PIL or Pillow.  Uses nothing exotic.

## General usage

Connect your Pixel Artboard to your computer via USB, and copy over the .PIX files you're 
interested in.  They are sorted in directories, one per page, with a suffix indicating their
position on that page.

Then run the script against your image file:

  `./pixconvert.py -i <your input file>`

There are some optional parameters:

```
$ ./pixconvert.py -h
usage: pixconvert.py [-h] -i IN_FILE [-o OUT_FILE] [-b] [-p]

Converts Minbay Pixel Artboard .PIX files to PNG or BMP files

options:
  -h, --help            show this help message and exit
  -i IN_FILE, --infile IN_FILE
                        input filename
  -o OUT_FILE, --outfile OUT_FILE
                        output filename
  -b, --bmp             produce BMP instead of PNG outut
  -p, --playdate        produce Playdate-compatible PNG output
```

If `--outfile` is omitted, it will default to matching filename, with an appropriate extension 
for the output format (defaults to PNG, `.png`).

## Playdate Mode

The `--playdate` option will convert the files to PNG files compatible with the 
[Panic Playdate](https://play.date/) SDK. It does this by interpreting only white and black 
pixels, and setting any other colors to full transparent.

## A note on the palette

The Minbay Pixel Artboard's 100-color palette does include a true white, but oddly enough does
*not* include a true black.  The 'black' color is actually `0x211e1f`.  This is preserved in
the standard mode, but corrected in the Playdate-compatibility mode to true black.

## How did you do this??

Reverse engineering.  Dragons and black magic.

## License

I provide neither warranty nor support for this script.  You are free to do with it as you please
under the terms of the WTFPLv2:

```
           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                   Version 2, December 2004
 
Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>

Everyone is permitted to copy and distribute verbatim or modified
copies of this license document, and changing it is allowed as long
as the name is changed.
 
           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
  TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

 0. You just DO WHAT THE FUCK YOU WANT TO.
```