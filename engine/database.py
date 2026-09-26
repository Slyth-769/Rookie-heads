"""
SQLite Database Schema and Seed Data for Disaster Alert Management System
Maintains Citizens, Wardens, Alerts, Delivery Logs, and Telecom Event Stream.
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "disaster_alert.db")

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables and seeds initial data if empty"""
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS wardens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        district TEXT NOT NULL,
        block_village TEXT NOT NULL,
        role TEXT NOT NULL,
        status TEXT DEFAULT 'ACTIVE'
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS citizens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        language TEXT NOT NULL,
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        district TEXT NOT NULL,
        block_village TEXT NOT NULL,
        device_type TEXT NOT NULL DEFAULT 'smartphone',
        secondary_name TEXT,
        secondary_phone TEXT,
        warden_id INTEGER,
        created_at TEXT NOT NULL,
        FOREIGN KEY(warden_id) REFERENCES wardens(id)
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY,
        hazard_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        area_name TEXT NOT NULL,
        center_lat REAL NOT NULL,
        center_lng REAL NOT NULL,
        radius_km REAL NOT NULL,
        polygon_json TEXT,
        helplines TEXT NOT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        ack_timeout_seconds INTEGER NOT NULL DEFAULT 45,
        max_retries INTEGER NOT NULL DEFAULT 3
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS delivery_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alert_id TEXT NOT NULL,
        citizen_id INTEGER NOT NULL,
        channel TEXT NOT NULL, -- PUSH, SMS, IVR, WARDEN
        status TEXT NOT NULL,  -- PENDING, SENT, DELIVERED, READ, ACKNOWLEDGED, ESCALATED
        retry_count INTEGER NOT NULL DEFAULT 0,
        ack_response TEXT DEFAULT 'NONE', -- NONE, SAFE, RESCUE
        sent_at TEXT,
        delivered_at TEXT,
        read_at TEXT,
        acknowledged_at TEXT,
        offline_cached INTEGER DEFAULT 0,
        notes TEXT,
        FOREIGN KEY(alert_id) REFERENCES alerts(id),
        FOREIGN KEY(citizen_id) REFERENCES citizens(id)
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS telecom_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        direction TEXT NOT NULL, -- OUTBOUND, INBOUND
        channel TEXT NOT NULL,   -- SMS, IVR, USSD, PUSH
        phone TEXT NOT NULL,
        message TEXT NOT NULL,
        alert_id TEXT,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    conn.commit()

    # Seed initial wardens and citizens if empty
    c.execute("SELECT COUNT(*) FROM wardens")
    if c.fetchone()[0] == 0:
        seed_data(conn)

    conn.close()

def seed_data(conn):
    c = conn.cursor()
    
    wardens = [
        ("Inspector Bimal Nayak", "+919861011111", "Puri", "Puri Marine Drive", "Civil Defense & Coastal Warden"),
        ("Officer Alok Das", "+919861022222", "Balasore", "Chandipur Coastal Sector", "NDRF Sector Coordinator"),
        ("Smt. Gita Mohapatra", "+919861033333", "Cuttack", "Mahanadi Embankment", "Disaster Rapid Response Warden"),
        ("Captain Rajesh Rao", "+919861044444", "Ganjam", "Gopalpur Port Sector", "Coastal Guard & Rescue Warden"),
        ("Dr. Sujit Samal", "+919861055555", "Bhubaneswar", "Capital Disaster Cell", "Urban Emergency Evacuation Lead")
    ]
    c.executemany("INSERT INTO wardens (name, phone, district, block_village, role) VALUES (?,?,?,?,?)", wardens)

    now = datetime.now().isoformat()
    citizens = [
        ("Ramesh Mohanty", "+919437012345", "or", 19.7983, 85.8249, "Puri", "Swargadwar Fisherman Ward", "smartphone", "Laxmi Mohanty (Wife)", "+919437012346", 1, now),
        ("Sunita Sharma", "+919861234567", "hi", 20.4580, 85.8750, "Cuttack", "Badambadi Bus Colony", "smartphone", "Rajesh Sharma (Brother)", "+919861234568", 3, now),
        ("Debashis Roy", "+919437998877", "bn", 21.4682, 87.0125, "Balasore", "Chandipur Fishing Hamlet", "feature_phone", "Mitali Roy (Mother)", "+919437998878", 2, now),
        ("K. Venkat Rao", "+919777123987", "te", 19.2580, 84.9080, "Ganjam", "Gopalpur Beach Road", "smartphone", "K. Aruna (Sister)", "+919777123988", 4, now),
        ("Amina Begum", "+919937001122", "ur", 20.2405, 85.8340, "Bhubaneswar", "Old Town Heritage Area", "smartphone", "Farooq Ahmed (Son)", "+919937001123", 5, now),
        ("Murugan S.", "+919439887766", "ta", 19.3140, 84.7940, "Ganjam", "Berhampur Railway Colony", "feature_phone", "Kavitha M. (Wife)", "+919439887767", 4, now),
        ("John Smith", "+919811223344", "en", 19.8050, 85.8450, "Puri", "Chakratirtha Road Tourist Zone", "smartphone", "Sarah Smith (Embassy Liaison)", "+919811223345", 1, now),
        ("Priyabrata Jena", "+919438112233", "or", 20.6500, 86.8500, "Kendrapara", "Rajnagar Mangrove Belt", "feature_phone", "Sukanti Jena (Wife)", "+919438112234", 1, now),
        ("Bikram Dash", "+919861445566", "or", 21.4950, 86.9200, "Balasore", "Sahadevkhunta Ward 4", "smartphone", "Pratap Dash (Father)", "+919861445567", 2, now),
        ("Anita Soren", "+919437554433", "or", 20.2961, 85.8245, "Bhubaneswar", "Saheed Nagar Lowlands", "smartphone", "Manoj Soren (Brother)", "+919437554434", 5, now),
        ("Rahul Agarwal", "+919861778899", "hi", 19.8135, 85.8312, "Puri", "Grand Road Commercial", "smartphone", "Vikas Agarwal (Partner)", "+919861778890", 1, now),
        ("Subhashree Mohapatra", "+919437332211", "or", 19.8020, 85.8210, "Puri", "Pentakotta Fishery Village", "smartphone", "Dillip Mohapatra (Husband)", "+919437332212", 1, now)
    ]
    
    c.executemany("""
    INSERT INTO citizens 
    (name, phone, language, lat, lng, district, block_village, device_type, secondary_name, secondary_phone, warden_id, created_at)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, citizens)

    conn.commit()

# Call init_db on module import
init_db()
