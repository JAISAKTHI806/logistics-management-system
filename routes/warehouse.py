from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from models.order import Order
from models.inventory import Inventory
from models import db
from datetime import datetime

warehouse_bp = Blueprint('warehouse', __name__, url_prefix='/warehouse')

def warehouse_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'warehouse_staff':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@warehouse_bp.route('/dashboard')
@login_required
@warehouse_required
def dashboard():
    stats = {
        'total_inventory': Inventory.query.count(),
        'low_stock': Inventory.query.filter(Inventory.quantity < 10).count(),
        'out_of_stock': Inventory.query.filter(Inventory.quantity == 0).count(),
        'pending_packages': Order.query.filter_by(status='validated', is_prepared=False).count(),
        'prepared_today': Order.query.filter_by(is_prepared=True).count(),
    }
    pending_orders = Order.query.filter_by(status='validated', is_prepared=False)\
                                .order_by(Order.created_at.asc()).all()
    return render_template('warehouse/dashboard.html', stats=stats, pending_orders=pending_orders)

@warehouse_bp.route('/inbound-cargo', methods=['GET', 'POST'])
@login_required
@warehouse_required
def inbound_cargo():
    if request.method == 'POST':
        item_name = request.form.get('item_name', '').strip()
        sku       = request.form.get('sku', '').strip()
        quantity  = request.form.get('quantity', '0')
        location  = request.form.get('location', '').strip()

        existing = Inventory.query.filter_by(sku=sku).first()
        if existing:
            existing.quantity += int(quantity)
            existing.last_updated = datetime.utcnow()
            flash(f'Updated stock for {existing.item_name}. New quantity: {existing.quantity}', 'success')
        else:
            inv = Inventory(item_name=item_name, sku=sku, quantity=int(quantity),
                            location=location, warehouse_staff_id=current_user.id)
            db.session.add(inv)
            flash(f'New item "{item_name}" added to inventory.', 'success')
        db.session.commit()
        return redirect(url_for('warehouse.inventory'))
    return render_template('warehouse/inbound_cargo.html')

@warehouse_bp.route('/inventory')
@login_required
@warehouse_required
def inventory():
    items = Inventory.query.order_by(Inventory.item_name).all()
    return render_template('warehouse/inventory.html', items=items)

@warehouse_bp.route('/inventory/update/<int:item_id>', methods=['POST'])
@login_required
@warehouse_required
def update_inventory(item_id):
    item = Inventory.query.get_or_404(item_id)
    new_qty = request.form.get('quantity')
    if new_qty is not None:
        item.quantity = int(new_qty)
        item.last_updated = datetime.utcnow()
        db.session.commit()
        flash(f'Inventory for {item.item_name} updated.', 'success')
    return redirect(url_for('warehouse.inventory'))

@warehouse_bp.route('/prepare-package/<int:order_id>', methods=['POST'])
@login_required
@warehouse_required
def prepare_package(order_id):
    order = Order.query.get_or_404(order_id)
    order.is_prepared = True
    order.status = 'processing'
    db.session.commit()
    flash(f'Package for Order #{order.id} marked as prepared for pickup.', 'success')
    return redirect(url_for('warehouse.dashboard'))
