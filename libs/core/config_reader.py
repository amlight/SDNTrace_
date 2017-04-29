"""
    Class to store the configuration provided
"""
import sys
from ConfigParser import ConfigParser
from singleton import Singleton


class ConfigReader:

    __metaclass__ = Singleton

    def __init__(self, config_file='./docs/sdntrace.conf'):
        self.config_file = config_file
        self.general = None
        self.openflow = None
        self.trace = None
        self.ryu = None
        self.apps = None
        self.topo = None
        self.stats = None
        self.interdomain = None

        self.fill_sections(self.read_file(self.config_file))

    @staticmethod
    def read_file(config_file):
        config = ConfigParser()
        try:
            with open(config_file) as f:
                config.readfp(f)
        except Exception as err:
            print err

        config.read(config_file)
        sections = dict()
        for section in config.sections():
            configs = dict()
            options = config.options(section)
            for option in options:
                try:
                    configs[option] = config.get(section, option)
                except KeyError:
                    print("%s: Error on section %s param %s!" %
                          (config_file, section, option))
                    sys.exit(1)

            sections[section] = configs
            del configs
        return sections

    def fill_sections(self, configs):
        self.general = GeneralConfig(configs['general'])
        self.openflow = OpenflowConfig(configs['openflow'])
        self.trace = TraceConfig(configs['trace'])
        self.ryu = RyuConfig(configs['ryu'])
        self.apps = AppsConfig(configs['apps'])
        self.topo = TopologyConfig(configs['topo_discovery'])
        self.stats = StatisticsConfig(configs['statistics'])
        self.interdomain = InterdomainConfig(configs['inter-domain'])


def get_config(config, option, int_type=False, default=False):
    try:
        return int(config[option]) if int_type else config[option]
    except KeyError:
        return default


class GeneralConfig:

    DEBUG = False
    LOGFILE = None

    def __init__(self, config):
        self.debug = get_config(config, 'debug', default=self.DEBUG)
        self.logfile = get_config(config, 'log-file', default=self.LOGFILE)


class OpenflowConfig:

    VERSION = 'all'
    MIN_COOKIE = 2000000

    def __init__(self, config):
        self.version = get_config(config, 'version', default=self.VERSION)
        self.min_cookie = get_config(config, 'minimum_cookie_id', int_type=True,
                                     default=self.MIN_COOKIE)


class TraceConfig:

    COLOR_FIELD = 'dl_src'
    PUSH_COLOR_INTERVAL = 10
    FLOW_PRIORITY = 50000
    RUN_TRACE_INTERVAL = 1

    def __init__(self, config):
        self.color_field = get_config(config, 'color_field',
                                      default=self.COLOR_FIELD)
        self.push_color_interval = get_config(config, 'push_color_interval',
                                              int_type=True,
                                              default=self.PUSH_COLOR_INTERVAL)
        self.flow_priority = get_config(config, 'flow_priority', int_type=True,
                                        default=self.FLOW_PRIORITY)
        self.run_trace_interval = get_config(config, 'run_trace_interval',
                                             int_type=True,
                                             default=self.RUN_TRACE_INTERVAL)


class RyuConfig:

    LISTEN_PORT = 6633
    WSGI_PORT = 8080

    def __init__(self, config):
        self.listen_port = get_config(config, 'listen_port', int_type=True,
                                      default=self.LISTEN_PORT)
        self.wsgi_port = get_config(config, 'wsgi_port', int_type=True,
                                    default=self.WSGI_PORT)


class AppsConfig:

    LOAD = None

    def __init__(self, config):
        self.load = get_config(config, 'load', default=self.LOAD)


class TopologyConfig:

    PACKET_OUT_INTERVAL = 5
    VLAN_DISCOVERY = 100

    def __init__(self, config):
        self.packet_out_interval = get_config(config, 'packet_out_interval',
                                              int_type=True,
                                              default=self.PACKET_OUT_INTERVAL)
        self.vlan_discovery = get_config(config, 'vlan_discovery',
                                         int_type=True,
                                         default=self.VLAN_DISCOVERY)


class StatisticsConfig:

    COLLECT_INTERVAL = 30
    FLOWSTATS_INTERVAL = 10

    def __init__(self, config):
        self.collect_interval = get_config(config, 'collect_interval',
                                           int_type=True,
                                           default=self.COLLECT_INTERVAL)
        self.flowstats_interval = get_config(config, 'flowstats_interval',
                                             int_type=True,
                                             default=self.FLOWSTATS_INTERVAL)


class InterdomainConfig:

    MODE = 'off'
    MY_DOMAIN = 'local'
    PRIORITY = TraceConfig.FLOW_PRIORITY + 1
    COLOR_FIELD = TraceConfig.COLOR_FIELD
    COLOR_VALUE = 'ee:ee:ee:11:11:11'
    NEIGHBORS = None
    LOCALS = []

    def __init__(self, config):
        self.mode = get_config(config, 'mode', default=self.MODE)
        self.my_domain = get_config(config, 'my_domain',
                                    default=self.MY_DOMAIN)
        self.priority = get_config(config, 'priority', int_type=True,
                                   default=self.PRIORITY)
        self.color_field = get_config(config, 'color_field',
                                      default=self.COLOR_FIELD)
        self.color = get_config(config, 'color_value', default=self.COLOR_VALUE)
