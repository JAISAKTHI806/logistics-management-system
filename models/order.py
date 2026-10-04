from . import db
from datetime import datetime

class Order(db.Model):
    """Order model - represents a customer's shipping request"""
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pickup_address = db.Column(db.Text, nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    package_description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(20), default='pending')
    # Status flow: pending -> validated/rejected -> processing -> shipped -> delivered
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)
    is_prepared = db.Column(db.Boolean, default=False)  # Set by warehouse staff

    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref='orders')
    shipments = db.relationship('Shipment', backref='order', lazy=True)

    def status_badge(self):
        badge_map = {
            'pending': 'warning',
            'validated': 'info',
            'rejected': 'danger',
            'processing': 'primary',
            'shipped': 'info',
            'delivered': 'success'
        }
        return badge_map.get(self.status, 'secondary')

    def __repr__(self):
        return f'<Order #{self.id} {self.status}>'
