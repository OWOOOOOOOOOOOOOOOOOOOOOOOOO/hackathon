import re

def parse_duration(dur_str):
    total_minutes = 0.0
    matches = re.findall(r'(\d+)([dhms])', dur_str.lower())
    for num, unit in matches:
        num = int(num)
        if unit == 'd':
            total_minutes += num * 24 * 60
        elif unit == 'h':
            total_minutes += num * 60
        elif unit == 'm':
            total_minutes += num
        elif unit == 's':
            total_minutes += num / 60.0
    return total_minutes if total_minutes > 0 else None

# Test cases
test_cases = [
    ("1h55m", 115.0),
    ("2d3h4m5s", 2*1440 + 3*60 + 4 + 5/60),
    ("30m", 30.0),
    ("1h", 60.0),
    ("120s", 2.0),
    ("1d", 1440.0),
    ("", None),
    ("abc", None),
    ("1x", None),
    ("0h", None),  # Zero duration returns None
    ("-1h", None),  # Negative not parsed
    ("1h2m3s4d", 1*60 + 2 + 3/60 + 4*1440),  # Out of order
    ("10d", 10*1440),
    ("100h", 100*60),
    ("5000m", 5000.0),
    ("86400s", 1440.0),  # 1 day in seconds
    ("1h 30m", 90.0),  # Space separated, but regex handles
    ("1H55M", 115.0),  # Uppercase
]

for input_str, expected in test_cases:
    result = parse_duration(input_str)
    print(f"Input: '{input_str}' -> Expected: {expected}, Got: {result}, Pass: {result == expected}")
