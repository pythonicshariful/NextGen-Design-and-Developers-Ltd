from flask import Blueprint

admin_bp = Blueprint('admin_bp', __name__, template_folder='../templates/admin')

from admin import routes  # noqa: F401 — must be after blueprint creation
