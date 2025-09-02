# Week 2; Pandas Part 2

## Agenda 
0. Remind me to 
	* Start recording
	* Turn on CC's 
	* Enable screen sharing for everyone (for breakout rooms)
0. Annoucments
    * Goolge Workshop on Data Privacy (CTP Fellow Exclusive).  [All info on slack here.](https://ctpc11.slack.com/archives/C095CMC2JGG/p1756821811976879)
    * [RSVP Here ASAP](https://forms.gle/ZrBuqaD3G9FkULK2A)
0. Best way to ask questions on slack. 
    * Include a full screen shot of your error message and the code to get the error.  
    * "What did you do to debug this already?"
        * *Directly from Meta*
0. Review HW [15min]
    * Best Slack message. 
    * Share screen HW check, one error you encountered. 
0. Complete Pandas Lecture/s (Last & This Week)
0. ~~[Google Slide Lecture](https://docs.google.com/presentation/d/1uoWIMjfH70CUrHKJnckMfd6ppQTxFwDKFlonHElwpTQ/edit)[20-30min]~~
0. BREAK
0. Finding Data Live Demo [20min]
    * [Google Doc of good data sources](https://docs.google.com/document/d/1VvmTmHrURfV24owFeew33S8INOLE9iNnRFXntSFhZdc/edit) <-- please contribute
0. Cleaning Data Lecture.ipynb [45min]
0. SECRET STUFF
0. Review whats due for next week 
0. Weekly survey. 


# Homework [~1.5hrs]
_All HW's are due 1 day before the next class begins by 12:01pm (Noon)._  
_Submit them via the [HW Submssions Form](https://forms.gle/MFH173MZaQ5TquCB6)_  

### Pre-Class for Next Weeks Analytics Lecture [~30min] & Slack Message #1
After watching the following videos below... 
Post image in slack thread with one data viz YOU loved or YOU hated and why you felt that way. (I'm looking for the story and impact it had on your life.)

0. [Storytelling with data](https://www.youtube.com/watch?v=hVimVzgtD6w&ab_channel=TED) Ted (not TedX). [20min]
0. [BBC: Joy of Stats](https://www.youtube.com/watch?v=jbkSRLYSojo&ab_channel=BBC) [4min]
0. [Seaborn Tutorial](https://www.youtube.com/watch?v=LnGz20B3nTU&ab_channel=AbsentData) [15min]
0. [Charts in Seaborn](https://www.youtube.com/watch?v=Iui04c3tbH8&ab_channel=FaniloAndrianasolo) [4min]
0. Optional: [Joy of stats full documentary](https://www.gapminder.org/videos/the-joy-of-stats/) [1hr]

### Exercise [~45min]
0. MAKE A COPY of the Exercise file. 
0. Complete the questions. 
0. Create Pull Request

### Slack Message #2:
0. SLACK HW: One think you wish we covered in the Pandas Cleaning Data Series

_[end of hw section]_
---

# Finding Data in the Wild

#### Finding Data your project. 
0. Here we are going to mock data for a project about dogs. 
0. Google dog dataset. [google it, find kaggle and data world and stanford and opennyc]
0. Go to the dataworld link, about 5 links down you'll see the dog [NYC Dog Licensing Dataset](https://data.world/city-of-ny/nu7n-tubp). 
0. Point out it was last updated 2021-07-29.
0. Then go the the source, and see the source was updated this year. 
0. In the source, point out the data dictionary and user guide, scroll down to see the column descriptons. 
0. maybe sidetrack on doing one of those evolution trees (how to look how to make one of those evolution trees for dogs)
    * google dog evolution tree data
    * find research gate
    * see realted images
    * see the word 'phylogenetic', thats a new google term you can use. 
    * open paper, use command+f search for 'data' or 'download' 


#### [How I got the data for this lecture]
0. Google, ["pandas data cleaning tutorial"]((https://www.google.com/search?q=pandas+data+cleaning+tutorial&oq=pandas+data+cleaning+tutorial+&gs_lcrp=EgZjaHJvbWUyCAgAEEUYHhg5Mg0IARAAGIYDGIAEGIoFMg0IAhAAGIYDGIAEGIoFMg0IAxAAGIYDGIAEGIoFMgoIBBAAGIAEGKIEMgoIBRAAGIAEGKIEMgoIBhAAGIAEGKIE0gEINTAzNWowajGoAgCwAgA&sourceid=chrome&ie=UTF-8))
0. Open a few links. But end up on the [w3 schools tutorial](https://www.w3schools.com/python/pandas/pandas_cleaning.asp). 
0. Try and get that data. 
    - I did, copy and paste into sublime and did removing whitespace tricks in there. 
    - Then copy and did pd.read_clipboard() which works very well. 
0. Now load that data into the notebook and flow into the data cleaning lecture. 


## Cleaning data topics
0. Loading data, csvs, tsv, .zip, excels, clipboard, sql db
0. Whats the deal with missing values and NaNs. 
    * Identifying NaNs None 
    * dropping NaNs
    * Filling NaNs
0. Duplicate Rows
0. Annoying headers 
0. Dates
0. Numbers [TODO]
    * Numbers with commas 
    * Money Symbols
    * Percent symbols
    * Postal codes (numbers starting with 0)

0. String Stuff
    * splitting strings in columns
    * STRIPPING and REPLACING
    * Quotes
    * regex
0. Iterating through columns.
0. Iterating through rows. 

0. Exporting data and the infamous `Unnamed:` 
0. Multiple Datatypes in One Column [more help here](https://realpython.com/python-data-cleaning-numpy-pandas/#tidying-up-fields-in-the-data) and [here](https://www.osedea.com/insight/data-cleaning-with-python)


0. Delimiters
6. JSONs and Dictionaries 
0. Loading multiple files [nice to have]
7. Loading files from web. [do in intro]
9. Quickly throwing in sheets. [`pd.to_clipboard()`]
6. Encoding [nice to have] 


# HW Assignment
Due 1 day before class at 12:01pm (Noon).

## Pre-Class Videos
1. Watch this 
2. Do this tutorial 


## Exercise
0. Make a copy of the exercise file (see instructions above).
0. Complete the code in your new copy of the exercise file. 
0. Push that file to your fork. 
0. Copy that exact link, and paste it into the HW submission sheet. 


## LinkedIn Post



### Other shit
[NYC Open Data proposals](https://2025.open-data.nyc/) due Nov 1st.
