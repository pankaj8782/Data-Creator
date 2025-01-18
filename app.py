from flask import Flask, render_template, request, jsonify, send_file
from faker import Faker
import pandas as pd
import random
from datetime import datetime, timedelta
import os
import numpy as np
from flask_socketio import SocketIO, emit


def clear_csv_files_in_static_folder():
    static_folder = 'static'
    
    if os.path.exists(static_folder):
        for root, dirs, files in os.walk(static_folder):
            for file in files:
                if file.endswith('.csv'):
                    file_path = os.path.join(root, file)
                    os.remove(file_path)

clear_csv_files_in_static_folder()


np.random.seed(1500)
app = Flask(__name__)
faker = Faker()
socketio = SocketIO(app, cors_allowed_origins="*")

# Track unique numbers used
unique_numbers_used = set()
def generate_unique_number(min_val, max_val):
    while True:
        new_number = random.randint(min_val, max_val)
        if new_number not in unique_numbers_used:
            unique_numbers_used.add(new_number)
            return new_number

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data_name = request.form['data_name']
        num_columns = int(request.form['num_columns'])
        num_rows = int(request.form['num_rows'])
        return render_template('column_form.html', data_name=data_name, num_columns=num_columns, num_rows=num_rows, column_form=range(num_columns))
    return render_template('index.html')

@app.route('/generate_data', methods=['POST'])
def generate_data():
    try:
        data_name = request.form['data_name']
        num_columns = int(request.form['num_columns'])
        num_rows = int(request.form['num_rows'])

        # Initialize column configuration
        columns = []
        column_types = []
        unique_flags = []
        custom_types = []
        min_numbers = []
        max_numbers = []
        min_dates = []
        max_dates = []
        start_datetimes = []
        end_datetimes = []

        # Collect column configurations
        for col_id in range(num_columns):
            col_name = request.form[f'col_name_{col_id}']
            col_type = request.form[f'col_type_{col_id}']
            is_unique = request.form.get(f'unique_value_{col_id}') == 'on'
            custom_type = request.form.get(f'custom_type_{col_id}', '').split(',')
            min_number = request.form.get(f'min_number_{col_id}', None)
            max_number = request.form.get(f'max_number_{col_id}', None)
            min_date = request.form.get(f'min_date_{col_id}', None)
            max_date = request.form.get(f'max_date_{col_id}', None)
            start_datetime = request.form.get(f'start_datetime_{col_id}', None)
            end_datetime = request.form.get(f'end_datetime_{col_id}', None)

            columns.append(col_name)
            column_types.append(col_type)
            unique_flags.append(is_unique)
            custom_types.append(custom_type)
            min_numbers.append(min_number)
            max_numbers.append(max_number)
            min_dates.append(min_date)
            max_dates.append(max_date)
            start_datetimes.append(start_datetime)
            end_datetimes.append(end_datetime)

        # Generate data rows
        total_work = num_rows
        progress_interval = max(1, total_work // 100)  # Update progress every 1%

        # Emit initial progress (0%)
        socketio.emit('progress', {'progress': 0}, namespace='/')

        data = []
        for i in range(num_rows):
            row = {}
            for col_id, col_name in enumerate(columns):
                col_type = column_types[col_id]
                is_unique = unique_flags[col_id]
                custom_type = custom_types[col_id]
                
                if is_unique:
                    if col_type == 'number':
                        min_val = int(min_numbers[col_id]) if min_numbers[col_id] else 1
                        max_val = int(max_numbers[col_id]) if max_numbers[col_id] else 1000
                        row[col_name] = generate_unique_number(min_val, max_val)
                    elif col_type in ['address', 'email', 'name', 'phone_number', 'city', 'company', 'text', 'uuid4', 'boolean', 'json', 'ipv4', 'ipv6', 'url', 'latitude', 'longitude', 'credit_card_number', 'credit_card_expire', 'currency_name', 'job', 'file_name', 'street_address', 'postcode', 'state', 'state_abbr', 'country', 'country_code', 'color_name', 'paragraph', 'sentence', 'word', 'safe_email', 'domain_name', 'domain_word', 'locale', 'mime_type', 'slug']:
                        row[col_name] = getattr(faker.unique, col_type)()
                else:
                    if col_type == 'number':
                        min_val = int(min_numbers[col_id]) if min_numbers[col_id] else 1
                        max_val = int(max_numbers[col_id]) if max_numbers[col_id] else 1000
                        row[col_name] = random.randint(min_val, max_val+1)
                    elif col_type in ['address', 'email', 'name', 'phone_number', 'city', 'company', 'text', 'uuid4', 'boolean', 'json', 'ipv4', 'ipv6', 'url', 'latitude', 'longitude', 'credit_card_number', 'credit_card_expire', 'currency_name', 'job', 'file_name', 'street_address', 'postcode', 'state', 'state_abbr', 'country', 'country_code', 'color_name', 'paragraph', 'sentence', 'word', 'safe_email', 'domain_name', 'domain_word', 'locale', 'mime_type', 'slug']:
                        row[col_name] = getattr(faker, col_type)()

                if col_type == 'custom':
                    custom_values = custom_type
                    row[col_name] = random.choice(custom_values)

                if col_type == 'date':
                    min_date = datetime.strptime(min_dates[col_id], "%Y-%m-%d") if min_dates[col_id] else datetime.today()
                    max_date = datetime.strptime(max_dates[col_id], "%Y-%m-%d") if max_dates[col_id] else datetime.today()
                    delta = max_date - min_date
                    random_days = random.randint(0, delta.days)
                    row[col_name] = (min_date + timedelta(days=random_days)).strftime('%Y-%m-%d')

                if col_type == 'datetime':
                    start = datetime.strptime(start_datetimes[col_id], "%Y-%m-%dT%H:%M") if start_datetimes[col_id] else datetime.now()
                    end = datetime.strptime(end_datetimes[col_id], "%Y-%m-%dT%H:%M") if end_datetimes[col_id] else datetime.now()
                    delta = end - start
                    random_minutes = random.randint(0, int(delta.total_seconds() // 60))
                    row[col_name] = (start + timedelta(minutes=random_minutes)).strftime('%Y-%m-%d %H:%M:%S')

            data.append(row)
            # Emit progress every 1%
            if (i + 1) % progress_interval == 0 or i == num_rows - 1:
                progress = int(((i + 1) / total_work) * 100)
                socketio.emit('progress', {'progress': progress}, namespace='/')

        # Save data to CSV
        df = pd.DataFrame(data)
        os.makedirs('static', exist_ok=True)
        file_path = f'static/{data_name}_data.csv'
        df.to_csv(file_path, index=False)

        return jsonify({'file_path': file_path})

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/download_file/<filename>', methods=['GET'])
def download_file(filename):
    file_path = f'static/{filename}'
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    socketio.run(app, debug=True)