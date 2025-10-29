# Simulated storage using regular filesystem

from hal.interfaces import StorageInterface
import os


class StorageSim(StorageInterface):
    """Simulated storage for PC (uses regular filesystem)"""
    
    def read(self, path):
        """Read data from file"""
        with open(path, 'rb') as f:
            return f.read()
    
    def write(self, path, data):
        """Write data to file"""
        # Ensure directory exists
        dirname = os.path.dirname(path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        
        with open(path, 'wb') as f:
            f.write(data)
    
    def exists(self, path):
        """Check if file exists"""
        return os.path.exists(path)
    
    def remove(self, path):
        """Remove a file"""
        if os.path.exists(path):
            os.remove(path)

