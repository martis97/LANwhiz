import json
import re
from napalm import get_network_driver

class Utilities(object):
    """ Utilities class """
    def __init__(self, connection):
        self.connection = connection
        self.napalm_conn = self._get_napalm_connection()
        self.json_path = "C:/Users/User/Desktop/The vicious Snake/net_auto_config/devices.json"

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

    def read_config(self, hostname):
        """ Provide config information given device's hostname 
        
        Args:
            hostname: Hostname of device to get configuration for
        
        Returns:
            Dictionary of all configuration specifications for a 
            particular device.
        """
        with open(self.json_path, "r") as config_file:
            self.config = json.loads(config_file.read())
        
        return self.config[hostname]
    
    def write_config(self, hostname, new_config):
        """ Write config given device's hostname.

        Args:
            hostname: Hostname of device (Root key dict value)
        """
        self.config[hostname] = new_config
        with open(self.json_path, "w") as config_file:
            self.config = json.dumps(config_file.read())

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

# 'bgp_time_conversion',
# 'cli',
# 'close',
# 'commit_config',
# 'compare_config',
# 'compliance_report',
# 'connection_tests',
# 'dest_file_system',
# 'device',
# 'discard_config',
# 'get_arp_table',
# 'get_bgp_config',
# 'get_bgp_neighbors',
# 'get_bgp_neighbors_detail',
# 'get_config',
# 'get_environment',
# 'get_facts',
# 'get_firewall_policies',
# 'get_interfaces',
# 'get_interfaces_counters',
# 'get_interfaces_ip',
# 'get_ipv6_neighbors_table',
# 'get_lldp_neighbors',
# 'get_lldp_neighbors_detail',
# 'get_mac_address_table',
# 'get_network_instances',
# 'get_ntp_peers',
# 'get_ntp_servers',
# 'get_ntp_stats',
# 'get_optics',
# 'get_probes_config',
# 'get_probes_results',
# 'get_route_to',
# 'get_snmp_information',
# 'get_users',
# 'is_alive',
# 'load_merge_candidate',
# 'load_replace_candidate',
# 'load_template',
# 'open',
# 'parse_uptime',
# 'ping',
# 'post_connection_tests',
# 'pre_connection_tests',
# 'rollback',
# 'traceroute'


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