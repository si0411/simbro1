from flask import Flask, request, jsonify, render_template_string, 
send_file
import os
from datetime import datetime

app = Flask(__name__)

SAVE_PATH = "/home/pi/flask/notifications.csv"  # Your CSV file path
HTML_PATH = "/home/pi/flask/notification-app.html"  # Your HTML file path

@app.route('/update-csv', methods=['POST'])
def update_csv():
    data = request.get_data(as_text=True)
    if not data:
        return "No data received", 400
    try:
        # Parse the incoming data
        lines = data.strip().split('\n')
        if len(lines) < 2:
            return "Invalid CSV format", 400
        
        # Skip the header line from the incoming data
        data_lines = lines[1:]  # Skip first line (header)
        
        # Check if file exists and has content
        if not os.path.exists(SAVE_PATH) or os.path.getsize(SAVE_PATH) == 
0:
            # File doesn't exist or is empty - write header first
            with open(SAVE_PATH, 'w') as f:
                f.write("Date,Message,Source,IconType\n")
        
        # Append only the data lines (no header)
        with open(SAVE_PATH, 'a') as f:
            for line in data_lines:
                if line.strip():  # Only write non-empty lines
                    f.write(line.strip() + '\n')
        
        return f"CSV updated at {datetime.now()}", 200
    except Exception as e:
        return str(e), 500

# Add a new route for adding single notifications more easily
@app.route('/add-notification', methods=['POST'])
def add_notification():
    try:
        # Get individual parameters
        date = request.form.get('date', 
datetime.now().strftime('%Y-%m-%d'))
        message = request.form.get('message', '')
        source = request.form.get('source', '')
        icon_type = request.form.get('icon_type', 'Info')
        
        if not message:
            return "Message is required", 400
        
        # Ensure file exists with header
        if not os.path.exists(SAVE_PATH) or os.path.getsize(SAVE_PATH) == 
0:
            with open(SAVE_PATH, 'w') as f:
                f.write("Date,Message,Source,IconType\n")
        
        # Append the new notification
        with open(SAVE_PATH, 'a') as f:
            f.write(f"{date},{message},{source},{icon_type}\n")
        
        return f"Notification added at {datetime.now()}", 200
    except Exception as e:
        return str(e), 500

@app.route('/get-csv', methods=['GET'])
def get_csv():
    if not os.path.exists(SAVE_PATH):
        return "CSV file not found", 404
    with open(SAVE_PATH, 'r') as f:
        return f.read(), 200

# NEW ENDPOINTS BELOW:

# Serve the notification app HTML
@app.route('/')
@app.route('/notifications')
def notifications_app():
    try:
        with open(HTML_PATH, 'r') as f:
            html_content = f.read()
        return render_template_string(html_content)
    except FileNotFoundError:
        return "Notification app HTML file not found", 404
    except Exception as e:
        return f"Error loading notification app: {str(e)}", 500

# Check last modified time (efficient change detection)
@app.route('/last-modified')
def last_modified():
    try:
        if os.path.exists(SAVE_PATH):
            timestamp = os.path.getmtime(SAVE_PATH)
            return jsonify({
                'timestamp': timestamp,
                'last_modified': 
datetime.fromtimestamp(timestamp).isoformat(),
                'success': True
            })
        else:
            return jsonify({
                'error': 'CSV file not found',
                'success': False
            }), 404
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

# Get CSV info without downloading full content
@app.route('/csv-info')
def csv_info():
    try:
        if os.path.exists(SAVE_PATH):
            file_size = os.path.getsize(SAVE_PATH)
            timestamp = os.path.getmtime(SAVE_PATH)
            
            # Count lines in CSV (to know number of notifications)
            with open(SAVE_PATH, 'r') as f:
                line_count = sum(1 for line in f) - 1  # Subtract 1 for 
header
            
            return jsonify({
                'file_size': file_size,
                'timestamp': timestamp,
                'last_modified': 
datetime.fromtimestamp(timestamp).isoformat(),
                'notification_count': line_count,
                'success': True
            })
        else:
            return jsonify({
                'error': 'CSV file not found',
                'success': False
            }), 404
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

# Serve the ping sound file
@app.route('/ping_sound.mp3')
def ping_sound():
    try:
        return send_file('/home/pi/flask/ping_sound.mp3', 
mimetype='audio/mpeg')
    except FileNotFoundError:
        return "Audio file not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
