from LANwhiz.utils import Utilities
import re


class Static(object):
    def __init__(self, connection):
        self.connection = connection
        self.utils = Utilities(self.connection)
        self.utils.ensure_global_config_mode()

    def send_static_route_command(self, network, subnetmask, forward_to):
        """ Configures a static route on a device """
        self.utils.send_command(
            f"ip route {network} {subnetmask} {forward_to}"
        )


class OSPF(object):
    def __init__(self , connection, ospf_data):
        self.connection = connection
        self.utils = Utilities(self.connection)
        self.ospf_data = ospf_data
        self.utils.ensure_global_config_mode()
        self.utils.send_command(
            f"router ospf {self.ospf_data['instance_id']}"
        )
    
    def router_id(self):
        """ Define the router's ID for OSPF instance """
        self.utils.send_command(
            f"router-id {self.ospf_data['router_id']}"
        )

    def advertise_static_routes(self):
        """ Distribute default static routes to OSPF network """
        self.utils.send_command("default-information originate")
    
    def advertise_networks(self):
        """ Advertises OSPF networks """
        for network in self.ospf_data["advertise_networks"]:
            ip, cidr, area = network.split("/")
            wildcard = self.utils.cidr_to_wildcard_mask(int(cidr))
            self.utils.send_command(f"network {ip} {wildcard} {area}")
    
    def passive_interfaces(self):
        """ Defines all passive interfaces """
        for interface in self.ospf_data["passive_interfaces"]:
            self.utils.send_command(f"passive-interface {interface}")