import json
import re
import os
from time import sleep
from socket import inet_ntoa
from struct import pack
from napalm import get_network_driver
from LANwhiz.exceptions import DeviceNotFoundException, InvalidCommandException
from LANwhiz.connect import Connect

class Utilities(object):
    """ Utilities class """
    home_path = os.path.abspath('')
    for replace in (('\\', '/'), ('web', '')):
        home_path = home_path.replace(*replace)
    devices_path = f"{home_path}devices/"
    supported_device_types = ("routers", "switches")

    def __init__(self, connection=None):
        self.connection = connection
        self.napalm_connection = self._get_napalm_connection() if connection else None
        self.path = "C:/Users/User/Desktop/The vicious Snake/LANwhiz/cmds.txt"

    def send_command(self, command, on_fail_reload=False, web=False):
        """ Helper function to send a command to device """
        response = ""
        
        if "sh" == command[:2]:
            self.connection.write_channel(f"{command}\r\n")
            # Reading the channel after a second for more output
            for _ in range(2):
                response += self.connection.read_channel()
                sleep(0.5)
            while "--More--" in response:
                response = response.replace("--More--", "")
                self.connection.write_channel(r"\s")
                sleep(0.3)
                response += self.connection.read_channel()

            return response
        else:
            response = self.connection.send_command(command, expect_string="")
            
        # Check if command sent has not been rejected by IOS
        if not web and "Invalid input detected" in response:
            prompt = self.connection.find_prompt()
            self.connection.send_command("end", expect_string="")
            if on_fail_reload:    
                response = self.connection.send_command("reload", expect_string="")
                if "configuration has been modified. Save?" in response:
                    self.connection.send_command("no", expect_string="")
                self.connection.send_command("", expect_string="")
            raise InvalidCommandException(
                f"'{prompt}{command}' marked invalid by IOS. "
                "Reloading device - revert back to startup config."
            )
        
        return response

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
        path = Utilities.devices_path
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

    def cidr_to_subnet_mask(self, cidr):
        """ Convert CIDR to Subnet Mask
        
        Args:
            cidr: CIDR to be converted

        Returns:
            Converted Subnet Mask
        """
        assert cidr in range(8, 31), f"Invalid CIDR value {cidr}!"

        return inet_ntoa(pack('!I', (1 << 32) - (1 << 32 - cidr)))

    def cidr_to_wildcard_mask(self, cidr):
        """ Convert CIDR to Wildcard Mask
        
        Args:
            cidr: CIDR to be converted

        Returns:
            Converted Wildcard Mask
        """
        assert cidr in range(8, 31), f"Invalid CIDR value {cidr}!"
        subnetmask = self.cidr_to_subnet_mask(cidr)

        return ".".join([str(255 - int(octet)) for octet in subnetmask.split(".")])

    def get_interfaces(self):
        """ Returns a list of interfaces using Napalm """
        interfaces = self.napalm_connection.get_interfaces()
        
        return list(interfaces.keys())

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
    
    def get_structured_config(self, config_type="startup"):
        """ Use Napalm connection to retrieve config and use it to
        form a hierarchical dictionary.
        """
        struct_config = {
            "global_commands": [],
        }
        device_config = self.napalm_connection.get_config()
        config = [
            line for line in device_config[config_type].split("\n") 
                if line and "!" not in line 
        ]
        config = config[4:-1] if config_type == "running" else config[1:-1]

        for line in config:
            if line[0] == " ":
                try:
                    struct_config[last_key].append(line[1:])
                except KeyError:
                    struct_config[last_key] = [line[1:]]
                if last_key in struct_config["global_commands"]:
                    struct_config["global_commands"].remove(last_key)
            else:
                last_key = line
                struct_config["global_commands"].append(line)

        return struct_config

    @staticmethod
    def get_all_devices():
        """ Gets all device records from ./devices """
        home_path = Utilities.devices_path
        devices = {}
        for device_type in Utilities.supported_device_types:
            devices_dir = os.listdir(f"{home_path}{device_type}")
            devices[device_type] = [
                device.rstrip(".json") for device in devices_dir
            ]

        return devices

    @staticmethod
    def add_new_device(host, port, username=None, password=None):
        """ Connect to device and create a JSON record of it """
        
        params = {
            "mgmt_ip": host, 
            "port": port,
            "username": username,
            "password": password
        }

        connect_to = Connect()
        
        # TODO: Change print statements to JSON response to UI
        try:
            print("Connecting..")
            connection = connect_to.cisco_device(**params)
        except Exception as e:
            print("Connection failed.")
            print(f"Message: {e.args[0]}")

        utils = Utilities(connection)
        hostname = connection.find_prompt().rstrip("#")

        new_config = {
            "hostname": hostname,
            "mgmt_ip": host,
            "mgmt_port": port,
            "username": username,
            "password": password,    # Use Salting/Hashing/Secure Storage
            "config": {
                "interfaces": {
                    interface: {
                        "ipv4": "",
                        "ipv6": "",
                        "description": "",
                        "acl": {
                            "outbound": [],
                            "inbound": []
                        },
                        "nat": ""
                    } for interface in utils.get_interfaces()
                }
            } 
        }

        with open(
            f"{utils.devices_path}routers/{hostname}.json", "w"
        ) as config_file:
            config_file.write(json.dumps(new_config, indent=4))

        return new_config