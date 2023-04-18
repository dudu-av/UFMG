#################################################################
# pppsrt.py - protocolo ponto-a-ponto simples com retransmissão
#           - entrega interface semelhante a um socket
#################################################################
# fornece a classe PPPSRT, que tem os métodos:
#
# contrutor: pode receber um ou dois parâmetros, para criar um
#            canal que implementa o protocolo PPPSRT;
#            - o servidor cria o objeto apenas com o porto;
#            - o cliente cria o objeto com host e porto.
# close: encerra o enlace
# send(m): envia o array de bytes m pelo canal, calculando o 
#           checksum, fazendo o enquadramento e controlando a
#           retransmissão, se necessário.
# recv(): recebe um quadro e retorna-o como um array de bytes,
#         conferindo o enquadramento, conferindo o checksum e
#         enviando uma mensagem de confirmação, se for o caso.
# OBS: o tamanho da mensagem enviada/recebida pode variar, 
#      mas não deve ser maior que 1500 bytes.
################################################################
# PPPSRT utiliza o módulo dcc023_tp1 como API para envio e recepção
#        pelo enlace; o qual não deve ser alterado.
# PPPSRT não pode utilizar a interface de sockets diretamente.
################################################################

from asyncio.format_helpers import extract_stack
from asyncore import read
from secrets import token_bytes
from typing import final
import dcc023_tp1

class PPPSRT:
  
    msg_dic = {}
    flag = b'\x7e'
    addr = b'\xff' 
    ctrl_data = b'\x03'
    ctrl_ack = b'\x07'
    subs_esc = b'\x5d'
    subs_flag = b'\x5e'
    esc = b'\x7d'
    max_payload_in_bytes = 10
    max_tries = 10

    def __init__(self, port, host='' ):
        self.link = dcc023_tp1.Link(port,host)

    def close(self):
        self.link.close()
        
