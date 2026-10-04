-- Logistics Management System - SQL Schema Reference
-- (Tables are auto-created by SQLAlchemy. This file is for reference.)

CREATE TABLE user (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    VARCHAR(64) UNIQUE NOT NULL,
    email       VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256),
    role        VARCHAR(30) NOT NULL,  -- admin/customer/dispatcher/delivery_agent/warehouse_staff
    full_name   VARCHAR(100),
    phone       VARCHAR(20),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active   BOOLEAN DEFAULT 1
);

CREATE TABLE "order" (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id         INTEGER REFERENCES user(id),
    pickup_address      TEXT NOT NULL,
    delivery_address    TEXT NOT NULL,
    package_description TEXT NOT NULL,
    quantity            INTEGER NOT NULL DEFAULT 1,
    status              VARCHAR(20) DEFAULT 'pending',
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes               TEXT,
    is_prepared         BOOLEAN DEFAULT 0
);

CREATE TABLE shipment (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id         INTEGER REFERENCES "order"(id),
    tracking_number  VARCHAR(50) UNIQUE NOT NULL,
    current_status   VARCHAR(50),
    current_location VARCHAR(150),
    estimated_delivery DATETIME,
    actual_delivery  DATETIME,
    shipment_date    DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE route (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    route_name         VARCHAR(100),
    start_location     VARCHAR(150) NOT NULL,
    end_location       VARCHAR(150) NOT NULL,
    distance_km        REAL,
    estimated_time_mins INTEGER,
    is_optimized       BOOLEAN DEFAULT 0,
    created_by         INTEGER REFERENCES user(id),
    created_at         DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE delivery (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    shipment_id              INTEGER REFERENCES shipment(id),
    agent_id                 INTEGER REFERENCES user(id),
    dispatcher_id            INTEGER REFERENCES user(id),
    scheduled_date           DATETIME,
    actual_delivery_date     DATETIME,
    proof_of_delivery_notes  TEXT,
    pod_image_path           VARCHAR(200),
    delivery_status          VARCHAR(20) DEFAULT 'assigned',
    route_id                 INTEGER REFERENCES route(id),
    created_at               DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name           VARCHAR(100) NOT NULL,
    sku                 VARCHAR(50) UNIQUE NOT NULL,
    quantity            INTEGER DEFAULT 0,
    location            VARCHAR(50),
    warehouse_staff_id  INTEGER REFERENCES user(id),
    last_updated        DATETIME DEFAULT CURRENT_TIMESTAMP
);
