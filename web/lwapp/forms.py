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
    forward_choices = [
        ("interface", "Interface"),
        ("network", "Network")
    ]
    forward_to = forms.ChoiceField(
        choices=forward_choices, 
        widget=forms.RadioSelect, 
        label="Forward To:",
    )
