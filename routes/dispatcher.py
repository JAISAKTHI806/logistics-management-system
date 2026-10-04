from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from models.user import User
from models.order import Order
from models.shipment import Shipment
from models.delivery import Delivery
from models.route import Route
from models import db
from datetime import datetime

dispatcher_bp = Blueprint('dispatcher', __name__, url_prefix='/dispatcher')

def dispatcher_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'dispatcher':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@dispatcher_bp.route('/dashboard')
@login_required
@dispatcher_required
def dashboard():
    stats = {
        'pending_assign': Shipment.query.join(Order).filter(
            Order.status.in_(['validated', 'processing']),
            ~Shipment.deliveries.any()
        ).count(),
        'in_transit': Delivery.query.filter_by(delivery_status='in_transit').count(),
        'delivered_today': Delivery.query.filter_by(delivery_status='delivered').count(),
        'failed': Delivery.query.filter_by(delivery_status='failed').count(),
        'routes': Route.query.count(),
    }
    recent_deliveries = Delivery.query.order_by(Delivery.created_at.desc()).limit(6).all()
    return render_template('dispatcher/dashboard.html', stats=stats, recent_deliveries=recent_deliveries)

@dispatcher_bp.route('/assign-delivery', methods=['GET', 'POST'])
@login_required
@dispatcher_required
def assign_delivery():
    if request.method == 'POST':
        shipment_id = request.form.get('shipment_id')
        agent_id    = request.form.get('agent_id')
        route_id    = request.form.get('route_id')
        sched_date  = request.form.get('scheduled_date')

        shipment = Shipment.query.get(shipment_id)
        if not shipment:
            flash('Shipment not found.', 'danger')
        else:
            # Update shipment status
            shipment.current_status = 'Dispatched'
            shipment.order.status = 'shipped'

            # Create delivery record
            d = Delivery(
                shipment_id=int(shipment_id),
                agent_id=int(agent_id),
                dispatcher_id=current_user.id,
                route_id=int(route_id) if route_id else None,
                scheduled_date=datetime.strptime(sched_date, '%Y-%m-%d') if sched_date else None,
                delivery_status='assigned'
            )
            db.session.add(d)
            db.session.commit()
            flash(f'Delivery assigned successfully to agent.', 'success')
            return redirect(url_for('dispatcher.assign_delivery'))

    # Shipments that have no delivery assigned yet
    assigned_ids = [d.shipment_id for d in Delivery.query.all()]
    unassigned_shipments = Shipment.query.filter(~Shipment.id.in_(assigned_ids)).all() if assigned_ids else Shipment.query.all()
    agents = User.query.filter_by(role='delivery_agent', is_active=True).all()
    routes = Route.query.all()
    return render_template('dispatcher/assign_delivery.html',
                           shipments=unassigned_shipments, agents=agents, routes=routes)

@dispatcher_bp.route('/optimize-routes', methods=['GET', 'POST'])
@login_required
@dispatcher_required
def optimize_routes():
    if request.method == 'POST':
        route_name = request.form.get('route_name', '').strip()
        start = request.form.get('start_location', '').strip()
        end   = request.form.get('end_location', '').strip()
        dist  = request.form.get('distance_km', '0')
        time  = request.form.get('estimated_time', '0')
        r = Route(
            route_name=route_name, start_location=start, end_location=end,
            distance_km=float(dist), estimated_time_mins=int(time),
            is_optimized=True, created_by=current_user.id
        )
        db.session.add(r)
        db.session.commit()
        flash(f'Route "{route_name}" created and optimized!', 'success')
        return redirect(url_for('dispatcher.optimize_routes'))
    routes = Route.query.order_by(Route.created_at.desc()).all()
    return render_template('dispatcher/optimize_routes.html', routes=routes)

@dispatcher_bp.route('/fleet-status')
@login_required
@dispatcher_required
def fleet_status():
    agents = User.query.filter_by(role='delivery_agent', is_active=True).all()
    agent_deliveries = {}
    for agent in agents:
        agent_deliveries[agent.id] = Delivery.query.filter_by(agent_id=agent.id)\
                                                    .order_by(Delivery.created_at.desc()).all()
    return render_template('dispatcher/fleet_status.html', agents=agents, agent_deliveries=agent_deliveries)

@dispatcher_bp.route('/reschedule/<int:delivery_id>', methods=['POST'])
@login_required
@dispatcher_required
def reschedule(delivery_id):
    delivery = Delivery.query.get_or_404(delivery_id)
    new_date = request.form.get('new_date')
    delivery.delivery_status = 'rescheduled'
    delivery.shipment.current_status = 'Rescheduled'
    if new_date:
        delivery.scheduled_date = datetime.strptime(new_date, '%Y-%m-%d')
    db.session.commit()
    flash('Delivery rescheduled successfully.', 'success')
    return redirect(url_for('dispatcher.fleet_status'))
