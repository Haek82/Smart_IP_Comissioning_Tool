import argparse
import logging
import socket
from time import sleep
from typing import cast
import json

import requests
from requests.auth import HTTPBasicAuth

from zeroconf import IPVersion, ServiceBrowser, ServiceStateChange, Zeroconf, ZeroconfServiceTypes

from SpeakerClass import Speaker
from xlsxClass import Xlsx

spkrList = []

xlsx = Xlsx("masterList.xlsx")

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
            #print(x)
            barCodeSet = x["barcode"]

            if x["ip"] == ip and x["gw"] == gw and x["mask"] == mask:
                print("Speaker config matches master list")
            else:
                if yes_or_no("%s not in sync with master document, do you wish to update ip address?" % barCodeSet):

                    return x
    if result == False:
        print("Not in master list")
        x = {}
        return x

def on_service_state_change(
    zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange
) -> None:
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
                print("Adding MAC address and Dante name to master list")
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


if __name__ == '__main__':

    #logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--find', action='store_true', help='Browse all available services')
    version_group = parser.add_mutually_exclusive_group()
    version_group.add_argument('--v6', action='store_true')
    version_group.add_argument('--v6-only', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)
    if args.v6:
        ip_version = IPVersion.All
    elif args.v6_only:
        ip_version = IPVersion.V6Only
    else:
        ip_version = IPVersion.V4Only

    zeroconf = Zeroconf(ip_version=ip_version)

    services = ["_smart_ip._tcp.local."]
    if args.find:
        services = list(ZeroconfServiceTypes.find(zc=zeroconf))

    print("\nBrowsing %d service(s), press Ctrl-C to exit...\n" % len(services))
    browser = ServiceBrowser(zeroconf, services, handlers=[on_service_state_change])

    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        zeroconf.close()
