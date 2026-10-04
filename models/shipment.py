from . import db
from datetime import datetime
import random
import string

class Shipment(db.Model):
    """Shipment model - created when an order is validated"""
    __tablename__ = 'shipment'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    tracking_number = db.Column(db.String(50), unique=True, nullable=False)
    current_status = db.Column(db.String(50), default='Order Placed')
    current_location = db.Column(db.String(150))
    estimated_delivery = db.Column(db.DateTime)
    actual_delivery = db.Column(db.DateTime)
    shipment_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    deliveries = db.relationship('Delivery', backref='shipment', lazy=True)

    @staticmethod
    def generate_tracking():
        date_str = datetime.utcnow().strftime('%Y%m%d')
        suffix = ''.join(random.choices(string.digits, k=4))
        return f'LMS-{date_str}-{suffix}'

    def status_badge(self):
        badge_map = {
            'Order Placed': 'warning',
            'Package Prepared': 'secondary',
            'Dispatched': 'primary',
            'In Transit': 'info',
            'Delivered': 'success',
            'Failed': 'danger',
            'Rescheduled': 'warning'
        }
        return badge_map.get(self.current_status, 'secondary')

    def __repr__(self):
        return f'<Shipment {self.tracking_number}>'
