from LANwhiz.config.base import BaseConfig


class StaticRoute(BaseConfig):
    def __init__(self, connection, config):
        super().__init__(connection, config)

    def send_static_route_command(self):
        """ Configures a static route on a device """
        self.utils.send_command(
            f"ip route {self.config['network']} {self.config['subnetmask']}"
            f" {self.config['forward_to']}"
        )


class OSPF(BaseConfig):
    def __init__(self, connection, config):
        super().__init__(connection, config)
        self.utils.send_command(
            f"router ospf {self.config['instance_id']}"
        )
    
    def router_id(self):
        """ Define the router's ID for OSPF instance """
        self.utils.send_command(
            f"router-id {self.config['router_id']}"
        )

    def advertise_static_routes(self):
        """ Distribute default static routes to OSPF network """
        if self.config.get("advertise_static"):
            self.utils.send_command("default-information originate")
    
    def advertise_networks(self):
        """ Advertises OSPF networks """
        if self.config.get("advertise_networks"):
            for network in self.config["advertise_networks"]:
                ip, cidr, area = network.split("/")
                wildcard = self.utils.cidr_to_wildcard_mask(int(cidr))
                self.utils.send_command(f"network {ip} {wildcard} {area}")
    
    def passive_interfaces(self):
        """ Defines all passive interfaces """
        if self.config.get("passive_interfaces"):
            for interface in self.config["passive_interfaces"]:
                self.utils.send_command(f"passive-interface {interface}")

    def other_commands(self):
        """ Sends other commands on OSPF-level configuration """
        if self.config.get("other_commands"):
            for cmd in self.config["other_commands"]:
                self.utils.send_command(cmd)