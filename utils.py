import json
import os

class Utilities():

    def read_config(self, hostname):
        """ Provide config information given device's hostname
        
        Args:
            hostname: Hostname of device to get configuration for
        
        Returns:
            Dictionary of all configuration specifications for a 
            particular device.
        """
        json_path = f"{os.getcwd()}\\devices.json".replace("\\", "/")
        with open(json_path, "r") as config_file:
            self.config = json.loads(config_file.read())
        
        return self.config[hostname]

    def cidr_to_subnet_mask(self, cidr):
        assert cidr in range(8, 31), "Invalid value for CIDR!"
        octets = []
        possible_octets = ["128","192","224","240","248","252","254"]
        full_octets = cidr // 8
        for _ in range(full_octets):
            octets.append("255")
        leftover_bits = cidr - (full_octets * 8)
        if leftover_bits:
            octets.append(f"{possible_octets[leftover_bits-1]}")
        while not len(octets) == 4:
            octets.append("0")

        return ".".join(octets)

    def cidr_to_wildcard_mask(self, cidr):
        assert cidr in range(8, 31), "Invalid value for CIDR!"
        octets = []
        for octet in self.cidr_to_subnet_mask(cidr).split("."):
            octet = 255 - int(octet)
            octets.append(str(octet))

        return ".".join(octets)