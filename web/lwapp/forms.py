from django import forms
from LANwhiz.utils import Utilities


class AddDeviceForm(forms.Form):

    mgmt_ip = forms.CharField(label="IP/Domain Name:")
    mgmt_port = forms.IntegerField(label="Management Port:")
    username = forms.CharField(label="Username:", required=False)
    password = forms.CharField(
        label="Password:", 
        widget=forms.PasswordInput(render_value=True),
        required=False
    )
    new_hostname = forms.CharField(
        label="New Hostname:",
        widget=forms.TextInput(attrs={"placeholder": "Leave Blank To Use Existing"}),
        required=False
    )


class AccessForm(forms.Form):
    
    hostname = forms.CharField(label="Device Hostname:")
    mgmt_ip = forms.CharField(label="IP/Domain Name:")
    mgmt_port = forms.IntegerField(label="Management Port:")
    username = forms.CharField(label="Username:", required=False)
    password = forms.CharField(
        label="Password:", 
        widget=forms.PasswordInput(render_value=True),
        required=False
    )


class InterfaceConfigForm(forms.Form):

    # Interface Dropdown
    shutdown = forms.BooleanField(required=False)
    ipv4 = forms.CharField(label="IPv4 Address:", required=False)
    ipv6 = forms.CharField(label="IPv6 Address:", required=False)
    description = forms.CharField(label="Description:", required=False)
    bandwidth = forms.IntegerField(label="Bandwidth:", required=False)
    nat_choices = [
        ("inside", "Inside"),
        ("outside", "Outside"),
        ("off", "Off")
    ]
    nat = forms.ChoiceField(
        choices=nat_choices, 
        widget=forms.RadioSelect, 
        label="NAT",
        required=False
    )

    # Some hiddens to be displayed as cards
    inbound_acl = forms.CharField(widget=forms.HiddenInput, required=False)
    outbound_acl = forms.CharField(widget=forms.HiddenInput, required=False)
    other_commands = forms.CharField(widget=forms.HiddenInput, required=False)


class GlobalCmdsForm(forms.Form):

    global_commands = forms.CharField(
        widget=forms.HiddenInput(attrs={"id": "globalCmds"}),
        required=False
    )


class LineConfigForm(forms.Form):
    password = forms.CharField(
        label="Password:", 
        widget=forms.PasswordInput(render_value=True),
        required=False
    )
    synchronous_logging = forms.BooleanField(required=False)
    inbound_acl = forms.CharField(widget=forms.HiddenInput, required=False)
    outbound_acl = forms.CharField(widget=forms.HiddenInput, required=False)
    other_commands = forms.CharField(widget=forms.HiddenInput, required=False)


class OSPFConfigForm(forms.Form):
    instance_id = forms.IntegerField(label="Instance ID:", required=False)
    router_id = forms.CharField(label="Router ID:", required=False)
    advertise_static = forms.BooleanField(required=False)
    advertise_networks = forms.CharField(widget=forms.HiddenInput, required=False)
    passive_interfaces = forms.CharField(widget=forms.HiddenInput, required=False)
    other_commands = forms.CharField(widget=forms.HiddenInput, required=False)

class NewStaticRouteForm(forms.Form):
    network = forms.CharField(label="Destination Network:", required=False)
    subnet_mask = forms.CharField(label="Subnet Mask:", required=False)


class StandardACLForm(forms.Form):
    action_choices = [
        ("permit", "Permit"),
        ("deny", "Deny")
    ]
    action = forms.ChoiceField(
        choices=action_choices, 
        widget=forms.RadioSelect, 
        label="Action",
    )
    source = forms.CharField(
        label="Source:", 
        widget=forms.TextInput(attrs={'placeholder': 'Network/Host Address[/Prefix]'}),
    )


