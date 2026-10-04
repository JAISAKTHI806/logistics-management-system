import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from models import db
from models.user import User
from models.order import Order
from models.shipment import Shipment
from models.delivery import Delivery
from models.inventory import Inventory
from models.route import Route
from config import Config
from datetime import datetime, timedelta
from sqlalchemy import inspect, text

from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.customer import customer_bp
from routes.dispatcher import dispatcher_bp
from routes.delivery_agent import delivery_agent_bp
from routes.warehouse import warehouse_bp

app = Flask(__name__, static_folder='public/static', static_url_path='/static')
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register all blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(dispatcher_bp)
app.register_blueprint(delivery_agent_bp)
app.register_blueprint(warehouse_bp)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

def seed_database():
    """Seed the database with demo users and sample data"""
    if User.query.first():
        return  # Already seeded

    # Create demo users
    users_data = [
        ('admin',      os.environ.get('DEMO_ADMIN_PASSWORD', 'admin123'), 'admin',           'Admin User',       'admin@lms.com',       '9000000001'),
        ('customer',   os.environ.get('DEMO_CUSTOMER_PASSWORD', 'cust123'), 'customer',      'Priya Sharma',     'priya@example.com',   '9000000002'),
        ('dispatcher', os.environ.get('DEMO_DISPATCHER_PASSWORD', 'disp123'), 'dispatcher',  'Rajan Kumar',      'rajan@lms.com',       '9000000003'),
        ('agent',      os.environ.get('DEMO_AGENT_PASSWORD', 'agent123'), 'delivery_agent',  'Arjun Singh',      'arjun@lms.com',      '9000000004'),
        ('warehouse',  os.environ.get('DEMO_WAREHOUSE_PASSWORD', 'ware123'), 'warehouse_staff', 'Meena Patel',   'meena@lms.com',      '9000000005'),
        ('agent2',     os.environ.get('DEMO_AGENT_PASSWORD', 'agent123'), 'delivery_agent',  'Suresh Nair',      'suresh@lms.com',     '9000000006'),
        ('customer2',  os.environ.get('DEMO_CUSTOMER_PASSWORD', 'cust123'), 'customer',      'Amit Verma',       'amit@example.com',   '9000000007'),
    ]

    users = {}
    for username, password, role, full_name, email, phone in users_data:
        u = User(username=username, email=email, role=role, full_name=full_name, phone=phone)
        u.set_password(password)
        db.session.add(u)
        users[username] = u
    db.session.flush()

    # Create sample orders
    orders_data = [
        (users['customer'].id,  'Bengaluru Warehouse, Bengaluru, Karnataka', '45 HSR Layout, Bengaluru', 'Electronics - Laptop',        1, 'validated'),
        (users['customer'].id,  'Bengaluru Warehouse, Bengaluru, Karnataka', '90 Anna Nagar, Chennai',    'Clothing Package',            2, 'delivered'),
        (users['customer2'].id, 'Bengaluru Warehouse, Bengaluru, Karnataka', '200 Whitefield, Bengaluru','Books and Stationery',        3, 'processing'),
        (users['customer2'].id, 'Bengaluru Warehouse, Bengaluru, Karnataka', '55 Connaught Place, Delhi','Fragile - Glassware',         1, 'pending'),
        (users['customer'].id,  'Bengaluru Warehouse, Bengaluru, Karnataka', '10 Jubilee Hills, Hyderabad','Pharmaceutical Supplies',   4, 'shipped'),
    ]

    orders = []
    for cid, pickup, delivery, desc, quantity, status in orders_data:
        o = Order(customer_id=cid, pickup_address=pickup, delivery_address=delivery,
                  package_description=desc, quantity=quantity, status=status,
                  created_at=datetime.utcnow() - timedelta(days=3),
                  is_prepared=(status not in ['pending', 'rejected']))
        db.session.add(o)
        orders.append(o)
    db.session.flush()

    # Create shipments for validated/processing/shipped/delivered orders
    tracking_nos = ['LMS-20241001-1001', 'LMS-20241002-1002', 'LMS-20241003-1003', 'LMS-20241004-1004']
    shipment_data = [
        (orders[0].id, tracking_nos[0], 'Package Prepared',  'Bengaluru Warehouse',      datetime.utcnow() + timedelta(days=1)),
        (orders[1].id, tracking_nos[1], 'Delivered',         'Delivered to Recipient',   datetime.utcnow() - timedelta(days=1)),
        (orders[2].id, tracking_nos[2], 'In Transit',        'En Route - Bengaluru',     datetime.utcnow() + timedelta(days=2)),
        (orders[4].id, tracking_nos[3], 'Dispatched',        'Hyderabad Hub',            datetime.utcnow() + timedelta(days=1)),
    ]

    shipments = []
    for oid, tn, status, location, eta in shipment_data:
        s = Shipment(order_id=oid, tracking_number=tn, current_status=status,
                     current_location=location, estimated_delivery=eta,
                     actual_delivery=(datetime.utcnow() - timedelta(days=1) if status == 'Delivered' else None))
        db.session.add(s)
        shipments.append(s)
    db.session.flush()

    # Create routes
    routes_data = [
        ('Route BLR-North', 'Bengaluru Central', 'Bengaluru North Zone', 25.5, 55,  True),
        ('Route BLR-South', 'Bengaluru Central', 'Bengaluru South Zone', 18.2, 40,  True),
        ('Route HYD-City',  'Hyderabad Hub',     'Hyderabad City Zone',  12.0, 30,  False),
    ]

    routes = []
    for name, start, end, dist, time, optimized in routes_data:
        r = Route(route_name=name, start_location=start, end_location=end,
                  distance_km=dist, estimated_time_mins=time, is_optimized=optimized,
                  created_by=users['dispatcher'].id)
        db.session.add(r)
        routes.append(r)
    db.session.flush()

    # Create deliveries
    deliveries_data = [
        (shipments[0].id, users['agent'].id,  users['dispatcher'].id, routes[0].id, 'assigned',  datetime.utcnow() + timedelta(days=1),  None),
        (shipments[1].id, users['agent'].id,  users['dispatcher'].id, routes[1].id, 'delivered', datetime.utcnow() - timedelta(days=1),  datetime.utcnow() - timedelta(days=1)),
        (shipments[2].id, users['agent2'].id, users['dispatcher'].id, routes[0].id, 'in_transit',datetime.utcnow(),                       None),
        (shipments[3].id, users['agent2'].id, users['dispatcher'].id, routes[2].id, 'assigned',  datetime.utcnow() + timedelta(days=1),  None),
    ]

    for sid, aid, did, rid, status, sched, actual in deliveries_data:
        d = Delivery(shipment_id=sid, agent_id=aid, dispatcher_id=did, route_id=rid,
                     delivery_status=status, scheduled_date=sched, actual_delivery_date=actual,
                     proof_of_delivery_notes=('Package delivered and signed.' if status == 'delivered' else None))
        db.session.add(d)

    # Create inventory items
    inventory_data = [
        ('Cardboard Boxes (Large)',  'SKU-BOX-L-001', 150, 'Shelf A-1', users['warehouse'].id),
        ('Cardboard Boxes (Medium)', 'SKU-BOX-M-002', 200, 'Shelf A-2', users['warehouse'].id),
        ('Bubble Wrap Roll',         'SKU-WRAP-001',   45, 'Shelf B-1', users['warehouse'].id),
        ('Packing Tape',             'SKU-TAPE-001',   80, 'Shelf B-2', users['warehouse'].id),
        ('Fragile Stickers',         'SKU-STK-F-001', 500, 'Shelf C-1', users['warehouse'].id),
        ('Foam Peanuts (1kg)',        'SKU-FOAM-001',   30, 'Shelf C-2', users['warehouse'].id),
        ('Thermal Labels',           'SKU-LBL-001',   400, 'Shelf D-1', users['warehouse'].id),
        ('Stretch Film Roll',        'SKU-FILM-001',   20, 'Shelf D-2', users['warehouse'].id),
        ('Wooden Pallet',            'SKU-PAL-001',     8, 'Dock Area', users['warehouse'].id),
        ('Hand Pallet Jack',         'SKU-JACK-001',    3, 'Equipment', users['warehouse'].id),
    ]

    for item, sku, qty, loc, wid in inventory_data:
        inv = Inventory(item_name=item, sku=sku, quantity=qty, location=loc, warehouse_staff_id=wid)
        db.session.add(inv)

    db.session.commit()
    print("✅ Database seeded with demo data.")

