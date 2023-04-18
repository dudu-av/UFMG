debug = False

def extract_info(data: bytes):

  msg_type = int.from_bytes(data[:2], 'big')
  sender_id = int.from_bytes(data[2:4], 'big')
  receiver_id = int.from_bytes(data[4:6], 'big')
  seq_num = int.from_bytes(data[6:8], 'big')


  if (msg_type != 5):
    if (debug): print(f'extract_info: {msg_type} + {sender_id} + {receiver_id} + {seq_num}')
    return (msg_type, sender_id, receiver_id, seq_num)

  else:
    msg_size = int.from_bytes(data[8:12], 'big')
    msg = data[12:].decode()
    if (debug): print(f'extract_info: {msg_type} + {sender_id} + {receiver_id} + {seq_num} + {msg_size} + {msg}')
    return (msg_type, sender_id, receiver_id, seq_num, msg_size, msg)

class Protocol:

  sender: bytes = b''
  receiver: bytes = b''
  seq_num: int = 0

  ok = b'\x00\01'
  erro = b'\x00\x02'
  oi = b'\x00\x03'
  flw = b'\x00\x04'
  msg = b'\x00\x05'
  server = (65535).to_bytes(2, 'big')

  def __init__(self, sender: int|bytes, receiver: int|bytes = server) -> None:
    
    if (type(sender) == int):
      self.sender = sender.to_bytes(2, 'big')
    else:
      self.sender = sender

    if (type(receiver) == int):
      self.receiver = receiver.to_bytes(2, 'big')
    else:
      self.receiver = receiver

  def change_receiver(self, receiver: int|bytes) -> None:
    if (type(receiver) == int):
      self.receiver = receiver.to_bytes(2, 'big')
    else:
      self.receiver = receiver


  def make_frame(self, msg_type: str, seq: int = None, msg: str = None) -> bytes:
    frame = b''
    
    if (self.sender == self.server):
      self.seq_num = seq

    match msg_type:
      case 'ok':
        if (self.sender != self.server):
          self.receiver = self.sender
          aux_seq = self.seq_num
          self.seq_num = seq
        frame = self.ok
      case 'erro':
        frame = self.erro
      case 'oi':
        self.seq_num = 0
        self.receiver = self.server
        frame = self.oi
      case 'flw':
        self.receiver = self.server
        frame = self.flw
      case 'msg':
        frame = self.msg
        # Pega o destinatário da mensagem
        if (msg != None):
          self.receiver = int(msg.split(' ')[1]).to_bytes(2, 'big')
      case _:
        return b''

    # if (debug): print(f'frame até agora: {frame}')
    
    frame += self.sender + \
      self.receiver + \
      self.seq_num.to_bytes(2, 'big')

    if (self.sender == self.server and msg_type == 'msg'):
      self.seq_num = aux_seq
    
    # if (debug): print(f'frame até agora: {frame}')

    if (msg != None):
      real_msg_encoded = msg.split(maxsplit=2)[2].encode()
      if (len(real_msg_encoded) > 200):
        print('Mensagem muito grande. Não pode ser enviada.')
        frame = b''
      else:
        frame += len(real_msg_encoded).to_bytes(4, 'big')
        frame += real_msg_encoded

    self.seq_num += 1

    # if (debug): print(f'frame final: {frame}')
    return frame



    