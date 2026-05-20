"""
============================================================
COLORFUL CANVAS — Flask Backend
Ultra-lightweight, optimised for Raspberry Pi Zero W
============================================================
Environment variables (set in .env or system):
  ADMIN_PASSWORD   — Password for the /admin panel (default: changeme123)
  AYRSHARE_API_KEY — Your Ayrshare API key for social media posting
  SECRET_KEY       — Flask session secret key (change before production!)
  MAIL_TO          — Email address to receive booking notifications (optional)
============================================================
"""

import os
import json
import uuid
import logging
import requests
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify, flash
)
from werkzeug.utils import secure_filename

# ============================================================
# APP CONFIGURATION
# ============================================================
app = Flask(__name__)

# Secret key — CHANGE THIS before deploying!
app.secret_key = os.environ.get('SECRET_KEY', 'colorful-canvas-secret-2026-change-me')

# Upload folder (inside static so files are servable)
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'avi'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Bookings storage (JSON file — lightweight, no DB needed on Pi Zero W)
BOOKINGS_FILE = os.path.join(app.root_path, 'bookings.json')

# Admin credentials
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'changeme123')

# Ayrshare API key for social media cross-posting
AYRSHARE_API_KEY = os.environ.get('AYRSHARE_API_KEY', '')

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# GALLERY ITEMS (placeholder — replace with real uploads)
# ============================================================
DEFAULT_GALLERY = [
    {'emoji': '🦋', 'caption': 'Butterfly Princess', 'file': None},
    {'emoji': '🦁', 'caption': 'Roaring Lion', 'file': None},
    {'emoji': '🦄', 'caption': 'Magical Unicorn', 'file': None},
    {'emoji': '🕷️', 'caption': 'Spider-Man', 'file': None},
    {'emoji': '🌸', 'caption': 'Cherry Blossom', 'file': None},
    {'emoji': '🐯', 'caption': 'Tiger Cub', 'file': None},
    {'emoji': '✨', 'caption': 'Glitter Star Tattoo', 'file': None},
    {'emoji': '🐉', 'caption': 'Dragon Fire', 'file': None},
]

