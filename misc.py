def enum(*sequential, **named):
    # copied from: http://stackoverflow.com/a/1695250
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)


class MutableString(object):
    # copied from: http://stackoverflow.com/a/10572792
    def __init__(self, data):
        self.data = list(data)

    def __repr__(self):
        return "".join(self.data)

    def __setitem__(self, index, value):
        self.data[index] = value

    def __getitem__(self, index):
        if type(index) == slice:
            return "".join(self.data[index])
        return self.data[index]

    def __delitem__(self, index):
        del self.data[index]

    def __add__(self, other):
        self.data.extend(list(other))

    def __len__(self):
        return len(self.data)
