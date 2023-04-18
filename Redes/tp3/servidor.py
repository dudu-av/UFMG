import select
import socket
import sys
import queue
from comum import Protocol, extract_info

debug = False

clients_dic = {}
bye_bye = False

if len(sys.argv) != 2:
  print('Argumentos: <', sys.argv[0],'> <porto>')
  exit()

my_id = 65535
host = ''
port = int(sys.argv[1])

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)

server_address = (host, port)

server.bind(server_address)
print('Esperando conexão...')
server.listen(5)

inputs = [server]
outputs = []
msg_queues = {}

while (inputs):

  print('Esperando pelo próximo evento')
  readable, writable, exceptional = select.select(inputs, outputs, inputs)
  if (debug): print(f'readable: {readable}\nwritable: {writable}\nexceptional: {exceptional}')

  for s in readable:

    if (s is server):

      connection, client_address = s.accept()
      
      # Primeiro contato
      if (debug): print('esperando mensagem de "oi"')
      
      oi_msg = connection.recv(8)

      if (len(clients_dic) >= 256):
        print(f'O cliente {connection} quis se conectar, mas o servidor já está lotado.')
        bye_bye = True

      msg_type, client_id, server_id, seq_num = extract_info(oi_msg)
      
      if (debug): 
        print('mensagem de "oi" recebida')
        print(f'* oi msg: {oi_msg}\n* msg type: {msg_type}\n* client id: {client_id}\n* server id: {server_id}\nmsg seq num: {seq_num}')
      
      frame = Protocol(my_id, client_id)
      
      if ((msg_type == 3) and (not client_id in clients_dic) and not bye_bye):
      
        clients_dic[client_id] = connection
        if (debug): print(f'Conexão com {client_address} que tem identificador {client_id}')
        connection.send(frame.make_frame('ok', seq_num))
    
        connection.setblocking(0)
        inputs.append(connection)

        msg_queues[connection] = queue.Queue()
      
      else:
        connection.send(frame.make_frame('erro', seq_num))
        if (debug): print('Mensagem de "oi" não enviada ou identificador já usado ou servidor lotado.')
        connection.close()
      
      bye_bye = False

    else:

      if (debug): print(f'tá no recv')
      data = s.recv(212)

      if data:

        if (debug): print(f'tem data: {data}')

        try:
          msg_type, sender_id, receiver_id, seq_num, msg_size, msg = extract_info(data)
        except:
          msg_type, sender_id, receiver_id, seq_num = extract_info(data)

        if (s == clients_dic[sender_id]):
          receiver_socket = clients_dic[receiver_id]
          
          if (msg_type == 5):

            if (debug): print(f'{s}, número {sender_id}, quer enviar mensagem "{msg}" para {receiver_socket}, número {receiver_id}.')

            if (receiver_id in clients_dic):
            
              frame = Protocol(my_id, sender_id)
              msg_queues[s].put(frame.make_frame('ok', seq_num))
              if (receiver_id == 0):
                for x in clients_dic:
                  msg_queues[clients_dic[x]].put(data)
              else:
                msg_queues[receiver_socket].put(data)
              if (debug): print(f'Su-su-su-sucesso! Indo entregar {data}')

            else:

              frame = Protocol(my_id, sender_id)
              msg_queues[s].put(frame.make_frame('erro', seq_num))
              if (debug): print(f'Mensagem não pode ser entregue a quem não existe.')

          # quando o cliente digitar só 'S', ele tem que enviar um 'flw'
          if (msg_type == 4):

            if (debug): print(f'cliente {sender_id} deseja sair. Tchau tchau!')

            frame = Protocol(my_id, sender_id)
            s.send(frame.make_frame('ok', seq_num))
            outputs.remove(s)
            inputs.remove(s)
            s.close()

          if (msg_type == 1):

            print(f'O cliente {s}, Nº {sender_id}, confirma que recebeu a mensagem de sequência {seq_num}')

          if (s not in outputs):
              outputs.append(s)

      else:

        print(f'X--Fechando {client_address}')

        if (s in outputs):
            outputs.remove(s)
        
        inputs.remove(s)
        s.close()

        del msg_queues[s]

  for s in writable:

    inverse_clients_dic = {y: x for x,y in clients_dic.items()}
    
    try:
      next_msg = msg_queues[s].get_nowait()

    except queue.Empty:
      print(f'A fila de {inverse_clients_dic[s]} está vazia')
      outputs.remove(s)

    else:
      print(f'*Enviando {next_msg} para {inverse_clients_dic[s]}')
      try:
        s.send(next_msg)
      except:
        outputs.remove(s)
        inputs.remove(s)
        del clients_dic[inverse_clients_dic[s]]
        s.close()


  for s in exceptional:

    print(f'X--Exceção em {s.getpeername()}')
    inputs.remove(s)

    if (s in outputs):
        outputs.remove(s)
    
    s.close()

    del msg_queues[s]