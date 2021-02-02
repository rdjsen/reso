# ResoBot
Telegram Bot to track New Years Resolutions

A telegram bot that will track new years resolutions for users.  The bot allows users to add, delete, and update new years resolutions with Telegram.  It can also display the status for each resolution, compared to the target pace for that point in the year.

The following commands are available:  
/start - Starts the bot.  This will also DELETE any currently tracked resolutions.  
/track - Displays the current status of each tracked resolution.  Compares current progress to the "pace" for this point in the year.  
/add - starts a dialogue to add a new resolutions.  Options are one-off (completed once during the year) and yearly total (complete a target amount during the year).  
/update - Goes through each resolution one by one and asks for an update.  
/delete <num> - Deletes resolution <num>.  Specify the number listed in /track.  
/help - lists available commands.  
  
Planned features:  
A reminder command, so the bot will message you once a week to ask for an update

