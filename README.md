# ADB Notification Parser

![Android Debug Bridge](https://img.shields.io/badge/ADB-Android%20Debug%20Bridge-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8%2B-blue)

A Python tool that parses raw `adb shell dumpsys notification` output into structured JSON data, extracting:
- Notification titles and text
- Timestamps
- Channels and priorities
- Actions (buttons)
- Package names
- Importance levels

## 📋 Prerequisites

### Hardware Requirements
- Android device (with USB debugging or WiFi debugging enabled)
- Computer (Windows/macOS/Linux)

### Software Requirements
- [ADB (Android Debug Bridge)](https://developer.android.com/studio/command-line/adb)
- Python 3.8+
- Required Python packages (install via `requirements.txt`)

## 🛠 Setup Instructions

### 1. Enable Developer Options
1. Go to `Settings > About Phone`
2. Tap `Build Number` 7 times
3. Enter your PIN if prompted

### 2. Enable Debugging
#### USB Method:
1. Connect device via USB
2. Enable `USB Debugging` in Developer Options
3. Verify connection: `adb devices`

#### Wireless Method:
``` bash
adb tcpip 5555
adb connect <device-ip>:5555
```
Video Tutorial

3. Install Python Dependencies
 ```
bash
pip install -r requirements.txt
```
🚀 Usage
1. Capture Notification Data
```
bash
adb shell dumpsys notification --noredact > notifications_raw.txt
```
3. Parse with Python
```bash
python notifications_parser.py
```
Sample Output Structure
```
json
{
  "package": "com.whatsapp",
  "title": "New message",
  "text": "Hello from John",
  "timestamp": "2023-11-15 14:30:22",
  "channel": "messages",
  "priority": "HIGH",
  "actions": ["Reply", "Mark as read"]
}
```
🔧 Technical Implementation
Key Parsing Logic
```
python
def parse_notification(raw_text):
    # Regex patterns for extraction
    patterns = {
        'title': r'android.title=String\((.*?)\)',
        'text': r'android.text=String\((.*?)\)',
        'timestamp': r'postTime=(\d+)',
        'package': r'pkg=(.*?)\s',
        'channel': r'Channel\{.*?\s(.*?)\s'
    }
```
    # ... parsing implementation ...
Features
Multi-notification handling

Error-resistant parsing

Structured JSON output

Support for notification actions

📊 Example Use Cases
Notification Analytics: Track which apps send most notifications

Debugging: Monitor notification content during development

Automation: Trigger actions based on specific notifications

📜 License
This project is licensed under MIT License - see LICENSE file for details.

🙋 FAQ
Q: Can I use this without physical USB connection?
A: Yes! Use WiFi debugging as shown in the setup.

Q: How do I analyze notifications over time?
A: Schedule regular ADB dumps and aggregate the JSON results.

Q: Is root access required?
A: No, standard debugging access is sufficient.

