---
title: '2024 ▸ 08 ▸ Weeknote'
date: 2024-02-27
excerpt: 
 
editedDate:
tags: posts
draft: false
---

This week I had calls with various communities of practice I’m a member of — on Python, Information Management, geospatial and data science. That’s a lot of CoP calls for one week! For the Python and geospatial ones, I facilitate the calls, for the others I just attend.

# Python User Group

I’ve been gathering together other people from BRC who use Python for a monthly call where we hear from someone on how they’ve been using Python in their work. It’s been a good way to meet people in other teams using the same tools for different purposes (other people’s use of Python is more statistics and data science-oriented, whereas mine is more data engineering).

This week, we heard from a colleague in the [Insight team](https://medium.com/insight-and-improvement-at-british-red-cross) who shared a project to map out loneliness trends (available on [GitHub](https://github.com/humaniverse/loneliness)). The project implemented an [ONS method](https://www.ons.gov.uk/peoplepopulationandcommunity/wellbeing/methodologies/measuringlonelinessguidanceforuseofthenationalindicatorsonsurveys) for generating a proxy measure for loneliness by looking at GP prescriptions associated with loneliness, and the Python code was then published in an R repo to be consistent with the team’s other products.

There were interesting tangents on combining R and Python, the benefits of virtual environments and packaging/publishing workso it’s more accessible outside of the team that made it.

# RC Geo call 
On our twice-monthly Red Cross/Red Crescent geospatial community of practice — [RC Geo](https://medium.com/digital-and-innovation-at-british-red-cross/red-cross-geo-calls-2023-summary-b5af16caae15) — we heard an update from the IFRC’s [GO platform](https://go.ifrc.org/about) team about the geospatial side of the project. The priorities for the first part of 2024 are implementing a system to manage data on where RC National Societies have infrastructure (mostly different types of buildings, e.g. health or education facilities ). [This video](https://youtu.be/izIb-H56gms?si=6e40yEKZvUPOS1jd&t=2379) from a separate event has an overview from the team.

# Vehicle location history data
I’m running a proof of concept project to see what use we can make of the data we have from BRC vehicles’ GPS trackers. Coming back to it this week, I ran into an issue trying to expand our usage of the API that provides the vehicle location history. After making a script that pulls the last 24 hours of activity for each vehicle, I tried to expand this to pull 90-day history for a smaller group of vehicles from one department. The API returned couple of errors (depending on the parameters I used) but the API is poorly documented so it wasn’t clear what the errors meant or what parameters would make the API call work.

Luckily, the provider is very quick to respond to emails — they told me that requesting activity over longer time periods puts too much strain on the server, so requests are restricted to 24 hour periods in the last week. As a workaround, I’ll start building a historic dataset locally — it will take a bit longer to get to a point where I can see analysis over 90 days but as this isn’t an urgent task we can afford to wait.

# Broken flooding layer on ArcGIS Online
I’ve had a script running for a while which updates a layer on ArcGIS Online with the latest flood warnings for England. (Data for Wales is published through a separate API, and data for Scotland isn’t available yet.) A colleague flagged that it hasn’t been updating so I spent a morning troubleshooting it. In the end it turned out to be an invalid column name and invalid attribute data in a couple of other columns (where the values were nested JSON data). None of these columns were needed for the dataset so I left them out and the process started working again.

It took me a long time to figure out what was causing the issue, even though I’ve come across both types of error before — so I’ve started a troubleshooting checklist for the next time something like this happens.
