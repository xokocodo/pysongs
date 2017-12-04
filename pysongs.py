import crawl
import database
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pdb
import time
import urllib2
import database
import os
import glob
import socket
from threading import Thread
from pandora import APIClient, clientbuilder
import unidecode

from utils import *
import database
import version
import crawl

class system():

    def __init__(self):
        self.db = database.SongList(CSV_FILE)
        self.db.load()
        self.crawlers = []
        
        for account in PANDORA_ACCOUNTS:
            pandora_crawler = crawl.PandoraCrawler(self.db, account[0], account[1])
            self.crawlers.append(pandora_crawler)

    def spawnGUI(self):
        import gui

    def loadDB(self):
        self.db.load()       

    def saveDB(self):
        self.db.save()
      
    def crawl(self):
        for crawler in self.crawlers:
            crawler.crawl()
        self.db.save()
        
    def getMP3s(self):

        log("Downloading MP3s for URLs")
        
        # Get Targets
        targets = self.db.getSongsByProperty('status', READY_TO_DOWNLOAD)
    
        num = 0
    
        for target in targets:
            num += 1
            log("\n%d of %d" % (num, len(targets)))

            log("Beginning Download Sequence for %s..."%(target.url))
            
            # Open the browser to link
            browser.get(YT2MP3_URL)
            assert YT2MP3_TITLE in browser.title

            # Enter Video URL and Submit
            browser.find_element_by_id("input").send_keys('https://www.youtube.com/watch?v=' + target.url)
            browser.find_element_by_id("submit").click()

            # Wait for conversion to finish
            log("\tWaiting for Conversion...")
            for i in range(20):
                try:
                    a = browser.find_element_by_id('file')
                    if a.get_attribute('href') != u'' and len(a.get_attribute('href')) != 0:
                        break
                    time.sleep(1)
                except:
                    time.sleep(1)

            # Get Download Link
            log("\tLooking for Download Link...")
            download_link = a.get_attribute('href')
            log("\tDownload Link: %s"%(download_link))

            # Check for Bad Link/Conversion
            fail = "none"
            video_title = browser.find_element_by_id("title").text
            if fail in video_title or download_link == None or download_link == '':
                log("\tBad Conversion. Skipping.")
                continue
                
            # Download
            log("\tDownloading...")

            thread = Thread(target = browser.get, args = (download_link, ))
            thread.start()

            dl_file = None
            for i in range(600):
                try:
                    dl_file = max(glob.iglob(DOWNLOAD_PATH + '\*.crdownload'), key=os.path.getctime)
                except:
                    time.sleep(0.1)
                if dl_file:
                    break

            if dl_file:
            
                dl_file = dl_file.replace(".crdownload", "")
                log("\tFilename = %s" % dl_file)

                # Wait for Download to Complete
                for i in range(60):
                    complete = os.path.exists(dl_file)
                    if not complete:
                        time.sleep(1)
                    else:
                        break

                if not complete:
                    log("\tBad Download - Not Complete. Skipping.")
                    continue

            else:
                log("\tBad download - Too Fast. Skipping ")
                continue
                
            # Get Filename
            for i in range(10):
                try:
                    f = open(dl_file, "r")
                    f.close()
                    target.filename = dl_file
                    break
                except:
                    time.sleep(1)
                    log(".", newline=False)

            if not target.filename or target.filename == "":
                log("\tBad download - Didn't Get File Name. Skipping ")
                continue  
            
            # Change Metadata
            log("\tUpdating metadata for %s..."%target.name())
            try:
                changeTags(dl_file, target)
            except:
                log("\tFailed to modify metadata. Skipping.")
                continue
            
            # Route
            log("\tRouting file to proper folders...")
            try:
                route(dl_file, target)
            except:
                log("\tFailed to Route File. Skipping.")
                continue

            # All Passed
            log("\tMarking %s as downloaded..."%(target.name()))
            target.status = DOWNLOADED
            target.filename = dl_file
            
            self.db.save()

    def getURLs(self):
        log("Getting URLs for Songs")
        
        # Get Targets
        targets = self.db.getSongsByProperty('status', ADDED)

        num = 0
        
        for song in targets:
        
            num += 1
            log("\n%d of %d" % (num, len(targets)))
        
            log("%s:" % song.name())

            # Create Text Query
            if "mix" not in song.title.lower():
                query = "%s %s lyrics"%(song.artist, song.title)
            else:
                query = "%s"%(song.title)
                
            # Create YT friendly query
            query = query.replace(" ", "+")
            query = query.translate(None, '!@#$%^&*()=~`"/\:;.,<>?`') # Removes Special Chars
            log("\tQuery: %s:" % query)
			
            # Open Browser to Search

            browser.get("https://www.youtube.com/results?search_query=%s"%(query))
            assert 'YouTube' in browser.title
                                                        
            # Get Results
            list_of_videos = browser.find_elements_by_class_name('yt-simple-endpoint')

            url = None

            url_list = []

            for video in list_of_videos[1:]:

                if video:
                    video_link = video.get_attribute('href')
                    if '=' not in video_link:
                        continue
                    video_link = video_link[video_link.find('=')+1:]
                    if video_link:
                        video_url = unidecode.unidecode(video_link) 

                        url_list.append(video_url)
            
            # Get URL of next Available Video
            for url in url_list:
            
                url = url[:12]
                log("\tURL: %s:" % url)

                # Check Relevance
                log("\tChecking Relevance: %s:" % url)
                browser.get("https://www.youtube.com/watch?v=%s"%(url))
                title_class = browser.find_elements_by_class_name('ytp-title-link')[0]
                title_uni = title_class.get_attribute('textContent')
                title = unidecode.unidecode(title_uni)
            
                log("\tVideo Title: %s"%title)

                title_pieces = title.split()
                song_pieces = song.title.split()
                artist_pieces = song.artist.split()
                music_pieces = ["mix", "remix", "song", "music", "lyrics",
                                "Radio", "Edit", "Feat", "audio", "lyric", "acoustic"]

                score = 0

                for piece in song_pieces:
                    for title_piece in title_pieces:
                        if piece.lower() in title_piece.lower():
                            score += 100 / len(song_pieces)

                for piece in artist_pieces:
                    for title_piece in title_pieces:
                        if piece.lower() in title_piece.lower():
                            score += 100 / len(artist_pieces)

                for piece in music_pieces:
                    for title_piece in title_pieces:
                        if piece.lower() in title_piece.lower():
                            score += 100

                log("\tScore: %s:" % score)
                
                if score < 150:
                    url = None
                    log("\tFAILED RELEVANCE CHECK" )
                    continue
                else:
                    log("\tPassed Relevance Check" )
                    break
                
            if url != "" and url != None:
                log("\t%s = %s"%(song.name(),url))
                song.status = READY_TO_DOWNLOAD
                song.url = url
            else:
                log("\tInvalid URL for %s" % song.name())

            
            self.db.save()
            
if __name__ == "__main__":
    log("Running Pysongs %s" % version.version)
    
    ps = system()
    
    help = """pysongs runs in the command line to create a database of songs, find YouTube video links that match that song title and artist, and then downloads that song for you."""
    
    while True:
        options = """
        (0) Help
        (1) Crawl for Songs
        (2) Get URL for Songs
        (3) Get MP3 for Songs
        (4) Open GUI
        (5) Full Sequence (Crawl, URL, MP3)
        (6) Save Database
        (7) Load Database"""
        
        input = raw_input("Select an option: \n%s\n" % options)
        
        if input in [str(x) for x in range(0,8)]:
            if input == '0':
                log(help)
            if input == '1':
                ps.crawl()
            if input == '2':
                ps.getURLs()
            if input == '3':
                ps.getMP3s()
            if input == '4':
                ps.spawnGUI()
            if input == '5':
                ps.crawl()
                ps.getURLs()
                ps.getMP3s()
            if input == '6':
                ps.saveDB()
            if input == '7':
                ps.loadDB()
