#import eyed3
import urllib2
import cStringIO
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import eyed3
import time
import os
from shutil import copyfile

# Default Configuration
CHROMEDRIVER = ''
ADBLOCKPATH = ''
DOWNLOAD_PATH = 'C:/Users/Daniel/Downloads/'
SAVE_PATH = ''
ADDITIONAL_PATHS = []
HIERARCHY_PATH = ''
PANDORA_ACCOUNTS = []
LOGSDIR = ''

# Import Configuration Settings
with open("settings.cfg", 'r') as f:
    for line in f:
        exec(line)

YT2MP3_URL = 'https://ytmp3.cc/'
YT2MP3_TITLE = 'YtMp3'    

  
READY_TO_DOWNLOAD = "Ready to Download"
DOWNLOADED = "Downloaded"
ADDED = "Added"

# Initialize Broswer and Chrome Driver
chrome_options = Options()
chrome_options.add_extension(ADBLOCKPATH)
chrome_options.add_argument("test-type")
browser = webdriver.Chrome(CHROMEDRIVER, chrome_options = chrome_options)

class logging():

    def __init__(self):
        self.log_file = LOGSDIR + "log_%d.txt" % time.time()

    def log(self, text, newline=True):
        print text,
        if newline:
            print
        with open(self.log_file, "a") as f:
            f.write(text)
            if newline:
                f.write("\n")
                
l = logging()
log = l.log
                
def changeTags(fname, song):

    mp3file = eyed3.load(fname)
    
    if song.title and song.title != "":
        mp3file.tag.title = u"%s" % song.title
        
    if song.artist and song.artist != "":
        mp3file.tag.artist = u"%s"%song.artist
        
    if song.album and song.album != "":
        mp3file.tag.album = u"%s"%song.album
        
    if song.artwork and song.artwork != "":
        image = None
        
        if "_130W_130H.jpg" in song.artwork:
            url = song.artwork.replace("_130W_130H.jpg","_500W_500H.jpg")
        else:
            url = song.artwork

        try:
            image = urllib2.urlopen(url)
            
        except urllib2.HTTPError, e:
            log("Error opening 500x500 album art URL for %s" % song.name())
            log("\tURL = %s"%url)
            if url != song.artwork:
                url = song.artwork
                try:
                    image = urllib2.urlopen(song.artwork)
                except urllib2.HTTPError, e:
                    log("Error opening original album art URL for %s"%song.name())
                    log("\tURL = %s"%url)

        if image:
            imagedata = cStringIO.StringIO(image.read()).getvalue()
            mp3file.tag.images.set(3,imagedata,"image/jpeg",u"%s"%song.album)

    mp3file.tag.save()
 

def route(dl_file, song):

    dl_folder, dl_name = os.path.split(dl_file)
    
    # Save File to Locations
    
    # Main Save Location
    copyfile( dl_file, SAVE_PATH + dl_name)
        
    # Hierarchy Path
    
    hier = song.source.replace(".com", "").replace(".", "/")
    path = HIERARCHY_PATH + hier

    if not os.path.exists(path):
        os.makedirs(path)
        
    copyfile( dl_file, path + "/" + dl_name)
    
    # Additional Path(s)
    for path in ADDITIONAL_PATHS:
        copyfile( dl_file, path + "/" + dl_name)
    
    os.remove(dl_file)