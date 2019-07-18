from net_auto_config.utils import Utilities
import re


class Static(object):
    def __init__(self, connection):
        self.connection = connection
        self.utils = Utilities()
        self.utils.ensure_global_config_mode(connection)

    def send_static_route_command(self, network, subnetmask, forward_to):
        """ Configures a static route on a device """
        self.connection.send_command(
            f"ip route {network} {subnetmask} {forward_to}",
            expect_string=""
        )


class OSPF(object):
    def __init__(self , connection, ospf_data):
        self.connection = connection
        self.utils = Utilities()
        self.ospf_data = ospf_data
        self.utils.ensure_global_config_mode(connection)
        self.connection.send_command(
            f"router ospf {self.ospf_data['instance_id']}",
            expect_string=""
        )
    
    def router_id(self):
        """ Define the router's ID for OSPF instance """
        self.connection.send_command(
            f"router-id {self.ospf_data['router_id']}",
            expect_string=""
        )

    def advertise_static_routes(self):
        """ Distribute default static routes to OSPF network """
        self.connection.send_command(
            "default-information originate",
            expect_string=""
        )
    
    def advertise_networks(self):
        """ Advertises OSPF networks """
        for network in self.ospf_data["advertise_networks"]:
            ip = network.split("/")[0]
            wildcard = self.utils.cidr_to_wildcard_mask(
                int(network.split("/")[1])
            )
            area = network.split("/")[2]
            self.connection.send_command(
                f"network {ip} {wildcard} {area}",
                expect_string=""
            )
    
    def passive_interfaces(self):
        """ Defines all passive interfaces """
        for interface in self.ospf_data["passive_interfaces"]:
            self.connection.send_command(
                f"passive-interface {interface}",
                expect_string=""
            )