"""
LabSteward Management Agent (M1 - M4 Modules)
"""
from typing import Dict, Any
from tools.inventory import query_assets, transition_asset_status
from tools.valuation import estimate_residual_value
from tools.docgen import generate_disposal_draft

def handle_management_intent(intent: str, params: Dict[str, Any], operator_role: str) -> Dict[str, Any]:
    """
    Execute Asset Management tasks:
    M1: Import / Register
    M2: Lend / Return
    M3: Value / Residual Estimation
    M4: Dispose / Scrap application
    """
    if intent == "LEND":
        asset_id = params.get("asset_id", "")
        borrower = params.get("borrower", "碩士班學生")
        assets = query_assets(keyword=asset_id)
        if not assets:
            return {"status": "ERROR", "message": f"找不到指定資產：{asset_id}"}
        asset = assets[0]
        if asset["status"] != "IN_STOCK":
            return {
                "status": "REJECTED",
                "message": f"資產 {asset_id} 目前狀態為 [{asset['status']}]，無法辦理借調！"
            }
        transition_asset_status(asset_id, "ON_LOAN", operator_role)
        return {
            "status": "SUCCESS",
            "action": "LOAN_CHECKOUT",
            "asset_id": asset_id,
            "borrower": borrower,
            "message": f"資產 {asset_id} ({asset['asset_name']}) 成功借出登記予 {borrower}，已排程到期歸還提醒。"
        }

    elif intent == "VALUE":
        asset_id = params.get("asset_id", "")
        assets = query_assets(keyword=asset_id)
        if not assets:
            return {"status": "ERROR", "message": f"找不到指定資產：{asset_id}"}
        asset = assets[0]
        val = estimate_residual_value(asset, condition=params.get("condition", "normal"))
        return {
            "status": "SUCCESS",
            "action": "RESIDUAL_VALUATION",
            "valuation": val,
            "message": f"資產 {asset_id} 雙軌殘值預估完成：法定帳面 NT${val['book_value']:,}，市場估值 NT${val['market_value']:,}。"
        }

    elif intent == "DISPOSE":
        asset_id = params.get("asset_id", "")
        assets = query_assets(keyword=asset_id)
        if not assets:
            return {"status": "ERROR", "message": f"找不到指定資產：{asset_id}"}
        asset = assets[0]
        val = estimate_residual_value(asset)
        
        # Check disposal eligibility
        if val["advice"] == "KEEP_USING":
            return {
                "status": "GUARDRAIL_BLOCKED",
                "asset_id": asset_id,
                "message": f"合規阻斷：資產 {asset_id} 雖達法定年限但功能正常（is_functional=1），依法不得逕行報廢！{val['reason']}"
            }
        
        # Generate disposal draft
        draft_path = generate_disposal_draft(asset, val)
        return {
            "status": "SUCCESS",
            "action": "DISPOSAL_DRAFT_READY",
            "asset_id": asset_id,
            "draft_path": draft_path,
            "valuation": val,
            "message": f"資產 {asset_id} 符合報廢檢核標準，已產出送審公文草稿：{draft_path}。"
        }

    return {"status": "UNKNOWN_INTENT", "message": f"未知的管理意圖：{intent}"}
