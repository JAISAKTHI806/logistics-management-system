from . import db
from datetime import datetime

class Inventory(db.Model):
    """Inventory model - managed by warehouse staff"""
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    location = db.Column(db.String(50))  # e.g. "Shelf A-3"
    warehouse_staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    managed_by = db.relationship('User', foreign_keys=[warehouse_staff_id])

    def stock_status(self):
        if self.quantity == 0:
            return ('Out of Stock', 'danger')
        elif self.quantity < 10:
            return ('Low Stock', 'warning')
        else:
            return ('In Stock', 'success')

    def __repr__(self):
        return f'<Inventory {self.sku}: {self.quantity}>'
