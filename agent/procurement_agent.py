"""
LabSteward Procurement Agent (P1 - P4 Modules, Algorithm 3)
"""
from typing import Dict, Any
from tools.inventory import check_idle_or_stock
from tools.web_search import search_vendor_quotes
from tools.guardrail import check_procurement_compliance
from tools.docgen import generate_procurement_draft

def handle_procurement_intent(params: Dict[str, Any], recent_history: list = None) -> Dict[str, Any]:
    """
    Execute Procurement Sub-Agent (Algorithm 3):
    P1: Normalize Spec
    P2: Mandatory Inventory Check (Utilize before Acquire)
    P3: Web Search, Joint Contract, Entity Match, TCO Ranking
    P4: Threshold Rule Evaluation & Draft Generation
    """
    spec = params.get("spec", "GPU工作站")
    qty = params.get("qty", 1)
    budget = params.get("budget", 150000)

    # 1. P2 Mandatory Inventory Pre-check (先共享再採購)
    keywords = [k for k in ["4090", "3090", "GPU", "示波器", "主機", "筆電"] if k.lower() in spec.lower()]
    if not keywords:
        keywords = [spec]
        
    idle_matches = check_idle_or_stock(keywords)
    if idle_matches and not params.get("force_new_purchase", False):
        idle_item = idle_matches[0]
        return {
            "status": "INVENTORY_SATISFIED",
            "action": "SUGGEST_INTERNAL_SHARE",
            "matched_asset": idle_item,
            "message": f"💡【先共享再採購建議】：在庫存排查中發現相符之閒置設備 [{idle_item['asset_id']}: {idle_item['asset_name']}]（保管人：{idle_item['custodian']}，位置：{idle_item['location']}）。建議優先辦理內部借調或移撥手續，免花公帑 NT$ {budget:,} 元！",
            "estimated_savings": budget
        }

    # 2. P3 Multi-vendor Search & TCO Ranking
    quotes = search_vendor_quotes(spec)
    if len(quotes) < 3:
        warning_msg = "有效報價不足 3 家，送審時需補足書面報價或簽請主管核定。"
    else:
        warning_msg = None

    if not quotes:
        return {
            "status": "ERROR",
            "message": f"未搜尋到符合規格 [{spec}] 之有效合格商品！"
        }

    best_quote = quotes[0]
    total_amount = best_quote["price"] * qty

    # 3. P4 Compliance Guardrail & Threshold Evaluation
    compliance = check_procurement_compliance(total_amount, spec, recent_history)
    
    plan = {
        "spec": spec,
        "qty": qty,
        "quotes": quotes,
        "best_quote": best_quote,
        "total_amount": total_amount,
        "route": compliance["route"],
        "route_desc": compliance["route_desc"],
        "required_quotes": compliance["required_quotes"],
        "violations": compliance["violations"],
        "is_compliant": compliance["is_compliant"],
        "citations": compliance["citations"],
        "warning": warning_msg
    }

    if not compliance["is_compliant"]:
        return {
            "status": "GUARDRAIL_VIOLATION",
            "plan": plan,
            "message": f"🚨【採購法規違規阻斷】：{compliance['violations'][0]['message']}"
        }

    # 4. Generate Official Draft
    draft_file = generate_procurement_draft(plan)
    plan["draft_file"] = draft_file

    return {
        "status": "SUCCESS",
        "action": "PROCUREMENT_PLAN_READY",
        "plan": plan,
        "message": f"採購比價與門檻檢核完成（{compliance['route_desc']}）。最優候選廠商：{best_quote['vendor']} (單價 NT${best_quote['price']:,}，TCO NT${best_quote['tco']:,})。已產出送審公文草稿：{draft_file}。"
    }

if __name__ == "__main__":
    res = handle_procurement_intent({"spec": "RTX 4090 工作站", "qty": 1, "budget": 120000})
    print("Procurement Plan:", res)
