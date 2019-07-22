import json
import re

class Utilities():

    def read_config(self, hostname):
        """ Provide config information given device's hostname 
        
        Args:
            hostname: Hostname of device to get configuration for
        
        Returns:
            Dictionary of all configuration specifications for a 
            particular device.
        """
        with open("C:/Users/User/Desktop/The vicious Snake/net_auto_config/devices.json", "r") as config_file:
            self.config = json.loads(config_file.read())
        
        return self.config[hostname]

    def cidr_to_subnet_mask(self, cidr):
        """ Convert CIDR to Subnet Mask
        
        Args:
            cidr: CIDR to be converted

        Returns:
            Converted Subnet Mask
        """
        assert cidr in range(8, 31), f"Invalid CIDR value {cidr}!"
        octets = []
        possible_octets = ["128","192","224","240","248","252","254"]
        for _ in range(cidr // 8):
            octets.append("255")
        bits_left = cidr % 8
        if bits_left:
            octets.append(possible_octets[bits_left - 1])
        while not len(octets) == 4:
            octets.append("0")

        return ".".join(octets)

    def cidr_to_wildcard_mask(self, cidr):
        """ Convert CIDR to Wildcard Mask
        
        Args:
            cidr: CIDR to be converted

        Returns:
            Converted Wildcard Mask
        """
        assert cidr in range(8, 31), f"Invalid CIDR value {cidr}!"
        octets = []
        for octet in self.cidr_to_subnet_mask(cidr).split("."):
            octet = 255 - int(octet)
            octets.append(str(octet))

        return ".".join(octets)

    @staticmethod
    def ensure_global_config_mode(connection):
        """ Ensures the configuration level is set to global config mode.
        Will exit down to privileged exec mode, then escalate to global 
        config. 

        E.g.
            If the prompt is:
                R1(config-if)#
            It will send commands 'end' (CTRL+Z) and 'conf t'.

        or,
            If the prompt is:
                R1#
            It will send a command 'conf t' only.

        Args: 
            connection: Netmiko connection object
        """
        if re.match(r"^.+\(config.+\)#$", connection.find_prompt()):
            connection.send_command("end", expect_string="")
            connection.send_command("conf t", expect_string="")
        elif re.match(r"^[A-Za-z0-9\-]+\#$", connection.find_prompt()):
            connection.send_command("conf t", expect_string="")