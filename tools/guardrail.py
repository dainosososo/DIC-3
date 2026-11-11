"""
LabSteward Compliance Guardrail and Audit Engine
"""
try:
    import yaml
except ImportError:
    yaml = None
import os
import glob
import re
from typing import Dict, Any, List

RULES_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "rules.yaml")
REGS_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge", "regulations")

def load_rules() -> Dict[str, Any]:
    if os.path.exists(RULES_PATH):
        if yaml:
            try:
                with open(RULES_PATH, mode="r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except Exception:
                pass
        # Fallback simple parser for rules.yaml
        rules = {"procurement": {"thresholds": {}}}
        try:
            with open(RULES_PATH, mode="r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "small_purchase:" in line:
                        m = re.search(r"small_purchase:\s*(\d+)", line)
                        if m: rules["procurement"]["thresholds"]["small_purchase"] = int(m.group(1))
                    elif "announcement:" in line:
                        m = re.search(r"announcement:\s*(\d+)", line)
                        if m: rules["procurement"]["thresholds"]["announcement"] = int(m.group(1))
            if "small_purchase" in rules["procurement"]["thresholds"]:
                return rules
        except Exception:
            pass
    return {
        "procurement": {
            "thresholds": {"small_purchase": 150000, "announcement": 1500000}
        }
    }

def check_procurement_compliance(total_amount: float, item_name: str, recent_purchases: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Evaluate procurement compliance:
    - Route determination (Small / Under Announcement / Tender)
    - Anti-split order detection (Government Procurement Act Article 14)
    - Regulation citations
    """
    rules = load_rules()
    t_small = rules.get("procurement", {}).get("thresholds", {}).get("small_purchase", 150000)
    t_announce = rules.get("procurement", {}).get("thresholds", {}).get("announcement", 150000)

    violations = []
    warnings = []

    # 1. Route Determination
    if total_amount <= t_small:
        route = "SMALL_PURCHASE"
        route_desc = "小額採購 (NT$ 150,000 以下)：得免公開徵求，由單位主管核決逕洽廠商辦理。"
        required_quotes = 1
    elif total_amount < t_announce:
        route = "UNDER_ANNOUNCEMENT"
        route_desc = "未達公告金額 (逾 15 萬至 150 萬元)：應公開取得 3 家以上廠商書面報價或企劃書。"
        required_quotes = 3
    else:
        route = "PUBLIC_TENDER"
        route_desc = "公告金額以上 (NT$ 1,500,000 以上)：須刊登政府採購公報公開招標，並檢附詳細市價行情與底價分析。"
        required_quotes = 3

    # 2. Anti-split Order Detection
    if recent_purchases:
        cumulative_sim = 0.0
        for p in recent_purchases:
            p_name = p.get("item_name", "")
            # check simple token overlap similarity
            if any(k in item_name for k in ["GPU", "主機", "電腦", "示波器"]) and any(k in p_name for k in ["GPU", "主機", "電腦", "示波器"]):
                cumulative_sim += float(p.get("amount", 0.0))
        
        if (total_amount + cumulative_sim) > t_small and total_amount <= t_small:
            violations.append({
                "code": "SPLIT_ORDER_SUSPECTED",
                "law": "政府採購法第十四條",
                "message": f"偵測到 30 天內同類品項累計金額已達 NT${cumulative_sim:,.0f}，本次加總達 NT${(total_amount+cumulative_sim):,.0f}，疑似化整為零分批採購規避招標程序！"
            })

    # 3. Retrieve Law Citations
    citations = []
    if os.path.exists(REGS_DIR):
        for fpath in glob.glob(os.path.join(REGS_DIR, "*.md")):
            with open(fpath, mode="r", encoding="utf-8") as f:
                content = f.read()
                if "政府採購法" in content and ("招標" in content or "金額" in content):
                    citations.append({
                        "source": os.path.basename(fpath),
                        "snippet": "政府採購法金額門檻：小額採購 15 萬元以下、公告金額 150 萬元以上。"
                    })

    return {
        "total_amount": total_amount,
        "route": route,
        "route_desc": route_desc,
        "required_quotes": required_quotes,
        "violations": violations,
        "is_compliant": len(violations) == 0,
        "citations": citations
    }

if __name__ == "__main__":
    res = check_procurement_compliance(120000, "GPU運算主機", [{"item_name": "GPU伺服器", "amount": 80000}])
    print("Compliance Check Result:", res)
