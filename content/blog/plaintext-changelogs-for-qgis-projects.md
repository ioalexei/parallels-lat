---
title: "Using plaintext changelogs for shared QGIS projects"
date: 2023-07-05
excerpt: 
 
editedDate:
tags: posts
draft: false
---
Published a post on the Learn SIMS site on how I use [plaintext changelogs for shared QGIS projects](https://learn-sims.org/resources-and-standards/managing-product-updates-with-a-changelog/) (with some helpful edits from a colleague).

The context is that when different people work on the same QGIS project, e.g. on Dropbox, it can be hard to tell what has changed between iterations. 

I tend to save a new copy of the `.qgs` project file at the end of each day of working on it, with the date in the file name (in ISO format for easy sorting).

I also write a plaintext changelog file adapted from this [changelog standard](https://keepachangelog.com/en/1.1.0/) summarising the changes (added, changed, removed, fixed, published) and using [semantic versioning](https://www.geeksforgeeks.org/introduction-semantic-versioning/) to communicate the level of changes between versions.
