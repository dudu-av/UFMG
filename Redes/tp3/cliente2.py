from io import StringIO

import socket
import sys
import select
import queue
from comum import Protocol, extract_info

debug = True
debug_writable = True

# se retornar 0: tudo certo.
# se retornar 1: a mensagem não inicia com 'M' nem com 'S'.
# se retornar 2: a mensagem não tem um destinatário numérico.
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

if (my_id > 65534):
  print(f'Identificador muito grande. Escolha um número entre 1 e 65534.')
else:
  host = sys.argv[2]
  port = int(sys.argv[3])
  frame = Protocol(my_id)

  inputs = [sys.stdin]
  outputs = [sys.stdout]

  socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client_address = (host, port)
  socket_to_server.connect(client_address)
  inputs.append(socket_to_server)
  outputs.append(socket_to_server)
  if (debug): print('enviando mensagem de "oi"')
  socket_to_server.send(frame.make_frame('oi'))
  if (debug): print('mensagem de "oi" enviada')
  oi_answer = socket_to_server.recv(8)

  msg_type, sender_id, receiver_id, seq_num = extract_info(oi_answer)

  if (msg_type == 1 and seq_num == 0):
    print('Conexão estabelecida! Para sair envie uma mensagem apenas com "S"')

    out_queue = queue.Queue()
    in_queue  = queue.Queue()

    while(inputs):
    
      readable, writable, exceptional = select.select(inputs, outputs, inputs)

      #print(f'readable: {readable}')
      #while (socket_to_server.fileno() != -1):

      #if (debug): print(f'entrou no while')

      for s in readable:

        data = s.recv(212)

        try:
          msg_type, sender_id, receiver_id, seq_num = extract_info(data)
        except:
          msg_type, sender_id, receiver_id, seq_num, msg_size, msg = extract_info(data)

        if (receiver_id == my_id):

          if (msg_type == 5):

            print(f'Mensagem de {sender_id}: {msg}')

          if (msg_type == 1):

            print(f'Mensagem de número {seq_num} confirmada')

          if (msg_type == 2):

            print(f'Mensagem de número {seq_num} com erro')

      for s in writable:

            

        if (s is sys.stdin):

          for line in s:

            if (debug): print(f'line in sys.stdin: {line}')
            debug_writable = True

            match msg_valida(line):
              case 0:
                if (debug): print(f'mensagem captada com sucesso: {line}')
                in_queue.put(line.replace('\n', ''))
              case 1:
                print('Mensagem inválida: comece com M ou S e um espaço em seguida.')
              case 2:
                print('Destinatário inválido: digite um número seguido de espaço.')

        else:

          if (debug): print('esperando ler data')
          data = s.recv(212)
          if (debug): print('leu data')

          if (data):

            try:
              msg_type, sender_id, receiver_id, seq_num, msg_size, msg = extract_info(data)
            except:
              msg_type, sender_id, receiver_id, seq_num = extract_info(data)

            if (receiver_id == my_id):

              if (msg_type == 5):
                s.send(frame.make_frame('ok', seq_num))
                out_queue.put((sender_id, msg))

              if (msg_type == 1):
                print('Mensagem confirmada pelo servidor')

            if (not in_queue.empty()):
              msg = in_queue.get_nowait()

              if (msg[0] == 'M'):
                muda_receptor(msg, frame)
                s.send(frame.make_frame('msg', msg=msg))

              else:
                s.send(frame.make_frame('flw'))
                s.recv(8)
                s.close()

      for s in writable:

        if (debug_writable):
          print(f'em writable com s: {s}\né sys.stdout? {s is sys.stdout}')
          print(f'out_queue.empty()? {out_queue.empty()}')
          debug_writable = False
          
        
        if (s is sys.stdout and not out_queue.empty()):
          if (debug): print(f'entrou aqui')
          msg = out_queue.get_nowait()
          if (debug): print(f'pegou mensagem: {msg}')
          s.write(f'Mensagem de {msg[0]}: {msg[1]}')
          print(f'Mensagem de {msg[0]}: {msg[1]}')

      for s in exceptional:

        if (debug): print(f'em exceptional com s: {s}')

    else:
      print('Identificador já usado ou servidor lotado.')
