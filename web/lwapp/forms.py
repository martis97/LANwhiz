from django import forms
from LANwhiz.utils import Utilities  


class AccessForm(forms.Form):
    
    hostname = forms.CharField(label="Device Hostname:")
    mgmt_ip = forms.GenericIPAddressField(label="Management IP:")
    mgmt_port = forms.IntegerField(label="Management Port:")
    username = forms.CharField(label="Username:", required=False)
    password = forms.PasswordInput()


class InterfaceConfigForm(forms.Form):
    ipv4 = forms.GenericIPAddressField(label="IPv4 Address:", help_text="Format: IPv4/CIDR")
    ipv6 = forms.GenericIPAddressField(label="IPv6 Address:")
    description = forms.CharField(label="Description:")

    nat_choices = [
        ("inside", "Inside"),
        ("outside", "Outside"),
        ("off", "Off")
    ]
    nat = forms.ChoiceField(choices=nat_choices, widget=forms.RadioSelect)