with app.app_context():
    db.create_all()
    order_columns = {column['name'] for column in inspect(db.engine).get_columns('order')}
    if 'quantity' not in order_columns:
        # Preserve existing weight values under a legacy name and migrate old
        # orders with a default quantity of one item.
        with db.engine.begin() as connection:
            if 'weight_kg' in order_columns:
                connection.execute(text('ALTER TABLE "order" RENAME COLUMN weight_kg TO legacy_weight_kg'))
            connection.execute(text('ALTER TABLE "order" ADD COLUMN quantity INTEGER NOT NULL DEFAULT 1'))
    is_vercel = os.environ.get('VERCEL') == '1'
    seed_demo_data = os.environ.get('SEED_DEMO_DATA', 'true').lower() == 'true'
    if not is_vercel or seed_demo_data:
        if is_vercel and not User.query.first():
            required_passwords = [
                'DEMO_ADMIN_PASSWORD', 'DEMO_CUSTOMER_PASSWORD',
                'DEMO_DISPATCHER_PASSWORD', 'DEMO_AGENT_PASSWORD',
                'DEMO_WAREHOUSE_PASSWORD',
            ]
            missing_passwords = [key for key in required_passwords if not os.environ.get(key)]
            if missing_passwords:
                raise RuntimeError('Set all DEMO_*_PASSWORD variables before enabling demo-data seeding.')
        seed_database()

@app.context_processor
def inject_demo_credentials_visibility():
    return {'show_demo_credentials': os.environ.get('VERCEL') != '1'}

if __name__ == '__main__':
    print("🚀 Starting Logistics Management System...")
    print("📌 Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True)
