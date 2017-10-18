import sys
from scapy.all import *
IpScan = '192.168.1.1/24'


def ARP_scan(ip_scan):
    try:
        ans, unans = srp(Ether(dst="FF:FF:FF:FF:FF:FF") /
                         ARP(pdst=ip_scan), timeout=2)
    except Exception as e:
        print(e)
    else:
        for send, rcv in ans:
            ListMACAddr = rcv.sprintf("scan %Ether.src% %ARP.psrc%")
            print(ListMACAddr)

# ARP_scan(IpScan)


def arp_monitor_callback(pkt):
    if ARP in pkt and pkt[ARP].op in (1, 2):  # who-has or is-at
        # print(dir(ARP))
        # print(ARP.who_has)
        if pkt[ARP].op == 1:
            return pkt.sprintf("who-has %ARP.hwsrc% %ARP.psrc% ask %ARP.hwdst% %ARP.pdst%")
        else:
            return pkt.sprintf("is-at %ARP.hwsrc% %ARP.psrc% to %ARP.hwdst% %ARP.pdst%")


def get_gateway():
    p = sr1(IP(dst="www.baidu.com", ttl=0) / ICMP() / "XXXXXXXXXXX")
    print('gateway', p.src)
# sniff(prn=arp_monitor_callback, filter="arp", store=0)
# ARP_scan(IpScan)
# def arp_monitor_callback()


def main(argv):
    if argv[0] == 'scan':
        ARP_scan(IpScan)
    elif argv[0] == 'sniff':
        sniff(prn=arp_monitor_callback, filter="arp", store=0)
    elif argv[0] == 'gateway':
        get_gateway()
    return


if __name__ == "__main__":
    main(sys.argv[1:])
