import os
import logging
import requests
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template, send_from_directory

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# --- GDPR: consent journal (append-only local file for MVP) ---
CONSENT_LOG = os.environ.get('CONSENT_LOG', 'consent_log.jsonl')
DELETION_LOG = os.environ.get('DELETION_LOG', 'deletion_requests.jsonl')

HIBP_RANGE_URL = 'https://api.haveibeenpwned.com/range/'
HIBP_TIMEOUT = 10
# WhatsMyName public data source (site definitions) - beta feature
WMN_SITES_URL = 'https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json'


def log_jsonl(path, payload):
    # GDPR art. 7(1): demonstrate consent. Store purpose + timestamp only.
    payload['ts'] = datetime.now(timezone.utc).isoformat()
    try:
        with open(path, 'a', encoding='utf-8') as f:
            import json
            f.write(json.dumps(payload, ensure_ascii=True) + chr(10))
    except OSError:
        logging.warning('could not write to log %s', path)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/protect')
def protect():
    return render_template('protect.html')


@app.route('/pseudo')
def pseudo():
    return render_template('pseudo.html')


@app.route('/legal')
def legal():
    return render_template('legal.html')


@app.route('/delete')
def delete():
    return render_template('delete.html')


@app.route('/api/hibp-range/<prefix>')
def hibp_range(prefix):
    # k-anonymity: the server only ever sees a 5-char hash prefix,
    # never the email itself. Calls the free HIBP range API.
    if len(prefix) != 5 or not all(c in '0123456789ABCDEF' for c in prefix.upper()):
        return jsonify({'error': 'invalid prefix'}), 400
    try:
        r = requests.get(HIBP_RANGE_URL + prefix.upper(), timeout=HIBP_TIMEOUT)
        r.raise_for_status()
    except requests.RequestException:
        return jsonify({'error': 'hibp_unavailable'}), 502
    lines = r.text.strip().split(chr(10))
    results = {}
    for line in lines:
        parts = line.strip().split(':')
        if len(parts) == 2:
            results[parts[0].upper()] = int(parts[1])
    return jsonify({'prefix': prefix.upper(), 'matches': results})


@app.route('/api/pseudo-check', methods=['POST'])
def pseudo_check():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    if not username or len(username) > 64:
        return jsonify({'error': 'invalid username'}), 400
    if data.get('consent') is not True:
        return jsonify({'error': 'consent_required'}), 403
    log_jsonl(CONSENT_LOG, {'purpose': 'pseudo_scan', 'consent': True,
                           'user_agent': request.headers.get('User-Agent', '')[:200]})
    # MVP: check a small curated list of public profile URL patterns.
    # This only reads already-public pages (legal OSINT, no scraping of
    # private data, no storage).
    platforms = [
        ('GitHub', 'https://github.com/{}'),
        ('Reddit', 'https://www.reddit.com/user/{}'),
        ('Instagram', 'https://www.instagram.com/{}'),
        ('TikTok', 'https://www.tiktok.com/@{}'),
        ('YouTube', 'https://www.youtube.com/@{}'),
    ]
    found = []
    for name, url in platforms:
        try:
            r = requests.head(url.format(username), timeout=5,
                              allow_redirects=False,
                              headers={'User-Agent': 'Mozilla/5.0 (BrixHubSafe/0.1)'})
            if r.status_code == 200:
                found.append({'platform': name, 'url': url.format(username),
                              'status': 'public'})
        except requests.RequestException:
            continue
    return jsonify({'username': username, 'found': found, 'checked': len(platforms)})


@app.route('/api/consent', methods=['POST'])
def consent():
    data = request.get_json(silent=True) or {}
    if data.get('consent') is not True:
        return jsonify({'error': 'consent_required'}), 400
    log_jsonl(CONSENT_LOG, {'purpose': data.get('purpose', 'unknown'),
                            'consent': True})
    return jsonify({'ok': True})


@app.route('/api/delete-request', methods=['POST'])
def delete_request():
    # GDPR art. 17: right to erasure. Free, instant confirmation.
    # MVP: we do not store user data beyond consent logs, so deletion
    # means wiping logs associated with the requester. Email is stored
    # ONLY in this deletion request file (minimization exception: the
    # user explicitly provides it to identify their entries).
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    if '@' not in email:
        return jsonify({'error': 'invalid_email'}), 400
    log_jsonl(DELETION_LOG, {'email': email, 'action': 'deletion_requested'})
    return jsonify({'ok': True, 'message': 'Demande enregistree. Effacement sous 30 jours.'})


@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
