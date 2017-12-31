import pymysql
import datetime
import requests
import http.cookiejar
import re,  calendar, requests, json, time, glob
import urllib
from bs4 import BeautifulSoup
import os
import uuid
import threading
import subprocess
import shlex
import math
import glob
import shutil
from urllib3.exceptions import MaxRetryError, NewConnectionError
import socket
from requests.exceptions import ConnectionError
import sys

def main():

    args = sys.argv[1:]
    values = []
    i = 0

    username = ""
    password = ""
    mysql_username = ""
    mysql_password = ""
    db_name = ""
    #default ipv4 addr of mysql server running in docker container
    host = "10.20.0.5"
    using_docker = True
    
    
    while(i<len(args)):
        if(args[i] == "-u"):
            username = args[i + 1]
            i += 1
        elif(args[i] == "-p"):
            password = args[i + 1]
            i += 1
        elif(args[i] == "-mu"):
            mysql_username = args[i + 1]
            i+= 1
        elif(args[i] == "-mp"):
            mysql_password = args[i + 1]
            i+= 1
        elif(args[i] == "-db"):
            db_name = args[i + 1]
        elif(args[i] == "-hn"):
            host = args[i+1]
            i+= 1
        elif(args[i] == "-d"):
            using_docker = False
        else:
            values.append(args[i])
        i += 1

        
    n = nicoExtractor(username, password, mysql_username, mysql_password, db_name, host, using_docker)

    if(values[0] == "Channel"):
        if(values[1] == "fillStack" and len(values) >= 3):
            n.fillChanStack(values[2])
        elif(values[1] == "dlStack" and len(values) >= 3):
            n.dlChanStack(values[2])
        elif(values[1] == "both" and len(values) >= 3):
            n.fillChanStack(values[2])
            n.dlChanStack(values[2])
        else:
            print(args)
            print("Invalid arguments. Format: nicovideo_dl <Channel or Tag> <fillStack or dlStack> <specific tag or channel>", file=sys.stderr)
            return

    elif(values[0] == "Tag"):
        if(values[1] == "fillStack" and len(values) >= 3):
            n.fillTagStack(values[2])
        elif(values[1] == "dlStack" and len(values) >= 3):
            n.dlTagStack(values[2])
        elif(values[1] == "both" and len(values) >= 3):
            n.fillTagStack(values[2])
            n.dlTagStack(values[2])
        else:
            print(values)
            print("Invalid arguments. Format: nicovideo_dl <Channel or Tag> <fillStack or dlStack> <specific tag or channel>", file=sys.stderr)
            return
    else:
        print(args)
        print("Invalid arguments. Format: nicovideo_dl <Channel or Tag> <fillStack or dlStack> <specific tag or channel>", file=sys.stderr)
        return

    
    
