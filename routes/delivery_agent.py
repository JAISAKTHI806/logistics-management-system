from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from models.delivery import Delivery
from models.shipment import Shipment
from models import db
from datetime import datetime

delivery_agent_bp = Blueprint('delivery_agent', __name__, url_prefix='/agent')

def agent_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'delivery_agent':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@delivery_agent_bp.route('/dashboard')
@login_required
@agent_required
def dashboard():
    my_deliveries = Delivery.query.filter_by(agent_id=current_user.id)\
                                  .order_by(Delivery.created_at.desc()).all()
    stats = {
        'assigned': sum(1 for d in my_deliveries if d.delivery_status == 'assigned'),
        'in_transit': sum(1 for d in my_deliveries if d.delivery_status == 'in_transit'),
        'delivered': sum(1 for d in my_deliveries if d.delivery_status == 'delivered'),
        'failed': sum(1 for d in my_deliveries if d.delivery_status == 'failed'),
    }
    return render_template('delivery_agent/dashboard.html', deliveries=my_deliveries, stats=stats)

@delivery_agent_bp.route('/jobs')
@login_required
@agent_required
def assigned_jobs():
    jobs = Delivery.query.filter_by(agent_id=current_user.id)\
                         .order_by(Delivery.created_at.desc()).all()
    return render_template('delivery_agent/assigned_jobs.html', jobs=jobs)

@delivery_agent_bp.route('/jobs/<int:delivery_id>/start', methods=['POST'])
@login_required
@agent_required
def start_delivery(delivery_id):
    delivery = Delivery.query.get_or_404(delivery_id)
    if delivery.agent_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('delivery_agent.assigned_jobs'))
    delivery.delivery_status = 'in_transit'
    delivery.shipment.current_status = 'In Transit'
    delivery.shipment.current_location = 'En Route'
    db.session.commit()
    flash('Delivery marked as In Transit. Navigate to the destination.', 'info')
    return redirect(url_for('delivery_agent.assigned_jobs'))

@delivery_agent_bp.route('/jobs/<int:delivery_id>/pod', methods=['GET', 'POST'])
@login_required
@agent_required
def record_pod(delivery_id):
    delivery = Delivery.query.get_or_404(delivery_id)
    if delivery.agent_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('delivery_agent.assigned_jobs'))

    if request.method == 'POST':
        notes   = request.form.get('pod_notes', '').strip()
        outcome = request.form.get('outcome', 'delivered')  # delivered or failed

        delivery.proof_of_delivery_notes = notes
        delivery.actual_delivery_date = datetime.utcnow()

        if outcome == 'delivered':
            delivery.delivery_status = 'delivered'
            delivery.shipment.current_status = 'Delivered'
            delivery.shipment.current_location = 'Delivered to Recipient'
            delivery.shipment.actual_delivery = datetime.utcnow()
            delivery.shipment.order.status = 'delivered'
            flash('Package delivered successfully! POD recorded.', 'success')
        else:
            delivery.delivery_status = 'failed'
            delivery.shipment.current_status = 'Failed'
            delivery.shipment.order.status = 'shipped'
            flash('Delivery marked as failed. Dispatcher will reschedule.', 'warning')

        db.session.commit()
        return redirect(url_for('delivery_agent.assigned_jobs'))

    return render_template('delivery_agent/record_pod.html', delivery=delivery)
