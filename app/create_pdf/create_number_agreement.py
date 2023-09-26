from random import choice

lst_symbols = ['q', 'w', 'r', 'e', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x',
               'c', 'v', 'b', 'n', 'm', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

random_number_agreement = ''
for i in range(8):
    random_number_agreement += choice(lst_symbols)
