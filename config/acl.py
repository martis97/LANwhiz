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
        contains_cidr = re.compile(
            r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b\/\d{1,2}"
        )

        for identifier, config_data in self.standard_acls.items():
            self.utils.ensure_global_config_mode(self.connection)
            # if it contains CIDR, create command with wildcard mask
            if re.match(contains_cidr, config_data["source"]):
                ip = config_data["source"].split("/")[0]
                cidr = config_data["source"].split("/")[1]
                wildcard = self.utils.cidr_to_wildcard_mask(int(cidr))
                std_acl = f"{ip} {wildcard}"
            # if not, assume it's one host
            else:
                std_acl = f"host {config_data['source']}"
            if identifier.isalpha():
                named_acl_cmds = [
                    f"ip access-list standard {identifier}",
                    f"{config_data['action']} {std_acl}"
                ]
                for cmd in named_acl_cmds:
                    self.connection.send_command(cmd, expect_string="")
                return
            elif identifier.isnumeric():
                self.connection.send.command(
                    f"access-list {identifier} {config_data['action']}"
                )
                return