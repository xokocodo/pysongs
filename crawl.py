from pandora import APIClient, clientbuilder
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import unidecode
import socket
import tempfile
import os

import database
from utils import *

class Crawler():
    
    def __init__(self, songs):
        self.songs = songs
        
    def crawl(self):
        pass
        
class PandoraCrawler(Crawler):
    # add 'feedback = Field("feedback", [])' to pandora model
    
    def __init__(self, songs, username, password):
        Crawler.__init__(self, songs)
        self.username = username
        self.password = password
        
        self.cfg_file = self.generateConfigFile()
        
        self.quiet = True
        
    def generateConfigFile(self):
        text = """[api]
encryption_key = 721^26xE22776
decryption_key = 20zE1E47BE57$51
username = iphone
password = P2E4FC0EAD3*878N92B2CDp34I0B1@388137C
device = IP01

[user]
username = %s
password = %s""" % (self.username, self.password)

        new_file, filename = tempfile.mkstemp()
        os.write(new_file, text)
        os.close(new_file)
        return filename
        
    def crawl(self):
        log("Getting Liked Songs for %s\n" % self.username)

        builder = clientbuilder.PydoraConfigFileBuilder(self.cfg_file)
        client = builder.build()
        slist = client.get_station_list()

        stations = []

        for i, s in enumerate(slist):
            stations.append(s.token)
    
        for station in stations:
            station_detail = client.get_station(station)

            if not hasattr(station_detail, "feedback"):
                continue
            if station_detail.feedback:

                likes = station_detail.feedback.get('thumbsUp')

                if likes:
                    for item in likes:
                        station_name = unidecode.unidecode(station_detail.name)
                        source = "Pandora.Liked.%s.%s"%(self.username, station_name)
                        title = unidecode.unidecode(item['songName'])
                        artist = unidecode.unidecode(item['artistName'])
                        raw_album = item.get('albumName')
                        if raw_album:
                            album = unidecode.unidecode(raw_album)
                        else:
                            album = ""
                        art_url = unidecode.unidecode(item['albumArtUrl'])
                        song = database.SongRow(title=title,
                                              artist=artist,
                                              album=album,
                                              artwork=art_url,
                                              source=source,
                                              status="Added")
                        
                        self.songs.add(song, log_new=True, log_dup=False)
                        if not self.quiet:
                            log("\tFound Liked Song: %s" % song.name())


class YouTubeUpNextCrawler(Crawler):


    def __init__(self, songs, seed, depth=0):
        Crawler.__init__(self, songs)
        self.seed = seed
        self.depth = depth
                        
    def crawl(self):
        # Open Browser to Seed
        browser.get("https://www.youtube.com/watch?v=%s"%(seed))
        assert 'YouTube' in browser.title

        title_class = browser.find_elements_by_class_name('watch-title ')[0]
        title_uni = title_class.get_attribute('title')
        seed_name = unidecode.unidecode(title_uni)
                                                        
        seen = []

        log("Getting YouTube Playlist for Seed %s with depth %s\n"%(seed_name, depth))

        for i in range(depth):
            
            # Find next video
            up_next = browser.find_elements_by_class_name('content-link')
            next_video_full = unidecode.unidecode(up_next[0].get_attribute('href'))
            next_video = next_video_full.replace("https://www.youtube.com/watch?v=","")

            # go to next video
            if next_video in seen:
                log("Failed to get %s videos without repeat: %s"%(depth, next_video))
                break
            browser.get(next_video_full)
            assert 'YouTube' in browser.title

            seen.append(next_video)
            
            source = "YouTube.UpNext.%s.%s"%(seed, i)

            title_class = browser.find_elements_by_class_name('watch-title ')[0]
            title_uni = title_class.get_attribute('title')
            title = unidecode.unidecode(title_uni)
            

            artist = "Unknown"
            album = "Unknown"
            song = database.SongRow(title=title,
                                  source=source,
                                  status="Added")
                            
            self.songs.add(song)
            log("\tFound Song/Video: %s" % song.name())


class YouTubePlaylistCrawler(Crawler):

    def __init__(self, songs, seed, depth=0):
        Crawler.__init__(self, songs)
        self.seed = seed
        self.depth = depth

    def crawl(self):

        remainder = depth
        i = 0
        
        while remainder > 0 :
    
            # Open Browser to Seed
            browser.get("https://www.youtube.com/watch?v=%s&list=%s"%(seed, listid))
            assert 'YouTube' in browser.title

            if seen == None:
                seen = []
                
            log("Getting YouTube Playlist %s with seed %s\n"%(listid, seed))

            video_list = browser.find_elements_by_class_name('yt-uix-scroller-scroll-unit')

            video_id = seed

            for video in video_list:

                # Skip the video if None ID
                if not video.get_attribute('data-video-id'):
                    continue
                
                # Find video id and name
                video_id = unidecode.unidecode(video.get_attribute('data-video-id'))
                video_title = unidecode.unidecode(video.get_attribute('data-video-title'))

                if video_id in seen:
                    log("Skipped %s (%s)\n"%(video_title, video_id))
                    continue

                seen.append(video_id)

                source = "YouTube.Playlist.%s"%(seed)

                artist = "Unknown"
                album = "Unknown"
                song = database.SongRow(Title=video_title,
                                      Source=source,
                                      Status="Ready for Download",
                                      URL=video_id)
                                
                self.songs.add(song)
                log("\tFound Song/Video: %s" % song.name())
                i += 1
                
            remainder = remainder - i

    
