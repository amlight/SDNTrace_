"""

"""
import libs.openflow.of10.openflow_helper as of10
import libs.openflow.of13.openflow_helper as of13


def process_flow_stats(switch, flow):
    """

    Args:
        switch:
        flow:

    Returns:

    """
    if switch.version_name == '1.0':
        return of10.process_flows_stats(flow)
    elif switch.version_name == '1.3':
        return of13.process_flows_stats(flow)