class ExtendedACLForm(forms.Form):
    action_choices = [
        ("permit", "Permit"),
        ("deny", "Deny")
    ]
    action = forms.ChoiceField(
        choices=action_choices, 
        widget=forms.RadioSelect, 
        label="Action",
    )

    protocol_choices = [
        ("tcp", "TCP"),
        ("udp", "UDP"),
        ("ip", "IP"),
    ]
    protocol = forms.ChoiceField(
        choices=protocol_choices,
        widget=forms.RadioSelect,
        label="Protocol"
    )
    source = forms.CharField(
        label="Source:", 
        widget=forms.TextInput(attrs={"placeholder": "Network/Host Address[/Prefix]"}),
    )
    destination = forms.CharField(
        label="Destination:", 
        widget=forms.TextInput(attrs={"placeholder": "Network/Host Address[/Prefix]"}),
    )
    port = forms.CharField(
        label="Port:", 
        widget=forms.TextInput(attrs={"placeholder": "[eq <port>] [established]"}),
        required=False
    )


class DHCPPoolForm(forms.Form):

    network = forms.CharField(
        label="Network:", 
        widget=forms.TextInput(attrs={"placeholder": "Network Address/Prefix"}),
        required=False
    )
    default_gateway = forms.CharField(
        label="Default Gateway:", 
        widget=forms.TextInput(attrs={"placeholder": "Default Gateway"}),
        required=False
    )
    dns = forms.CharField(
        label="DNS Address:", 
        widget=forms.TextInput(attrs={"placeholder": "DNS"}),
        required=False
    )


class FormInitials():

    @staticmethod
    def interface_config(config):
        other_cmds = ",".join(config["other_commands"]) \
            if config.get("other_commands") else ""

        initial = {
            "shutdown": config.get("shutdown"),
            "ipv4": config.get("ipv4"),
            "ipv6": config.get("ipv6"),
            "description": config.get("description"),
            "nat": config["nat"] if config.get("nat") else "off",
            "bandwidth": config.get("bandwidth"),
            "other_commands": other_cmds
        }

        if config.get("acl"):
            initial.update({
                "inbound_acl": ",".join(config["acl"].get("inbound")),
                "outbound_acl": ",".join(config["acl"].get("outbound")),
            })
        
        return initial

    @staticmethod
    def line_config(config):
        line_config_initial = {
            "password": config["password"],
            "synchronous_logging": config["synchronous_logging"],
            "other_commands": ",".join(config.get("other_commands"))  \
                            if config.get("other_commands") else ""
        }

        if config.get("acl"):
            line_config_initial.update({
                "inbound_acl": ",".join(config["acl"].get("inbound")),
                "outbound_acl": ",".join(config["acl"].get("outbound"))
            })

        return line_config_initial



