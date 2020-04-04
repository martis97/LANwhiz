from LANwhiz.exceptions import InvalidInputException
from LANwhiz.config.base import BaseConfig
import re


class AccessControlLists(BaseConfig):
    def __init__(self, connection, config):
        super().__init__(connection, config)

    def standard(self):
        """ Configures standard Access Control Lists on the device """
        for identifier, config_data in self.config["standard"].items():
            std_source = self._format_acl_target(config_data["source"])
            # Numbered ACL            
            if identifier.isnumeric():
                assert 0 < int(identifier) <= 100, \
                    f"Standard ACL '{identifier}' out of range"
                self.utils.send_command(
                    f"access-list {identifier} "
                    f"{config_data['action']} {std_source}"
                )
            # Named ACL
            else: 
                acl_cmds = [
                    f"ip access-list standard {identifier}",
                    f"{config_data['action']} {std_source}"
                ]
                for cmd in acl_cmds:
                    self.utils.send_command(cmd)

    def extended(self):
        """ Configures extended Access Control Lists on the device """
        for identifier, config_data in self.config["extended"].items():
            source = self._format_acl_target(config_data["source"])
            dest = self._format_acl_target(config_data["destination"])
            # Named ACL
            if re.match(r"[A-Za-z0-9\_\-]+", identifier):
                named_acl_cmds = [
                    f"ip access-list extended {identifier}",
                    f"{config_data['action']} {config_data['protocol']} "
                    f"{source} {dest} {config_data['port']}"
                ]
                self.connection.send_config_set(named_acl_cmds)
            # Numbered ACL
            elif identifier.isnumeric():
                assert 100 < int(identifier) <= 200, \
                    f"Extended ACL '{identifier}' out of range"
                self.utils.send_command(
                    f"access-list {identifier} "
                    f"{config_data['action']} {config_data['protocol']} "
                    f"{source} {dest} {config_data['port']}"
                )
            else:
                raise InvalidInputException(
                    f"'{identifier}' is not a valid ACL name/number. "
                    "Named ACLs are only allowed to contain letters, dash"
                    " or an underscore.\n"
                )
    
    def _format_acl_target(self, target):
        """ Forms a command subset where the source or destination 
        needs to be defined. 
        
        Example:
            If target passed in is '192.168.1.0/24', then it will 
            return '192.168.1.0 0.0.0.255'
            
            or,
            
            If target passed in is 192.168.1.15, it will assume
            the ACL is for a single host and will return
            "host 192.168.1.15"
        
            If 'any' is passed, it's returned as it is.
        """
        contains_cidr = re.compile(
            r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b\/\d{1,2}"
        )
        just_ip = re.compile(
            r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
        )

        if target == "any":
            return target
        # if it contains CIDR, create command with wildcard mask
        elif contains_cidr.match(target):
            ip, cidr = target.split("/")
            wildcard = self.utils.prefix_to_wildcard_mask(int(cidr))
            acl_target = f"{ip} {wildcard}"
        # if only IP is provided, it's one host
        elif just_ip.match(target):
            acl_target = f"host {target}"
        else:
            raise InvalidInputException(
                f"Target IP/Subnet '{target}' not recognised."
                " Should be xxx.xxx.xxx.xxx/xx for subnet"
                ", xxx.xxx.xxx.xxx for a single host"
                " and 'any' for any src/dest."
            )
        
        return acl_target
