from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import os
import json
from datetime import datetime
import threading
import requests
from urllib.parse import quote

app = Flask(__name__)
app.config['RESULTS_FOLDER'] = 'results'

# Store active searches
active_searches = {}

@app.route('/')
def index():
    return render_template('index.html')


def generate_username_variations(full_name):
    """Generate common username variations from a full name"""
    # Clean and split the name
    name_parts = full_name.lower().strip().split()

    if len(name_parts) == 0:
        return []

    variations = set()

    if len(name_parts) == 1:
        # Single name (could be username already)
        variations.add(name_parts[0])
    elif len(name_parts) == 2:
        first, last = name_parts[0], name_parts[1]
        # Common patterns for first + last name
        variations.add(f"{first}{last}")           # johnsmith
        variations.add(f"{first}_{last}")          # john_smith
        variations.add(f"{first}.{last}")          # john.smith
        variations.add(f"{first}-{last}")          # john-smith
        variations.add(f"{first[0]}{last}")        # jsmith
        variations.add(f"{first}{last[0]}")        # johns
        variations.add(f"{last}{first}")           # smithjohn
        variations.add(f"{last}_{first}")          # smith_john
        variations.add(f"{last}.{first}")          # smith.john
        variations.add(f"{first}{last}123")        # johnsmith123
        variations.add(f"{first}_{last}123")       # john_smith123
    elif len(name_parts) >= 3:
        # Handle middle names
        first, middle, last = name_parts[0], name_parts[1], name_parts[-1]
        variations.add(f"{first}{last}")           # johnsmith
        variations.add(f"{first}_{last}")          # john_smith
        variations.add(f"{first}.{last}")          # john.smith
        variations.add(f"{first}{middle[0]}{last}") # johnmsmith
        variations.add(f"{first[0]}{middle[0]}{last}") # jmsmith
        variations.add(f"{first}_{middle}_{last}") # john_michael_smith

    return list(variations)

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    search_mode = data.get('mode', 'username')  # 'username' or 'name'
    options = data.get('options', {})

    usernames = []

    if search_mode == 'name':
        # Generate username variations from full name
        full_name = data.get('fullname', '').strip()
        if not full_name:
            return jsonify({'error': 'Please provide a full name'}), 400
        usernames = generate_username_variations(full_name)
        if not usernames:
            return jsonify({'error': 'Could not generate usernames from name'}), 400
    else:
        # Direct username search
        usernames = data.get('usernames', '').strip().split()
        if not usernames:
            return jsonify({'error': 'Please provide at least one username'}), 400

    if not usernames:
        return jsonify({'error': 'Please provide at least one username'}), 400

    # Generate unique search ID
    search_id = f"search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Build sherlock command
    cmd = ['sherlock'] + usernames

    # Add verbose flag to see each site being checked
    cmd.append('--verbose')

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
            # Use Popen for real-time output streaming
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            output_lines = []

            # Read output in real-time
            for line in process.stdout:
                output_lines.append(line)
                # Update live results
                active_searches[search_id] = {
                    'status': 'running',
                    'output': ''.join(output_lines),
                    'folder': output_folder
                }

            # Wait for process to complete
            process.wait()
            stderr_output = process.stderr.read()

            active_searches[search_id] = {
                'status': 'completed',
                'output': ''.join(output_lines),
                'error': stderr_output,
                'folder': output_folder
            }
        except Exception as e:
            active_searches[search_id] = {
                'status': 'error',
                'error': str(e),
                'folder': output_folder
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

    # Parse results even if still running to show live updates
    if 'output' in search_info and search_info['output']:
        results = parse_results(search_info['output'])
        response = {
            'status': search_info['status'],
            'results': results,
            'raw_output': search_info['output'],
            'folder': search_info.get('folder', '')
        }

        return jsonify(response)

    return jsonify(search_info)

def parse_results(output):
    """Parse sherlock output to extract found accounts"""
    results = {
        'found': [],
        'not_found': [],
        'checking': [],
        'total_checked': 0
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
                results['total_checked'] += 1
        elif line.startswith('[-]'):
            # Not found
            site = line[4:].strip()
            results['not_found'].append(site)
            results['total_checked'] += 1
        elif line.startswith('[*]'):
            # Currently checking (verbose mode)
            site = line[4:].strip()
            if site:
                results['checking'].append(site)

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
    print("Open your browser and go to: http://0.0.0.0:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

