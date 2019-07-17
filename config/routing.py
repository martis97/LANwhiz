from net_auto_config.utils import Utilities
import re

class Static(object):
    def __init__(self, connection):
        self.connection = connection
        self.utils = Utilities()
        self.connection.config_mode()
        if "config-" in self.connection.find_prompt():
            self.connection.send_command("end", expect_string="")
            self.connection.send_command("conf t", expect_string="")
    
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
        self.connection.send_command(
            f"router ospf {self.ospf_data['instance_id']}",
            expect_string=""
        )
    
    def router_id(self):
        self.connection.send_command(
            f"router-id {self.ospf_data['router_id']}",
            expect_string=""
        )

    def advertise_static_routes(self):
        self.connection.send_command(
            "default-information originate",
            expect_string=""
        )