from django import forms
from LANwhiz.utils import Utilities  


class AccessForm(forms.Form):
    
    hostname = forms.CharField(label="Device Hostname:")
    mgmt_ip = forms.CharField(label="IP/Domain Name:")
    mgmt_port = forms.IntegerField(label="Management Port:")
    username = forms.CharField(label="Username:", required=False)
    password = forms.CharField(
        label="Password:", 
        widget=forms.PasswordInput(render_value=True)
    )


class InterfaceConfigForm(forms.Form):
    #  placeholder="IPv4/CIDR"
    ipv4 = forms.CharField(label="IPv4 Address:")
    ipv6 = forms.CharField(label="IPv6 Address:")
    description = forms.CharField(label="Description:")


class NATRadioForm(forms.Form):
    nat_choices = [
        ("inside", "Inside"),
        ("outside", "Outside"),
        ("off", "Off")
    ]
    nat = forms.ChoiceField(choices=nat_choices, widget=forms.RadioSelect, label="NAT")