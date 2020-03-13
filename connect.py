from netmiko import Netmiko

"""
AutoConf: Connection Module

- Sets up SSH/Telnet connections and handles them
- Authenticates to devices with adequate credentials

"""
class Connect(object):

    def __init__(self):
        self.active = {}
        
    def cisco_device(
        self,
        mgmt_ip,
        port,
        username=None,
        password=None,
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

        if port == 23 or port >= 5000:
            cisco_device["device_type"] += "_telnet"

        connection = Netmiko(**cisco_device)
        hostname = connection.find_prompt().rstrip("#")

        self.active.update({hostname: connection})

        return connection 
        
