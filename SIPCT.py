import argparse
import logging
import socket
import sys
import time
import os

from netifaces import interfaces, ifaddresses, AF_INET
from netaddr import IPNetwork, IPAddress

from time import sleep
from typing import cast
import json

import requests
from requests.auth import HTTPBasicAuth

from zeroconf import IPVersion, ServiceBrowser, ServiceStateChange, Zeroconf, ZeroconfServiceTypes

from SpeakerClass import Speaker
from xlsxClass import Xlsx

spkrList = []

def blink(spkr):
    while True :
        #input("\nPress enter to blink.. or Ctrl-C to quit")
        reply = str(input("Blink or next? (b/n): ")).lower().strip()
        if reply[0] == 'b':
            spkr.blink(True)
            print("Blinking...")
            time.sleep(5)
            spkr.blink(False)
        if reply[0] == 'n':
            break


def yes_or_no(question):
    reply = str(input(question+' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False
    else:
        return yes_or_no("Uhhhh... please enter ")

def checkBarcodeAndIp(barcode, ip, gw, mask, barcodesInMaster):
    result = False
    for x in barcodesInMaster:
        if barcode.find(x["barcode"]) != -1:
            result = True
            print(x["barcode"] + " found in master list")
            barCodeSet = x["barcode"]

            if x["ip"] == ip and x["gw"] == gw and x["mask"] == mask:
                print("Speaker config matches master list")
            else:
                print("\nDesired configuration found in list")
                print("====================================")
                print("IP: " + x["ip"])
                print("Mask: " + x["mask"])
                print("GW: " + x["gw"])
                print("")
                if yes_or_no("%s not in sync with master document, do you wish to update ip address?" % barCodeSet):
                    return x
    if result == False:
        print("Not in master list")


def on_service_state_change_search(
    zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange
) -> None:

    if state_change is ServiceStateChange.Added:
        info = zeroconf.get_service_info(service_type, name)

        if info:
            addresses = ["%s:%d" % (socket.inet_ntoa(addr), cast(int, info.port)) for addr in info.addresses]
            ip = "".join(["%s" % socket.inet_ntoa(addr) for addr in info.addresses]) ## join list together
            if info.properties:

                for key, value in info.properties.items(): ## parse properties to strings
                    if (key.decode("utf-8").find("mac") != -1):
                        mac = value.decode("utf-8")

                    if (key.decode("utf-8").find("zonename") != -1):
                        zoneName = value.decode("utf-8")

                    if (key.decode("utf-8").find("zoneid") != -1):
                        zoneId = value.decode("utf-8")


        spkr = Speaker(ip, mac, zoneName, zoneId, "admin", "admin")
        spkr.speakerStatus()
        if args.searchSN is not None:
            #if spkr.getBarcode() == args.searchSN:
            if spkr.getBarcode().find(args.searchSN) != -1:
                print("\nSpeaker found !")
                spkr.printAll()
                blink(spkr)
        elif args.searchHN is not None:
            #if spkr.getHostName() == args.searchHN:
            if spkr.getHostName().find(args.searchHN) != -1:
                print("\nSpeaker found !")
                spkr.printAll()
                blink(spkr)
        elif args.searchDN is not None:
            #if spkr.getDanteName() == args.searchDN:
            if spkr.getDanteName().find(args.searchDN) != -1:
                print("\nSpeaker found !")
                spkr.printAll()
                blink(spkr)


    else:
        print("  No info")
    print('\n')


def on_service_state_change(
    zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange
) -> None:
    print("##################################################################################################################\n")

    print("Service %s of type %s state changed: %s" % (name, service_type, state_change))

    if state_change is ServiceStateChange.Added:
        info = zeroconf.get_service_info(service_type, name)
        print("Info from zeroconf.get_service_info: %r" % (info))
        if info:
            addresses = ["%s:%d" % (socket.inet_ntoa(addr), cast(int, info.port)) for addr in info.addresses]
            ip = "".join(["%s" % socket.inet_ntoa(addr) for addr in info.addresses]) ## join list together
            print("  Address: %s" % ", ".join(addresses))
            print("  Weight: %d, priority: %d" % (info.weight, info.priority))
            print("  Server: %s" % (info.server,))
            if info.properties:
                ##print("  Properties are:")
                for key, value in info.properties.items(): ## parse properties to strings
                    ##print("    %s: %s" % (key, value))
                    if (key.decode("utf-8").find("mac") != -1):
                        mac = value.decode("utf-8")

                    if (key.decode("utf-8").find("zonename") != -1):
                        zoneName = value.decode("utf-8")

                    if (key.decode("utf-8").find("zoneid") != -1):
                        zoneId = value.decode("utf-8")
            else:
                print("  No properties")


            spkr = Speaker(ip, mac, zoneName, zoneId, "admin", "admin")
            spkr.speakerStatus()
            spkr.printAll()
            list = xlsx.getList()
            print("\nSpeaker barcode: " + spkr.getBarcode())
            spkr.updateSpeaker(checkBarcodeAndIp(spkr.getBarcode(), spkr.getIp(), spkr.getGw(), spkr.getMask(), list))
            if spkr.getUpdated():
                print("Adding MAC address and Dante name written to master list")
                for i in range(0, len(list)):
                    if list[i]["barcode"] == spkr.getBarcode():
                        i = i + 2
                        xlsx.setDanteNameAndMac(i, spkr.getDanteName(), spkr.getMac())
            else:
                print("Master list not updated")
            #spkrList.append(spkr)


        else:
            print("  No info")
        print('\n')

        if autoEnter is False:
            input("Press enter to continue...\n")
    print("Waiting for Speaker...")





if __name__ == '__main__':

    os.system("cls")
    #logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('--file', action="store", dest="fileName", help="Config Speakers i batch run, define excel file." )
    parser.add_argument('--auto', action="store_true", dest="autoEnter", help="Skips speakers that is in sync, or not found in the master list (Auto Enter)" )
    parser.add_argument('--search_sn', action="store", dest="searchSN", help="Search for Speaker by S/N")
    parser.add_argument('--search_hn', action="store", dest="searchHN", help="Search for Speaker by Host Name")
    parser.add_argument('--search_dn', action="store", dest="searchDN", help="Search for Speaker by Dante Name")
    args = parser.parse_args()

    if args.fileName is not None:
        print("File name is: " + args.fileName)
        xlsx = Xlsx(args.fileName)
        try:
            xlsx.setDate()
        except OSError as err:
            print("\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ EXCEPTION !!!! @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ ")
            print("\nOS error: {0}".format(err))
            print("Excel file open!")
            print("\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ ")
            sys.exit()
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
        search = False
    elif args.searchSN is not None:
        search = True
    elif args.searchHN is not None:
        search = True
    elif args.searchDN is not None:
        search = True
    else:
        print("No filename")
        sys.exit()

    if args.autoEnter is True:
        autoEnter = True
    else:
        autoEnter = False

    #xlsx.printAllSpeakersInExcel()

    zeroconf = Zeroconf(ip_version=IPVersion.V4Only)

    services = ["_smart_ip._tcp.local."]

    if search is True:
        print("Searching for Speaker ")
        browser = ServiceBrowser(zeroconf, services, handlers=[on_service_state_change_search])
    else:
        print("\nBrowsing %d service(s), press Ctrl-C to exit...\n" % len(services))
        print("Waiting for Speaker...")
        browser = ServiceBrowser(zeroconf, services, handlers=[on_service_state_change])


    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        zeroconf.close()
