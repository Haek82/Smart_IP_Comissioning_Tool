from netifaces import interfaces, ifaddresses, AF_INET
from netaddr import IPNetwork, IPAddress

def checkSubNet(SpeakerIP, SubNet):

    count = 0

    for ifaceName in interfaces():
        addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'0.0.0.0'}] )]
        print ('%s: %s' % (ifaceName, ', '.join(addresses)))
        ip = ".".join(addresses)
        if IPAddress(ip) in IPNetwork(SpeakerIP+"/"+SubNet):
            #print("Yay!")
            count +=1

    if count > 0:
        return True
    else:
        return False

print(checkSubNet("169.254.43.1", "16"))
