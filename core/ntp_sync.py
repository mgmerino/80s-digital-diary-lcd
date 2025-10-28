# NTP Time Synchronization for MicroPython

import time
try:
    import socket
    import struct
    SOCKET_AVAILABLE = True
except ImportError:
    SOCKET_AVAILABLE = False

class NTPSync:
    """Synchronizes time using NTP (Network Time Protocol)"""
    
    # NTP servers
    NTP_SERVERS = [
        "pool.ntp.org",
        "time.google.com",
        "time.cloudflare.com",
        "time.nist.gov"
    ]
    
    # NTP epoch is 1900-01-01, Unix epoch is 1970-01-01
    NTP_DELTA = 2208988800
    
    def __init__(self, rtc, settings):
        self.rtc = rtc
        self.settings = settings
        self.last_sync = None
    
    def is_available(self):
        """Check if NTP sync is available"""
        return SOCKET_AVAILABLE
    
    def get_ntp_time(self, host="pool.ntp.org", timeout=5):
        """
        Get time from NTP server
        
        Args:
            host: NTP server hostname
            timeout: Socket timeout in seconds
        
        Returns:
            Unix timestamp or None on failure
        """
        if not self.is_available():
            return None
        
        try:
            # Resolve hostname
            addr_info = socket.getaddrinfo(host, 123)
            addr = addr_info[0][-1]
            
            # Create socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(timeout)
            
            # NTP request packet (48 bytes)
            # LI=0, VN=3, Mode=3 (client)
            ntp_packet = bytearray(48)
            ntp_packet[0] = 0x1b  # 00 011 011
            
            # Send request
            s.sendto(ntp_packet, addr)
            
            # Receive response
            data, address = s.recvfrom(48)
            s.close()
            
            # Extract transmit timestamp (bytes 40-47)
            timestamp = struct.unpack('!I', data[40:44])[0]
            
            # Convert from NTP to Unix timestamp
            unix_time = timestamp - self.NTP_DELTA
            
            return unix_time
            
        except Exception as e:
            print(f"NTP error ({host}): {e}")
            return None
    
    def sync_time(self, offset_minutes=None):
        """
        Synchronize RTC with NTP server
        
        Args:
            offset_minutes: Timezone offset in minutes (uses stored setting if None)
        
        Returns:
            True if sync successful, False otherwise
        """
        if not self.is_available():
            print("NTP not available (no network support)")
            return False
        
        # Get timezone offset
        if offset_minutes is None:
            offset_minutes = self.settings.get("local_offset_min", 0)
        
        # Try each NTP server until one works
        unix_time = None
        for server in self.NTP_SERVERS:
            print(f"Trying NTP server: {server}")
            unix_time = self.get_ntp_time(server)
            if unix_time is not None:
                break
        
        if unix_time is None:
            print("Failed to get time from any NTP server")
            return False
        
        # Apply timezone offset
        local_time = unix_time + (offset_minutes * 60)
        
        # Convert to time tuple
        time_tuple = time.localtime(local_time)
        
        # Set RTC
        # RTC.datetime() expects: (year, month, day, weekday, hours, minutes, seconds, subseconds)
        rtc_tuple = (
            time_tuple[0],  # year
            time_tuple[1],  # month
            time_tuple[2],  # day
            time_tuple[6],  # weekday (0=Monday)
            time_tuple[3],  # hours
            time_tuple[4],  # minutes
            time_tuple[5],  # seconds
            0               # subseconds
        )
        
        try:
            self.rtc.datetime(rtc_tuple)
            self.last_sync = time.time()
            print(f"Time synchronized: {time_tuple[0]}-{time_tuple[1]:02d}-{time_tuple[2]:02d} {time_tuple[3]:02d}:{time_tuple[4]:02d}:{time_tuple[5]:02d}")
            return True
        except Exception as e:
            print(f"Failed to set RTC: {e}")
            return False
    
    def auto_sync(self):
        """Automatically sync time if WiFi is available"""
        return self.sync_time()
    
    def get_last_sync(self):
        """Get timestamp of last successful sync"""
        return self.last_sync


