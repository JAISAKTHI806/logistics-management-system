from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from models import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_by_role(current_user.role)
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            return redirect_by_role(user.role)
        flash('Invalid username or password.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        full_name = request.form.get('full_name', '').strip()
        phone    = request.form.get('phone', '').strip()
        if User.query.filter_by(username=username).first():
            flash('Username already taken. Please choose another.', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
        else:
            user = User(username=username, email=email, role='customer',
                        full_name=full_name, phone=phone)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

def redirect_by_role(role):
    role_dashboard = {
        'admin':           'admin.dashboard',
        'customer':        'customer.dashboard',
        'dispatcher':      'dispatcher.dashboard',
        'delivery_agent':  'delivery_agent.dashboard',
        'warehouse_staff': 'warehouse.dashboard',
    }
    return redirect(url_for(role_dashboard.get(role, 'auth.login')))
