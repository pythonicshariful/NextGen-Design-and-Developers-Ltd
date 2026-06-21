import os
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import LoginManager
from models import db, AdminUser, SiteSetting, PageSEO, Testimonial, Project


def create_app():
    app = Flask(
        __name__,
        static_folder='assets',
        static_url_path='/assets'
    )

    # ── Configuration ─────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'nddl-super-secret-key-change-me-2024')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ── Extensions ────────────────────────────────────────────────────────────
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'admin_bp.login'
    login_manager.login_message = 'Please log in to access the admin area.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(int(user_id))

    # ── Admin Blueprint ────────────────────────────────────────────────────────
    from admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # ── Serve uploaded files ───────────────────────────────────────────────────
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # ── Helper ────────────────────────────────────────────────────────────────
    def ctx(page_slug):
        """Return common template context for a given page."""
        return {
            'settings': SiteSetting.get_all_as_dict(),
            'seo': PageSEO.for_page(page_slug),
        }

    # ── Public Routes ─────────────────────────────────────────────────────────
    @app.route('/')
    def index():
        c = ctx('home')
        c['testimonials'] = (Testimonial.query
                             .filter_by(is_active=True)
                             .order_by(Testimonial.sort_order, Testimonial.id)
                             .all())
        c['projects'] = (Project.query
                         .filter_by(is_active=True)
                         .order_by(Project.sort_order, Project.id)
                         .all())
        return render_template('index.html', **c)

    @app.route('/about')
    def about():
        return render_template('about.html', **ctx('about'))

    @app.route('/properties')
    def properties():
        c = ctx('properties')
        c['projects'] = (Project.query
                         .filter_by(is_active=True)
                         .order_by(Project.sort_order, Project.id)
                         .all())
        return render_template('properties.html', **c)

    @app.route('/landowner')
    def landowner():
        return render_template('landowner.html', **ctx('landowner'))

    @app.route('/construction-status')
    def construction_status():
        return render_template('construction-status.html', **ctx('construction-status'))

    @app.route('/referral-program')
    def referral_program():
        return render_template('referral-program.html', **ctx('referral-program'))

    @app.route('/nrb')
    def nrb():
        return render_template('nrb.html', **ctx('nrb'))

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        if request.method == 'POST':
            flash('Your message has been sent! We will get back to you shortly.', 'success')
            return redirect(url_for('contact'))
        return render_template('contact.html', **ctx('contact'))

    # ── DB Init ───────────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()
        _seed_defaults()

    return app


def _seed_defaults():
    """Populate default settings on first run (idempotent)."""
    # Admin user
    if not AdminUser.query.first():
        admin = AdminUser(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)

    # Site settings
    defaults = {
        'site_name':      'NextGen Design & Developers Ltd',
        'site_tagline':   'A Leading Real Estate Developer',
        'logo_url':       '/assets/images/logo.svg',
        'favicon_url':    '/assets/images/fav.png',
        'phone':          '+880 1234-567890',
        'email':          'info@nddl.com',
        'address':        'Dhaka, Bangladesh',
        'footer_about':   'We are committed to building exceptional properties with innovation and integrity.',
        'facebook_url':   '#',
        'instagram_url':  '#',
        'linkedin_url':   '#',
        'youtube_url':    '#',
        'ga4_tracking_id': '',
        'fb_pixel_id':    '',
    }
    for key, value in defaults.items():
        if not SiteSetting.query.filter_by(key=key).first():
            db.session.add(SiteSetting(key=key, value=value))

    # Page SEO defaults
    pages = [
        ('home',                'Home',                'NextGen Design & Developers Ltd – Premium Real Estate in Bangladesh',
         'We build exceptional homes and commercial spaces across Bangladesh with innovation and integrity.'),
        ('about',               'About Us',            'About Us – NextGen Design & Developers Ltd',
         'Learn about our journey, mission, values and the team behind NextGen Design & Developers Ltd.'),
        ('properties',          'Properties',          'Our Properties – NextGen Design & Developers Ltd',
         'Browse our curated portfolio of residential and commercial properties across Bangladesh.'),
        ('landowner',           'Landowner',           'Landowner Program – NextGen Design & Developers Ltd',
         'Partner with us as a landowner and benefit from our joint-venture real estate development program.'),
        ('construction-status', 'Construction Status', 'Construction Status – NextGen Design & Developers Ltd',
         'Track the live construction progress of all ongoing real estate projects.'),
        ('referral-program',    'Referral Program',    'Referral Program – NextGen Design & Developers Ltd',
         'Earn rewards by referring friends and family to our exclusive real estate properties.'),
        ('nrb',                 'NRB',                 'NRB Services – NextGen Design & Developers Ltd',
         'Dedicated services for Non-Resident Bangladeshis looking to invest in premium real estate back home.'),
        ('contact',             'Contact Us',          'Contact Us – NextGen Design & Developers Ltd',
         'Get in touch with our team for property inquiries, partnerships, and general information.'),
    ]
    for slug, name, title, desc in pages:
        if not PageSEO.query.filter_by(page_slug=slug).first():
            db.session.add(PageSEO(
                page_slug=slug, page_name=name,
                title=title, description=desc,
                og_title=title, og_description=desc,
            ))

    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
