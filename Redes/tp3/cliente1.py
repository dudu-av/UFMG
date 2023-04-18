import socket
import sys
import select
import queue
from comum import Protocol, extract_info

debug = True

def msg_valida(msg: str) -> int:

    msg_array = msg.replace('\n', '').split(' ', maxsplit=2)

    if (msg_array[0] != 'M' and msg_array[0] != 'S'):
        return 1

    if (msg_array[0] == 'M'):
        try:
            int(msg_array[1])
        except:
            return 2
    
    return 0

def cria_msg() -> str:
    while(True):

        msg = input()

        match msg_valida(msg):
            case 0:
                break
            case 1:
                print('Mensagem inválida: comece com M ou S e um espaço em seguida.')
            case 2:
                print('Destinatário inválido: digite um número seguido de espaço.')

    return msg

def muda_receptor(msg: str, prot: Protocol) -> None:

  msg_array = msg.split(' ')

  if (msg_array[0] == 'M'):
    prot.change_receiver(int(msg_array[1]))

if len(sys.argv) != 4:
  print('Argumentos: <', sys.argv[0],'> <id> <ip/nome> <porto>')
  exit()

my_id = int(sys.argv[1])

if (my_id > 65534 or my_id < 1):
  print(f'Identificador errado. Escolha um número entre 1 e 65534.')
else:
  host = sys.argv[2]
  port = int(sys.argv[3])
  frame = Protocol(my_id)

  socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client_address = (host, port)
  socket_to_server.connect(client_address)
  
  if (debug): print('enviando mensagem de "oi"')
  
  socket_to_server.send(frame.make_frame('oi'))
  
  if (debug): print('mensagem de "oi" enviada')
  
  oi_answer = socket_to_server.recv(8)

  msg_type, sender_id, receiver_id, seq_num = extract_info(oi_answer)

  if (msg_type == 1 and receiver_id == my_id and seq_num == 0):
    print('Conexão estabelecida! Para sair envie uma mensagem apenas com "S"')

    msg = cria_msg()
        
    while ( msg[0] == 'M' ):
      socket_to_server.send(frame.make_frame('msg', msg=msg))
      
      # recebendo status do envio
      answer = socket_to_server.recv(8)

      msg_type, sender_id, receiver_id, seq_num = extract_info(answer)

      if (seq_num == frame.seq_num):
        if (msg_type == 1):
          print(f'status da mensagem: ok')
        else:
          print(f'status da mensagem: erro')

      other_msg = socket_to_server.recv(212)

      msg_type, sender_id, receiver_id, seq_num, msg_size, msg = extract_info(other_msg)
      print(f'Mensagem de {sender_id}: {msg}')

      msg = cria_msg()
      muda_receptor(msg, frame)

    socket_to_server.send(frame.make_frame('flw'))
    socket_to_server.recv(8)
    socket_to_server.close()

  else:
    print('"oi" não aceito.')
    socket_to_server.close()