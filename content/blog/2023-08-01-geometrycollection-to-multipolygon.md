---
title: "GeoPandas: Convert GeometryCollection to MultiPolygon"
date: 2023-08-01
excerpt: 
 
editedDate:
tags: posts
draft: false
---
I've been using food security data from the the [Integrated Phase Classificaiton API](https://www.ipcinfo.org/). As it's a work in progress, there are some quirks for how data is returned for different countries. When accessing the Niger data, I noticed my standard script failed as the geometries are returned as a GeometryCollection rather than as simple MultiPolygon. 

After much searching and testing out different approaches for converting the geometry, the answer turned out to be surprisingly simple - you can use `explode()` on the GeometryCollection to return it's constituent parts. In this case, as each collection only held a single MultiPolygon, the returned values could be directly used as the new feature geometry. 

`df.geometry = df.geometry.explode()[0:].values`

The page that was most helpful in figuring this out was [this bug report](https://github.com/geopandas/geopandas/issues/1665) on the GeoPandas GitHub.
