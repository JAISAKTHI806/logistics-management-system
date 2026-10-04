from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from models.order import Order
from models.shipment import Shipment
from models import db

customer_bp = Blueprint('customer', __name__, url_prefix='/customer')
PRODUCT_CATEGORIES = [
    'Electronics',
    'Electrical Appliances',
    'Cosmetics & Personal Care',
    'Clothing & Accessories',
    'Books & Documents',
    'Food & Groceries',
    'Home & Kitchen',
    'Fragile Items',
    'Medical Supplies',
    'Sports & Fitness',
    'Other',
]
PICKUP_HUB_ADDRESS = 'Bengaluru Warehouse, Bengaluru, Karnataka'

def customer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'customer':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@customer_bp.route('/dashboard')
@login_required
@customer_required
def dashboard():
    orders = Order.query.filter_by(customer_id=current_user.id)\
                        .order_by(Order.created_at.desc()).limit(5).all()
    return render_template('customer/dashboard.html', orders=orders)

@customer_bp.route('/place-order', methods=['GET', 'POST'])
@login_required
@customer_required
def place_order():
    if request.method == 'POST':
        delivery = request.form.get('delivery_address', '').strip()
        desc     = request.form.get('package_description', '').strip()
        product_type = request.form.get('product_type', '').strip()
        quantity_input = request.form.get('quantity', '0')
        notes    = request.form.get('notes', '').strip()

        if product_type not in PRODUCT_CATEGORIES:
            flash('Please choose a valid product type.', 'danger')
        elif not delivery or not desc:
            flash('Please fill in all required fields.', 'danger')
        else:
            package_description = f'{product_type}: {desc}'
            try:
                quantity = int(quantity_input)
            except ValueError:
                quantity = 0
            if quantity < 1:
                flash('Order rejected: Quantity must be a whole number greater than zero.', 'danger')
                order = Order(customer_id=current_user.id, pickup_address=PICKUP_HUB_ADDRESS,
                              delivery_address=delivery, package_description=package_description,
                              quantity=quantity, status='rejected', notes='Invalid quantity specified.')
                db.session.add(order)
                db.session.commit()
            else:
                order = Order(customer_id=current_user.id, pickup_address=PICKUP_HUB_ADDRESS,
                              delivery_address=delivery, package_description=package_description,
                              quantity=quantity, status='validated', notes=notes)
                db.session.add(order)
                db.session.flush()
                # Auto-create shipment with tracking number
                shipment = Shipment(
                    order_id=order.id,
                    tracking_number=Shipment.generate_tracking(),
                    current_status='Order Placed',
                    current_location='Order Processing Center'
                )
                db.session.add(shipment)
                db.session.commit()
                flash(f'Order placed successfully! Tracking: {shipment.tracking_number}', 'success')
                return redirect(url_for('customer.order_history'))
    return render_template('customer/place_order.html',
                           product_categories=PRODUCT_CATEGORIES,
                           pickup_hub=PICKUP_HUB_ADDRESS)

@customer_bp.route('/track', methods=['GET', 'POST'])
@login_required
@customer_required
def track_shipment():
    if request.method == 'POST':
        tracking_number = request.form.get('tracking_number', '').strip()
        if not tracking_number:
            flash('Enter a tracking number to search.', 'warning')
            return redirect(url_for('customer.track_shipment'))
        # Redirect after POST so refreshing the results page never resubmits
        # the tracking form.
        return redirect(url_for('customer.track_shipment', tracking_number=tracking_number))

    shipment = None
    tracking_number = request.args.get('tracking_number', '').strip()
    if tracking_number:
        # Tracking details include addresses, so only show shipments owned by
        # the signed-in customer.
        shipment = Shipment.query.join(Order).filter(
            Shipment.tracking_number == tracking_number,
            Order.customer_id == current_user.id
        ).first()
        if not shipment:
            flash('No shipment found with that tracking number.', 'warning')
    return render_template('customer/track_shipment.html', shipment=shipment)

@customer_bp.route('/order-history')
@login_required
@customer_required
def order_history():
    orders = Order.query.filter_by(customer_id=current_user.id)\
                        .order_by(Order.created_at.desc()).all()
    return render_template('customer/order_history.html', orders=orders)

@customer_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@customer_required
def profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', '').strip()
        current_user.phone     = request.form.get('phone', '').strip()
        current_user.email     = request.form.get('email', '').strip()
        db.session.commit()
        flash('Profile updated successfully.', 'success')
    return render_template('customer/profile.html')