####################################################################
# A princípio, só é preciso alterar as duas funções a seguir.
    def byte_stuffing(self, msg_in_bytes):
        msg_byte_stuffed = b''

        for i in msg_in_bytes:

            if (i == self.flag[0]):
                msg_byte_stuffed = msg_byte_stuffed + self.esc + self.subs_flag
                continue

            if (i == self.esc[0]):
                msg_byte_stuffed = msg_byte_stuffed + self.esc + self.subs_esc
                continue
            
            msg_byte_stuffed = msg_byte_stuffed + chr(i).encode('latin-1')

        return msg_byte_stuffed


    def byte_destuffing(self, frame):
        is_escape = False
        new_frame = b''

        for byte_int in frame:
            byte = chr(byte_int).encode('latin-1') 
            if (is_escape):
                byte_to_add = self.esc if (byte == self.subs_esc) else self.flag
                new_frame = new_frame + byte_to_add
                is_escape = False
                continue
            if (byte == self.esc):
                is_escape = True
                continue
            new_frame = new_frame + byte

        return new_frame


    def sum_msg(self, msg):
        csm = 0
        elem = 0
        aux = 'vazio'

        for i in range(len(msg)):
            if (i % 2 == 0):
                aux = f'{msg[i]:08b}'
            else:
                if (i == 1):
                    csm = int(f'{msg[i]:08b}' + aux, 2)
                else:
                    elem = int(f'{msg[i]:08b}' + aux, 2)
                    csm = elem + csm
                    if (len(f'{csm:16b}') == 17):
                        csm = csm + 1
                        csm = int(f'{csm:16b}'[1:], 2)
                aux = ''
                
        if (aux != ''):
            elem = int(f'{0:08b}' + aux, 2)
            csm = elem + csm
            if (len(f'{csm:16b}') == 17):
                csm = csm + 1
                csm = int(f'{csm:16b}'[1:], 2)

        return csm

  
    def checksum(self, msg_in_bytes):
        
        csm = self.sum_msg(msg_in_bytes)

        complement_csm = csm ^ 65535

        mode = 'little' if (len(msg_in_bytes) % 2 == 0) else 'big'

        return complement_csm.to_bytes(2, mode)

            
    def check_checksum(self, frame):

        frame_without_flags = frame[1:-1]

        csm = self.sum_msg(frame_without_flags)

        return csm == 65535


    def send_ack(self, num):
        frame = frame = self.addr \
            + self.ctrl_ack \
            + (num).to_bytes(2, 'big') \

        frame = self.flag \
            + frame \
            + self.checksum(frame) \
            + self.flag

        frame = self.byte_stuffing(frame)

        print(f'├ sending stuffed ack: {frame}')
        self.link.send(frame)


    def extract_msg(self, destuffed_frame):
        msg = b''

        for byte_int in destuffed_frame[5:-3]:
            byte = byte_int.to_bytes(1, 'big')
            msg = msg + byte

        return msg


    def send(self, message):
        # Aqui, PPSRT deve fazer:
        #   - OK fazer o encapsulamento de cada mensagem em um quadro PPP,
        #   - OK calcular o Checksum do quadro e incluído,
        #   - OK fazer o byte stuffing durante o envio da mensagem,
        #   - OK aguardar pela mensagem de confirmação,
        #   - OK retransmitir a mensagem se a confirmação não chegar.
        pieces_of_msg_in_bytes = []
        frames = []

        msg_in_bytes = message.encode('latin-1') if type(message) != type(b'') else message

        while (len(msg_in_bytes) > self.max_payload_in_bytes):

            pieces_of_msg_in_bytes.append(msg_in_bytes[:self.max_payload_in_bytes])
            msg_in_bytes = msg_in_bytes[self.max_payload_in_bytes:]

        pieces_of_msg_in_bytes.append(msg_in_bytes)

        for i in range(len(pieces_of_msg_in_bytes)):

            # para reverter a função (<int>).to_bytes(<num de bytes>, <byte order>)
            # é usada a função int.from_bytes(<int>, <byte order>)
            protocol = (i).to_bytes(2, 'big')

            frame = self.addr \
                + self.ctrl_data \
                + protocol \
                + pieces_of_msg_in_bytes[i]

            frame = self.flag \
                + frame \
                + self.checksum(frame) \
                + self.flag

            frame = self.byte_stuffing(frame)
            frames.append(frame)
        
        for frame in frames:
            acknowledged = False
            stuffed_ack = 0
            self.link.send(frame)
            frame_protocol = int.from_bytes(frame[4:6], 'big')
            print(f'┌ sending {frame}, index: {frame_protocol}')
            counter = 0
            while (not acknowledged):
                try:
                    stuffed_ack = self.link.recv(12)
                    ack = self.byte_destuffing(stuffed_ack)
                    ack_protocol = int.from_bytes(ack[3:5], "big")
                    acknowledged = (ack_protocol == frame_protocol) and (self.check_checksum(ack))
                    counter = counter + 1
                    if (counter > self.max_tries):
                        print(f'\n {frame} was NOT acknowledged!!!\n')
                        break
                    print(f'├ receving ack: {ack} ---index---> {int.from_bytes(ack[3:5], "big")}')
                    print(f'├ accepted: {self.check_checksum(ack)}')
                except TimeoutError:
                    self.link.send(frame)
            else:
                print(f'└ frame {frame} was acknowledged!!!\n')

    def recv(self):
        # Aqui, PPSRT deve fazer:
        #   - OK identificar começo de um quadro,
        #   - OK receber a mensagem byte-a-byte, para retirar o stuffing,
        #   - OK detectar o fim do quadro,
        #   - OK calcular o checksum do quadro recebido,
        #   - OK descartar silenciosamente quadros com erro,
        #   - OK enviar uma confirmação para quadros recebidos corretamente,
        #   - conferir a ordem dos quadros e descartar quadros repetidos.
        try:
            stuffed_pck = self.link.recv(1500)
            pck = self.byte_destuffing(stuffed_pck)

            print(f'┌ received package: {pck}')
            if (pck == b''):
                final_msg = ''
                for i in self.msg_dic.keys():
                    final_msg = final_msg + str(self.msg_dic[i], 'latin-1')
                print(f"└ last package was b'' so the final message so far is:\n{final_msg}")
                return b''

            frame = pck
            accept = self.check_checksum(frame)
            index = int.from_bytes(frame[3:5], "big")
            print(f'├ accept: {accept}')

            if (accept):
                self.send_ack(index)

            msg = self.extract_msg(frame)
            self.msg_dic[index] = msg

            final_msg = msg

        except TimeoutError:
            print("Timeout")

        print(f'└ final msg (return do recv): {final_msg}\n')
        return final_msg
