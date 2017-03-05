

def read_config():
    """
        Read the configuration file (sdntrace.conf) to import
        global variables. If file does not exist, ignore.
    """

    # These are configurable on the sdntrace.conf file
    configs = dict()
    configs['MINIMUM_COOKIE_ID'] = 2000000
    configs['PACKET_OUT_INTERVAL'] = 5
    configs['PUSH_COLORS_INTERVAL'] = 10
    configs['COLLECT_INTERVAL'] = 30
    configs['VLAN_DISCOVERY'] = 100
    configs['FLOW_PRIORITY'] = 50000

    params = ['MINIMUM_COOKIE_ID', 'PACKET_OUT_INTERVAL', 'PUSH_COLORS_INTERVAL',
              'COLLECT_INTERVAL', 'VLAN_DISCOVERY', 'FLOW_PRIORITY']

    config_file = "conf/sdntrace.conf"
    try:
        f = open(config_file, 'ro')
    except:
        return configs

    for line in f:
        if line[0].isalpha():
            variable, param = line.split('=')
            variable = variable.strip(' ')
            param = param.strip('\n').strip(' ')

            if variable in params:
                configs[variable] = int(param)
            else:
                print('Invalid Option: %s' % variable)
    return configs