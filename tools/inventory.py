"""
LabSteward SQLite Inventory and State Machine Tool
"""
import sqlite3
import csv
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "labsteward.db")
SAMPLE_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "sample_assets.csv")

VALID_STATUSES = {"IN_STOCK", "ON_LOAN", "IDLE", "UNDER_MAINTENANCE", "PENDING_DISPOSAL", "DISPOSED"}

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DB_PATH, csv_file: str = SAMPLE_CSV) -> None:
    """Initialize database tables and seed from sample CSV if empty."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        asset_id TEXT PRIMARY KEY,
        asset_name TEXT NOT NULL,
        category_code TEXT NOT NULL,
        cost REAL NOT NULL,
        purchase_date TEXT NOT NULL,
        custodian TEXT NOT NULL,
        location TEXT NOT NULL,
        status TEXT NOT NULL,
        is_functional INTEGER NOT NULL,
        utilization_rate REAL NOT NULL,
        estimated_repair_cost REAL NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS loan_records (
        loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id TEXT NOT NULL,
        borrower TEXT NOT NULL,
        borrow_date TEXT NOT NULL,
        expected_return_date TEXT NOT NULL,
        actual_return_date TEXT,
        status TEXT NOT NULL,
        FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        operator_role TEXT NOT NULL,
        action TEXT NOT NULL,
        details TEXT NOT NULL
    );
    """)
    conn.commit()

    # Seed if assets table empty
    cur.execute("SELECT COUNT(*) FROM assets")
    if cur.fetchone()[0] == 0 and os.path.exists(csv_file):
        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                cur.execute("""
                INSERT INTO assets (asset_id, asset_name, category_code, cost, purchase_date, custodian, location, status, is_functional, utilization_rate, estimated_repair_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    r["asset_id"], r["asset_name"], r["category_code"], float(r["cost"]),
                    r["purchase_date"], r["custodian"], r["location"], r["status"],
                    int(r["is_functional"]), float(r["utilization_rate"]), float(r["estimated_repair_cost"])
                ))
        conn.commit()
    conn.close()

def query_assets(keyword: Optional[str] = None, status_filter: Optional[List[str]] = None, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Query assets matching keywords and statuses."""
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()
    
    query = "SELECT * FROM assets WHERE 1=1"
    params = []
    
    if keyword:
        query += " AND (asset_name LIKE ? OR asset_id LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])
        
    if status_filter:
        placeholders = ",".join(["?"] * len(status_filter))
        query += f" AND status IN ({placeholders})"
        params.extend(status_filter)
        
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def check_idle_or_stock(spec_keywords: List[str], db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Check if any idle or available asset in stock matches the required spec keywords."""
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM assets WHERE status IN ('IDLE', 'IN_STOCK')")
    candidates = [dict(r) for r in cur.fetchall()]
    conn.close()
    
    matches = []
    for asset in candidates:
        name_lower = asset["asset_name"].lower()
        if any(kw.lower() in name_lower for kw in spec_keywords):
            matches.append(asset)
    return matches

def transition_asset_status(asset_id: str, new_status: str, operator_role: str, db_path: str = DB_PATH) -> bool:
    """Transition asset state machine safely."""
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {new_status}")
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT status FROM assets WHERE asset_id = ?", (asset_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False
    
    old_status = row["status"]
    cur.execute("UPDATE assets SET status = ? WHERE asset_id = ?", (new_status, asset_id))
    cur.execute("""
    INSERT INTO audit_logs (timestamp, operator_role, action, details)
    VALUES (datetime('now', 'localtime'), ?, 'STATUS_TRANSITION', ?)
    """, (operator_role, f"Asset {asset_id} transitioned from {old_status} to {new_status}"))
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    init_db()
    assets = query_assets()
    print(f"Initialized inventory DB with {len(assets)} assets.")
