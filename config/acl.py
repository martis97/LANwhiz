from net_auto_config.utils import Utilities
import re


class AccessControlLists(object):
    def __init__(self, connection, acl_config):
        self.connection = connection
        self.utils = Utilities()
        self.standard_acls = acl_config["standard"]
        self.extended_acls = acl_config["extended"]
        self.utils.ensure_global_config_mode(self.connection)

    def standard(self):
        """ Configures standard Access Control Lists on the device """
        for identifier, config_data in self.standard_acls.items():
            std_source = self.format_acl_cmd_target(config_data["source"])
            # Named ACL
            if identifier.isalpha():
                named_acl_cmds = [
                    f"ip access-list standard {identifier}",
                    f"{config_data['action']} {std_source}"
                ]
                for cmd in named_acl_cmds:
                    self.connection.send_command(cmd, expect_string="")
            # Numbered ACL
            elif identifier.isnumeric():
                self.connection.send_command(
                    f"access-list {identifier} " 
                    f"{config_data['action']} {std_source}"
                )
    
    def extended(self):
        """ Configures extended Access Control Lists on the device """
        for identifier, config_data in self.extended_acls.items():
            ext_source = self.format_acl_cmd_target(config_data["source"])
            ext_dest = self.format_acl_cmd_target(config_data["destination"])
            # Named ACL
            if identifier.isalpha():
                named_acl_cmds = [
                    f"ip access-list standard {identifier}",
                    f"{config_data['action']} {config_data['protocol']} "
                    f"{ext_source} {ext_dest} {config_data['port']}"
                ]
                for cmd in named_acl_cmds:
                    self.connection.send_command(cmd, expect_string="")
            # Numbered ACL
            elif identifier.isnumeric():
                self.connection.send_command(
                    f"access-list {identifier} " 
                    f"{config_data['action']} {config_data['protocol']} "
                    f"{ext_source} {ext_dest} {config_data['port']}"
                )
    
    def format_acl_cmd_target(self, target):
        """ Forms a command subset where the source or destination 
        needs to be defined. 
        
        Example:
            If target passed in is 192.168.1.0/24, then it will 
            return '192.168.1.0 0.0.0.255'
            
            or,
            
            If target passed in is 192.168.1.15, it will assume
            the ACL is for a single host and will return
            "host 192.168.1.15"
        """
        contains_cidr = re.compile(
            r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b\/\d{1,2}"
        )
        # if it contains CIDR, create command with wildcard mask
        if re.match(contains_cidr, target):
            ip = target.split("/")[0]
            cidr = target.split("/")[1]
            wildcard = self.utils.cidr_to_wildcard_mask(int(cidr))
            acl_target = f"{ip} {wildcard}"
        # if not, assume it's one host
        else:
            acl_target = f"host {target}"
        
        return acl_target
