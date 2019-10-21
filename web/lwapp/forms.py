from django import forms
from LANwhiz.utils import Utilities  


class RemoteAccessForm(forms.Form):
    def __init__(self, hostname):
        self.config = Utilities.read_config(hostname)
        
    hostname = forms.CharField(initial=self.config["hostname"])
    mgmt_ip = forms.GenericIPAddressField(initial=self.config["mgmt_ip"])
    mgmt_port = forms.CharField(initial=self.config["port"])