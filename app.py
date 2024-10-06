from flask import Flask, render_template, request, jsonify
import mock_data
from config import TIME_INTERVAL

app = Flask(__name__)

# Mock data retrieval, replace with real database query
def get_data():
    return mock_data.get_mock_data()

# Dashboard route
@app.route('/')
def dashboard():
    user_name = "Josh"  # Replace with dynamic user retrieval if needed
    return render_template('dashboard.html', user_name=user_name, time_interval=TIME_INTERVAL)

# Endpoint to update data fetch interval
@app.route('/update_interval', methods=['POST'])
def update_interval():
    global TIME_INTERVAL
    new_interval = request.json.get('interval')
    TIME_INTERVAL = new_interval
    return jsonify({'success': True, 'interval': TIME_INTERVAL})

# Endpoint to fetch data
@app.route('/get_data')
def fetch_data():
    data = get_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
