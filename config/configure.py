from LANwhiz.utils import Utilities
from LANwhiz.config.interface import Interface, Line
from LANwhiz.config.routing import Static, OSPF
from LANwhiz.config.acl import AccessControlLists
from LANwhiz.config.dhcp import DHCPPool
from LANwhiz.config.base import BaseConfig


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
            init_cmds = (f"interface {interface}", "no shutdown")
            for cmd in init_cmds:
                self.utils.send_command(cmd)
            configure_interface.ipv4()
            configure_interface.ipv6()
            configure_interface.description()
            configure_interface.acl()
            configure_interface.nat()

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
        static_routing = Static(self.connection)
        for static_info in self.config["routing"].get("static"):
            static_routing.send_static_route_command(**static_info)
        if self.config["routing"].get("ospf"):
            ospf_routing = OSPF(
                self.connection,
                self.config["routing"]["ospf"]
            )
            ospf_routing.router_id()
            ospf_routing.advertise_static_routes()
            ospf_routing.advertise_networks()
            ospf_routing.passive_interfaces()
    
    def acl(self):
        """ Configure ACLs on the device """
        config_acl = AccessControlLists(self.connection, self.config["acl"])
        for acl_type in ("standard", "extended"):
            if self.config["acl"].get(acl_type):
                getattr(config_acl, acl_type)()

    def dhcp(self):
        """ Configures DHCP on the device """
        for pool in self.config["dhcp"]:
            dhcp_pool = DHCPPool(self.connection, config=pool)            
            methods = [
                method for method in dir(DHCPPool) if method[0] != "_"
            ]
            for method in methods:
                getattr(dhcp_pool, method)()