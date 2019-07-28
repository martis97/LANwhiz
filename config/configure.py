from net_auto_config.utils import Utilities
from net_auto_config.config.interface import Interface, Line
from net_auto_config.config.routing import Static, OSPF
from net_auto_config.config.acl import AccessControlLists


class Configure(object):
    def __init__(self, *, device_config, connection):
        self.config = device_config
        self.connection = connection
        self.utils = Utilities(connection)
        
    def default_commands(self):
        """ Sends pre-defined default commands to the console. """
        for cmd in self.config["default_commands"]:
            self.connection.send_command(cmd, expect_string="")

    def superuser(self):
        details = self.config["superuser"]
        command = (
            f"username {details['username']} "
            f"password {details['pass']} "
            f"privilege {details['privilege']}"
        )
        self.connection.send_command(command, expect_string="")

    def interfaces(self):
        """ Pass configuration information to class methods for interface
        configuration.
        """
        configure_interface = Interface(self.connection)
        for interface, int_config in self.config["interfaces"].items():
            self.utils.ensure_global_config_mode()
            access_interface = f"interface {interface}"
            self.connection.send_command(
                access_interface, expect_string=""
            )
            self.connection.send_command("no shutdown", expect_string="")
            if int_config["ipv4"]:
                configure_interface.ipv4(int_config["ipv4"])
            if int_config["ipv6"]:
                configure_interface.ipv6(int_config["ipv6"])
            if int_config["description"]:
                configure_interface.description(
                    int_config["description"]
                )
            if int_config["acl"]:
                configure_interface.acl(
                    interface,
                    inbound=int_config["acl"].get("inbound"),
                    outbound=int_config["acl"].get("outbound")
                )
            if int_config["nat"]:
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
            self.connection.send_command(access_line, expect_string="")
            if line_config["password"]:
                configure_line.password(line_config["password"])
            if line_config["acl"]["inbound"] \
                or line_config["acl"]["outbound"]:
                configure_line.acl(**line_config["acl"])
            if line_config["synchronous_logging"]:
                configure_line.synchronous_logging()
    
    def routing(self):
        """ Pass config information to class methods for routing """
        static_routing = Static(self.connection)
        for static_info in self.config["routing"]["static"]:
            static_routing.send_static_route_command(**static_info)
        if self.config["routing"]["ospf"]:
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
        config_acl.standard()
        config_acl.extended()