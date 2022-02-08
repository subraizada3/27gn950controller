import socket
import re

class lightpack:

#	host = '127.0.0.1'    # The remote host
#	port = 3636           # The same port as used by the server
#	apikey = 'key'        # Secure API key which generates by Lightpack software on Dev tab
#	ledMap = [1,2,3,4,5,6,7,8,9,10]  # Mapped LEDs
    
    def __init__(self, _host, _port, _ledMap = None, _apikey = None):
        self.host = _host
        self.port = _port
        self.ledMap = _ledMap if _ledMap is not None else []
        self.apikey = _apikey		
    
    def __readResult(self):  # Return last-command API answer (call in every local method)
        total_data = []
        data = self.connection.recv(8192)
        total_data.append(data)
        return b"".join(total_data).decode()
    
    def getProfiles(self):
        self.connection.send(b"getprofiles\n")
        profiles = self.__readResult()
        return profiles.split(':')[1].rstrip(';\n\r').split(';')
    
    def getProfile(self):
        self.connection.send(b"getprofile\n")
        profile = self.__readResult()
        profile = profile.split(':')[1]
        return profile
        
    def getStatus(self):
        self.connection.send(b"getstatus\n")
        status = self.__readResult()
        status = status.split(':')[1]
        return status
    
    def getCountLeds(self):
        self.connection.send(b"getcountleds\n")
        count = self.__readResult()
        count = count.split(':')[1]
        return int(count)
        
    def getAPIStatus(self):
        self.connection.send(b"getstatusapi\n")
        status = self.__readResult()
        status = status.split(':')[1]
        return status
    
    def connect(self):
        try:  # Try to connect to the server API
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((self.host, self.port))
            self.__readResult()
            if self.apikey is not None:	
                cmd = 'apikey:' + self.apikey + '\n'
                self.connection.send(str.encode(cmd))
                self.__readResult()
            self.getLedMap()
            return 0
        except:
            print('Lightpack API server is missing')
            return -1
        
    def disconnect(self):
        self.unlock()
        self.connection.close()

    def getColors(self):
        try:
            self.connection.send(b"getcolors\n")
            status = self.__readResult()
            #print(status)
            pixels = status.split(':')[1]
            rgb = re.findall(r"(\d+)-(\d+),(\d+),(\d+);", pixels or "")
            return rgb if rgb else None
        finally:
            pass