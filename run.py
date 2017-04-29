import sys
import argparse
from ryu.cmd import manager
from libs.core.read_config import read_config
from libs.core.config_reader import ConfigReader


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('-V', '--version', action='version', version='SDNTrace 1.0')
    parser.add_argument("-v", "--verbose",
                        help="Set Verbose Level (info|warning|debug)",
                        default='info')
    parser.add_argument("-f", "--config-file",
                        help="Configuration file (default conf/sdntrace.conf",
                        default='./conf/sdntrace.conf')
    return parser.parse_args()


def load_ryu_options(app, verbose, configs):
    options = list()
    options.append(app)

    if verbose in ('warning', 'debug') or configs.general.debug is True:
        options.append('--verbose')
        options.append('--enable-debugger')

    options.append('--ofp-tcp-listen-port')
    options.append(configs.ryu.listen_port)
    options.append('--wsapi-port')
    options.append(configs.ryu.wsgi_port)

    if configs.general.logfile:
        options.append('--log-file')
        options.append(configs.general.log_file)

    options.append('--config-file')
    options.append(configs.config_file)

    return options


def get_params(app):
    args = cli()
    configs = ConfigReader(args.config_file)
    params = load_ryu_options(app, args.verbose, configs)
    return params


def main():
    args = get_params(app='sdntraceRest.py')
    print(args)
    manager.main(args=args)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
