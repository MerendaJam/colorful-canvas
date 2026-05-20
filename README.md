# 🎨 Colorful Canvas — Face Painting Website

**Professional multi-page website for face painting & glitter tattoos.**
Ultra-lightweight Flask app, optimised for **Raspberry Pi Zero W** (512 MB RAM).

---

## 📁 Project Structure

```
colorful_canvas/
├── app.py                  ← Flask backend (all routes & logic)
├── requirements.txt        ← Python dependencies
├── bookings.json           ← Auto-created: stores booking requests
├── .env.example            ← Copy to .env and fill in your values
├── static/
│   ├── css/style.css       ← Global stylesheet (sales-psychology colors)
│   ├── js/main.js          ← Lightweight vanilla JS
│   └── uploads/            ← Gallery images & temp social media uploads
└── templates/
    ├── base.html           ← Shared header, nav & footer
    ├── index.html          ← Home page
    ├── face_painting.html  ← Face Painting service page
    ├── glitter_tattoos.html← Glitter Tattoos service page
    ├── sensory_friendly.html← Sensory-Friendly packages page
    ├── booking.html        ← Pricing & Booking form
    └── admin.html          ← Admin panel (password protected)
```

---

## 🚀 Raspberry Pi Zero W — Quick Setup

### Step 1: Install Python & pip (if not already installed)
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip -y
```

### Step 2: Copy project to your Pi
```bash
# On your computer, copy the zip to the Pi:
scp colorful_canvas.zip pi@raspberrypi.local:/home/pi/

# On the Pi:
cd /home/pi
unzip colorful_canvas.zip
cd colorful_canvas
```

### Step 3: Install dependencies
```bash
pip3 install -r requirements.txt
```

### Step 4: Set environment variables
```bash
cp .env.example .env
nano .env
# Fill in your ADMIN_PASSWORD, SECRET_KEY, and optionally AYRSHARE_API_KEY
```

### Step 5: Run the app
```bash
python3 app.py
```

The website will be available at:
- **On your local network:** `http://raspberrypi.local:5000` or `http://<PI_IP>:5000`
- **Admin panel:** `http://<PI_IP>:5000/admin`

---

## 🔄 Auto-start on Boot (systemd service)

Create a systemd service so the website starts automatically when the Pi boots:

```bash
sudo nano /etc/systemd/system/colorfulcanvas.service
```

Paste this content:
```ini
[Unit]
Description=Colorful Canvas Face Painting Website
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/colorful_canvas
Environment="ADMIN_PASSWORD=your_password_here"
Environment="SECRET_KEY=your_secret_key_here"
Environment="AYRSHARE_API_KEY=your_ayrshare_key_here"
ExecStart=/usr/bin/python3 /home/pi/colorful_canvas/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable colorfulcanvas
sudo systemctl start colorfulcanvas
sudo systemctl status colorfulcanvas
```

---

## 🌐 Access from the Internet (Optional)

To make the site accessible from outside your home network, use **ngrok** (free):

```bash
# Install ngrok on Pi
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Run (get your token from ngrok.com — free account)
ngrok http 5000
```

---

## 📱 Social Media Posting (Admin Panel)

The admin panel at `/admin` lets you upload photos/videos and post them to all your social media platforms at once.

**Supported via Ayrshare API (free tier available):**
- Instagram
- Facebook
- TikTok
- X / Twitter

**Setup:**
1. Create a free account at [ayrshare.com](https://www.ayrshare.com)
2. Connect your social media accounts in the Ayrshare dashboard
3. Copy your API key
4. Set `AYRSHARE_API_KEY=your_key` in your `.env` file

---

## 🔐 Admin Panel

- **URL:** `/admin`
- **Default password:** `changeme123`
- **Change it:** Set `ADMIN_PASSWORD=yourpassword` in `.env`

---

## 🎨 Customisation

### Change business details:
Edit `templates/base.html` — update the phone number, email, and address in the footer.

### Add your own gallery photos:
Drop `.jpg`, `.png` or `.webp` files into `static/uploads/` — they will automatically appear in the home page gallery.

### Change prices:
Edit `templates/booking.html` — find the pricing cards section.

### Change the business name:
Search and replace `Colorful Canvas` across all template files.

---

## 🛡️ Security Notes

- Change `ADMIN_PASSWORD` and `SECRET_KEY` before going live
- The site runs on HTTP by default — for HTTPS, use nginx as a reverse proxy with Let's Encrypt
- Booking data is stored in `bookings.json` — back this up regularly

---

## 📞 Support

Built with ❤️ for Raspberry Pi Zero W. Tested on Python 3.9+.
