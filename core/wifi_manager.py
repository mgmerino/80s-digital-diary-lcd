# WiFi Manager for Raspberry Pico 2 W

import time
from secrets import secrets

SSID = secrets.get("WIFI_SSID")
PWD  = secrets.get("WIFI_PASSWORD")
if not SSID or not PWD:
    raise ValueError("Missing WIFI_SSID or WIFI_PASSWORD in secrets.py")

try:
    import network
    WIFI_AVAILABLE = True
except ImportError:
    WIFI_AVAILABLE = False

class WiFiManager:
    """Manages WiFi connections on Raspberry Pico 2 W"""
    
    def __init__(self, settings):
        self.settings = settings
        self.wlan = None
        self.connected = False
        
        if WIFI_AVAILABLE:
            self.wlan = network.WLAN(network.STA_IF)
        
    def is_available(self):
        """Check if WiFi hardware is available"""
        return WIFI_AVAILABLE and self.wlan is not None
    
    def is_connected(self):
        """Check if WiFi is currently connected"""
        if not self.is_available():
            return False
        assert self.wlan is not None
        return self.wlan.isconnected()
    
    def get_status(self):
        """Get WiFi connection status as a string"""
        if not self.is_available():
            return "No WiFi hardware"
        assert self.wlan is not None
        if self.is_connected():
            return "Connected"
        if self.wlan.active():
            return "Connecting..."
        return "Disconnected"
    
    def get_ip(self):
        """Get current IP address"""
        if not self.is_connected():
            return None
        assert self.wlan is not None
        try:
            return self.wlan.ifconfig()[0]
        except:
            return None
    
    def get_rssi(self):
        """Get signal strength (RSSI)"""
        if not self.is_connected():
            return None
        assert self.wlan is not None
        try:
            return self.wlan.status('rssi')
        except:
            return None
    
    def scan(self):
        """Scan for available networks"""
        if not self.is_available():
            return []
        
        assert self.wlan is not None  # Type narrowing for type checker
        
        try:
            if not self.wlan.active():
                self.wlan.active(True)
            
            networks = self.wlan.scan()
            # Returns list of tuples: (ssid, bssid, channel, RSSI, security, hidden)
            result = []
            for net in networks:
                try:
                    ssid = net[0].decode('utf-8')
                    rssi = net[3]
                    result.append({'ssid': ssid, 'rssi': rssi})
                except:
                    pass
            
            # Sort by signal strength
            result.sort(key=lambda x: x['rssi'], reverse=True)
            return result
        except Exception as e:
            print("WiFi scan error:", e)
            return []
    
    def connect(self, ssid=None, password=None, timeout=15):
        """
        Connect to WiFi network
        
        Args:
            ssid: WiFi network name (uses stored setting if None)
            password: WiFi password (uses stored setting if None)
            timeout: Connection timeout in seconds
        
        Returns:
            True if connected, False otherwise
        """
        if not self.is_available():
            return False
        
        assert self.wlan is not None
        
        # Use stored credentials if not provided
        if ssid is None:
            ssid = self.settings.get("wifi_ssid", "")
        if password is None:
            password = self.settings.get("wifi_password", "")
        
        if not ssid:
            return False
        
        try:
            # Activate WiFi interface
            if not self.wlan.active():
                self.wlan.active(True)
            
            # Disconnect if already connected
            if self.wlan.isconnected():
                self.wlan.disconnect()
                time.sleep(0.5)
            
            # Connect to network
            print(f"Connecting to WiFi: {ssid}")
            self.wlan.connect(ssid, password)
            
            # Wait for connection
            start = time.time()
            while not self.wlan.isconnected():
                if time.time() - start > timeout:
                    print("WiFi connection timeout")
                    return False
                time.sleep(0.5)
            
            self.connected = True
            ip = self.get_ip()
            print(f"WiFi connected! IP: {ip}")
            return True
            
        except Exception as e:
            print(f"WiFi connection error: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from WiFi"""
        if not self.is_available():
            return
        
        assert self.wlan is not None
        
        try:
            if self.wlan.isconnected():
                self.wlan.disconnect()
            self.wlan.active(False)
            self.connected = False
            print("WiFi disconnected")
        except Exception as e:
            print(f"WiFi disconnect error: {e}")
    
    def auto_connect(self):
        """Attempt to connect using stored credentials"""
        ssid = self.settings.get("wifi_ssid", SSID)
        if ssid:
            return self.connect(SSID, PWD)
        return False


