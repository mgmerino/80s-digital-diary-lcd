# Timezone Manager with DST support

try:
    import utime as time
except ImportError:
    import time


class Timezone:
    """Represents a timezone with DST rules"""
    
    def __init__(self, name, std_offset, dst_offset=None, dst_start=None, dst_end=None):
        """
        Args:
            name: Display name of the timezone
            std_offset: Standard time offset in minutes from UTC
            dst_offset: DST offset in minutes from UTC (None if no DST)
            dst_start: Function that returns DST start date for a given year (month, week, dow)
            dst_end: Function that returns DST end date for a given year (month, week, dow)
        """
        self.name = name
        self.std_offset = std_offset
        self.dst_offset = dst_offset if dst_offset is not None else std_offset
        self.dst_start = dst_start
        self.dst_end = dst_end
        self.has_dst = dst_offset is not None and dst_start is not None and dst_end is not None
    
    def get_offset(self, timestamp=None):
        """
        Get the current offset for this timezone
        
        Args:
            timestamp: Unix timestamp (uses current time if None)
        
        Returns:
            Offset in minutes from UTC
        """
        if not self.has_dst or self.dst_offset is None:
            return self.std_offset
        
        if timestamp is None:
            timestamp = time.time()
        
        if self.is_dst(timestamp):
            return self.dst_offset
        return self.std_offset
    
    def is_dst(self, timestamp):
        """Check if DST is active for the given timestamp"""
        if not self.has_dst or self.dst_start is None or self.dst_end is None:
            return False
        
        tm = time.localtime(timestamp)
        year = tm[0]
        month = tm[1]
        day = tm[2]
        hour = tm[3]
        
        # Get DST transition dates for this year
        dst_start = self.dst_start(year)
        dst_end = self.dst_end(year)
        
        start_month, start_day = dst_start
        end_month, end_day = dst_end
        
        # Simple comparison based on date (DST changes at 2 AM)
        # Northern hemisphere (DST starts before it ends)
        if start_month < end_month:
            # Before DST start
            if month < start_month:
                return False
            # After DST start month but not yet started
            if month == start_month:
                if day < start_day:
                    return False
                if day == start_day and hour < 2:
                    return False
            # After DST end month
            if month > end_month:
                return False
            # In DST end month but still in DST
            if month == end_month:
                if day > end_day:
                    return False
                if day == end_day and hour >= 2:
                    return False
            # Between start and end = DST active
            return True
        else:  # Southern hemisphere
            # DST end before DST start in same year
            if month < end_month:
                return True
            if month == end_month:
                if day < end_day or (day == end_day and hour < 2):
                    return True
            if month > start_month:
                return True
            if month == start_month:
                if day > start_day or (day == start_day and hour >= 2):
                    return True
            return False

