from net_auto_config.configure import Configure

class Routing(Configure):
    def __init__(self):
        super().__init__()
    

class Static(Routing):
    def __init__(self, static_data):
        super().__init__()
        self.static_data = static_data


class OSPF(Routing):
    def __init__(self, ospf_data):
        super().__init__()
        self.ospf_data = ospf_data

    
