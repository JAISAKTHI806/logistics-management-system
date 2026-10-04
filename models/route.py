from . import db
from datetime import datetime

class Route(db.Model):
    """Route model - optimized delivery routes created by dispatcher"""
    __tablename__ = 'route'

    id = db.Column(db.Integer, primary_key=True)
    route_name = db.Column(db.String(100))
    start_location = db.Column(db.String(150), nullable=False)
    end_location = db.Column(db.String(150), nullable=False)
    distance_km = db.Column(db.Float)
    estimated_time_mins = db.Column(db.Integer)
    is_optimized = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    creator = db.relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f'<Route {self.start_location} -> {self.end_location}>'
