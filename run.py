import sys
from ryu.cmd import manager


def main():
    sys.argv.append('sdntraceRest.py')
    manager.main()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

