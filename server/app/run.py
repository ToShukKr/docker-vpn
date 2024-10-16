import os
import json
import random
import string
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify

app = Flask(__name__)
app.secret_key = os.urandom(12)

SESSION_TOKEN = ''.join(random.choices(string.ascii_letters + string.digits, k=256))
USER_CREDENTIALS = {'username': os.getenv("UI_ADMIN_LOGIN"), 'password': os.getenv("UI_ADMIN_PASS")}

@app.route('/')
def index():
    if 'logged_in' in session and session['logged_in']:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

@app.route('/api/v1/get-clients', methods=['POST'])
def get_clients():
    session_token = request.json.get('session_token')
    if session_token != SESSION_TOKEN or not session_token:
        return jsonify({'error': 'Missing or invalid session_token'}), 400
    users = []
    for idx, filename in enumerate(os.listdir(os.getenv("CLIENTS_CONFIG_DIR")), start=1):
        file_path = os.path.join(os.getenv("CLIENTS_CONFIG_DIR"), filename)
        with open(file_path, 'r') as file:
            content = file.read().strip()
            ip_address = content.split()[1]
        file_stat = os.stat(file_path)
        creation_date = datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d')
        response = subprocess.run(['ping', '-c', '1', '-W', '1', ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status = 'active' if response.returncode == 0 else 'inactive'
        user_data = {
            "id": idx,
            "name": filename,
            "ip": ip_address,
            "date": creation_date,
            "status": status
        }
        users.append(user_data)
    return jsonify(users)

@app.route('/api/v1/get-client-config', methods=['POST'])
def get_client_config():
    session_token = request.json.get('session_token')
    config_name = request.json.get('config_name')
    if session_token != SESSION_TOKEN or not session_token:
        return jsonify({'error': 'Missing or invalid session_token'}), 400
    if not config_name:
        return jsonify({'error': 'Missing config_name'}), 400
    file_path = os.path.join(os.getenv("OVPN_CONFIG_DIR"), f"{config_name}.ovpn")
    if not os.path.exists(file_path):
        return jsonify({'error': 'Config file not found'}), 404
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return jsonify({'config_name': config_name, 'content': content})
    except Exception as e:
        return jsonify({'error': f'Failed to read config: {str(e)}'}), 500


@app.route('/api/v1/delete-client', methods=['POST'])
def delete_client():
    session_token = request.json.get('session_token')
    config_name = request.json.get('config_name')
    if session_token != SESSION_TOKEN or not session_token:
        return jsonify({'error': 'Missing or invalid session_token'}), 400
    if not config_name:
        return jsonify({'error': 'Missing config_name'}), 400

    FILES_TO_REMOVE = [
        f'{os.getenv("EASYRSA_WORKDIR")}/pki/reqs/{config_name}.req',
        f'{os.getenv("EASYRSA_WORKDIR")}/pki/private/{config_name}.key',
        f'{os.getenv("EASYRSA_WORKDIR")}/pki/issued/{config_name}.crt',
        os.path.join(os.getenv("OVPN_CONFIG_DIR"), f"{config_name}.ovpn"),
        os.path.join(os.getenv("CLIENTS_CONFIG_DIR"), f"{config_name}")
    ]
    for file in FILES_TO_REMOVE:
        if os.path.exists(file):
            print(file, flush=True)
            os.remove(file)
    return jsonify({'message': f'Successfully removed {config_name}'}), 200


@app.route('/api/v1/check-ip', methods=['POST'])
def check_ip():
    session_token = request.json.get('session_token')
    ip_address = request.json.get('ip_address')
    client_name = request.json.get('name')
    if session_token != SESSION_TOKEN or not session_token:
        return jsonify({'status': False, 'message': 'Missing or invalid session_token'}), 400
    if not ip_address or not client_name:
        return jsonify({'status': False, 'message': 'IP address or client name is missing'}), 400
    ALL_IPS = []
    ALL_NAMES = []
    for idx, filename in enumerate(os.listdir(os.getenv("CLIENTS_CONFIG_DIR")), start=1):
        file_path = os.path.join(os.getenv("CLIENTS_CONFIG_DIR"), filename)
        with open(file_path, 'r') as file:
            content = file.read().strip()
            ALL_IPS.append(content.split()[1])
            ALL_NAMES.append(filename)
    if ip_address in ALL_IPS:
        return jsonify({'status': False, 'message': f'IP {ip_address} is in use'}), 200

    if client_name in ALL_NAMES:
        return jsonify({'status': False, 'message': f'Name {client_name} is in use'}), 200

    try:
        response = subprocess.run(['ping', '-c', '1', '-W', '1', ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if response.returncode == 0:
            return jsonify({'status': False, 'message': f'IP {ip_address} is in use'}), 200
        else:
            return jsonify({'status': True, 'message': f'IP {ip_address} is free'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/add-client', methods=['POST'])
def add_client():
    session_token = request.json.get('session_token')
    ip_address = request.json.get('ip_address')
    client_name = request.json.get('name')
    if session_token != SESSION_TOKEN or not session_token:
        return jsonify({'status': False, 'message': 'Missing or invalid session_token'}), 400
    if not ip_address or not client_name:
        return jsonify({'status': False, 'message': 'IP address or client name is missing'}), 400
    response = subprocess.run(['client-mgr', 'add', client_name, ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if response.returncode == 0:
        return jsonify({'status': True, 'message': f'Client {client_name} successfully created'}), 200
    else:
        return jsonify({'status': False, 'message': f'Failed to create {client_name}'}), 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USER_CREDENTIALS['username'] and password == USER_CREDENTIALS['password']:
            session['logged_in'] = True
            response = make_response(redirect(url_for('index')))
            response.set_cookie('session_token', SESSION_TOKEN)
            return response
        else:
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    response = make_response(redirect(url_for('login')))
    response.set_cookie('session_token', '', expires=0)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("UI_PORT", 5555)), debug=True)
