from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import os
import json
from datetime import datetime
import threading

app = Flask(__name__)
app.config['RESULTS_FOLDER'] = 'results'

# Store active searches
active_searches = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    usernames = data.get('usernames', '').strip().split()
    options = data.get('options', {})

    if not usernames:
        return jsonify({'error': 'Please provide at least one username'}), 400

    # Generate unique search ID
    search_id = f"search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Build sherlock command
    cmd = ['sherlock'] + usernames

    if options.get('timeout'):
        cmd.extend(['--timeout', str(options['timeout'])])

    if options.get('csv'):
        cmd.append('--csv')

    if options.get('xlsx'):
        cmd.append('--xlsx')

    if options.get('nsfw'):
        cmd.append('--nsfw')

    if options.get('sites'):
        for site in options['sites']:
            cmd.extend(['--site', site])

    if options.get('proxy'):
        cmd.extend(['--proxy', options['proxy']])

    # Output folder for results
    output_folder = os.path.join(app.config['RESULTS_FOLDER'], search_id)
    os.makedirs(output_folder, exist_ok=True)
    cmd.extend(['--folderoutput', output_folder])

    # Run search in background
    def run_search():
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            active_searches[search_id] = {
                'status': 'completed',
                'output': result.stdout,
                'error': result.stderr,
                'folder': output_folder
            }
        except subprocess.TimeoutExpired:
            active_searches[search_id] = {
                'status': 'timeout',
                'error': 'Search timed out after 5 minutes'
            }
        except Exception as e:
            active_searches[search_id] = {
                'status': 'error',
                'error': str(e)
            }

    active_searches[search_id] = {'status': 'running'}
    thread = threading.Thread(target=run_search)
    thread.start()

    return jsonify({
        'search_id': search_id,
        'message': 'Search started',
        'usernames': usernames
    })

@app.route('/status/<search_id>')
def get_status(search_id):
    if search_id not in active_searches:
        return jsonify({'error': 'Search not found'}), 404

    search_info = active_searches[search_id]

    if search_info['status'] == 'completed':
        # Parse results
        results = parse_results(search_info['output'])
        return jsonify({
            'status': 'completed',
            'results': results,
            'raw_output': search_info['output'],
            'folder': search_info['folder']
        })

    return jsonify(search_info)

def parse_results(output):
    """Parse sherlock output to extract found accounts"""
    results = {
        'found': [],
        'not_found': []
    }

    lines = output.split('\n')
    for line in lines:
        if line.startswith('[+]'):
            # Found account
            parts = line[4:].split(': ', 1)
            if len(parts) == 2:
                results['found'].append({
                    'site': parts[0].strip(),
                    'url': parts[1].strip()
                })
        elif line.startswith('[-]'):
            # Not found
            site = line[4:].strip()
            results['not_found'].append(site)

    return results

@app.route('/download/<search_id>/<filename>')
def download_file(search_id, filename):
    if search_id not in active_searches:
        return jsonify({'error': 'Search not found'}), 404

    folder = active_searches[search_id].get('folder')
    if not folder:
        return jsonify({'error': 'Results folder not found'}), 404

    file_path = os.path.join(folder, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)

    return jsonify({'error': 'File not found'}), 404

@app.route('/list_files/<search_id>')
def list_files(search_id):
    if search_id not in active_searches:
        return jsonify({'error': 'Search not found'}), 404

    folder = active_searches[search_id].get('folder')
    if not folder or not os.path.exists(folder):
        return jsonify({'files': []})

    files = os.listdir(folder)
    return jsonify({'files': files})

if __name__ == '__main__':
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
    print("Starting Sherlock Web Interface...")
    print("Open your browser and go to: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
