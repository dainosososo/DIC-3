"""
LabSteward Multi-Vendor Web Search & Entity Matching Tool
"""
from typing import List, Dict, Any

MOCK_VENDORS = [
    {
        "vendor": "聯強國際校園特約商",
        "product_name": "NVIDIA GeForce RTX 4090 24GB AI 訓練工作站",
        "price": 118000,
        "warranty_years": 3,
        "shipping_cost": 0,
        "lead_time_days": 5,
        "source": "電子採購網/共同供應契約",
        "is_joint_contract": True
    },
    {
        "vendor": "欣亞數位科技",
        "product_name": "華碩 ROG RTX 4090 深度學習研發主機 (i9/64G/2TB SSD)",
        "price": 112000,
        "warranty_years": 3,
        "shipping_cost": 500,
        "lead_time_days": 3,
        "source": "電商報價",
        "is_joint_contract": False
    },
    {
        "vendor": "原價屋線上估價",
        "product_name": "微星 RTX 4090 24G 創作者客製主機 (含營業稅發票)",
        "price": 109000,
        "warranty_years": 1,
        "shipping_cost": 300,
        "lead_time_days": 7,
        "source": "實體通路",
        "is_joint_contract": False
    },
    {
        "vendor": "未知蝦皮賣場 (異常低價)",
        "product_name": "二手散熱片 RTX 4090 顯卡專用風扇配件",
        "price": 2500,
        "warranty_years": 0,
        "shipping_cost": 60,
        "lead_time_days": 14,
        "source": "拍賣網站",
        "is_joint_contract": False
    }
]

def search_vendor_quotes(spec_keyword: str) -> List[Dict[str, Any]]:
    """
    Search candidate quotations, perform entity matching to discard accessories/noise,
    and rank by Total Cost of Ownership (TCO).
    """
    candidates = []
    kw_lower = spec_keyword.lower()
    
    for item in MOCK_VENDORS:
        # Entity matching & noise filtering
        name_lower = item["product_name"].lower()
        if "配件" in name_lower or "風扇" in name_lower or "二手" in name_lower:
            continue # Entity match failure: accessory/refurbished
        if "4090" in kw_lower and "4090" in name_lower:
            candidates.append(item)
        elif "示波器" in kw_lower and "示波器" in name_lower:
            candidates.append(item)
            
    # Calculate Total Cost of Ownership (TCO)
    # TCO = Price + Shipping + Risk_adjustment(Warranty penalty: NT$ 5000 per year below 3 years)
    for c in candidates:
        warranty_penalty = max(0, 3 - c["warranty_years"]) * 5000
        c["tco"] = c["price"] + c["shipping_cost"] + warranty_penalty
        
    candidates.sort(key=lambda x: x["tco"])
    return candidates

if __name__ == "__main__":
    quotes = search_vendor_quotes("RTX 4090 工作站")
    for q in quotes:
        print(f"Vendor: {q['vendor']} | Price: NT${q['price']:,} | TCO: NT${q['tco']:,}")
