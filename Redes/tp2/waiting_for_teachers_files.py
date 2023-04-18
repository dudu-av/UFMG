# Imageinei que a tabela que cada roteador vai guardar é um dicionário
# onde cada chave é um roteador de destino e cada valor é uma lista
# com dois elementos: distância e próximo roteador para alcançar o destino,
# respectivamente.
#
# Por exemplo:
# my_dic = {'hello': [1, 'a'], 'hi mom': [2, 'b'], 'haiyaaa': [3, 'b']}

# Se não puder usar essa biblioteca, tem que implementar a função
# deepcopy na mão!!!
import copy
ROUTER_NAME_SIZE = 5

# Essa função supõe que os caracteres | e : não podem fazer parte
# do nome do roteador. Caso possam, mude a mensagem a ser codificada
# dentro de `for route in routes_dic:`!!!
#
# Lembre-se de que nesse caso é necessário mudar também a função
# breaking_msg!!!
def router_msg(router_orig, num_routes, routes_dic, short_int=11111):

    msg_fragments = []

    msg_fragments.append( (short_int).to_bytes(2, 'big') )
    msg_fragments.append( router_orig.encode('latin-1') )
    msg_fragments.append( num_routes.to_bytes(2, 'big') )

    for name, distance in routes_dic.items():

        msg_fragments.append( f'|{name}:{distance}'.encode('latin-1') )

    msg = b''
    for msg_frag in msg_fragments:
        msg = msg + msg_frag

    return msg

def breaking_msg(msg):

    next_step = 2
    short_int = int.from_bytes(msg[:next_step], 'big')

    last_step = next_step
    next_step = last_step + ROUTER_NAME_SIZE
    router_orig = msg[last_step:next_step].decode('latin-1')

    last_step = next_step
    next_step = next_step + 2
    num_routes = int.from_bytes(msg[last_step:next_step], 'big')

    last_step = next_step
    routes_dic = msg[last_step:].decode('latin-1')
    routes_dic = routes_dic.split('|')[1:]
    routes_dic = list(map(lambda x: x.split(','), routes_dic))
    routes_dic = list(map(lambda x: [x[0], int(x[1])], routes_dic))
    routes_dic = {route[0]: route[1] for route in routes_dic}

    return (short_int, router_orig, num_routes, routes_dic)

# Pode usar a biblioteca copy.py? Se não puder a função
# deepcopy tem que ser feita na mão!!!
def update_router_list(my_dic, sender_name, other_dic):

    new_dic = copy.deepcopy(my_dic)

    for name, distance in other_dic.items():
        if (not name in new_dic):
            new_dic[name] = [distance, sender_name]
        elif (distance < new_dic[name][0]):
            new_dic[name] = [distance, sender_name]

    return new_dic