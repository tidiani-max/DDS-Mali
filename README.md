# Diawara Digital & Software – Django Website

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run migrations
```bash
python manage.py migrate
```

### 3. Load initial data (projects, scholarships, webinars, admin user)
```bash
python manage.py setup_site
```

### 4. Run the development server
```bash
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

### 5. Access Admin Panel
Go to http://127.0.0.1:8000/admin/
- Username: `admin`
- Password: `dds2026admin`

---

## 📁 Project Structure
```
dds_mali/
├── core/           → Home page, Projects, Testimonials
├── scholarships/   → Scholarship listings + Application forms
├── webinars/       → Webinar listings + Registration forms
├── contact/        → Contact form
├── templates/      → All HTML templates
├── static/         → CSS, JS, images
├── media/          → Uploaded files + site images
└── manage.py
```

## 🌐 Deploy to Production (Railway / Render)

1. Set `DEBUG=False` in settings.py
2. Set `SECRET_KEY` to a secure random string
3. Run `python manage.py collectstatic`
4. Use gunicorn: `gunicorn dds_mali.wsgi:application`

## ✉️ Contact
contact@dds-mali.com
