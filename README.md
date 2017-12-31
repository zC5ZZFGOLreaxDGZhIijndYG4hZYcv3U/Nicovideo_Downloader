# Nicovideo_Downloader
A command-line utility which allows efficient downloads of all videos on nicovideo under a given tag, or uploaded by a given user.
It will download various pieces of metadata about each video, such as the tags, uploader id, number of views, number of comments, and so on, and store this information in a mysql database.

It's awkwardly written, but it should get the job done. 

This is a work in progress.

Dependencies:
1. ffmpeg
2. youtube-dl
3. mysql
4. various python libraries

To take care of the above, install docker and docker-compose, and then run install.sh with sudo from the nicovideo_downloader directory.
Should be usable on windows, apple OS, and whatever else, provided you can install docker and docker-compose, and then run the installation script. I'm continuously working on streamlining the installation and usage.


Usage:

docker exec nicovideodownloader_python_1  python3 ./nicovideo_downloader.py <Tag or Channel> <fillStack, dlStack, or both> -u <nico username> -p <nico password> -mp <mysql root password (root by default)> -mu <mysql root username, which is 'root'> <the specific tag, or channel id, depending on what you specified previously> -db <the database name, which should be 'nico_archive' unless it was altered>

Videos should be downloaded into the Videos subdirectory of the nicovideo_downloader folder.


Overview of operations:
fillStack for tags will attempt to retrieve all videos under the specified tag by using nicovideo's API for videos of a given tag for a specific date. Only entries whose upload date is greater than or equal to the most recent entry stored will be checked. So, for example, if I run fillStack for particular tag and store all associations until Dec 10, 2017, and then I run it again, it will check nicovideo's entries for that tag starting on December 10, and stop after reaching today's date.
dlStack will attempt to download, in descending order by upload date, all videos which have been associated with that particular tag (by fillStack) which have not been downloaded (present in the "nicovideo" table) or marked as deleted (present in the "delVideos" table).
These operations for channels are similar, but rather than using nicovideo's api to find associations between users and videos, nicochart's api is used. Nicochart seems to be frequently down, I'm not sure why, so that could cause the operation to fail.
