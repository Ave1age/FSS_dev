import os
import socket
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash, jsonify

app = Flask(__name__)
SHARED_FOLDER = 'shared_files'
app.config['UPLOAD_FOLDER'] = SHARED_FOLDER
app.secret_key = 'super_secret_key'  # Needed for flashing messages

# Ensure shared folder exists
if not os.path.exists(SHARED_FOLDER):
    os.makedirs(SHARED_FOLDER)

def get_all_ips():
    ip_list = []
    try:
        # Get all network interfaces
        hostname = socket.gethostname()
        # Get all IP addresses associated with the hostname
        # This usually returns the main IP, but we can try to get more
        local_ips = socket.gethostbyname_ex(hostname)[2]
        for ip in local_ips:
            if not ip.startswith('127.'):
                ip_list.append(ip)
    except Exception:
        pass
    
    # Try the connect method as a backup/primary way to get the "route to internet" IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        primary_ip = s.getsockname()[0]
        s.close()
        if primary_ip not in ip_list:
            ip_list.insert(0, primary_ip)
    except Exception:
        pass

    if not ip_list:
        ip_list = ['127.0.0.1']
    return ip_list

@app.route('/')
@app.route('/index.html')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    # Filter out hidden files if necessary, or just list all
    files = [f for f in files if not f.startswith('.')]
    # Get the primary IP (first one) for display, but user can access via any
    ips = get_all_ips()
    ip_addr = ips[0]
    port = 5000
    return render_template('index.html', files=files, ip_addr=ip_addr, port=port)

@app.errorhandler(404)
def page_not_found(e):
    # If a 404 occurs, redirect to the home page
    # This handles cases where users might type /index.html or other paths
    return redirect(url_for('index'))

@app.route('/files')
def list_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    # Filter out hidden files
    files = [f for f in files if not f.startswith('.')]
    return jsonify(files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件部分'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400
    
    if file:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'success': True, 'filename': filename})

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<path:filename>', methods=['POST'])
def delete_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'success': True, 'message': '文件删除成功'})
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    host_ip = '0.0.0.0'
    port = 5000
    local_ips = get_all_ips()
    
    print("\n" + "="*50)
    print(f" * 局域网文件共享服务已启动")
    print(f" * 服务端口: {port}")
    print(f" * 可用的局域网 IP 地址:")
    for ip in local_ips:
        print(f"   -> http://{ip}:{port}")
    print("-" * 50)
    print(" [!] 注意: 如果无法访问，请检查 Windows 防火墙设置")
    print("     确保允许 'python' 或 'app.py' 通过防火墙")
    print("     (或者暂时关闭防火墙进行测试)")
    print("="*50 + "\n")
    
    app.run(host=host_ip, port=port, debug=False)
