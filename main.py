import proxyserver


class DummyPacket(proxyserver.Parser):
    def __init__(self, data):
        self.data = data
        super(self.__class__, self).__init__(data)

    def to_string(self):
        return self.data


if __name__ == "__main__":
    Proxy = proxyserver.ProxyServer(DummyPacket)
    Proxy.new_interface("Mw_UNI",
                        proxyserver.interface_type.SERVER,
                        ("192.168.1.119", 11112))
