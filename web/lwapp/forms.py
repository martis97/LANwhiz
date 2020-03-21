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
    ipv4 = forms.CharField(label="IPv4 Address:")
    ipv6 = forms.CharField(label="IPv6 Address:", required=False)
    description = forms.CharField(label="Description:", required=False)
    nat_choices = [
        ("inside", "Inside"),
        ("outside", "Outside"),
        ("off", "Off")
    ]
    nat = forms.ChoiceField(
        choices=nat_choices, 
        widget=forms.RadioSelect, 
        label="NAT",
    )

    # Some hiddens to be displayed as cards
    inbound_acl = forms.CharField(widget=forms.HiddenInput)
    outbound_acl = forms.CharField(widget=forms.HiddenInput)
    other_commands = forms.CharField(widget=forms.HiddenInput)


class GlobalCmdsForm(forms.Form):

    global_commands = forms.CharField(
        widget=forms.HiddenInput(attrs={"id": "globalCmds"}),
    )


class LineConfigForm(forms.Form):
    synchronous_logging = forms.BooleanField(required=False)
    inbound_acl = forms.CharField(widget=forms.HiddenInput)
    outbound_acl = forms.CharField(widget=forms.HiddenInput)


class OSPFConfigForm(forms.Form):
    instance_id = forms.IntegerField(label="Instance ID:", required=False)
    router_id = forms.CharField(label="Router ID:", required=False)
    advertise_static = forms.BooleanField()
    advertise_networks = forms.CharField(widget=forms.HiddenInput)
    passive_interfaces = forms.CharField(widget=forms.HiddenInput)
    other_commands = forms.CharField(widget=forms.HiddenInput)

class NewStaticRouteForm(forms.Form):
    network = forms.CharField(label="Destination Network:", required=False)
    subnet_mask = forms.CharField(label="Subnet Mask:", required=False)


class StandardACLForm(forms.Form):
    action_choices = [
        ("permit", "Permit"),
        ("deny", "Deny")
    ]
    action = forms.MultipleChoiceField(
        required=False,
        widget=forms.Select,
        choices=action_choices
    )
    source = forms.CharField(
        label="Source:", 
        widget=forms.TextInput(attrs={'placeholder': 'Network/Host Address[/Prefix]'}),
        required=False
    )


class ExtendedACLForm(forms.Form):
    action_choices = [
        ("permit", "Permit"),
        ("deny", "Deny")
    ]
    action = forms.MultipleChoiceField(
        required=False,
        widget=forms.Select,
        choices=action_choices
    )

    protocol_choices = [
        ("tcp", "TCP"),
        ("udp", "UDP"),
        ("ip", "IP"),
    ]
    protocol = forms.MultipleChoiceField(
        required=False,
        widget=forms.Select,
        choices=protocol_choices
    )
    source = forms.CharField(
        label="Source:", 
        widget=forms.TextInput(attrs={"placeholder": "Network/Host Address[/Prefix]"}),
        required=False
    )
    destination = forms.CharField(
        label="Destination:", 
        widget=forms.TextInput(attrs={"placeholder": "Network/Host Address[/Prefix]"}),
        required=False
    )
    port = forms.CharField(
        label="Port:", 
        widget=forms.TextInput(attrs={"placeholder": "[eq <port>] [established]"}),
        required=False
    )


class DHCPPoolForm(forms.Form):
    pool_name = forms.CharField(
        label="Pool Name:", 
        widget=forms.TextInput(attrs={"placeholder": "Name"}),
        required=False
    )
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



def get_interface_config_initial(interface, config):
    other_cmds = ",".join(config["other_commands"]) \
        if config.get("other_commands") else ""

    initial = {
        "ipv4": config.get("ipv4"),
        "ipv6": config.get("ipv6"),
        "description": config.get("description"),
        "nat": config["nat"] if config.get("nat") else "off",
        "other_commands": other_cmds
    }

    if config.get("acl"):
        initial.update({
            "inbound_acl": ",".join(config["acl"].get("inbound")),
            "outbound_acl": ",".join(config["acl"].get("outbound")),
        })

    return InterfaceConfigForm(initial=initial, prefix=interface)


def get_line_config_initial(line, config):
    line_config_initial = {
        "password": config["password"],
        "synchronous_logging": config["synchronous_logging"]
    }

    if config.get("acl"):
        line_config_initial.update({
            "inbound_acl": ",".join(config["acl"].get("inbound")),
            "outbound_acl": ",".join(config["acl"].get("outbound")),
        })

    return LineConfigForm(initial=line_config_initial, prefix=line)