def write_txt(file, data):
    f = open(file, 'w')
    f.write(data)
    f.close()


def read_txt(file):
    f = open(file, 'r')
    data = f.read()
    f.close()
    return data

