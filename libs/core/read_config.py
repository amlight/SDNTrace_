import sys, ConfigParser


dict_type = {'trace': {'push_color_interval': 'int',
                       'flow_priority': 'int'},
             'topo_discovery':{'packet_out_interval': 'int',
                               'vlan_discovery': 'int'},
             'statistics': {'collect_interval': 'int',
                            'flowstats_interval': 'int'},
             'openflow': {'minimum_cookie_id': 'int'}
             }


def read_config(config_file='./conf/sdntrace.conf'):
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    sections = dict()
    for section in config.sections():
        configs = dict()
        options = config.options(section)
        for option in options:
            try:
                try:
                    if dict_type[section][option] == 'int':
                        configs[option] = int(config.get(section, option))
                    else:
                        configs[option] = config.get(section, option)
                except:
                    configs[option] = config.get(section, option)
            except:
                print("%s: Error on section %s param %s!" %
                      (config_file, section, option))
                sys.exit(1)

        sections[section] = configs
        del configs
    return sections
