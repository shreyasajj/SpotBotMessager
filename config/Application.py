import random
import string

tokenFileName = "data/token.txt"


def random_string_generator(str_size, howmany, allowed_chars=string.ascii_letters + string.digits):
    f = open(tokenFileName, "w+")
    for i in range(0, howmany):
        token = ''.join(random.choice(allowed_chars) for x in range(str_size))
        f.write(token + "\n")
    f.close()


def validateToken(string):
    f = open(tokenFileName, "r")
    while True:
        token = f.readline()
        if token == "":
            break
        if token.strip() == string.strip():
            return True
    return False
