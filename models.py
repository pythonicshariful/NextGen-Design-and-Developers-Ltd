from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<AdminUser {self.username}>'


class SiteSetting(db.Model):
    __tablename__ = 'site_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, default='')

    @staticmethod
    def get(key, default=''):
        s = SiteSetting.query.filter_by(key=key).first()
        return s.value if s else default

    @staticmethod
    def set_value(key, value):
        s = SiteSetting.query.filter_by(key=key).first()
        if s:
            s.value = value
        else:
            s = SiteSetting(key=key, value=value)
            db.session.add(s)
        db.session.commit()

    @staticmethod
    def get_all_as_dict():
        return {s.key: s.value for s in SiteSetting.query.all()}


class PageSEO(db.Model):
    __tablename__ = 'page_seo'
    id = db.Column(db.Integer, primary_key=True)
    page_slug = db.Column(db.String(100), unique=True, nullable=False)
    page_name = db.Column(db.String(100), default='')
    title = db.Column(db.String(300), default='')
    description = db.Column(db.Text, default='')
    keywords = db.Column(db.Text, default='')
    og_title = db.Column(db.String(300), default='')
    og_description = db.Column(db.Text, default='')
    og_image = db.Column(db.String(500), default='')

    @staticmethod
    def for_page(slug):
        seo = PageSEO.query.filter_by(page_slug=slug).first()
        if not seo:
            seo = PageSEO(page_slug=slug, page_name=slug.replace('-', ' ').title())
        return seo


class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    position = db.Column(db.String(200), default='')
    company = db.Column(db.String(200), default='')
    quote = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    image_url = db.Column(db.String(500), default='')
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Testimonial {self.name}>'


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    location = db.Column(db.String(200), default='')
    property_type = db.Column(db.String(100), default='')
    status = db.Column(db.String(100), default='Ongoing')
    image_url = db.Column(db.String(500), default='')
    description = db.Column(db.Text, default='')
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Project {self.name}>'
