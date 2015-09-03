import mpd

client = mpd.MPDClient(use_unicode=True)
class MusicPlayer:
    
    
        
    def connect(self):
        
        print("connecting to mopidy")
        self.client = mpd.MPDClient(use_unicode=True)
        self.client.connect("localhost", 6600)    
        print("finished connecting to mopidy")
        print(client.mpd_version)

    def play(self, uri):
        self.client.clear()
        self.client.add(uri)
        self.client.play(0)

    def stop(self):
        self.client.stop()
        self.client.clear()

    def ping(self):
        self.client.ping()
        

