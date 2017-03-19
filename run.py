import sys, argparse
from ryu.cmd import manager
from libs.core.read_config import read_config


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


def load_ryu_options(app, conf_file, verbose, listen_port, wsgi_port, log_file):
    options = list()
    options.append(app)

    if verbose in ('warning', 'debug'):
        options.append('--verbose')
        options.append('--enable-debugger')

    options.append('--ofp-tcp-listen-port')
    options.append(listen_port)
    options.append('--wsapi-port')
    options.append(wsgi_port)

    if log_file:
        options.append('--log-file')
        options.append(log_file)

    options.append('--config-file')
    options.append(conf_file)

    return (options)


def get_params(app):
    args = cli()
    configs = read_config(args.config_file)
    try:
        log_file = configs['ryu']['log_file']
    except:
        log_file = None
    params = load_ryu_options(app, args.config_file, args.verbose,
                              configs['ryu']['listen_port'],
                              configs['ryu']['wsgi_port'],
                              log_file)
    return params


def main():
    args = get_params(app='sdntraceRest.py')
    manager.main(args=args)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)

