# Nicovideo_Downloader
A command-line utility which allows efficient downloads of all videos on nicovideo under a given tag, or uploaded by a given user. Channel download currently doesn't work, I'll fix it later. Tag download works fine.

It's awkwardly written, but it should get the job done. 

This is a work in progress.

Dependencies:
1. ffmpeg
2. youtube-dl
3. mysql (create a database with whatever name, then import the sql file in this project to create the schema)
4. various python libraries (use the command "pip3 install -r requirements.txt" to install these)

Usage:
nicovideo_downloader (Tag or Channel) (dlStack or fillStack) (the specific tag or channel user id you want to download from) -u (your nicovideo username) -p (your nicovideo password) -mu (mysql login username) -mp (mysql login password) -db (database name that you created)
  
fillStack will fetch all of the relevant entries (for example, retrieving all of the entries under that tag), and store them in the database.
dlStack will download everything that's listed for that tag which hasn't already been downloaded.

