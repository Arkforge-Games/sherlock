# Sherlock Web Interface

A modern, user-friendly web interface for the Sherlock username search tool.

## Features

- **Easy-to-use Interface**: No command line required
- **Real-time Search**: Watch results appear as the search progresses
- **Multiple Export Formats**: Download results as CSV, XLSX, or TXT
- **Advanced Options**: Configure timeout, specific sites, proxy settings, and more
- **Beautiful Results Display**: Organized tabs for found accounts, not found sites, and raw output
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Quick Start

1. Make sure you've installed Sherlock and its dependencies
2. Run the startup script:
   ```bash
   ./start_web.sh
   ```
   Or manually:
   ```bash
   source venv/bin/activate
   cd web_interface
   python app.py
   ```

3. Open your browser and go to: **http://127.0.0.1:5000**

## How to Use

1. **Enter Username(s)**: Type one or more usernames separated by spaces
2. **Configure Options** (optional):
   - Choose export formats (CSV, XLSX)
   - Set timeout duration
   - Specify particular sites to search
   - Include NSFW sites if needed
   - Configure proxy settings
3. **Click "Start Search"**: The search will begin and results will appear automatically
4. **View Results**:
   - See summary of found/not found accounts
   - Browse found accounts with clickable links
   - Download exported files
   - View raw terminal output

## Search Options

- **Export as CSV**: Creates a comma-separated values file
- **Export as Excel**: Creates an XLSX spreadsheet
- **Include NSFW sites**: Searches adult content platforms
- **Timeout**: Maximum seconds to wait for each site (default: 60)
- **Specific Sites**: Limit search to particular platforms (e.g., GitHub, Twitter)
- **Proxy**: Route requests through a proxy server

## Tips

- Results are saved in the `web_interface/results` folder
- Each search gets a unique ID and folder
- Downloaded files include timestamps for easy tracking
- Use specific sites option to speed up searches when you know where to look

## Technical Details

- **Backend**: Flask (Python)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Architecture**: Asynchronous search with status polling
- **Port**: 5000 (configurable in app.py)
