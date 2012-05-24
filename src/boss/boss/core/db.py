
import os
import jsonpickle
import hashlib
from time import sleep
from random import random
from boss.core.utils import abspath

class JsonDB(object):
    def __init__(self, file_path):
        self.file_path = abspath(file_path)
        self.lock_path = "%s/.%s.lock" % (
            os.path.dirname(self.file_path), 
            os.path.basename(self.file_path)
            )
        
    def connect(self):
        if not os.path.exists(self.file_path):
            self._write(dict())
    
    def _get_lock(self):
        while True:
            if os.path.exists(self.lock_path):
                sleep(.10)
                continue
            else:
                break
                
        code = hashlib.md5(str(random() + random())).hexdigest()
        f = open(self.lock_path, 'w+')
        f.write(code)
        f.close()
        return code
    
    def _release_lock(self, code):
        if not os.path.exists(self.lock_path):
            return True
        curcode = open(self.lock_path, 'r').read()
        if curcode == code:
            os.remove(self.lock_path)
            return True
        return False
    
    def _write(self, data):
        code = self._get_lock()
        f = open(self.file_path, 'w+')
        f.write(jsonpickle.encode(data))
        f.close()
        self._release_lock(code)
        return True
        
    def _read(self):
        code = self._get_lock()
        f = open(self.file_path, 'r')
        data = f.read()
        f.close()
        self._release_lock(code)
        return jsonpickle.decode(data)
        
    def get(self, key, fallback=None):
        data = self._read()
        ret = None
        
        if data.has_key(key):
            return data[key]
        elif fallback:
            self.set(key, fallback)
            return fallback
        else:
            return None
        
    def set(self, key, value):
        data = self._read()
        data[key] = value
        self._write(data)
        return True
        
    def delete(self, key):
        data = self._read()
        if data.has_key(key):
            del data[key]
        self._write(data)
        return True