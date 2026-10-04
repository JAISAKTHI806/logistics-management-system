from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    """User model covering all 5 roles: admin, customer, dispatcher, delivery_agent, warehouse_staff"""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(30), nullable=False)  # admin/customer/dispatcher/delivery_agent/warehouse_staff
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_role_display(self):
        role_map = {
            'admin': 'Administrator',
            'customer': 'Customer',
            'dispatcher': 'Dispatcher',
            'delivery_agent': 'Delivery Agent',
            'warehouse_staff': 'Warehouse Staff'
        }
        return role_map.get(self.role, self.role.title())

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
