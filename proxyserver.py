import socket
from _thread import *
import sys
from misc import *


interface_type = enum('SERVER', 'CLIENT')


class ParserException(Exception):
    pass


class NoRoutingRuleFound(Exception):
    pass


class Parser(object):
    def __init__(self, data):
        pass

    def to_string(self):
        raise NotImplementedError


class ProxyServer:
    interfaces = dict()
    routing_rules = []
    message_rules = []
    _globals = dict()

    def __init__(self, parser):
        if not issubclass(parser, Parser):
            print("Parser should be inherited from proxyserver.Parser")
            sys.exit()

        self.running = True
        self.parser = parser
        self.buffer = ""

    def new_interface(self, name, _type, local_addr, remote_addr=None):
        try:
            if _type == interface_type.SERVER:
                self.new_server(name, local_addr)
            elif _type == interface_type.CLIENT:
                self.new_client(name, local_addr, remote_addr)
            else:
                raise Exception("Interface type is not recognised")
        except KeyboardInterrupt:
            self.running = False

    def new_server(self, name, local_addr):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(local_addr)
        except socket.error as msg:
            print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

        sock.listen(10)

        self.interfaces[name] = dict()
        while self.running:
            connection, remote_addr = sock.accept()
            print(name, "connected from:", remote_addr)
            self.interfaces[name][remote_addr[0] + ':' + str(remote_addr[1])] = connection
            start_new_thread(self.listening, (name, remote_addr))

    def new_client(self, name, local_addr, remote_addr):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(local_addr)
        except socket.error as msg:
            print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

        sock.connect(remote_addr)
        self.interfaces[name] = dict()
        self.interfaces[name][remote_addr[0] + ':' + str(remote_addr[1])] = sock
        start_new_thread(self.listening, (name, remote_addr))

    def listening(self, if_name, client):
        while True:
            try:
                data = self.interfaces[if_name][client[0] + ':' + str(client[1])].recv(1024)
            except KeyError:  # connection closed
                break
            else:
                self.process_data(if_name, client, data)

    def send(self, if_name, client, data):
        self.interfaces[if_name][client[0] + ':' + str(client[1])].sendall(data)

    def process_data(self, if_name, client, data):
        if not data:
            self.close_connection(if_name, client)
            return
        print(data)
        try:
            message = self.parser(self.buffer+data)
        except ParserException:
            self.buffer += data
        else:
            self.buffer = ""
            try:
                dest_if, dest_addr = self.get_routing(message, if_name, client)
            except NoRoutingRuleFound:
                print("packet dropped, no routing found")
                return
            for rule in self.message_rules:
                rule(message, if_name, client, dest_if, dest_addr)

            self.send(dest_if, dest_addr, message.to_string())

    def add_routing_rule(self, boolean_method):
        self.routing_rules.append(boolean_method)

    def get_routing(self, message, source_if, source_addr):
        dest_if = MutableString("")
        dest_addr = tuple()
        for rule in self.routing_rules:
            if rule(message, source_addr, source_if, self._globals):
                break
        else:
            raise NoRoutingRuleFound
        return dest_if, dest_addr

    def close_connection(self, if_name, client):
        self.interfaces[if_name][client[0] + ':' + str(client[1])].close()
        del self.interfaces[if_name][client[0] + ':' + str(client[1])]
        print(if_name, "connection closed with ", client)

    def __del__(self):
        for _if in self.interfaces:
            for client in self.interfaces[_if]:
                _if[client].close()
                print(_if, "connection closed with ", client)
