"""

"""
import socket
import struct
import netaddr


def ip_addr(ip):
    """

    Args:
        ip:

    Returns:

    """
    return socket.inet_ntoa(struct.pack('!L', ip))


def ip6_addr(ip6):
    """

    Args:
        ip:

    Returns:

    """
    o1, o2, o3, o4, o5, o6, o7, o8 = ip6
    ipv6 = '%x:%x:%x:%x:%x:%x:%x:%x' % (o1, o2, o3, o4, o5, o6, o7, o8)
    return ipv6


def eth_addr(a):
    """
        Print Mac Address in the human format
    Args:
        a: string "6s"
    Returns:
        mac in the human format
    """
    string = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x"
    mac = string % (ord(a[0]), ord(a[1]), ord(a[2]),
                    ord(a[3]), ord(a[4]), ord(a[5]))
    return mac