# ============================================================
# HELPERS
# ============================================================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_bookings():
    """Load bookings from JSON file."""
    if not os.path.exists(BOOKINGS_FILE):
        return []
    try:
        with open(BOOKINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_booking(data):
    """Append a new booking to the JSON file."""
    bookings = load_bookings()
    data['id'] = str(uuid.uuid4())[:8]
    data['submitted_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    bookings.insert(0, data)  # newest first
    with open(BOOKINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(bookings, f, ensure_ascii=False, indent=2)
    return data


def post_to_social_media(file_path, caption, platforms):
    """
    Post media to social platforms via Ayrshare API.
    Docs: https://docs.ayrshare.com/rest-api/endpoints/post
    Returns (success: bool, message: str)
    """
    if not AYRSHARE_API_KEY:
        logger.warning('AYRSHARE_API_KEY not set — social posting skipped.')
        return False, 'Social API key not configured. File uploaded locally only.'

    try:
        # Upload file to Ayrshare media endpoint first
        with open(file_path, 'rb') as f:
            upload_resp = requests.post(
                'https://app.ayrshare.com/api/media/upload',
                headers={'Authorization': f'Bearer {AYRSHARE_API_KEY}'},
                files={'file': f},
                timeout=30
            )
        upload_data = upload_resp.json()
        if upload_resp.status_code != 200 or 'url' not in upload_data:
            return False, f'Media upload failed: {upload_data.get("message", "Unknown error")}'

        media_url = upload_data['url']

        # Determine media type
        ext = file_path.rsplit('.', 1)[-1].lower()
        is_video = ext in {'mp4', 'mov', 'avi'}

        # Post to platforms
        payload = {
            'post': caption,
            'platforms': platforms,
            'mediaUrls': [media_url],
            'isVideo': is_video,
        }
        post_resp = requests.post(
            'https://app.ayrshare.com/api/post',
            headers={
                'Authorization': f'Bearer {AYRSHARE_API_KEY}',
                'Content-Type': 'application/json',
            },
            json=payload,
            timeout=30
        )
        post_data = post_resp.json()
        if post_resp.status_code == 200:
            return True, f'Successfully posted to: {", ".join(platforms)}'
        else:
            return False, f'Post failed: {post_data.get("message", "Unknown error")}'

    except requests.exceptions.Timeout:
        return False, 'Request timed out. Check your internet connection.'
    except requests.exceptions.RequestException as e:
        return False, f'Network error: {str(e)}'
    except Exception as e:
        logger.error(f'Social posting error: {e}')
        return False, f'Unexpected error: {str(e)}'


def admin_required(f):
    """Decorator: redirect to admin login if not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin'))
        return f(*args, **kwargs)
    return decorated


# ============================================================
# ROUTES — PUBLIC PAGES
# ============================================================

@app.route('/')
def index():
    """Home page with gallery."""
    # Load uploaded gallery images if any exist
    gallery_items = list(DEFAULT_GALLERY)
    uploads_dir = app.config['UPLOAD_FOLDER']
    if os.path.exists(uploads_dir):
        uploaded = [
            f for f in os.listdir(uploads_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
        ]
        for i, fname in enumerate(sorted(uploaded)[:8]):
            if i < len(gallery_items):
                gallery_items[i]['file'] = fname
                gallery_items[i]['caption'] = fname.rsplit('.', 1)[0].replace('-', ' ').replace('_', ' ').title()

    return render_template('index.html', gallery_items=gallery_items)


@app.route('/face-painting')
def face_painting():
    return render_template('face_painting.html')


@app.route('/glitter-tattoos')
def glitter_tattoos():
    return render_template('glitter_tattoos.html')


@app.route('/sensory-friendly')
def sensory_friendly():
    return render_template('sensory_friendly.html')


@app.route('/booking', methods=['GET'])
def booking():
    success = request.args.get('success')
    error = request.args.get('error')
    return render_template('booking.html', success=success, error=error)


# ============================================================
# ROUTES — BOOKING FORM SUBMISSION
# ============================================================

@app.route('/book', methods=['POST'])
def book():
    """Handle booking form submission."""
    try:
        data = {
            'name':       request.form.get('name', '').strip(),
            'email':      request.form.get('email', '').strip(),
            'phone':      request.form.get('phone', '').strip(),
            'event_date': request.form.get('event_date', '').strip(),
            'service':    request.form.get('service', '').strip(),
            'location':   request.form.get('location', '').strip(),
            'guests':     request.form.get('guests', '').strip(),
            'details':    request.form.get('details', '').strip(),
        }

        # Basic validation
        required = ['name', 'email', 'event_date', 'service', 'location']
        if not all(data.get(k) for k in required):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'Please fill in all required fields.'})
            return redirect(url_for('booking', error=1))

        save_booking(data)
        logger.info(f'New booking from {data["name"]} for {data["event_date"]}')

        # AJAX response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
           request.content_type == 'application/x-www-form-urlencoded':
            return jsonify({'success': True})

        return redirect(url_for('booking', success=1))

    except Exception as e:
        logger.error(f'Booking error: {e}')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Server error. Please try again.'})
        return redirect(url_for('booking', error=1))


# ============================================================
# ROUTES — ADMIN PANEL
# ============================================================

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Admin panel — login and upload/blast interface."""
    logged_in = session.get('admin_logged_in', False)
    login_error = False
    flash_message = None
    flash_type = 'info'

    if request.method == 'POST':
        action = request.form.get('action')

        # --- LOGIN ---
        if action == 'login':
            password = request.form.get('password', '')
            if password == ADMIN_PASSWORD:
                session['admin_logged_in'] = True
                logged_in = True
            else:
                login_error = True

        # --- UPLOAD & BLAST ---
        elif action == 'upload' and logged_in:
            media_file = request.files.get('media')
            caption = request.form.get('caption', '').strip()
            platforms = request.form.getlist('platforms')

            if not media_file or media_file.filename == '':
                flash_message = '⚠️ Please select a file to upload.'
                flash_type = 'error'
            elif not allowed_file(media_file.filename):
                flash_message = '⚠️ File type not allowed. Use JPG, PNG, GIF, MP4 or MOV.'
                flash_type = 'error'
            elif not platforms:
                flash_message = '⚠️ Please select at least one platform.'
                flash_type = 'error'
            else:
                # Save file temporarily
                filename = secure_filename(media_file.filename)
                # Add timestamp to avoid collisions
                ts = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = ts + filename
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                media_file.save(save_path)
                logger.info(f'Admin uploaded: {filename}')

                # Post to social media
                success, message = post_to_social_media(save_path, caption, platforms)

                if success:
                    # Purge from local storage after successful post
                    try:
                        os.remove(save_path)
                        logger.info(f'Purged temp file: {filename}')
                    except OSError:
                        pass
                    flash_message = f'🚀 {message}'
                    flash_type = 'success'
                else:
                    # Keep file locally if posting failed (it will appear in gallery)
                    flash_message = f'📁 File saved locally. Social posting: {message}'
                    flash_type = 'info'

    bookings = load_bookings()[:10] if logged_in else []

    return render_template(
        'admin.html',
        logged_in=logged_in,
        login_error=login_error,
        flash_message=flash_message,
        flash_type=flash_type,
        bookings=bookings,
    )


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin'))


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return render_template('base.html'), 404


@app.errorhandler(413)
def file_too_large(e):
    return jsonify({'success': False, 'message': 'File too large. Maximum size is 50 MB.'}), 413


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Get host and port from environment (useful for Pi deployment)
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'

    logger.info(f'Starting Colorful Canvas on {host}:{port}')
    app.run(host=host, port=port, debug=debug, threaded=True)
