
class RedisConfParser(object):
    _kv = dict()
    _has_sub_key = set()
    _file = ""
    def __init__(self, file):
        self._file = file
        with open(self._file) as f:
            for s in f.readlines():
                if not s or s[0] == '#' or s[0] == '\n':
                    continue
                k, v = s.split(' ',1)
                if k in self._kv or k in self._has_sub_key:
                    self._has_sub_key.update({k})
                    sk, v = v.split(' ', 1)
                    old_val = self._kv.get(k)
                    old_sub_key, old_val = old_val.split(' ', 1)
                    old_key = k + ' '+ old_sub_key
                    self._kv.update({old_key:old_val})
                    k = k + ' ' + sk
                self._kv.update({k:v})

        for k in self._has_sub_key:
            self._kv.pop(k)



    def update_key(self, key, value):
        value = value + '\n'
        self._kv.update({key:value})

    def get_key(self, key):
        return self._kv.get(key, None)

    def update_subkey(self, pk, sk, value):
        value = value + '\n'
        self._kv.update({pk + ' ' + sk : value})
        
    def get_subkey(self, pk, sk):
        key = pk + ' ' + sk
        return self._kv.get(key, None)

    def dump(self):
        with open(self._file,'w') as f:
            for k, v in self._kv.items():            
                f.write(k)
                f.write(' ')
                f.write(v)


c = RedisConfParser("./redis.conf")
c.dump()
print(c.get_key("bind"))
print(c.get_subkey("save", "300"))
print(c.get_key("blah"))

c.update_key("ohio", "wtf")
c.update_subkey("if", "then", "else")
print(c.get_key("ohio"))
print(c.get_subkey("if", "then"))

