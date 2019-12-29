from LANwhiz.config.base import BaseConfig
from LANwhiz.config.interface import Interface, Line
from LANwhiz.config.routing import StaticRoute, OSPF
from LANwhiz.config.acl import AccessControlLists
from LANwhiz.config.dhcp import DHCPPool


class ConfigActions(BaseConfig):
    def __init__(self, *, connection, device_config):
        super().__init__(connection, device_config)

    def default_commands(self):
        """ Sends pre-defined default commands to the console. """
        for cmd in self.config["default_commands"]:
            self.utils.send_command(cmd)

    def superuser(self):
        details = self.config["superuser"]
        command = (
            f"username {details['username']} "
            f"password {details['pass']} "
            f"privilege {details['privilege']}"
        )
        self.utils.send_command(command)

    def interfaces(self):
        """ Pass configuration information to class methods for interface
        configuration.
        """
        int_config = self.config["interfaces"]
        for interface, config in int_config.items():
            configure_interface = Interface(self.connection, config)
            for cmd in (f"interface {interface}", "no shutdown"):
                self.utils.send_command(cmd)
            configure_interface.ipv4()
            configure_interface.ipv6()
            configure_interface.description()
            configure_interface.acl()
            configure_interface.nat()
            configure_interface.other_config()

    def lines(self):
        """ Pass configuration information to class methods for line
        configuration.
        """
        for line, line_config in self.config["lines"].items():
            configure_line = Line(self.connection, line_config)
            access_line = f"line {line}"
            if line == "console":
                access_line += " 0"
            elif line == "vty":
                access_line += " 0 4"
            self.utils.send_command(access_line)
            configure_line.password()
            configure_line.acl()
            configure_line.synchronous_logging()
    
    def routing(self):
        """ Pass config information to class methods for routing """
        if self.config.get("routing"):
            config = self.config["routing"]
            if config.get("static"):
                for static_route_config in config.get("static"):
                    static_routing = StaticRoute(self.connection, static_route_config)
                    static_routing.send_static_route_command()
            if config.get("ospf"):
                ospf_routing = OSPF(
                    self.connection,
                    config.get("ospf")
                )
                ospf_routing.router_id()
                ospf_routing.advertise_static_routes()
                ospf_routing.advertise_networks()
                ospf_routing.passive_interfaces()
                ospf_routing.other_commands()
        
    def acl(self):
        """ Configure ACLs on the device """
        acl = AccessControlLists(self.connection, self.config["acl"])
        for acl_type in ("standard", "extended"):
            if acl.config.get(acl_type):
                getattr(acl, acl_type)()

    def dhcp(self):
        """ Configures DHCP on the device """
        for pool in self.config["dhcp"]:
            dhcp_pool = DHCPPool(self.connection, config=pool)            
            methods = [
                method for method in dir(DHCPPool) if method[0] != "_"
            ]
            for method in methods:
                getattr(dhcp_pool, method)()