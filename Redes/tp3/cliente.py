import socket
import sys
import select
import queue
from comum import Protocol, extract_info

debug = False
debug_writable = False

# se retornar 0: tudo certo.
# se retornar 1: a mensagem não inicia com 'M' nem com 'S'.
# se retornar 2: a mensagem não tem um destinatário numérico.
def msg_validation(msg: str) -> int:

    msg_array = msg.replace('\n', '').split(' ', maxsplit=2)

    if (msg_array[0] != 'M' and msg_array[0] != 'S'):
        return 1

    if (msg_array[0] == 'M'):
        try:
            int(msg_array[1])
        except:
            return 2
    
    return 0

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

  socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client_address = (host, port)
  socket_to_server.connect(client_address)
  socket_to_server.send(frame.make_frame('oi'))
  if (debug): print('mensagem de "oi" enviada')
  oi_answer = socket_to_server.recv(8)

  msg_type, sender_id, receiver_id, seq_num = extract_info(oi_answer)

  if (msg_type == 1 and seq_num == 0):
    print('Conexão estabelecida! Para sair envie uma mensagem apenas com "S"')

    out_queue = queue.Queue()
    in_queue = queue.Queue()

    inputs = [sys.stdin, socket_to_server]
    outputs = [sys.stdout, socket_to_server]

    while(inputs):
    
      readable, writable, exceptional = select.select(inputs, outputs, inputs)

      for s in writable:          
        
        if (s is sys.stdout and not out_queue.empty()):
          msg = out_queue.get_nowait()
          s.write(f'\nMensagem de {msg[0]}: {msg[1]}')

        elif (not s is sys.stdout and not in_queue.empty()):
          msg = in_queue.get_nowait()

          if (msg[0] == 'M'):
            frame.change_receiver(int(msg.split(' ', maxsplit=2)[1]))
            s.send(frame.make_frame('msg', msg=msg))

          else:
            s.send(frame.make_frame('flw'))
            s.recv(8)
            s.close()
      
      for s in readable:

        
        if (debug): print(f'no for de readable com s: {s}\nreadable: {readable}')

        if (s is sys.stdin):

          if (select.select([sys.stdin, ], [], [], 0.0)[0]):
            for line in s:

              match msg_validation(line):
                case 0:
                  if (debug): print(f'mensagem captada com sucesso: {line}')
                  in_queue.put(line.replace('\n', ''))
                case 1:
                  print('Mensagem inválida: comece com M ou S e um espaço em seguida.')
                case 2:
                  print('Destinatário inválido: digite um número seguido de espaço.')

              break

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
                print('\nMensagem confirmada pelo servidor')


      for s in exceptional:

        if (debug): print(f'em exceptional com s: {s}')
        print(f'fechando o socket')
        inputs.remove(socket_to_server)
        outputs.remove(socket_to_server)
        socket_to_server.close()
        finish = True

      if (finish):
        break

    else:
      print('Identificador já usado ou servidor lotado.')

    if (debug): print(f'saiu do while')

  if (debug): print(f'saiu da conexão')

try:
  inputs.remove(socket_to_server)
  outputs.remove(socket_to_server)
  socket_to_server.close()
  print('fim do programa, socket fechado')
except:
  print('programa finalizado')