from typing import cast
import json
import sys

import requests
from requests.auth import HTTPBasicAuth

class Speaker:
    #This is the speaker class

    spkCount = 0

    def __init__(self, ip, mac, zoneName, zoneId, user, passwd): #class constructor
        self.barcode = ""
        self.ipMode= ""
        self.ip = ip
        self.mac = mac
        self.gw = ""
        self.mask = ""
        self.hostname = ""
        self.zoneName = zoneName
        self.zoneId = zoneId
        self.user =  user
        self.passwd = passwd
        self.danteName = ""
        self.danteMac = ""
        self.updated = False
        self.ipv4 = {}
        self.zone = {}
        self.id = {}
        self.danteIdentity = {}

        self.boot = {
            "boot" : True
        }

        Speaker.spkCount += 1 #increment speaker count

    def printAll(self):
        print("\n")
        print("Current Speaker setting")
        print("=======================")
        print("Barcode: " + self.barcode)
        print("IP: " + self.ip)
        print("MAC: " + self.mac)
        print("GW: " + self.gw)
        print("Mask: " + self.mask)
        print("Hostname: " + self.hostname)
        print("Zone Name: " + self.zoneName)
        print("Zone Id: " + self.zoneId)
        #print("User: " + self.user)
        #print("Password: " + self.passwd)
        print("Dante Name: " + self.danteName)
        print("Dante MAC:" + self.danteMac)


    def getRequest(self, url):
        r = requests.get("http://%s:9000%s" % (self.ip, url), auth=HTTPBasicAuth(self.user, self.passwd))
        #print("Status code: %s" % r.status_code)
        #print("Payload: %s" % r.text) ##debug
        return r.text


    def putRequest(self, url, payload):
        JsonPayload = json.dumps(payload) # Convert dictonary to JSON string
        #print(JsonPayload)
        headers = {"Content-Type": "application/json"}
        r = requests.put("http://%s:9000%s" % (self.ip, url), auth=HTTPBasicAuth(self.user, self.passwd), headers = headers, data = JsonPayload)

    def getNetworkInfo(self): ## http request ipv4 to speaker, parse json string to dictonary
        ipv4 = self.getRequest('/api/v1/network/ipv4')
        self.ipv4 = json.loads(ipv4)

    def getZone(self): ## http request zone to speaker, pase json string to dictonary
        zone = self.getRequest('/api/v1/network/zone')
        self.zone = json.loads(zone)

    def getDanteIdentity(self): ## http request Dante identity, pase json string to dictonary
        danteId = self.getRequest('/api/v1/aoip/dante/identity')
        self.danteIdentity = json.loads(danteId)

    def getId(self):
        id = self.getRequest('/api/v1/device/id')
        self.id = json.loads(id)

    def getDanteName(self):
        return self.danteName

    def getIp(self):
        return self.ip

    def getMask(self):
        return self.mask

    def getGw(self):
        return self.gw

    def getBarcode(self):
        return self.barcode

    def getHostName(self):
        return self.hostname

    def getUpdated(self):
        return self.updated

    def blink(self, state):
        blinkOn = {
            'take' : True,
            'flash' : True,
            'color' : "YELLOW",
            'intensity' : 100,
            "ledIntensity" : 100
        }

        blinkOff = {
            'take' : False,
            'flash' : False,
            'color' : "YELLOW",
            'intensity' : 100,
            "ledIntensity" : 100
        }

        if state is True:
            self.putRequest("/api/v1/device/led", blinkOn)
        if state is False:
            self.putRequest("/api/v1/device/led", blinkOff)

    def updateSpeaker(self, inputDict):

        if inputDict is None:
            print("No Update.")
            self.updated = False

        bootDict = {
            'boot' : True
        }

        if inputDict != None:
            #print(inputDict)
            self.ipv4["ip"] = inputDict["ip"]
            self.ipv4["gw"] = inputDict["gw"]
            self.ipv4["mask"] = inputDict["mask"]
            self.ipv4["mode"] = "static"
            self.putRequest("/api/v1/network/ipv4", self.ipv4)
            self.putRequest("/api/v1/network/zone", self.zone)
            self.putRequest("/api/v1/device/boot",bootDict)
            self.updated = True

    def speakerStatus(self):
        try:
            self.getNetworkInfo()
            self.getZone()
            self.getId()
            self.getDanteIdentity()
            self.initialSpeakerValues()
        except OSError as err:
            print("\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ EXCEPTION !!!! @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ ")
            print("\nOS error: {0}".format(err))
            print("\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ ")
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

    def initialSpeakerValues(self):
        self.barcode = self.id["barcode"]
        self.gw = self.ipv4["gw"]
        self.mask = self.ipv4["mask"]
        self.ipMode = self.ipv4["mode"]
        self.hostname = self.ipv4["hostname"]
        self.danteName = self.danteIdentity["fname"]
        self.danteMac = self.danteIdentity["mac"]

    def getMac(self):
        return self.mac

    def getBarcode(self):
        return self.barcode

    def getCumulativeSpeakerCount(self):
        return Speaker.spkCount
