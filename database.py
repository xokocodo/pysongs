import csv
import os
from utils import *

class SongList():
    def __init__(self, fname):
        self.songs = {}
        self.fname = fname
        self.current_key = 0

    def save(self):
        with open(self.fname, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_ALL)
            for k, song in self.songs.iteritems():
                writer.writerow(song.toCSV())

    def load(self):
        self.songs = {}
        if not os.path.exists(self.fname):
            log("CSV File Doesn't Exist")
            return
        log("Opening CSV File and Loading Database")
        with open(self.fname, 'r') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.readline())
            csvfile.seek(0)
            reader = csv.reader(csvfile, dialect)
            for line in reader:
                temp = SongRow()
                temp.fromCSV(line)
                self.add(temp, log_new=False)
        log("Loaded %d Songs from Database." % self.current_key)
                
    def add(self, song, log_new=True, log_dup=True):
        if not self.checkDuplicate(song.title, song.artist):
            self.songs[self.current_key] = song
            self.songs[self.current_key].key = self.current_key
            self.current_key += 1
            if log_new:
                log("Added %s to list" % song.name())
        else:
            if log_dup:
                log("%s is already in the list" % song.name())
        
    def remove(self, i):
        del self.songs[i]
        
    def checkDuplicate(self, title, artist):
        for k, song in self.songs.iteritems():
            if song.title == title.replace('"', "'") and song.artist.replace('"', "'") == artist:
                return True
        return False
        
    def getSongsByProperty(self, property, value):
        matches = []
        for k, song in self.songs.iteritems():
            if getattr(song, property) == value:
                matches.append(song)
        return matches
        
        
        
class SongRow():

    def __init__(self, key=0, title="", artist="", album="", artwork="", source="Unknown", status="Unknown", url="", filename=""):
    
        self.key = key
        self.title = title.replace('"', "'")
        self.artist = artist.replace('"', "'")
        self.album = album
        self.artwork = artwork
        self.source = source
        self.status = status
        self.url = url
        self.filename = filename

    def toCSV(self):
        return [self.key, self.title, self.artist, self.album, self.artwork, self.source, self.status, self.url, self.filename]
    
    def fromCSV(self, list):
        try:
            self.key = list[0]
            self.title = list[1]
            self.artist = list[2]
            self.album = list[3]
            self.artwork = list[4]
            self.source = list[5]
            self.status = list[6]
            self.url = list[7]
            self.filename = list[9]
        except:
            pass
        
    def name(self):
        return "%s by %s" % (self.title, self.artist)
