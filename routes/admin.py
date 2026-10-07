from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from models.user import User
from models.order import Order
from models.shipment import Shipment
from models.delivery import Delivery
from models import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_orders': Order.query.count(),
        'total_shipments': Shipment.query.count(),
        'total_deliveries': Delivery.query.count(),
        'pending_orders': Order.query.filter_by(status='pending').count(),
        'delivered': Delivery.query.filter_by(delivery_status='delivered').count(),
    }
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent_orders=recent_orders)

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/manage_users.html', users=users)

@admin_bp.route('/users/create-agent', methods=['POST'])
@login_required
@admin_required
def create_delivery_agent():
    username = request.form.get('username', '').strip()
    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    if not username or not full_name or '@' not in email or len(password) < 8:
        flash('Enter a name, username, valid email, and password with at least 8 characters.', 'danger')
        return redirect(url_for('admin.manage_users'))
    if User.query.filter_by(username=username).first():
        flash('That username is already in use.', 'danger')
        return redirect(url_for('admin.manage_users'))
    if User.query.filter_by(email=email).first():
        flash('That email address is already in use.', 'danger')
        return redirect(url_for('admin.manage_users'))

    agent = User(username=username, full_name=full_name, email=email, role='delivery_agent', is_active=True)
    agent.set_password(password)
    db.session.add(agent)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash('The delivery agent account could not be saved. Please check the details and try again.', 'danger')
    else:
        flash(f'Delivery agent {full_name} created and activated.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/toggle/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'warning')
    else:
        user.is_active = not user.is_active
        db.session.commit()
        status = 'activated' if user.is_active else 'deactivated'
        flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    return render_template('admin/settings.html')
