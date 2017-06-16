"""
    Queues
"""
import logging
from libs.core.signals import Signal


# My Queues

# packet_in
packet_in_queue = Signal('packet_in_queue')

# topology advertisement
topology_adv_queue = Signal('topology_adv_queue')

# topology refresher
topology_refresher_queue = Signal('topology_refresher_queue')


# notification decorators
def topology_change(func):
    """ In situations were a new switch is added or deleted or
        there is a port status change, this decorator is used to
        notify all possible interested applications. Currently,
        only the Topology_Discovery app uses it to refresh
        its dictionary. With the decorator, the original method
        will not need to be modified for these notifications. It
        also makes it generic so new apps could be easily 
        added to the SDNTrace.
    Args:
        func: switches.add_switch, switches.del_switch and
            switch.port_status
    Returns:
        decorated func
    """
    def notify_topo_change(*args, **kwargs):
        logging.debug("Topology Change {0}".format(func.__name__))
        topology_refresher_queue.send(pkt=None)
        return func(*args, **kwargs)
    return notify_topo_change
