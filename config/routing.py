from net_auto_config.utils import Utilities

class Routing(object):
    def __init__(self, connection):
        self.connection = connection
        self.utils = Utilities()
    

class Static(Routing):
    def __init__(self):
        super().__init__()
    
    def send_static_route_command(self, network, subnetmask, forward_to):
        """ Configures a static route on a device """
        self.connection.send_command(
            f"ip route {network} {subnetmask} {forward_to}",
            expect_string=""
        )


class OSPF(Routing):
    def __init__(self, ospf_data):
        super().__init__()
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