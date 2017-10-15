
from scapy.all import srp, Ether, ARP,sniff
IpScan = '192.168.1.1/24'


def ARP_scan(ip_scan):
    try:
        ans, unans = srp(Ether(dst="FF:FF:FF:FF:FF:FF") /
                        ARP(pdst=ip_scan), timeout=2)
    except Exception as e:
        print(e)
    else:
        for send, rcv in ans:
            ListMACAddr = rcv.sprintf("%Ether.src%---%ARP.psrc%")
            print(ListMACAddr)

# ARP_scan(IpScan)
def arp_monitor_callback(pkt):
    if ARP in pkt and pkt[ARP].op in (1,2): #who-has or is-at
        # print(dir(ARP))
        # print(ARP.who_has)
        return pkt.sprintf("%ARP.hwsrc% %ARP.psrc% %ARP.hwdst% %ARP.pdst%")

sniff(prn=arp_monitor_callback, filter="arp", store=0)