class FormDiff():
    def __init__(self, post_data):
        self.post_data = post_data

    def interface_config(self, current):
        """ Retrieve all changes for Interfaces' configuration part """
        changes = {}
        for interface, config in current.items():
            initial = FormInitials.interface_config(config)
            form = InterfaceConfigForm(
                self.post_data, 
                prefix=interface, 
                initial=initial
            )
            if form.is_valid():
                for item in form.changed_data:
                    acl_changes = {}
                    new_value = form.cleaned_data.get(item)
                    if "acl" in item:
                        acl_type = item.split("_")[0]
                        new_acls = new_value.split(",") if new_value else []
                        if acl_changes.get(acl_type):
                            acl_changes[acl_type].update({acl_type: new_acls})
                        else:
                            acl_changes[acl_type] = new_acls
                    elif "other_commands" == item:
                        new_value = new_value.split(",") if new_value else []
                    
                    if acl_changes:
                        item = "acl"
                        new_value = acl_changes
                        if changes.get(interface):
                            if changes[interface].get("acl"):
                                changes[interface]["acl"].update(acl_changes)
                        else: 
                            changes.update(
                                {interface: {item: acl_changes}}
                            )
                        continue
                    
                    if changes.get(interface):
                        changes[interface].update(
                            {item: new_value}
                        )
                    else: 
                        changes.update(
                            {interface: {item: new_value}}
                        )

        return changes

    def line_config(self, current):
        """ Retrieve all changes for Lines' configuration part """

        changes = {}
        for line, config in current.items():
            initial = FormInitials.line_config(config)
            form = LineConfigForm(
                self.post_data, 
                prefix=line, 
                initial=initial
            )
            if form.is_valid():
                for item in form.changed_data:
                    acl_changes = {}
                    new_value = form.cleaned_data.get(item)
                    if "acl" in item:
                        acl_type = item.split("_")[0]
                        new_acls = new_value.split(",") if new_value else []
                        if acl_changes.get(acl_type):
                            acl_changes[acl_type].update({acl_type: new_acls})
                        else:
                            acl_changes[acl_type] = new_acls
                    elif "other_commands" == item:
                        new_value = new_value.split(",") if new_value else []
                    
                    if acl_changes:
                        item = "acl"
                        new_value = acl_changes
                        if changes.get(line):
                            if changes[line].get("acl"):
                                changes[line]["acl"].update(acl_changes)
                        else: 
                            changes.update(
                                {line: {item: acl_changes}}
                            )
                        continue
                    
                    if changes.get(line):
                        changes[line].update({
                            item: new_value
                        })
                    else: 
                        changes.update({
                            line: {item: new_value}
                        })

        return changes
    
    def routing(self, current):
        """ Retrieve all changes for routing configuration part """
        # Return if no OSPF config exists 
        if not current:
            return {}
        
        # All chagnes to be stored here 
        changes = {}
        
        # Slightly innefficient, but gets all static routes from form data
        if self.post_data.get("static_routes"):
            form_static_routes = self.post_data.get("static_routes").split(",")
            form_static_routes = [route.split("-") for route in form_static_routes]
            form_static_routes = [{
                "network": net,
                "subnetmask": sm,
                "forward_to": forward_to
            } for net, sm, forward_to in form_static_routes]
        else:
            form_static_routes = []

        list_items = (
            "advertise_networks", 
            "passive_interfaces", 
            "other_commands"
        )

        if current["static"] != form_static_routes:
            changes["static"] = form_static_routes
        
        # Get all OSPF Changes
        if current.get("ospf"):
            current_ospf = current["ospf"]
            
            for item in list_items:
                if current_ospf.get(item):
                    current_ospf[item] = ",".join(current_ospf[item])
                else:
                    current_ospf[item] = []
            
            form = OSPFConfigForm(self.post_data, initial=current_ospf)

            if form.is_valid():
                ospf_changes = {}

                for item in form.changed_data:
                    new_value = form.cleaned_data.get(item)
                  
                    if item in list_items:
                        new_value = new_value.split(",") if new_value else []

                    if new_value:
                        ospf_changes.update({item: new_value})

                if ospf_changes:
                    changes["ospf"] = ospf_changes 

        return changes
    
    def acl(self, current):
        """ Retrieve all changes for ACL configuration part """
        if not current:
            return {}
        changes = {}
        acls = [["standard", StandardACLForm], ["extended", ExtendedACLForm]]

        for acl_type, acl_form in acls:

            for acl_id, config in current[acl_type].items():
                form = acl_form(
                    self.post_data,
                    prefix=acl_id,
                    initial=config
                )
                if form.is_valid():
                    if form.changed_data:
                        print(form.changed_data)
                        if changes.get(acl_type):
                            changes[acl_type].update({acl_id: {}})
                        else:
                            changes[acl_type] = {acl_id: {}}

                        for item in form.changed_data:
                            new_value = form.cleaned_data.get(item)
                            changes[acl_type][acl_id].update({item: new_value})
                else:
                    print(form.errors)
                        
        return changes

    def dhcp(self, current):
        """ Retrieve all changes for DHCP configuration part """
        # Return if no DHCP config exists
        if not current:
            return {}

        # All DHCP changes to be stored here
        changes = {}

        # Checking for form changes
        for pool_name, config in current.items():
            form = DHCPPoolForm(
                self.post_data,
                prefix=pool_name,
                initial=config
            )

            if form.is_valid():
                # Get all changes
                for item in form.changed_data:
                    new_value = form.cleaned_data.get(item)
                    
                    # Create key or use existing
                    if changes.get(pool_name):
                        changes[pool_name].update({item: new_value})
                    else:
                        changes[pool_name] = {item: new_value}

        return changes