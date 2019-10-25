from LANwhiz.utils import Utilities
from LANwhiz.config.interface import Interface, Line
from LANwhiz.config.routing import Static, OSPF
from LANwhiz.config.acl import AccessControlLists
from LANwhiz.config.dhcp import DHCPPool


class Configure(object):
    def __init__(self, *, device_config, connection):
        self.config = device_config
        self.connection = connection
        self.utils = Utilities(connection)
        self.utils.ensure_global_config_mode()

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
        configure_interface = Interface(self.connection)
        for interface, int_config in self.config["interfaces"].items():
            self.utils.ensure_global_config_mode()
            access_interface = f"interface {interface}"
            self.utils.send_command(access_interface)
            self.utils.send_command("no shutdown")
            if int_config.get("ipv4"):
                configure_interface.ipv4(int_config["ipv4"])
            if int_config.get("ipv6"):
                configure_interface.ipv6(int_config["ipv6"])
            if int_config.get("description"):
                configure_interface.description(
                    int_config["description"]
                )
            if int_config["acl"].get("inbound") \
                or int_config["acl"].get("outbound"):
                configure_interface.acl(
                    interface,
                    inbound=int_config["acl"].get("inbound"),
                    outbound=int_config["acl"].get("outbound")
                )
            if int_config.get("nat"):
                configure_interface.nat(int_config["nat"])

    def lines(self):
        """ Pass configuration information to class methods for line
        configuration.
        """
        configure_line = Line(self.connection)
        for line, line_config in self.config["lines"].items():
            self.utils.ensure_global_config_mode()
            access_line = f"line {line}"
            if line == "console":
                access_line += " 0"
            elif line == "vty":
                access_line += " 0 4"
            self.utils.send_command(access_line)
            if line_config.get("password"):
                configure_line.password(line_config["password"])
            if line_config["acl"]["inbound"] \
                or line_config["acl"]["outbound"]:
                configure_line.acl(**line_config["acl"])
            if line_config.get("synchronous_logging"):
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