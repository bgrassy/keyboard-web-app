# keyboard-web-app
Version 2 (https://keyboard-layout-generator.herokuapp.com):

This version added additional capabilities which help with parsing longer text entries. Before, for any given text entry the same
methodology was used to calculate it. Consequentially, the time increased to massive proportions if the text was longer than a
certain point. To combat this, I returned to my original idea, which starts off by going through long pieces of text and
determining the most frequent letter pairs, and then calculating layouts which faciltate ergonomically optimized typing for those
respective pairs. I also made it so that there is a maximum time limit of 15 seconds when finding layouts, which should be more
than reasonable for general use; however, due to the slow processing speeds of the web app, it is necessary to do so to avoid server
timeouts. This is easy to fix if someone wishes to eliminate the time limit by entering app.py and removing the added condition for
the break in the for loop. 
