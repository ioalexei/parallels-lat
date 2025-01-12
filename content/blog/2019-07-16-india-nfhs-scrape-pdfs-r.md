---
title: "Using R to scrape Indian health survey data from PDFs"
date: 2019-07-16
excerpt: 
 
editedDate:
tags: posts
draft: false
---
# Aim 

I want to be able to create a map of district-level child malnutrition data for India. This data is available online at the [National Family Health Survey website](http://rchiips.org/nfhs/index.shtml), but unfortunately the data is only available in PDF form and the website is often offline. It would be useful to have the data in table format and stored locally so that it can be used in GIS software. 

If there were just a handful of data sheets to get data from, it would be easier to just copy the data by hand into a spreadsheet or add directly into GIS software. However, India has 33 states and over 600 districts, so clearly it would take too long to download each PDF and then copy out the data - I needed to find a way to automate this process. 

I wrote this script while learning R and trying to solve this particular problem. There was quite a lot of trial and error involved, and I didn't follow software engineering practices so the code could be improved. However, it works for what I needed and hopefully makes sense to you reading it. I've included footnotes for each section with links to the pages that helped me solve each step. 

# Automating the process

## Set-up

To begin, let's load the necessary libraries. 
```r
library(tidyverse)
library(stringr)
library(tabulizer)
library(rvest)
```
## Scrape web pages 

The [National Family Health Survey website](http://rchiips.org/nfhs/index.shtml) has a page for [district fact-sheets](http://rchiips.org/nfhs/districtfactsheet_NFHS-4.shtml) for the 2015-16 survey that allows you to click through two sets of menus to get to the PDFs. First you select the state and then the district, which downloads the data sheet for that district. 

After experimenting with a couple of scraping packages, I found `rvest`, which seemed the most intuitive to use. This chunk reads the list on the main page and creates a list of the URLs for each state. [^1]

```r
nfhs_site <- "http://rchiips.org/nfhs/districtfactsheet_NFHS-4.shtml"

state_pages <- read_html(nfhs_site) %>% 
  html_nodes('select') %>% 
  map(~html_nodes(.x, 'option') %>% 
        html_attr('value') %>% 
        gsub(pattern = '\\t|\\r|\\n', replacement = '')
  )
  
base_url <- "http://rchiips.org/nfhs/"

state_urls <- list()
for (i in 1:length(state_pages[[1]])){
  url <- paste0(base_url, state_pages[[1]][i])
  state_urls[[i]] <- url 
}

unlist(state_urls) # flatten the list
state_urls <- state_urls[-1] # remove a blank entry
```
The process repeats for each of those pages to create a list of data sheet PDFs for every district in a state. 

```r
district_pdfs <- list()
for (i in state_urls){
  district_pdfs[[i]] <- read_html(i) %>% html_nodes('option') %>% html_attr('value')
}
```
## Download PDFs

Now that I have a URL for every PDF, I can loop through and download them. To keep things tidy, I extracted the two-letter state code from the URL and made a folder using the code that I can save the PDFs for that state into. [^2] [^3] When I first tried this the PDFs downloaded as blank files. Adding the `mode="wb"` flag to `download.file` fixed this. [^4]

```r
ifelse(!dir.exists("data"), dir.create("data")) # check if data directory exists, if not create it. 

for (i in district_pdfs){ #do any filtering of states here - it can take a long time!
  d_code <- str_sub(i[2], start = 6, end=7)
  
  dir.create(file.path(paste0("data/", d_code)), recursive=TRUE)

  for (p in i[-1]){
    download.file(paste0("http://rchiips.org/nfhs/", p), paste0("data/", d_code, "/", str_sub(p, start = 9)),mode="wb")
  }
}
```
## Extract data from PDFs

The next step is to extract the data from the PDFs. As with scraping, I found a number of methods for reading table data from PDFs in R. The package I found most straighforward was `tabulizer`. [^5]

Now I can loop through each directory and process each PDF. [^6] Luckily, each PDF is in the same format and the data I want is on the same page in all of the files. This allowed me to set a single page to extract with `pages = 4` (only extract from page 4) which cuts down on processing time and avoids some extra steps of searching and extracting the right pages afterwards. 

First, I extract the data from page 4 of the PDF and convert it to a data.frame.

```r
files <- list() #  reset from previous run 
files <- list.files("data/", pattern=".pdf", recursive=TRUE, full.names=TRUE) # if you don't want to run for all states, change the directory here

for (f in files){
  df_results <- extract_tables(f, pages = 4)
  df2 <- data.frame(df_results)
```
Then, I do some tidying: fix the column names and remove some unneeded rows at the top. [^7] 
```r
  x1 <- df_results[[1]][1,1]
  x2 <- df_results[[1]][2,2]
  colnames(df2) <- c(x1, x2)
  df2 <- df2[-1,]
  df2 <- df2[-1,]
```
The data.frame is still a bit messy, but rather than spending lots of time tidying up formatting for rows I don't need to use, I decided to just extract the rows with the data I need. The survey questions relating to child malnutrition rates are numbers 68--71. As the question numbers are included in the data frame, I can run a text search for those numbers and pull them out into a new variable `q67_71`. [^9] 

```r
  q68_71 <- df2 %>% filter(str_detect(Indicators, "68.")|str_detect(Indicators, "69.")|str_detect(Indicators, "70.")|str_detect(Indicators, "71."))
```
At this stage I realised the PDFs are not quite all formatted the same. For districts that are only urban or rural, two columns are provided, `Urban`/`Rural` and `Total` but for districts that are both urban and rural, three columns are provided: `Urban`, `Rural` and `Total`. The PDF extraction bundles all of these into a single column, which I need to split apart. 

First, I use `if` statements to check the column name to see which category it falls into. For each option, I set a flag and then in the next chunk process the columns depending on which flag is set. 
```r
  # if cols are rural and total, set flag 
  if (colnames(q68_71)[2] == "Rural Total") {RT <-  TRUE} else {RT <- FALSE}
  
  # if cols are urban and total, set flag 
  if (colnames(q68_71)[2] == "Urban Total") {UT <- TRUE} else {UT <- FALSE}
  
  # if cols are urban, rural and total, set flag 
  if (colnames(q68_71)[2] == "Urban Rural Total") {URT <- TRUE} else {URT <- FALSE}
```
Now I can split the second column on the space character (`" "`) and insert the new columns into the data frame before removing the redundant data in the combined column. 
```r
  # split columns and rename depending on flag  
  if (RT == TRUE){
    q68_71["Rural"] <- str_split_fixed(q68_71$`Rural Total`, " ", 2)[,1] # insert split column into data.frame
    q68_71["Total"] <- str_split_fixed(q68_71$`Rural Total`, " ", 2)[,2]
    q68_71["Rural Total"] <- NULL    # remove original column 
    RT <- FALSE                   # reset the flag 
  }
  if (UT == TRUE){
    q68_71["Urban"] <- str_split_fixed(q68_71$`Urban Total`, " ", 2)[,1]
    q68_71["Total"] <- str_split_fixed(q68_71$`Urban Total`, " ", 2)[,2]
    q68_71["Urban Total"] <- NULL 
    UT <- FALSE
  }
  if (URT == TRUE){
    q68_71["Urban"] <- str_split_fixed(q68_71$`Urban Rural Total`, " ", 3)[,1]
    q68_71["Rural"] <- str_split_fixed(q68_71$`Urban Rural Total`, " ", 3)[,2]
    q68_71["Total"] <- str_split_fixed(q68_71$`Urban Rural Total`, " ", 3)[,3]
    q68_71["Urban Rural Total"] <- NULL
    URT <- FALSE
  }
```

## Export as csv

Now that I've got the data I need for this district, I'll write it out to CSV using `write_csv` (NB not `write.csv`).[^8] The code picks out the two-letter state code from the file path and saves the CSV into that folder with the state code, district code and district name. 

```r
  write_csv(q68_71, path = file.path(paste0("data/", str_sub(f, start = 9, end = 10), "/", 
  + str_sub(f, start = 9, end = -5), ".csv")), append = FALSE, col_names = TRUE)
  }
```
  
The loop then continues through all the PDFs in each folder in my data directory. 

While I've chosen to look specifically at the data on child malnutrition, it would be very easy to edit the script to pull out data for other questions by changing the search string that identifies the questions (or the page that gets extracted from the PDF). 
  
It would probably be better to get all of the data into a single file, but for now it's good enough to just have it extracted and waiting to be joined to district geographies. This next step will be the subject of another post. 
  
# Full script

```r
library(tidyverse)
library(stringr)
library(tabulizer)
library(rvest)

nfhs_site <- "http://rchiips.org/nfhs/districtfactsheet_NFHS-4.shtml"

state_pages <- read_html(nfhs_site) %>% 
  html_nodes('select') %>% 
  map(~html_nodes(.x, 'option') %>% 
        html_attr('value') %>% 
        gsub(pattern = '\\t|\\r|\\n', replacement = '')
  )
  
base_url <- "http://rchiips.org/nfhs/"

state_urls <- list()
for (i in 1:length(state_pages[[1]])){
  url <- paste0(base_url, state_pages[[1]][i])
  state_urls[[i]] <- url 
}

unlist(state_urls) # flatten the list
state_urls <- state_urls[-1] # remove a blank entry

district_pdfs <- list()
for (i in state_urls){
  district_pdfs[[i]] <- read_html(i) %>% html_nodes('option') %>% html_attr('value')
}

ifelse(!dir.exists("data"), dir.create("data")) # check if data directory exists, if not create it. 

for (i in district_pdfs){ #do any filtering of states here - it can take a long time!
  d_code <- str_sub(i[2], start = 6, end=7)
  
  dir.create(file.path(paste0("data/", d_code)), recursive=TRUE)

  for (p in i[-1]){
    download.file(paste0("http://rchiips.org/nfhs/", p), paste0("data/", d_code, "/", str_sub(p, start = 9)),mode="wb")
  }
}

files <- list() #  reset from previous run 
files <- list.files("data/", pattern=".pdf", recursive=TRUE, full.names=TRUE) # if you don't want to run for all states, change the directory here

for (f in files){
  df_results <- extract_tables(f, pages = 4)
  df2 <- data.frame(df_results)
  
  x1 <- df_results[[1]][1,1]
  x2 <- df_results[[1]][2,2]
  colnames(df2) <- c(x1, x2)
  df2 <- df2[-1,]
  df2 <- df2[-1,]
  
  q68_71 <- df2 %>% filter(str_detect(Indicators, "68.")|str_detect(Indicators, "69.")|str_detect(Indicators, "70.")|str_detect(Indicators, "71."))
  
    # if cols are rural and total, set flag 
  if (colnames(q68_71)[2] == "Rural Total") {RT <-  TRUE} else {RT <- FALSE}
  
  # if cols are urban and total, set flag 
  if (colnames(q68_71)[2] == "Urban Total") {UT <- TRUE} else {UT <- FALSE}
  
  # if cols are urban, rural and total, set flag 
  if (colnames(q68_71)[2] == "Urban Rural Total") {URT <- TRUE} else {URT <- FALSE}

  # split columns and rename depending on flag  
  if (RT == TRUE){
    q68_71["Rural"] <- str_split_fixed(q68_71$`Rural Total`, " ", 2)[,1] # insert split column into data.frame
    q68_71["Total"] <- str_split_fixed(q68_71$`Rural Total`, " ", 2)[,2]
    q68_71["Rural Total"] <- NULL    # remove original column 
    RT <- FALSE                   # reset the flag 
  }
  if (UT == TRUE){
    q68_71["Urban"] <- str_split_fixed(q68_71$`Urban Total`, " ", 2)[,1]
    q68_71["Total"] <- str_split_fixed(q68_71$`Urban Total`, " ", 2)[,2]
    q68_71["Urban Total"] <- NULL 
    UT <- FALSE
  }
  if (URT == TRUE){
    q68_71["Urban"] <- str_split_fixed(q68_71$`Urban Rural Total`, " ", 3)[,1]
    q68_71["Rural"] <- str_split_fixed(q68_71$`Urban Rural Total`, " ", 3)[,2]
    q68_71["Total"] <- str_split_fixed(q68_71$`Urban Rural Total`, " ", 3)[,3]
    q68_71["Urban Rural Total"] <- NULL
    URT <- FALSE
  }
    write_csv(q68_71, path = file.path(paste0("data/", str_sub(f, start = 9, end = 10), "/", str_sub(f, start = 9, end = -5), ".csv")), append = FALSE, col_names = TRUE)
  }
  ```
  
# Footnotes
[^1]:  [Tidyverse: rvest]( https://github.com/tidyverse/rvest) //  [Stack Overflow: Scrape and loop with Rvest](https://stackoverflow.com/questions/53679009/scrape-and-loop-with-rvest) // [Stack Overflow: How to read an HTML list from a webpage into R](https://stackoverflow.com/questions/42259300/how-to-read-an-html-list-from-a-webpage-into-r)
[^2]:  [Function of the day: dir.create](http://rfunction.com/archives/2432),  [Master Data Analysis: Working with files and folders in R](https://www.masterdataanalysis.com/r/working-with-files-and-folders-in-r/)
[^3]:  [Stack Overflow: How to index an element of a list object in R](https://stackoverflow.com/questions/21091202/how-to-index-an-element-of-a-list-object-in-r) // [Stack Overflow: How can two strings be concatenated?](https://stackoverflow.com/questions/7201341/how-can-two-strings-be-concatenated) // [Stack Overflow: How to remove last n characters from every element in the R vector](https://stackoverflow.com/questions/23413331/how-to-remove-last-n-characters-from-every-element-in-the-r-vector)
[^4]:  [Stack Overflow: Problems with Downloading pdf file using R](https://stackoverflow.com/questions/9280243/problems-with-downloading-pdf-file-using-r)
[^5]:  [tabulizer: Extract Tables from PDFs]( https://cran.r-project.org/web/packages/tabulizer/readme/README.html) // [Introduction to tabulizer](https://cran.r-project.org/web/packages/tabulizer/vignettes/tabulizer.html) // [ROpenSci: Tabulizer tutorial]( https://ropensci.org/tutorials/tabulizer_tutorial/)
[^6]:  [Stack Overflow: How to loop over files in different directories](https://stackoverflow.com/questions/18751361/how-to-loop-over-files-in-different-directories)
[^7]:  [Stack Overflow: Assign headers based on existing row in dataframe in R](https://stackoverflow.com/questions/20956119/assign-headers-based-on-existing-row-in-dataframe-in-r)
[^8]:  [Tidyverse: Write a data frame to a delimited file](https://readr.tidyverse.org/reference/write_delim.html)
[^9]:  [Sebastian Sauer: Some tricks on dplyr::filter](https://sebastiansauer.github.io/dplyr_filter/) // [Stack OVerflow: Filtering row which contains a certain string using dplyr](https://stackoverflow.com/questions/22850026/filtering-row-which-contains-a-certain-string-using-dplyr)
