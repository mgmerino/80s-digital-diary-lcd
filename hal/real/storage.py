# Real storage implementation using filesystem

from hal.interfaces import StorageInterface
import os


class StorageReal(StorageInterface):
    """Real storage implementation for Pico filesystem"""
    
    def read(self, path):
        """Read data from file"""
        with open(path, 'rb') as f:
            return f.read()
    
    def write(self, path, data):
        """Write data to file"""
        with open(path, 'wb') as f:
            f.write(data)
    
    def exists(self, path):
        """Check if file exists"""
        try:
            os.stat(path)
            return True
        except OSError:
            return False
    
    def remove(self, path):
        """Remove a file"""
        os.remove(path)

