from . import db
from datetime import datetime

class Delivery(db.Model):
    """Delivery model - represents the physical delivery assignment to an agent"""
    __tablename__ = 'delivery'

    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipment.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dispatcher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scheduled_date = db.Column(db.DateTime)
    actual_delivery_date = db.Column(db.DateTime)
    proof_of_delivery_notes = db.Column(db.Text)
    pod_image_path = db.Column(db.String(200))
    delivery_status = db.Column(db.String(20), default='assigned')
    # Status: assigned -> in_transit -> delivered / failed -> rescheduled
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    agent = db.relationship('User', foreign_keys=[agent_id], backref='deliveries_as_agent')
    dispatcher = db.relationship('User', foreign_keys=[dispatcher_id], backref='deliveries_as_dispatcher')
    route = db.relationship('Route', backref='deliveries')

    def status_badge(self):
        badge_map = {
            'assigned': 'warning',
            'in_transit': 'info',
            'delivered': 'success',
            'failed': 'danger',
            'rescheduled': 'secondary'
        }
        return badge_map.get(self.delivery_status, 'secondary')

    def __repr__(self):
        return f'<Delivery #{self.id} {self.delivery_status}>'
