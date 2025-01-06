---
title: "QGIS: match text buffer colour to symbol colour"
date: 
excerpt: 
 
editedDate:
tags: ["posts", "QGIS", "map styling"]
draft: true
---
# 

> Published on Dec 11, 2023

Coloured buffer in qgis - expression

`if(color_part(@symbol_color, 'lightness') < 40, 'white', @symbol_color)`
