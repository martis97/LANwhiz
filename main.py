"""
LANwhiz Network Device Configuration Automation 

Main script
"""

from LANwhiz.connect import Connect
from LANwhiz.utils import Utilities
from LANwhiz.config.configure import ConfigActions
from threading import Thread


class LANwhizMain(object):

    @staticmethod
    def configure_cisco_device(hostname):
        """ Connects to and configures a Cisco device """

        print(f"Starting configuration: {hostname}")

        device_config = Utilities.read_config(hostname)

        # Get SSH/Telnet channel
        print(f"{hostname}: Connecting to Cisco Device..")
        connection = Connect().cisco_device(
            *list(device_config.values())[1:5]
        )
        print(f"{hostname}: Successfully connected")

        # Only configure what's been defined in JSON config file
        methods = [
            method for method in device_config["config"] 
                if not "global" in method
        ]

        config_device = ConfigActions(
            device_config=device_config["config"], 
            connection=connection
        )

        # Ensuring initial commands are executed first
        print(f"{hostname}: Configuring Global commands... ")
        config_device.default_commands()
        print("Done!")

        for config_area in methods:
            print(f"{hostname}: Configuring: "
                f"{config_area.replace('_', ' ').title()}..."
            )
            getattr(config_device, config_area)()
            print("Done!")

        print(f"{hostname}: Configuration Complete!")
        print(f"{hostname}: Closing session..")
        connection.cleanup()


if __name__ == "__main__":
    lw = LANwhizMain()
    
    # devices = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
    
    # devices = ["R1", "R2", "R3", "S1", "S2"]

    devices = ["R2"]
    
    for device in devices:
        thread = Thread(
            target=lw.configure_cisco_device, 
            kwargs={"hostname": device}
        )
        try:
            thread.start()
        except Exception as e:
            pass