# Zeller's congruence for day of week
def day_of_week(y, m, d):
    """Returns 0=Sunday, 1=Monday, ..., 6=Saturday"""
    if m < 3:
        m += 12
        y -= 1
    q = d
    m = m
    k = y % 100
    j = y // 100
    h = (q + ((13 * (m + 1)) // 5) + k + (k // 4) + (j // 4) - (2 * j)) % 7
    # Convert to 0=Sunday format
    return (h + 6) % 7

def last_sunday_of_month(year, month):
    """
    Find the last Sunday of a given month
    
    Returns:
        (month, day) tuple
    """
    # Days in each month
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    # Check for leap year
    if month == 2 and (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
        last_day = 29
    else:
        last_day = days_in_month[month - 1]
    
    weekday = day_of_week(year, month, last_day)
    
    # Calculate how many days to go back to get to Sunday (weekday=0)
    days_back = weekday
    last_sunday = last_day - days_back
    
    return (month, last_sunday)

def nth_sunday_of_month(year, month, n):
    """
    Find the nth Sunday of a given month (1-based)
    
    Returns:
        (month, day) tuple
    """    
    # Find first day of month's weekday
    first_weekday = day_of_week(year, month, 1)
    
    # Calculate first Sunday
    if first_weekday == 0:  # Already Sunday
        first_sunday = 1
    else:
        first_sunday = 1 + (7 - first_weekday)
    
    # Calculate nth Sunday
    nth_sunday = first_sunday + (n - 1) * 7
    
    return (month, nth_sunday)

# ========== Timezone Definitions ==========

# Europe - uses last Sunday of March and October for DST transitions
def eu_dst_start(year):
    """European DST starts last Sunday of March"""
    return last_sunday_of_month(year, 3)

def eu_dst_end(year):
    """European DST ends last Sunday of October"""
    return last_sunday_of_month(year, 10)

# USA - uses second Sunday of March and first Sunday of November
def us_dst_start(year):
    """US DST starts second Sunday of March"""
    return nth_sunday_of_month(year, 3, 2)

def us_dst_end(year):
    """US DST ends first Sunday of November"""
    return nth_sunday_of_month(year, 11, 1)


# Lightweight timezone data (name, std_offset, dst_offset, dst_start_fn, dst_end_fn)
# dst_offset=None means no DST
TIMEZONE_DATA = {
    # UTC
    "UTC": ("UTC", 0, None, None, None),
    
    # Western Europe (GMT+0/+1)
    "WET": ("WET (Western Europe)", 0, 60, eu_dst_start, eu_dst_end),
    "GMT": ("GMT (London)", 0, 60, eu_dst_start, eu_dst_end),
    
    # Central Europe (GMT+1/+2) - DEFAULT
    "CET": ("CET (Central Europe)", 60, 120, eu_dst_start, eu_dst_end),
    
    # Eastern Europe (GMT+2/+3)
    "EET": ("EET (Eastern Europe)", 120, 180, eu_dst_start, eu_dst_end),
    
    # US East Coast (GMT-5/-4)
    "EST": ("EST (US East)", -300, -240, us_dst_start, us_dst_end),
    
    # US Central (GMT-6/-5)
    "CST": ("CST (US Central)", -360, -300, us_dst_start, us_dst_end),
    
    # US Mountain (GMT-7/-6)
    "MST": ("MST (US Mountain)", -420, -360, us_dst_start, us_dst_end),
    
    # US Pacific (GMT-8/-7)
    "PST": ("PST (US Pacific)", -480, -420, us_dst_start, us_dst_end),
    
    # Fixed offset timezones (no DST)
    "UTC-12": ("UTC-12", -720, None, None, None),
    "UTC-11": ("UTC-11", -660, None, None, None),
    "UTC-10": ("UTC-10 (Hawaii)", -600, None, None, None),
    "UTC-9": ("UTC-9 (Alaska)", -540, None, None, None),
    "UTC-8": ("UTC-8", -480, None, None, None),
    "UTC-7": ("UTC-7", -420, None, None, None),
    "UTC-6": ("UTC-6", -360, None, None, None),
    "UTC-5": ("UTC-5", -300, None, None, None),
    "UTC-4": ("UTC-4", -240, None, None, None),
    "UTC-3": ("UTC-3", -180, None, None, None),
    "UTC-2": ("UTC-2", -120, None, None, None),
    "UTC-1": ("UTC-1", -60, None, None, None),
    "UTC+1": ("UTC+1", 60, None, None, None),
    "UTC+2": ("UTC+2", 120, None, None, None),
    "UTC+3": ("UTC+3 (Moscow)", 180, None, None, None),
    "UTC+4": ("UTC+4 (Dubai)", 240, None, None, None),
    "UTC+5": ("UTC+5", 300, None, None, None),
    "UTC+5:30": ("UTC+5:30 (India)", 330, None, None, None),
    "UTC+6": ("UTC+6", 360, None, None, None),
    "UTC+7": ("UTC+7 (Bangkok)", 420, None, None, None),
    "UTC+8": ("UTC+8 (Beijing)", 480, None, None, None),
    "UTC+9": ("UTC+9 (Tokyo)", 540, None, None, None),
    "UTC+9:30": ("UTC+9:30 (Adelaide)", 570, None, None, None),
    "UTC+10": ("UTC+10 (Sydney)", 600, None, None, None),
    "UTC+11": ("UTC+11", 660, None, None, None),
    "UTC+12": ("UTC+12 (Auckland)", 720, None, None, None),
}


def create_timezone(tz_key):
    """
    Lazy factory function to create Timezone objects on demand
    
    Args:
        tz_key: Timezone key (e.g., "CET", "UTC")
    
    Returns:
        Timezone object or None if key not found
    """
    data = TIMEZONE_DATA.get(tz_key)
    if data is None:
        return None
    
    name, std_offset, dst_offset, dst_start, dst_end = data
    return Timezone(name, std_offset, dst_offset, dst_start, dst_end)


def get_timezone_info(tz_key):
    """
    Get timezone info without creating full Timezone object
    Useful for displaying timezone list
    
    Args:
        tz_key: Timezone key
    
    Returns:
        dict with name, std_offset, has_dst or None
    """
    data = TIMEZONE_DATA.get(tz_key)
    if data is None:
        return None
    
    name, std_offset, dst_offset, dst_start, dst_end = data
    has_dst = dst_offset is not None and dst_start is not None
    
    return {
        "name": name,
        "std_offset": std_offset,
        "dst_offset": dst_offset if has_dst else std_offset,
        "has_dst": has_dst
    }

# Ordered list for display in UI (just keys, lightweight!)
TIMEZONE_LIST = [
    "CET",  # Default (GMT+1/+2)
    "UTC",
    "WET",
    "GMT",
    "EET",
    "EST",
    "CST",
    "MST",
    "PST",
    "UTC-12",
    "UTC-11",
    "UTC-10",
    "UTC-9",
    "UTC-8",
    "UTC-7",
    "UTC-6",
    "UTC-5",
    "UTC-4",
    "UTC-3",
    "UTC-2",
    "UTC-1",
    "UTC+1",
    "UTC+2",
    "UTC+3",
    "UTC+4",
    "UTC+5",
    "UTC+5:30",
    "UTC+6",
    "UTC+7",
    "UTC+8",
    "UTC+9",
    "UTC+9:30",
    "UTC+10",
    "UTC+11",
    "UTC+12",
]


class TimezoneManager:
    """Manages timezone settings and conversions"""
    
    def __init__(self, settings):
        self.settings = settings
        self.current_tz = None
        self.current_tz_key = None
        self.load_timezone()
    
    def load_timezone(self):
        """Load timezone from settings (lazy instantiation)"""
        tz_key = self.settings.get("timezone", "CET")  # Default to CET (GMT+1)
        
        # Only create Timezone object if key changed or not yet created
        if self.current_tz_key != tz_key:
            self.current_tz = create_timezone(tz_key)
            if self.current_tz is None:
                # Fallback to CET if invalid key
                self.current_tz = create_timezone("CET")
                tz_key = "CET"
            self.current_tz_key = tz_key
    
    def set_timezone(self, tz_key):
        """Set the current timezone (lazy instantiation)"""
        if tz_key in TIMEZONE_DATA:
            self.current_tz = create_timezone(tz_key)
            self.current_tz_key = tz_key
            return True
        return False
    
    def get_timezone(self):
        """Get the current timezone object"""
        return self.current_tz
    
    def get_timezone_name(self):
        """Get the current timezone name"""
        return self.current_tz.name if self.current_tz else "Unknown"
    
    def get_offset(self, timestamp=None):
        """
        Get current timezone offset in minutes
        
        Args:
            timestamp: Unix timestamp (uses current time if None)
        
        Returns:
            Offset in minutes from UTC
        """
        if self.current_tz is None:
            self.load_timezone()
        
        if self.current_tz is None:
            return 0  # Fallback to UTC if timezone loading failed
        
        return self.current_tz.get_offset(timestamp)
    
    def is_dst_active(self, timestamp=None):
        """Check if DST is currently active"""
        if self.current_tz is None:
            self.load_timezone()
        
        if self.current_tz is None:
            return False  # Fallback if timezone loading failed
        
        if timestamp is None:
            timestamp = time.time()
        
        return self.current_tz.is_dst(timestamp)
    
    def utc_to_local(self, utc_timestamp):
        """
        Convert UTC timestamp to local time
        
        Args:
            utc_timestamp: Unix timestamp in UTC
        
        Returns:
            Unix timestamp in local time
        """
        offset = self.get_offset(utc_timestamp)
        return utc_timestamp + (offset * 60)
    
    def local_to_utc(self, local_timestamp):
        """
        Convert local timestamp to UTC
        
        Args:
            local_timestamp: Unix timestamp in local time
        
        Returns:
            Unix timestamp in UTC
        """
        offset = self.get_offset(local_timestamp)
        return local_timestamp - (offset * 60)

