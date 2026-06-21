import os
from flask import (render_template, redirect, url_for, flash,
                   request, current_app, jsonify)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from admin import admin_bp
from models import db, AdminUser, SiteSetting, PageSEO, Testimonial, Project

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'ico'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file_field_name):
    """Save an uploaded file and return its public URL, or None."""
    f = request.files.get(file_field_name)
    if f and f.filename and allowed_file(f.filename):
        filename = secure_filename(f.filename)
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        f.save(save_path)
        return f'/uploads/{filename}'
    return None


# ── Auth ──────────────────────────────────────────────────────────────────────

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_bp.dashboard'))
    if request.method == 'POST':
        user = AdminUser.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password', '')):
            login_user(user, remember=request.form.get('remember') == 'on')
            flash('Welcome back!', 'success')
            return redirect(request.args.get('next') or url_for('admin_bp.dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_bp.login'))


# ── Dashboard ─────────────────────────────────────────────────────────────────

@admin_bp.route('/')
@login_required
def dashboard():
    stats = {
        'testimonials': Testimonial.query.count(),
        'active_testimonials': Testimonial.query.filter_by(is_active=True).count(),
        'projects': Project.query.count(),
        'active_projects': Project.query.filter_by(is_active=True).count(),
        'site_name': SiteSetting.get('site_name', 'N/A'),
        'ga4_set': bool(SiteSetting.get('ga4_tracking_id')),
        'fb_pixel_set': bool(SiteSetting.get('fb_pixel_id')),
    }
    return render_template('admin/dashboard.html', stats=stats)


# ── General Settings ──────────────────────────────────────────────────────────

@admin_bp.route('/general', methods=['GET', 'POST'])
@login_required
def general():
    settings_keys = [
        'site_name', 'site_tagline', 'logo_url', 'favicon_url',
        'phone', 'email', 'address', 'footer_about',
        'facebook_url', 'instagram_url', 'linkedin_url', 'youtube_url',
    ]
    if request.method == 'POST':
        for key in settings_keys:
            if key not in ('logo_url', 'favicon_url'):
                SiteSetting.set_value(key, request.form.get(key, ''))

        # Handle logo upload
        logo_url = save_upload('logo_file')
        if logo_url:
            SiteSetting.set_value('logo_url', logo_url)
        elif request.form.get('logo_url'):
            SiteSetting.set_value('logo_url', request.form.get('logo_url'))

        # Handle favicon upload
        fav_url = save_upload('favicon_file')
        if fav_url:
            SiteSetting.set_value('favicon_url', fav_url)
        elif request.form.get('favicon_url'):
            SiteSetting.set_value('favicon_url', request.form.get('favicon_url'))

        flash('General settings saved successfully!', 'success')
        return redirect(url_for('admin_bp.general'))

    current = {k: SiteSetting.get(k) for k in settings_keys}
    return render_template('admin/general.html', current=current)


# ── Analytics & Tracking ──────────────────────────────────────────────────────

@admin_bp.route('/analytics', methods=['GET', 'POST'])
@login_required
def analytics():
    keys = ['ga4_tracking_id', 'fb_pixel_id']
    if request.method == 'POST':
        for k in keys:
            SiteSetting.set_value(k, request.form.get(k, '').strip())
        flash('Analytics settings saved!', 'success')
        return redirect(url_for('admin_bp.analytics'))
    current = {k: SiteSetting.get(k) for k in keys}
    return render_template('admin/analytics.html', current=current)


# ── SEO ────────────────────────────────────────────────────────────────────────

PAGES = [
    ('home',                'Home'),
    ('about',               'About Us'),
    ('properties',          'Properties'),
    ('landowner',           'Landowner'),
    ('construction-status', 'Construction Status'),
    ('referral-program',    'Referral Program'),
    ('nrb',                 'NRB'),
    ('contact',             'Contact Us'),
]


@admin_bp.route('/seo', methods=['GET', 'POST'])
@login_required
def seo():
    selected = request.args.get('page', 'home')
    seo_obj = PageSEO.for_page(selected)
    if seo_obj.id is None:  # not persisted yet
        db.session.add(seo_obj)
        db.session.flush()

    if request.method == 'POST':
        selected = request.form.get('page_slug', selected)
        seo_obj = PageSEO.for_page(selected)
        if seo_obj.id is None:
            db.session.add(seo_obj)

        seo_obj.title = request.form.get('title', '')
        seo_obj.description = request.form.get('description', '')
        seo_obj.keywords = request.form.get('keywords', '')
        seo_obj.og_title = request.form.get('og_title', '')
        seo_obj.og_description = request.form.get('og_description', '')

        og_img = save_upload('og_image_file')
        if og_img:
            seo_obj.og_image = og_img
        elif request.form.get('og_image'):
            seo_obj.og_image = request.form.get('og_image')

        db.session.commit()
        flash(f'SEO settings for "{selected}" saved!', 'success')
        return redirect(url_for('admin_bp.seo', page=selected))

    return render_template('admin/seo.html',
                           pages=PAGES, selected=selected, seo=seo_obj)


# ── Testimonials ──────────────────────────────────────────────────────────────

@admin_bp.route('/testimonials')
@login_required
def testimonials():
    items = Testimonial.query.order_by(Testimonial.sort_order, Testimonial.id).all()
    return render_template('admin/testimonials.html', items=items)


