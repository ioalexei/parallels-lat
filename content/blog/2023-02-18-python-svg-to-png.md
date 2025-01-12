---
title: "Python: Convert a folder of SVGs to PNGs"
date: 2023-02-18
excerpt: 
 
editedDate:
tags: posts
draft: false
---
For a work thing I had a folder of SVG icons to use for map symbology that I wanted to also have as PNGs to use in PowerPoints, Word docs, etc. when needed. 

IFRC [share icons](https://go-user-library.ifrc.org/brand-design/iconography) as SVGs which is good for graphic design and web development but not always user friendly for people who don't know how to use them. I thought it would be useful to have them as PNGs too, to have another option available. There are 185 icons, so saving as PNG manually in Inkscape would take too long. I had a go at using the Inkscape batch processing tool, but couldn't get it to work. So instead I looked up how to use Python and found a method on [Stack Exchange](https://superuser.com/a/1321947) that uses the [cairosvg](https://cairosvg.org/) library to convert from SVG. 

It's a simple loop that runs through every file in the directory and uses cairosvg to convert to PNG. It worked perfectly.  

```{python}

import os 
import cairosvg
 
for file in os.listdir('./SVG_icons/'):
	name = file.split('.svg')[0]	# get the file name before the extension
    cairosvg.svg2png(url='./SVG_icons/' + name + '.svg', write_to = './PNG_icons/' + name + '.png') 
    # use cairosvg to convert from SVG to PNG, using the same filename
```
