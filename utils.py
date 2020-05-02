import json
import re
import os
from time import strftime, localtime
from pathlib import Path
from netaddr import IPNetwork
from time import sleep
from socket import inet_ntoa
from struct import pack
from napalm import get_network_driver
from LANwhiz.exceptions import DeviceNotFoundException, InvalidCommandException
from LANwhiz.connect import Connect

class Utilities(object):
    """ Utilities class """
    home_path = Path(__file__).parent
    devices_path = f"{home_path}/devices/"

    def __init__(self, connection):
        self.connection = connection
        self.prompt = connection.find_prompt()
        self.napalm_connection = self._get_napalm_connection()

    def send_command(self, command, on_fail_reload=False, web=False):
        """ Helper function to send a command to device """
        response = ""
        
        if "sh" == command[:2] and "|" not in command:
            self.connection.write_channel(f"{command}\r\n")
            if re.match(r"^sh.*\s(run|start).*$", command):
                while "end\r\n" not in response:
                    response += self.connection.read_channel()
                    sleep(0.5)
                return response
            else:
                sleep(2)
            
            return self.connection.read_channel()
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
        hostname = hostname + ".json"
        if hostname in os.listdir(Utilities.devices_path):
            with open(f"{Utilities.devices_path}{hostname}", "r") as config_file:
                return json.loads(config_file.read())
        else:
            raise DeviceNotFoundException(
                f"Config for '{hostname}' "
                "does not exist"
            )

    @staticmethod
    def write_config(hostname, new_config):
        """ Write a new config to a template 
        
        Args:
            hostname: Hostname of device to write configuration for
        """
        hostname = hostname + ".json"
        if not hostname in os.listdir(Utilities.devices_path):
            raise DeviceNotFoundException(
                f"Config for '{hostname}' "
                "does not exist"
            )
        if new_config["config"]["routing"].get("ospf"):
            elems = ("advertise_networks", "passive_interfaces", "other_commands")
            for elem in elems:
                if new_config["config"]["routing"]["ospf"].get(elem):
                    if isinstance(new_config["config"]["routing"]["ospf"][elem], str):
                        cfg = new_config["config"]["routing"]["ospf"][elem]
                        new_config["config"]["routing"]["ospf"][elem] = cfg.split(",")
        with open(f"{Utilities.devices_path}{hostname}", "w") as config_file:
            config_file.write(json.dumps(new_config, indent=4))
                
    @staticmethod
    def prefix_to_subnet_mask(prefix):
        """ Convert Prefix to Subnet Mask
        
        Args:
            prefix: Prefix to be converted

        Returns:
            Converted Subnet Mask
        """
        assert prefix in range(8, 31), f"Invalid Prefix value {prefix}!"

        return inet_ntoa(pack('!I', (1 << 32) - (1 << 32 - prefix)))

    def prefix_to_wildcard_mask(self, prefix):
        """ Convert Prefix to Wildcard Mask
        
        Args:
            prefix: Prefix to be converted

        Returns:
            Converted Wildcard Mask
        """
        assert prefix in range(8, 31), f"Invalid Prefix value {prefix}!"
        subnetmask = self.prefix_to_subnet_mask(prefix)

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
        elif re.match(r".+\>$", prompt):
            self.send_command("enable")
            self.send_command("class")
            self.send_command("conf t")
    
    def get_structured_config(self, config_type="running"):
        """ Use Napalm connection to retrieve config and use it to
        form a hierarchical dictionary.
        """
        struct_config = {
            "global_commands": [],
        }

        # Dropping down to priv exec mode for config
        if "(config" in self.connection.find_prompt():
            self.send_command("end")

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
        devices_dir = os.listdir(Utilities.devices_path)
        return  {"devices": [device.rstrip(".json") for device in devices_dir]}

    @staticmethod
    def add_new_device(
        mgmt_ip, 
        mgmt_port, 
        username=None, 
        password=None, 
        new_hostname=None
    ):
        """ Connect to device and create a JSON record of it """
        
        params = {
            "mgmt_ip": mgmt_ip, 
            "port": int(mgmt_port),
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

        if new_hostname:
            hostname = new_hostname
            cmds = ["enable", "class", "conf t", f"hostname {hostname}", "quit"]
            utils = Utilities(connection)

            for cmd in cmds:
                utils.send_command(cmd)
        else:
            hostname = connection.find_prompt().rstrip("#>")

        new_config = {
            "hostname": hostname,
            "mgmt_ip": mgmt_ip,
            "mgmt_port": mgmt_port,
            "username": username,
            "password": password,    # Use Salting/Hashing/Secure Storage
            "last_modified": strftime("%d/%m/%Y %H:%M:%S", localtime()),
            "config": {
                "global_commands": [],
                "interfaces": {
                    interface: {
                        "shutdown": True,
                        "ipv4": "",
                        "ipv6": "",
                        "description": "",
                        "acl": {
                            "outbound": [],
                            "inbound": []
                        },
                        "nat": "",
                        "bandwidth": None,
                        "other_commands": []
                    } for interface in utils.get_interfaces()
                },
                "lines": {
                    line: {
                        "password": "",
                        "acl": {
                            "inbound": [],
                            "outbound": []
                        },
                        "synchronous_logging": False,
                        "other_commands": []
                    } for line in ("console", "vty")
                },
                "routing":{
                    "static": []
                },
                "acl": {},
                "dhcp": {}
            } 
        }

        with open(
            f"{utils.devices_path}/{hostname}.json", "w"
        ) as config_file:
            config_file.write(json.dumps(new_config, indent=4))

        return new_config

    @staticmethod
    def get_network_address(ip):
        """ Uses the IPv4 and prefix length combination to return a 
            network address
        """
        ip, prefix = ip.split("/")
        subnetmask = Utilities.prefix_to_subnet_mask(int(prefix))

        return str(IPNetwork(f"{ip}/{subnetmask}").network), prefix

    @staticmethod
    def merge_config(current, new):
        for k, v in new.items():
            if isinstance(v, dict):
                current[k] = merge_config(current.get(k, {}), v)
            else:
                current[k] = v
        return current

    