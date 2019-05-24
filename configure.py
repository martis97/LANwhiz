from net_auto_config.utils import Utilities
from net_auto_config.config.interface import Interface
from net_auto_config.connect import Connect


class Configure(object):
    def __init__(self, *, device_config, connection):
        self.config = device_config
        self.connection = connection
        self.utils = Utilities()
        self.configure_interface = Interface()

    def superuser(self):
        details = self.config["superuser"]
        command = (
            f"username {details['username']} " 
            f"password {details['pass']} " 
            f"privilege {details['privilege']}"
        )
        self.connection.send_command(command)

    def interfaces(self):
        """ Pass configuration information to class methods for interface
        configuration.
        """
        for interface, int_config in self.config["interfaces"].items():
            self.connection.send_command(f"interface {interface}")
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
                    inbound=int_config.get("inbound"),
                    outbound=int_config.get("outbound")
                )
            if int_config["nat"]:
                self.configure_interface.nat(int_config["nat"])