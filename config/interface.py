from net_auto_config.configure import Configure

class Interface(Configure):
    def __init__(self):
        super().__init__()

    def ipv4(self, ip):
        """ Sends command to configure IPv4 address """
        ipv4 = ip.split("/")[0]
        subnet_mask = self.utils.cidr_to_subnet_mask(ip.split("/")[1])
        ipv4_command = f"ip address {ipv4} {subnet_mask}"
        self.connection.send_command(ipv4_command, expect_string="")

    def ipv6(self, ip):
        """ Sends commmand to configure IPv6 address """
        ipv6_command = f"ipv6 address {ip}"
        self.connection.send_command(ipv6_command, expect_string="")
    
    def description(self, description):
        """ Sends command to configure interface description """
        self.connection.send_command(
            f"description {description}",
            expect_string=""
        )

    def acl(self, interface, *, inbound, outbound):
        """ Sends commands to configure ACLs on interfaces """
        acl_commands = []
        for rule in outbound:
            acl_commands.append(f"ip access-group {rule} out")
        for rule in inbound:
            acl_commands.append(f"ip access-group {rule} in")
        for command in acl_commands:
            if "vty" in interface:
                for replacement in (("ip ", ""), ("group", "class")):
                    command = command.replace(*replacement)
            self.connection.send_command(command, expect_string="")

    def nat(self, direction):
        """ Sends command to configure NAT on the interface """
        nat_command = f"ip nat {direction}"
        self.connection.send_command(nat_command, expect_string="")