"""
    
"""

def get_port_speed(speed):
    bws = {10000: '10MB',
           100000: '100MB',
           1000000: '1GB',
           10000000: '10GB',
           100000000: '100GB'}
    try:
        return bws[speed]
    except KeyError:
        return 'OtherSpeed(%s)' % speed