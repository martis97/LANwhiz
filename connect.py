from netmiko import Netmiko
from getpass import getpass

"""
AutoConf: Connection Module

- Sets up SSH connections and handles them
- Authenticates to devices with adequate credentials

"""
class Connect():

    def __init__(self):
        self.active_connections = 0
        
    def cisco_device(
        self,
        port,
        ip_address,
        username,
        password,
        telnet=False
    ):
        """ Establishes a connection to a Cisco devices

        Args:
            ip_address: Management IP address used to connect to the 
                device.
            username: Privileged user's username 
            password: Privileged user's password

        Returns:
            Netmiko connection object
        """
        cisco_device = {
            "ip": ip_address,
            "port": port,
            "username": username,
            "password": password,
            "device_type": "cisco_ios"
        }

        if telnet:
            cisco_device["device_type"] += "_telnet"

        self.active_connections += 1
        return Netmiko(**cisco_device)
