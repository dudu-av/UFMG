#################################################################
# dcc023_tp1.py - encapsulamento do socket para facilitar testes
#               - PPPSRT deve usar esta interface, não socket
#               - este arquivo não deve ser alterado
#################################################################
# Durante os testes da avaliação, uma versão alterada deste 
# arquivo será usada pelo professor, mas a interface não mudará.
#################################################################

import socket

class Link:
  
    def __init__(self, port = 0, host = '' ):
        if host == '':
            orig = (host, int(port))
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listen_socket.bind(orig)
            listen_socket.listen(1)
            print(f'Listening on port {port}...')
            self.tcp_socket, client = listen_socket.accept()
            print(f'Connected to host {client[0]}.\n')
        else:
            dest = (host,int(port))
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.settimeout(5) # usando 5 segundos
            self.tcp_socket.connect(dest)
            print(f'Conneceted on port {port}.\n')
  
    def send(self,message):
        self.tcp_socket.send(message)

    def recv(self,nbytes):
        try: # essa estrutura repassa temporizações para PPPSRT
            some_bytes = self.tcp_socket.recv(nbytes)
        except socket.timeout:
            raise TimeoutError
        return some_bytes

    def close(self):
        self.tcp_socket.close()