@admin_bp.route('/testimonials/new', methods=['GET', 'POST'])
@login_required
def testimonial_new():
    if request.method == 'POST':
        img_url = save_upload('image_file') or request.form.get('image_url', '')
        t = Testimonial(
            name=request.form['name'],
            position=request.form.get('position', ''),
            company=request.form.get('company', ''),
            quote=request.form['quote'],
            rating=int(request.form.get('rating', 5)),
            image_url=img_url,
            sort_order=int(request.form.get('sort_order', 0)),
            is_active=request.form.get('is_active') == 'on',
        )
        db.session.add(t)
        db.session.commit()
        flash('Testimonial added!', 'success')
        return redirect(url_for('admin_bp.testimonials'))
    return render_template('admin/testimonials_form.html', item=None, action='Add')


@admin_bp.route('/testimonials/<int:tid>/edit', methods=['GET', 'POST'])
@login_required
def testimonial_edit(tid):
    t = Testimonial.query.get_or_404(tid)
    if request.method == 'POST':
        img_url = save_upload('image_file')
        t.name = request.form['name']
        t.position = request.form.get('position', '')
        t.company = request.form.get('company', '')
        t.quote = request.form['quote']
        t.rating = int(request.form.get('rating', 5))
        t.sort_order = int(request.form.get('sort_order', 0))
        t.is_active = request.form.get('is_active') == 'on'
        if img_url:
            t.image_url = img_url
        elif request.form.get('image_url'):
            t.image_url = request.form.get('image_url')
        db.session.commit()
        flash('Testimonial updated!', 'success')
        return redirect(url_for('admin_bp.testimonials'))
    return render_template('admin/testimonials_form.html', item=t, action='Edit')


@admin_bp.route('/testimonials/<int:tid>/toggle', methods=['POST'])
@login_required
def testimonial_toggle(tid):
    t = Testimonial.query.get_or_404(tid)
    t.is_active = not t.is_active
    db.session.commit()
    return jsonify({'active': t.is_active})


@admin_bp.route('/testimonials/<int:tid>/delete', methods=['POST'])
@login_required
def testimonial_delete(tid):
    t = Testimonial.query.get_or_404(tid)
    db.session.delete(t)
    db.session.commit()
    flash('Testimonial deleted.', 'info')
    return redirect(url_for('admin_bp.testimonials'))


# ── Projects ──────────────────────────────────────────────────────────────────

@admin_bp.route('/projects')
@login_required
def projects():
    items = Project.query.order_by(Project.sort_order, Project.id).all()
    return render_template('admin/projects.html', items=items)


@admin_bp.route('/projects/new', methods=['GET', 'POST'])
@login_required
def project_new():
    if request.method == 'POST':
        img_url = save_upload('image_file') or request.form.get('image_url', '')
        p = Project(
            name=request.form['name'],
            location=request.form.get('location', ''),
            property_type=request.form.get('property_type', ''),
            status=request.form.get('status', 'Ongoing'),
            description=request.form.get('description', ''),
            image_url=img_url,
            sort_order=int(request.form.get('sort_order', 0)),
            is_active=request.form.get('is_active') == 'on',
        )
        db.session.add(p)
        db.session.commit()
        flash('Project added!', 'success')
        return redirect(url_for('admin_bp.projects'))
    return render_template('admin/projects_form.html', item=None, action='Add')


@admin_bp.route('/projects/<int:pid>/edit', methods=['GET', 'POST'])
@login_required
def project_edit(pid):
    p = Project.query.get_or_404(pid)
    if request.method == 'POST':
        img_url = save_upload('image_file')
        p.name = request.form['name']
        p.location = request.form.get('location', '')
        p.property_type = request.form.get('property_type', '')
        p.status = request.form.get('status', 'Ongoing')
        p.description = request.form.get('description', '')
        p.sort_order = int(request.form.get('sort_order', 0))
        p.is_active = request.form.get('is_active') == 'on'
        if img_url:
            p.image_url = img_url
        elif request.form.get('image_url'):
            p.image_url = request.form.get('image_url')
        db.session.commit()
        flash('Project updated!', 'success')
        return redirect(url_for('admin_bp.projects'))
    return render_template('admin/projects_form.html', item=p, action='Edit')


@admin_bp.route('/projects/<int:pid>/toggle', methods=['POST'])
@login_required
def project_toggle(pid):
    p = Project.query.get_or_404(pid)
    p.is_active = not p.is_active
    db.session.commit()
    return jsonify({'active': p.is_active})


@admin_bp.route('/projects/<int:pid>/delete', methods=['POST'])
@login_required
def project_delete(pid):
    p = Project.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    flash('Project deleted.', 'info')
    return redirect(url_for('admin_bp.projects'))


# ── Change Password ───────────────────────────────────────────────────────────

@admin_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_pw = request.form.get('current_password', '')
        new_pw = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')
        if not current_user.check_password(current_pw):
            flash('Current password is incorrect.', 'danger')
        elif new_pw != confirm:
            flash('New passwords do not match.', 'danger')
        elif len(new_pw) < 6:
            flash('Password must be at least 6 characters.', 'danger')
        else:
            current_user.set_password(new_pw)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('admin_bp.dashboard'))
    return render_template('admin/change_password.html')