class nicoExtractor():
    #these don't actually need to be instance variables; will only ever have one instance. It doesn't particularly matter.
    def __init__(self, username, password, mysql_username, mysql_password, db_name, host, using_docker):
        self.lower_bound = "2007-1-1"
        self.err_log_loc = "./Videos/error_logs/"
        self.tmp_video_loc = os.getcwd() + "/Videos/new_tmp/"
        self.cookie_file = os.getcwd() + "/Videos/cookies4.txt"
        self.thumbnail_path = "./Videos/Thumbnails/"
        self.description_path = "./Videos/Descriptions/"
        self.json_path = "./Videos/json/"
        self.deleted_path = "./Videos/Deleted/"
        self.username = username
        self.password = password
        self.mysql_username = mysql_username
        self.mysql_password = mysql_password
        self.db_name = db_name
        self.host = host
        self.using_docker = using_docker

        self.video_dir_loc = os.getcwd() + "/Videos/"

        if(not os.path.exists(self.video_dir_loc)):
            os.makedirs(self.video_dir_loc)
        if(not os.path.exists(self.description_path)):
            os.makedirs(self.description_path)
        if(not os.path.exists(self.json_path)):
            os.makedirs(self.json_path)
        if(not os.path.exists(self.deleted_path)):
            os.makedirs(self.deleted_path)
        if(not os.path.exists(self.thumbnail_path)):
            os.makedirs(self.thumbnail_path)
        if(not os.path.exists(self.tmp_video_loc)):
            os.makedirs(self.tmp_video_loc)
        if(not os.path.exists(self.err_log_loc)):
            os.makedirs(self.err_log_loc)

        
    def get_session(self):
        session_requests = requests.Session()
        cj = http.cookiejar.MozillaCookieJar(self.cookie_file)
        cj.load()
        session_requests.cookies = cj
        return(session_requests)

    
    def setNewCookie(self, video_id):
        print("Loading cookie...")
        session= requests.Session()
        if(self.using_docker):
            os.system("docker run -v %s:%s vimagick/youtube-dl:latest -u '%s' -p '%s' --skip-download --cookies %s www.nicovideo.jp/watch/%s" % (self.video_dir_loc, self.video_dir_loc, self.username, self.password, self.cookie_file, video_id))
        else:
            os.system("youtube-dl -u '%s' -p '%s' --skip-download --cookies %s www.nicovideo.jp/watch/%s" % (self.username, self.password, self.cookie_file, video_id))
        self.session_requests = self.get_session()
        
    def dlTagStack(self, tag):
        query = "select video_ID from tag_dl_stack where video_ID not in (select video_ID from nicovideo where downloaded = 1) AND video_ID not in (select video_ID from delVideos) AND Tag = %s order by Upload_Date desc"
        conn = self.getNewConn()
        curs = conn.cursor()
        curs.execute(query, (tag))
        dateStack = curs.fetchall()
        self.setNewCookie(dateStack[0][0])
        for entry in dateStack:
            self.threadmanage(entry[0], "Tag: %s" % tag)

    def dlChanStack(self, uid):
        query = "select video_ID from auth_dl_stack where video_ID not in (select video_ID from nicovideo where downloaded = 1) AND video_ID not in (select video_ID from delVideos) AND author_id = %s"
        conn = self.getNewConn()
        curs = conn.cursor()
        curs.execute(query, (uid))
        chanStack = curs.fetchall()
        self.setNewCookie(chanStack[0][0])

        for entry in chanStack:
            self.threadmanage(entry[0], "Channel: %s" % uid)

    def threadmanage(self, video_id, method):
        time.sleep(30)
        if(threading.activeCount() < 5):
            print("activating thread for %s" % video_id)
            threading.Thread(target=self.vidDl, args=(video_id, method)).start()
        else:
            time.sleep(30)
            self.threadmanage(video_id, method)

            
    def vidDl(self, video_id, method, overwrites = False):
        try:
            errLogLoc = "Error_Log" + str(threading.get_ident())
            nicoLink = "www.nicovideo.jp/watch/" + str(video_id)
            if(overwrites):
                sum = "youtube-dl --write-info-json --cookies '%s' --no-continue --write-thumbnail --write-description -o '"  % self.cookie_file + str(self.tmp_video_loc) + "/%(id)s.%(ext)s' -v {link}"
            else:
                sum = "youtube-dl --write-info-json --cookies '%s' --no-overwrites --continue --write-thumbnail --write-description -o '" % self.cookie_file + str(self.tmp_video_loc) + "/%(id)s.%(ext)s' -v {link}"

            arg1 = sum.format(link = nicoLink)
            if(self.using_docker):
                arg1 = 'docker run -v %s:%s vimagick/youtube-dl:latest ' % (self.video_dir_loc, self.video_dir_loc) + arg1.replace("youtube-dl ", "")

            dbConnection = self.getNewConn()
            dbIterator = dbConnection.cursor()
            #dbIterator.execute("select * from nicovideo where downloaded = '1' and video_ID = '" + str(video_id) + "'")
            #output = dbIterator.fetchall()
            #if it isn't deleted, and hasn't already been downloaded.
            if((not self.isDeleted(video_id))):
                a = subprocess.Popen(shlex.split(arg1), stderr = subprocess.PIPE, stdout=subprocess.PIPE)
                #will block until subprocess returns
                stdout, stderr = a.communicate()

                writeF(self.err_log_loc + str(video_id) + " " + str(datetime.datetime.now()) + ".txt", stdout.decode() + "\n\n" + stderr.decode())
                isLowQuality = 0
                if("low" in stdout.decode()):
                    isLowQuality = 1

                stdout_stderr =  stdout.decode() + "\n\n" + stderr.decode()
                
                #keep trying until it finishes correctly
                if("ERROR: content too short" in stdout_stderr or "Errno 104" in stdout_stderr):
                   self.vidDl(video_id, method)

                #check to see if everything was downloaded correctly
                videoArr = glob.glob(self.tmp_video_loc + "%s.flv" % video_id)
                videoArr.extend(glob.glob(self.tmp_video_loc + "%s.swf" % video_id))
                videoArr.extend(glob.glob(self.tmp_video_loc + "%s.mp4" % video_id))
                thmbnailArr = glob.glob(self.tmp_video_loc + "%s.jpg" % video_id)
                jsonArr = glob.glob(self.tmp_video_loc + "%s.info.json" % video_id)
                descArr = glob.glob(self.tmp_video_loc + "%s.description" % video_id)


                assert len(videoArr) == 1
                assert len(thmbnailArr) == 1
                assert len(jsonArr) == 1
                assert len(descArr) == 1

                ffmpegCom = "ffmpeg -v error -i %s -f null -" % videoArr[0]
                if(self.using_docker):
                    ffmpegCom = "docker run -v %s:%s  jrottenberg/ffmpeg:latest " % (self.video_dir_loc, self.video_dir_loc) + ffmpegCom.replace("ffmpeg ", "")
                b = subprocess.Popen(shlex.split(ffmpegCom), stderr = subprocess.PIPE, stdout=subprocess.PIPE)
                ffmpegStdout, ffmpegStderr = b.communicate()

                #if ffmpeg can't deal with it, something went wrong with the download, and we should replace the content of the video.
                if("get_buffer() failed" in str(ffmpegStderr)):
                    print("Ffmpeg err on %s" % video_id)
                    #mark as an incorrect download
                    inpNew_Filename = str(video_id) + str(uuid.uuid1())
                    shutil.copyfile(videoArr[0], self.tmp_video_loc + "bad/" + inpNew_Filename)
                    #apparently not being overwritten
                    if(os.path.exists(self.tmp_video_loc + "bad/" + inpNew_Filename)):
                        os.unlink(videoArr[0])
                    errConn = self.getNewConn(cursorclass=pymysql.cursors.DictCursor)
                    errIterator = errConn.cursor()
                    errIterator.execute("INSERT INTO erroneous_dls (video_ID, new_filename, ffmpeg_stderr) VALUES (%s, %s, %s)", (video_id, inpNew_Filename, ffmpegStderr))
                    errConn.commit()
                    #overwrite incorrect dl
                    return self.vidDl(video_id, method, True)
                
                try:
                    self.dbInteract(video_id, method, quality = isLowQuality)
                    self.copyDriver(self.tmp_video_loc, video_id)
                except Exception as e:
                    print("Error in mysql interaction for " + str(nicoLink) + ": "+ str(e))

        #deal with assertionerrors in another way
                    
        except (ConnectionError, socket.gaierror, MaxRetryError, NewConnectionError) as e:
            dbIterator.close()
            dbConnection.close()
            print(str(type(e).__name__), "on %s" % video_id)
            time.sleep(20)
            return self.vidDl(video_id, method, overwrites)


    def isDeleted(self, video_ID):
        url = "http://ext.nicovideo.jp/api/getthumbinfo/%s" % video_ID
        result = requests.get(url, headers = dict(referer = url)).content.decode()
        soup = BeautifulSoup(result, "lxml")
        deletionIndication = soup.find('code')
        if(deletionIndication != None and deletionIndication.string == "DELETED"):
            print("The video has been deleted.")
            dbConnection = self.getNewConn(cursorclass=pymysql.cursors.DictCursor)
            dbIterator = dbConnection.cursor()
            dbIterator.execute("INSERT INTO delVideos (video_ID) VALUES (%s)", (video_ID))
            dbConnection.commit()
            dbConnection.close()
            return True
        print("The video has not been deleted")
        return False

    #start at the oldest applicable entry and dl in ascending order so we can make the assumption that everything prior to the most recent date has been dled.
    def fillTagStack(self, tag):
        mostRecentDate = self.getLatestInStackForTag(tag)
        now = datetime.datetime.now().date()
        while(now > mostRecentDate):
            self.downloadDate(tag, mostRecentDate)
            mostRecentDate += datetime.timedelta(days=1)
        print("Stack filled for tag %s" % tag)

    def downloadDate(self, tag, date, pageNumber = 1):
        print("Now downloading from: %s" % date)
        url = "http://www.nicovideo.jp/search/%s?page=%ssort=h&order=d&start=%s&end=%s" % (tag, pageNumber, date, date)
        
        #resp = requests.get(url, headers = dict(referer = url)).content.decode()
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content, "lxml")
        #i = 1

        #string will be found if the page doesn't exist for this query.
        resp_content = resp.content.decode()
        if(resp_content.find("キーワードに一致する結果が見つかりませんでした") != -1 or resp_content.find("There were no results found matching your criteria") != -1):
            return
        
        dbConnection = self.getNewConn()
        dbIterator = dbConnection.cursor()
        i = 1
        for link in soup.find_all('a', 'itemThumbWrap', href=re.compile('^.*search_key_video.*$')):
            print(i)
            i += 1
            video_id =link['href'].split('/')[2].split("?")[0]
            conn = self.getNewConn()
            curs = conn.cursor()
            try:
                curs.execute("INSERT INTO tag_dl_stack (video_ID, Upload_Date, Tag) VALUES (%s, %s, %s)", (video_id, date, tag))
                conn.commit()
            except pymysql.err.IntegrityError as e:
                print("Integrity error: %s" % e)
                
            conn.close()
        dbConnection.close()
        if(i == 33):
            self.downloadDate(tag, date, pageNumber + 1)

    def getNewConn(self, **kwargs):
        return pymysql.connect(host = self.host, port = 3306, user=self.mysql_username, password = self.mysql_password, database=self.db_name, charset='utf8', **kwargs)
    
    def getLatestInStackForTag(self, tag):
        conn = self.getNewConn()
        curs = conn.cursor()
        #something like this
        sql = "select Upload_Date from tag_dl_stack where Tag = %s order by Upload_Date desc LIMIT 1"
        curs.execute(sql, (tag,))
        res = curs.fetchall()
        #i think this is right?
        if(len(res) == 0):
            return datetime.datetime.strptime(self.lower_bound, "%Y-%m-%d").date()
        return res[0][0]

    def fillChanStack(self, uid, pageNum = 1):
        resp = requests.get("http://www.nicochart.jp/user/" + str(uid) + "?page=" + str(pageNum)).content.decode()
        #message displayed when page is invalid
        if("に一致する動画は見つかりませんでした" in resp ):
            return
        soup = BeautifulSoup(resp, "lxml")
        for link in soup.find_all('a', href=re.compile('^watch/')):
            authConn = self.getNewConn(cursorclass=pymysql.cursors.DictCursor)
            authIterator = authConn.cursor()
            video_id = link['href'].split("/")[-1]
            try:
                authIterator.execute("INSERT INTO auth_dl_stack (video_ID, author_id) VALUES (%s, %s)", (video_id, uid))
                authConn.commit()
                print("Added video %s" % video_id)
            #if a duplicate entry is inserted, we can stop, and return.
            except pymysql.err.IntegrityError as e:
                return
        self.fillChanStack(uid, pageNum + 1)
    

    def dbInteract(self, video_ID, method, quality):
        url = "http://ext.nicovideo.jp/api/getthumbinfo/%s" % video_ID
        result = self.session_requests.get(url, headers = dict(referer = url)).content.decode()
        soup = BeautifulSoup(result, "lxml")
        inpTitle = soup.find('title').string
        inpViews = soup.find('view_counter').string
        inpComments = soup.find('comment_num').string
        inpMylists = soup.find('mylist_counter').string
        inpDlDate = datetime.datetime.now()
        inpUploadDate = soup.find('first_retrieve').string.replace("T", " ").split("+")[0]
        try:
            inpAuthorName = (soup.find('user_nickname').string)
            inpUploader = soup.find('user_id').string
        except Exception as e:
            #author not listed in nicovideo, so let's try nicochart
            try:
                resultNicoChart =  urllib.request.urlopen("http://www.nicochart.jp/watch/" + inpVideo_ID)
                nicoChartSoup = BeautifulSoup(resultNicoChart, "lxml", from_encoding=resultNicoChart.info().get_param('charset'))
                inpAuthorName = nicoChartSoup.find('em', 'name').find('a').string
                inpUploader = nicoChartSoup.find("a", "nicovideo-link")['href'][29:]
            except Exception as e:
                #no author on either
                inpAuthorName = None
                inpUploader = None
            
        tags = soup.find_all('tag')

        insert ="INSERT INTO nicovideo(title, views, mylists, comments, video_ID, upload_date, uploader, method, uploader_name, downloaded,  isLowQual) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        dbConnection = self.getNewConn()
        dbIterator = dbConnection.cursor()
        dbIterator.execute(insert, (inpTitle, inpViews, inpMylists, inpComments, video_ID, inpUploadDate, inpUploader, method, inpAuthorName, "1", quality))

        authInsert = "INSERT INTO nicovideo_users (user_ID, name) VALUES (%s, %s)"
        try:
            dbIterator.execute(authInsert, (inpUploader, inpAuthorName))
        except Exception as e:
            print("Duplicate author. Error: " + str(e))

        tagInsert = "INSERT INTO nico_tags (video_ID, tag) VALUES (%s, %s)"
        for tag in tags:
            try:
                dbIterator.execute(tagInsert, (video_ID, tag.string))
            except Exception as e:
                print("Could not insert tag %s. Error%s: " % (tag.string, str(e)))

        dbConnection.commit()
        dbIterator.close()
        dbConnection.close()


    def copyDriver(self, path, video_ID):
        for f in glob.glob(str(path) + str(video_ID) + ".*"):
            file = f.split("/")[-1]
            currentFilePath = path
            f_id = file.split(".")[0]
            if(str(f_id) != str(video_ID)):
                print("Returning...")
                pass
            fileExtension = file.split(".")[-1]
            if(fileExtension == "part"):
                pass
                #copyLinearProbe(currentFilePath, file, "../Videos/Part")
            elif(fileExtension == "mp4" or fileExtension == "flv" or fileExtension == "swf"):
                self.copyLinearProbe(currentFilePath, file, self.video_dir_loc)
            elif(fileExtension == "jpeg" or fileExtension == "jpg" or fileExtension == "png"):
                self.copyLinearProbe(currentFilePath, file, self.thumbnail_path)
            elif(fileExtension == "description"):
                self.copyLinearProbe(currentFilePath, file, self.description_path)
            elif(fileExtension == "json"):
                self.copyLinearProbe(currentFilePath, file, self.json_path)
            elif(fileExtension == "unknown_video"):
                selfcopyLinearProbe(currentFilePath, file, self.deleted_path)
            else:
                print("Mysterious file type! %s" % fileExtension)

    def alreadyExists(self, path):
        dbConnection = self.getNewConn(cursorclass=pymysql.cursors.DictCursor)
        dbIterator = dbConnection.cursor()
        dbIterator.execute("SELECT * FROM nicovideo_file_migrations where original_file_location = %s", (path))
        res = dbIterator.fetchall()
        if(len(res) != 0):
            return True
        return False

    def copyLinearProbe(self, copiedFileBaseDir, copiedFileName,  destinationFilePath):
        copiedFilePath = copiedFileBaseDir + copiedFileName
        #check here for primary key of this value. If one exists, skip.
        if(self.alreadyExists(copiedFilePath)):
            print("This file has already been copied: %s" % copiedFilePath)
            return
        #don't need -n for no clobber, because it won't overwrite in any case
        comm = "cp -v --archive -l --backup=numbered '{start}' '{destination}'".format(start = copiedFilePath, destination = destinationFilePath)
        copy = subprocess.Popen(shlex.split(comm), stderr = subprocess.PIPE, stdout=subprocess.PIPE)
        stdout = copy.communicate()[0].decode()
        if(" (backup: '" in stdout):
            #will take the part of the string after splitting by backup, split by /, take the last part of the split array, then return everything in that string except the last 2 letters.
            destinationFileName = stdout.split(" (backup: '")[1].split("/")[-1][:-3]
        else:
            destinationFileName = stdout.split("/")[-1][:-2]
        if(copy.returncode != 0):
            print("Copy failure on %s!" % copiedFilePath)
            raise RuntimeError
        destinationFileLocation = destinationFilePath + destinationFileName

        #what if copiedFileName is empty?
        #path.isfile won't return true if it's pointing to a directory, so should still be fine.
        if(os.path.isfile(copiedFilePath) and os.path.isfile(destinationFileLocation)):
            print("unlinking...")
            os.unlink(copiedFilePath)
            self.logOperation(copiedFilePath, destinationFileLocation)
    
    def logOperation(self, start, finish):
        dbConnection = self.getNewConn()
        dbIterator = dbConnection.cursor()
        dbIterator.execute("INSERT INTO nicovideo_file_migrations (original_file_location, destination_file_location) VALUES (%s, %s)", (start, finish))
        dbConnection.commit()
        dbConnection.close()
    
def writeF(file, text):
    if os.path.isfile("./" + file) == False:
        createfile = open(file, "w")
    text_file = open(file, "a")
    text_file.write(str(text) + "\n")
        
main()

