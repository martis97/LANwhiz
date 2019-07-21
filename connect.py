from netmiko import Netmiko
from getpass import getpass

"""
AutoConf: Connection Module

- Sets up SSH/Telnet connections and handles them
- Authenticates to devices with adequate credentials

"""
class Connect(object):

    def __init__(self):
        self.active_connections = 0
        
    def cisco_device(
        self,
        mgmt_ip,
        port,
        username,
        password,
        telnet=False
    ):
        """ Establishes a connection to a Cisco devices

        Args:
            mgmt_ip: Management IP address used to connect to the 
                device.
            port: Port number the device is listening to
            username: Privileged user's username 
            password: Privileged user's password
            telnet: (Default: False) Boolean value to specify whether 
                the connection will be established using Telnet. 

        Returns:
            Netmiko connection object
        """
        cisco_device = {
            "ip": mgmt_ip,
            "port": port,
            "username": username,
            "password": password,
            "device_type": "cisco_ios"
        }

        if telnet:
            cisco_device["device_type"] += "_telnet"

        print("Connecting to Cisco Device..")
        connection = Netmiko(**cisco_device)
        print("Connected")

        self.active_connections += 1

        return connection 
        
