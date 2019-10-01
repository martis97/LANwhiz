import json
import re
import os
from napalm import get_network_driver
from LANwhiz.exceptions import DeviceNotFoundException

class Utilities(object):
    """ Utilities class """
    home_path = "C:/Users/User/Desktop/The vicious Snake/LANwhiz/devices/"

    def __init__(self, connection):
        self.connection = connection
        self.napalm_conn = self._get_napalm_connection()

    def send_command(self, command):
        """ Helper function to send a command to device """
        self.connection.send_command(command, expect_string="")

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
            devices_path = path + "routers"
        elif hostname in os.listdir(f"{path}switches"):
            devices_path = path + "switches"
        else:
            raise DeviceNotFoundException(
                f"Config for '{hostname}' "
                "does not exist"
            )
        with open(f"{devices_path}/{hostname}", "r") as config_file:
                config = json.loads(config_file.read())
                
        return config
    
    # def write_config(self, hostname, new_config):
    #     """ Write config given device's hostname.

    #     Args:
    #         hostname: Hostname of device (Root key dict value)
    #     """
    #     self.config[hostname] = new_config
    #     with open(self.devices_path, "w") as config_file:
    #         self.config = json.dumps(config_file.read())

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
        interfaces = self.napalm_conn.get_interfaces()
        
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

    @staticmethod
    def get_all_devices():
        """ Gets all device records from ./devices """
        home_path = Utilities.home_path
        supported_device_types = ("routers", "switches")
        for device_type in supported_device_types:
            devices_dir = os.listdir(f"{home_path}{device_type}")
            hostnames = []
            for device in devices_dir:
                with open(
                    f"{home_path}/{device_type}/{device}", "r"
                ) as device_json:
                    content = json.loads(device_json.read())
                    hostnames.append(content["hostname"])
            globals()[device_type] = hostnames

        devices = {
            "routers": routers,
            "switches": switches
        }

        return devices
    
    def map_file_to_host_names(self):
        """ Maps JSON file names to the host name defined within the 
        file.
        
        Returns:
            host_to_file_name_map - Dictionary object containing all 
                names of config files maped with their device hostnames.
        """
        router_files = os.listdir(f"{self.home_path}/routers")


