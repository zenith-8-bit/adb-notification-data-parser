import re
from collections import defaultdict

def extract_value(pattern, line, default=None):
    """Helper to safely extract values from lines"""
    match = re.search(pattern, line)
    return match.group(1) if match else default

def parse_core_fields(line, current):
    """Handle fundamental notification fields"""
    if '=' in line:
        key, value = line.split('=', 1)
        current[key.strip()] = value.strip()

def update_extras(current, line):
    """Process nested extras content"""
    if '=' in line:
        key, value = line.split('=', 1)
        current['extras'][key.strip()] = value.strip()

NOTIFICATION_STRUCTURE = {
    'channel': (r'Channel{.*? id=(.*?),', str),
    'group': (r'GroupAlertBehavior=(\d+)', int),
    'badge': (r'showBadge=(true|false)', lambda x: x == 'true'),
    'visibility': (r'visibility=(\w+)', str),
    'category': (r'category=(\w+)', str),
    'color': (r'color=(\w+)', str),
    'sound': (r'sound=(.*?) ', str),
    'vibration': (r'vibration=\[([\d,]+)\]', lambda x: list(map(int, x.split(',')))),
}

def parse_notifications(dumpsys_output):
    state = defaultdict(str)
    current = {}
    notifications = []
    in_extras = False
    extras_depth = 0

    for line in dumpsys_output.split('\n'):
        line = line.strip()
        
        if 'NotificationRecord(' in line:
            if current:
                notifications.append(current)
                current = {}
            current.update({
                'package': extract_value(r'pkg=(.*?)(\s|$)', line),
                'id': extract_value(r'id=(0x[0-9a-f]+)', line),
                'flags': extract_value(r'flags=(.*?)\s', line),
                'when': extract_value(r'when=(\d+)', line),
                'priority': extract_value(r'priority=(\w+)', line),
                'importance': extract_value(r'importance=(\w+)', line),
            })
            continue
            
        if line.startswith(('android.title=', 'android.text=')):
            parse_core_fields(line, current)
            continue
            
        if 'extras={' in line:
            in_extras = True
            extras_depth = line.count('{') - line.count('}')
            current.setdefault('extras', {}).update(parse_bundle(line[line.index('{')+1:]))
            continue
            
        if in_extras:
            extras_depth += line.count('{') - line.count('}')
            if extras_depth <= 0:
                in_extras = False
            else:
                update_extras(current, line)
            continue
            
        for field, (pattern, converter) in NOTIFICATION_STRUCTURE.items():
            if value := extract_value(pattern, line):
                try:
                    current[field] = converter(value)
                except Exception:
                    current[field] = value

    if current:
        notifications.append(current)
    return notifications

def parse_bundle(content):
    """Advanced bundle parser with type inference"""
    bundle = {}
    buffer = []
    key = None
    depth = 0
    quote = False
    
    for char in content + ' ':
        if char == '"':
            quote = not quote
        if char == '=' and not quote and depth == 0:
            key = ''.join(buffer).strip()
            buffer = []
            continue
        if char in '{[' and not quote:
            depth += 1
        if char in '}]' and not quote:
            depth -= 1
        if char == ' ' and depth == 0 and not quote and key:
            value = ''.join(buffer).strip()
            bundle[key] = infer_type(value)
            key = None
            buffer = []
        else:
            buffer.append(char)
    
    return bundle

def infer_type(value):
    """Convert string values to proper types"""
    if value.lower() in ('true', 'false'):
        return value.lower() == 'true'
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            pass
    if re.match(r'^[\d,]+$', value):
        return [int(n) for n in value.split(',')]
    return value

def clean_output(notifications):
    return [{
        'app': n.get('package'),
        'title': n.get('android.title') or n.get('extras', {}).get('android.title'),
        'text': n.get('android.text') or n.get('extras', {}).get('android.text'),
        'timestamp': n.get('when'),
        'channel': n.get('channel'),
        'priority': n.get('priority'),
        'actions': list({a for a in n.get('actions', []) if a}),
        'importance': n.get('importance'),
        'badge': n.get('badge', False),
        'sound': n.get('sound'),
        'vibration': n.get('vibration', []),
    } for n in notifications]

def read_adb_output(filename):
    encodings = ['utf-8', 'utf-16', 'latin-1']
    for enc in encodings:
        try:
            with open(filename, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeError, FileNotFoundError):
            continue
    raise FileNotFoundError(f"Could not read {filename}")

def main():
    try:
        output = read_adb_output('demotext.txt')
        parsed = parse_notifications(output)
        cleaned = clean_output(parsed)
        
        for idx, notif in enumerate(cleaned, 1):
            print(f"[Notification {idx}]")
            print(f"Package: {notif['app']}")
            print(f"Title: {notif['title']}")
            print(f"Content: {notif['text']}")
            print(f"Timestamp: {notif['timestamp']}")
            print(f"Channel: {notif['channel']}")
            print(f"Priority: {notif['priority']}")
            if notif['actions']:
                print(f"Actions: {', '.join(notif['actions'])}")
            print("-" * 60)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
