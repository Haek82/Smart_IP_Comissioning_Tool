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


# spkr1 = {
#   "barcode": "4430AM173",
#   "ip": "169.254.55.8",
#   "mask": "255.255.0.0"
# }
#
# spkr2 = {
#   "barcode": "4430AM174",
#   "ip": "169.254.55.7",
#   "mask": "255.255.0.0"
# }
#
# boot = {
#     "boot": True
# }
#
#
# masterDoc = []
# spkrs = []
#
# masterDoc.append(spkr1)
# masterDoc.append(spkr2)

spkrList = []

xlsx = Xlsx("masterList.xlsx")
#print(xlsx.getList())



# def getRequest(ip, url):
#     r = requests.get("http://%s%s" % (ip, url), auth=HTTPBasicAuth('admin', 'admin'))
#     print("Status code: %s" % r.status_code)
#     ##print("Payload: %s" % r.text)
#     return r.text
#
# def putRequest(ip, url, payload):
#     JsonPayload = json.dumps(payload) # Convert dictonary to JSON string
#     print(JsonPayload)
#     headers = {"Content-Type": "application/json"}
#     r = requests.put("http://%s:9000%s" % (ip, url), auth=HTTPBasicAuth('admin', 'admin'), headers = headers, data = JsonPayload)
#
def yes_or_no(question):
    reply = str(input(question+' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False
    else:
        return yes_or_no("Uhhhh... please enter ")
#
# def checkIp(ip1, ip2):
#     if (ip1.find(ip2) != -1):
#         return True
#     else:
#         return False
#
# def updateSpeaker(bool, dict, ip, ipNow):
#     if bool:
#         dict["ipv4"]["ip"] = ip
#
#         putRequest(ipNow,"/api/v1/network/ipv4", dict["ipv4"])
#         putRequest(ipNow,"/api/v1/network/zone", dict["zone"])
#         putRequest(ipNow, "/api/v1/device/boot", boot)
#
#
# def checkBarCodeAndIp(dict):
#     result = False
#     for x in masterDoc:
#         if (dict["id"]["barcode"].find(x["barcode"]) != -1):
#             result = True
#             barCodeSet = x["barcode"]
#             ipCodeSet = x["ip"]
#     if result:
#         print("%s serialnumber found in master document, checking ip" % barCodeSet)
#         print("Master list ip : %s" % ipCodeSet)
#         print("Speaker ip : %s" % dict["ipv4"]["ip"])
#         #print(checkIp(ipCodeSet, dict["ipv4"]["ip"]))
#         if checkIp(ipCodeSet, dict["ipv4"]["ip"]):
#             print("speaker ip matched to master file")
#         else:
#             updateSpeaker(yes_or_no("%s not in sync with master document, do you wish to update ip address?" % barCodeSet), dict, ipCodeSet, dict["ipv4"]["ip"] )
#     else:
#         print("Serialnumber Not found in master document")

def checkBarcode(barcode, barcodesInMaster):
    result = False
    for x in barcodesInMaster:
        if barcode.find(x["barcode"]) != -1:
            result = True
            print(x["barcode"])
            barCodeSet = x["barcode"]

    return result


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
            print("\nSpeaker barcode: " + spkr.getBarcode())
            print(checkBarcode(spkr.getBarcode(), xlsx.getList()))

            spkrList.append(spkr)


        else:
            print("  No info")
        print('\n')


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

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
