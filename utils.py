import json
import re
import os
from napalm import get_network_driver
from LANwhiz.exceptions import DeviceNotFoundException, InvalidCommandException

class Utilities(object):
    """ Utilities class """
    home_path = "C:/Users/User/Desktop/The vicious Snake/LANwhiz/devices/"
    supported_device_types = ("routers", "switches")

    def __init__(self, connection):
        self.connection = connection
        self.napalm_connection = self._get_napalm_connection()

    def send_command(self, command):
        """ Helper function to send a command to device """
        response = self.connection.send_command(command, expect_string="")
        # Check if command sent has not been rejected by IOS
        if "Invalid input detected" in response:
            prompt = self.connection.find_prompt()
            self.connection.send_command("end", expect_string="")
            response = self.connection.send_command("reload", expect_string="")
            if "System configuration has been modified" in response:
                self.connection.send_command("no", expect_string="")
            self.connection.send_command("", expect_string="")
            raise InvalidCommandException(
                f"'{prompt}{command}' Has been detected as invalid by IOS"
            )

    def _get_napalm_connection(self):
        """ Gets a Napalm connection object """
        ios_driver = get_network_driver("ios")

        # Getting a Napalm instance with no connection needed
        napalm_connection = ios_driver(
            hostname=None, username=None, password=None
        )
        # ... and re-using our existing Netmiko connection object!
        napalm_connection.device = self.connection

        return napalm_connection

    @staticmethod
    def read_config(hostname):
        """ Provide config information given device's hostname 
        
        Args:
            hostname: Hostname of device to get configuration for
        
        Returns:
            Dictionary of all configuration specifications for a 
            particular device.
        """
        path = Utilities.home_path
        hostname = hostname + ".json"
        if hostname in os.listdir(f"{path}routers"):
            devices_path = path + "routers/"
        elif hostname in os.listdir(f"{path}switches"):
            devices_path = path + "switches/"
        else:
            raise DeviceNotFoundException(
                f"Config for '{hostname}' "
                "does not exist"
            )
        with open(f"{devices_path}{hostname}", "r") as config_file:
                config = json.loads(config_file.read())
                
        return config

    def cidr_to_subnet_mask(self, cidr, int_list=False):
        """ Convert CIDR to Subnet Mask
        
        Args:
            cidr: CIDR to be converted

        Returns:
            Converted Subnet Mask
        """
        assert cidr in range(8, 31), f"Invalid CIDR value: {cidr}!"
        octets = []
        possible_octets = ["128","192","224","240","248","252","254"]
        for _ in range(cidr // 8):
            octets.append("255")
        bits_left = cidr % 8
        if bits_left:
            octets.append(possible_octets[bits_left - 1])
        while not len(octets) == 4:
            octets.append("0")
        if int_list:
            return [int(octet) for octet in octets]

        return ".".join(octets)

    def cidr_to_wildcard_mask(self, cidr):
        """ Convert CIDR to Wildcard Mask
        
        Args:
            cidr: CIDR to be converted

        Returns:
            Converted Wildcard Mask
        """
        assert cidr in range(8, 31), f"Invalid CIDR value {cidr}!"
        subnetmask = self.cidr_to_subnet_mask(cidr, int_list=True)

        return ".".join([str(255 - octet) for octet in subnetmask])

    def get_interfaces(self):
        """ Returns a list of interfaces using Napalm """
        interfaces = self.napalm_connection.get_interfaces()
        
        return [interface for interface in interfaces.keys()]

    def ensure_global_config_mode(self):
        """ Ensures the configuration level is set to global config mode.
        Will exit down to privileged exec mode, then escalate to global 
        config. 

        E.g.
            If the prompt is:
                R1(config-if)#
            It will send commands 'end' and 'conf t' consequently.

        or,
            If the prompt is:
                R1#
            It will send a command 'conf t' only.
        """
        prompt = self.connection.find_prompt()
        if re.match(r"^.+\(config.+\)\#$", prompt):
            self.send_command("end")
            self.send_command("conf t")
        elif re.match(r"^[A-Za-z0-9\-]+\#$", prompt):
            self.send_command("conf t")

    def build_initial_config_template(self):
        """ Creates an initial 'config' section for config param file """
        interfaces = self.get_interfaces()
        config = {
            "default_commands": [
                "no ip domain-lookup",
                "service password-encryption"
            ],
            "interfaces": {},
            "lines": {
                "console": {
                    "password": "",
                    "acl": {
                        "inbound": [],
                        "outbound": []
                    },
                    "synchronous_logging": False
                },
                "vty": {
                    "password": "",
                    "acl": {
                        "inbound": [],
                        "outbound": []
                    },
                    "synchronous_logging": False
                }
            },
            "routing": {
                "static": [],
                "ospf": {}
            },
            "acl": {
                "standard": {},
                "extended": {}
            },
            "dhcp": []
        }

        for interface in interfaces:
            config["interfaces"][interface] = {
                "ipv4": "",
                "ipv6": "",
                "description": "",
                "acl": {
                    "outbound": [],
                    "inbound": []
                },
                "nat": ""
            }

        return config 

    @staticmethod
    def get_all_devices():
        """ Gets all device records from ./devices """
        home_path = Utilities.home_path
        devices = {}
        for device_type in Utilities.supported_device_types:
            devices_dir = os.listdir(f"{home_path}{device_type}")
            devices[device_type] = [
                device.rstrip(".json") for device in devices_dir
            ]

        return devices