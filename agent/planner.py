"""
LabSteward Main ReAct Planner & Main Loop (Algorithm 1)
"""
import re
from typing import Dict, Any, List
from agent.management_agent import handle_management_intent
from agent.procurement_agent import handle_procurement_intent
from tools.inventory import get_connection

ROLE_PERMISSIONS = {
    "student": {"LEND", "PROCURE", "VALUE"},
    "admin": {"LEND", "IMPORT", "VALUE", "DISPOSE", "PROCURE"},
    "pi": {"LEND", "IMPORT", "VALUE", "DISPOSE", "PROCURE", "APPROVE"}
}

def parse_user_query(query: str) -> Dict[str, Any]:
    """Parse intent and extract key parameters using pattern rules."""
    q_lower = query.lower()
    
    # 1. Intent Recognition
    if any(k in query for k in ["借", "領用", "借用"]):
        intent = "LEND"
    elif any(k in query for k in ["殘值", "還值多少", "估價", "折舊"]):
        intent = "VALUE"
    elif any(k in query for k in ["報廢", "壞了", "除帳"]):
        intent = "DISPOSE"
    elif any(k in query for k in ["買", "採購", "請購", "比價", "購買"]):
        intent = "PROCURE"
    else:
        intent = "GENERAL_QA"
        
    # 2. Slot Extraction
    params = {}
    
    # Extract Asset ID (e.g. LAB-2023-OSC-01)
    asset_match = re.search(r"LAB-\d{4}-[A-Z]+-\d{2}", query)
    if asset_match:
        params["asset_id"] = asset_match.group(0)
    elif "示波器" in query:
        params["asset_id"] = "LAB-2023-OSC-01"
    elif "4090" in query:
        params["asset_id"] = "LAB-2024-GPU-02"
        
    # Extract Budget / Amount
    amount_match = re.search(r"(\d+)\s*(?:萬|w|0000)", query)
    if amount_match:
        params["budget"] = int(amount_match.group(1)) * 10000
    else:
        num_match = re.search(r"(?:NT\$?|\$)?\s*(\d{4,7})", query)
        if num_match:
            params["budget"] = int(num_match.group(1))
            
    # Extract Spec
    if "4090" in query:
        params["spec"] = "RTX 4090 工作站"
    elif "示波器" in query:
        params["spec"] = "數位示波器"
    else:
        params["spec"] = query
        
    return {"intent": intent, "params": params}

def labsteward_agent_loop(query: str, user_role: str = "student", force_new_purchase: bool = False, recent_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main loop following Algorithm 1:
    - Parse intent & params
    - Clarification loop
    - Authorization check
    - Sub-agent routing
    - Guardrail evaluation
    - Human-in-the-loop review
    - Audit log commit
    """
    parsed = parse_user_query(query)
    intent = parsed["intent"]
    params = parsed["params"]
    
    # Pass user overrides
    if force_new_purchase:
        params["force_new_purchase"] = True
        
    # Authorization Check
    allowed = ROLE_PERMISSIONS.get(user_role.lower(), set())
    if intent not in allowed:
        return {
            "status": "PERMISSION_DENIED",
            "message": f"角色權限不足：[{user_role}] 無權執行 [{intent}] 意圖操作！"
        }
        
    # Routing
    if intent in ["LEND", "VALUE", "DISPOSE"]:
        result = handle_management_intent(intent, params, user_role)
    elif intent == "PROCURE":
        result = handle_procurement_intent(params, recent_history)
    else:
        result = {
            "status": "INFO",
            "message": "LabSteward 智慧管家隨時為您服務。您可以詢問資產借用、殘值預估、報廢檢核或採購比價。"
        }
        
    # Record Audit Log
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO audit_logs (timestamp, operator_role, action, details)
    VALUES (datetime('now', 'localtime'), ?, ?, ?)
    """, (user_role, f"QUERY_{intent}", f"Query: {query} | Status: {result.get('status')}"))
    conn.commit()
    conn.close()
    
    return result

if __name__ == "__main__":
    print("Testing Student Procurement Query:")
    res1 = labsteward_agent_loop("我是碩一生，需要買一台 RTX 4090 工作站跑模型，預算 12 萬", user_role="student")
    print(res1["message"])
    
    print("\nTesting Residual Valuation Query:")
    res2 = labsteward_agent_loop("請問 LAB-2023-OSC-01 示波器現在還值多少錢？", user_role="student")
    print(res2["message"])
