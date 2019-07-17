from net_auto_config.utils import Utilities
from net_auto_config.config.interface import Interface, Line
from net_auto_config.connect import Connect


class Configure(object):
    def __init__(self, *, device_config, connection):
        self.config = device_config
        self.connection = connection
        self.utils = Utilities()
        
        
    def default_commands(self):
        """ Sends pre-defined default commands to the console. """
        for cmd in self.config["default"]:
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
        self.configure_interface = Interface(self.connection)
        for interface, int_config in self.config["interfaces"].items():
            access_interface = f"interface {interface}"
            self.connection.send_command(
                access_interface, expect_string=""
            )
            if int_config["ipv4"]:
                self.configure_interface.ipv4(int_config["ipv4"])
            if int_config["ipv6"]:
                self.configure_interface.ipv6(int_config["ipv6"])
            if int_config["description"]:
                self.configure_interface.description(
                    int_config["description"]
                )
            if int_config["acl"]:
                self.configure_interface.acl(
                    interface,
                    inbound=int_config["acl"].get("inbound"),
                    outbound=int_config["acl"].get("outbound")
                )
            if int_config["nat"]:
                self.configure_interface.nat(int_config["nat"])

    def lines(self):
        """ Pass configuration information to class methods for line
        configuration.
        """
        self.configure_line = Line(self.connection)
        for line, line_config in self.config["lines"].items():
            access_line = f"line {line}"
            if line == "console":
                access_line += " 0"
            elif line == "vty":
                access_line += " 0 4"
            self.connection.send_command(access_line, expect_string="")
            if line_config["password"]:
                self.configure_line.password(line_config["password"])
            if line_config["acl"]["inbound"] \
                or line_config["acl"]["outbound"]:
                self.configure_line.acl(**line_config["acl"])
            if line_config["synchronous_logging"]:
                self.configure_line.synchronous_logging()