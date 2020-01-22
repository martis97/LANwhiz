from django import forms
from LANwhiz.utils import Utilities  


class AccessForm(forms.Form):
    
    hostname = forms.CharField(label="Username:")
    mgmt_ip = forms.GenericIPAddressField(label="Management IP:")
    mgmt_port = forms.IntegerField(label="Management Port:")
    username = forms.CharField(label="Username:", required=False)
    password = forms.PasswordInput()
