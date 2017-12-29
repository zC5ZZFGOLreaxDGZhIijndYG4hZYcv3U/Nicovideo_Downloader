# Nicovideo_Downloader
A command-line utility which allows efficient downloads of all videos on nicovideo under a given tag, or uploaded by a given user.

It's awkwardly written, but it should get the job done. 

This is a work in progress.

Dependencies:
1. ffmpeg
2. youtube-dl
3. mysql
4. various python libraries

To take care of the above, install docker and docker-compose, and then run install.sh with sudo.


Usage:

docker exec nicovideodownloader_python_1  python3 ./nicovideo_downloader.py <Tag or Channel> <fillStack, dlStack, or both> -u <nico username> -p <nico password> -mp <mysql root password (root by default)> -mu <mysql root username, which is 'root'> <the specific tag, or channel id, depending on what you specified previously> -db <the database name, which should be 'nico_archive' unless it was altered>

Videos should be downloaded into the Videos subdirectory of the nicovideo_downloader folder.


