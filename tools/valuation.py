"""
LabSteward Dual-Track Residual Value Estimation Engine (Algorithm 2)
"""
import csv
import os
import math
from datetime import datetime
from typing import Dict, Any, Tuple

CLASS_TABLE_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "std_class_table.csv")
MARKET_LISTINGS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "market_listings.csv")

def load_std_classes() -> Dict[str, Dict[str, Any]]:
    classes = {}
    if os.path.exists(CLASS_TABLE_PATH):
        with open(CLASS_TABLE_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                classes[r["category_code"]] = {
                    "category_name": r["category_name"],
                    "min_life_years": float(r["min_life_years"]),
                    "annual_market_depreciation_rate": float(r["annual_market_depreciation_rate"]),
                    "description": r["description"]
                }
    return classes

def calculate_years_since(purchase_date_str: str) -> float:
    try:
        p_date = datetime.strptime(purchase_date_str, "%Y-%m-%d")
        now = datetime(2026, 11, 11) # Benchmark reference date
        delta_days = (now - p_date).days
        return max(0.0, delta_days / 365.25)
    except Exception:
        return 3.0

def estimate_residual_value(asset: Dict[str, Any], condition: str = "normal") -> Dict[str, Any]:
    """
    Dual-track Residual Value Estimation:
    1. Book Value: Straight-line depreciation based on statutory minimum useful life.
    2. Market Value: Log-linear / Exponential depreciation adjusted for condition and confidence intervals.
    """
    classes = load_std_classes()
    cat_code = str(asset.get("category_code", "3140103"))
    meta = classes.get(cat_code, {
        "category_name": "一般資訊儀器",
        "min_life_years": 3.0,
        "annual_market_depreciation_rate": 0.20
    })
    
    cost = float(asset.get("cost", 100000))
    purchase_date = str(asset.get("purchase_date", "2023-01-01"))
    t = calculate_years_since(purchase_date)
    L = meta["min_life_years"]
    
    # 1. Statutory Book Value (Straight-line)
    v_book = cost * max(0.0, 1.0 - (t / L))
    
    # 2. Market Fair Value (Exponential decay)
    d = meta["annual_market_depreciation_rate"]
    q_map = {"normal": 1.0, "minor_flaw": 0.85, "faulty": 0.40}
    q = q_map.get(condition, 1.0)
    
    v_mkt = cost * math.pow(max(0.01, 1.0 - d), t) * q
    delta = 0.15 # 15% uncertainty band
    v_low = max(500.0, v_mkt * (1.0 - delta))
    v_high = v_mkt * (1.0 + delta)
    
    # 3. Decision Logic & Recommendation
    is_functional = int(asset.get("is_functional", 1)) == 1
    utilization = float(asset.get("utilization_rate", 0.5))
    repair_cost = float(asset.get("estimated_repair_cost", 0.0))
    
    if t >= L and is_functional:
        advice = "KEEP_USING"
        reason = f"已達法定年限({L:.0f}年)但功能正常，依法不得直接報廢，建議留任備用或教學使用。"
    elif not is_functional and repair_cost > v_high:
        advice = "DISPOSE"
        reason = f"設備損壞且預估修復費用(NT${repair_cost:,.0f})超過市場公允殘值上限(NT${v_high:,.0f})，符合專案報廢條件。"
    elif utilization < 0.15:
        advice = "TRANSFER_OR_SHARE"
        reason = f"設備年使用率僅 {utilization*100:.1f}%，建議登錄校內共享平台或移撥給其他實驗室以發揮效益。"
    else:
        advice = "REPAIR_OR_KEEP"
        reason = "設備運作或簡易維修效益優於報廢新購，建議保留日常使用。"
        
    return {
        "asset_id": asset.get("asset_id", "UNKNOWN"),
        "asset_name": asset.get("asset_name", "UNKNOWN"),
        "years_used": round(t, 2),
        "statutory_min_life": L,
        "book_value": round(v_book, 2),
        "market_value": round(v_mkt, 2),
        "market_interval": [round(v_low, 2), round(v_high, 2)],
        "confidence": "HIGH" if t < 5 else "LOW_CONFIDENCE",
        "advice": advice,
        "reason": reason
    }

if __name__ == "__main__":
    sample = {
        "asset_id": "LAB-2023-OSC-01",
        "asset_name": "Keysight 200MHz 示波器",
        "category_code": "3120101",
        "cost": 88000,
        "purchase_date": "2023-05-10",
        "is_functional": 1,
        "utilization_rate": 0.40,
        "estimated_repair_cost": 0
    }
    res = estimate_residual_value(sample)
    print("Residual Value Estimate:", res)
