"""
LabSteward Document Generation Tool
Generates formatted draft documents for official university review.
"""
import os
from typing import Dict, Any

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "generated_docs")

def ensure_out_dir():
    os.makedirs(OUT_DIR, exist_ok=True)

def generate_procurement_draft(plan: Dict[str, Any]) -> str:
    """Generate university procurement requisition draft."""
    ensure_out_dir()
    filepath = os.path.join(OUT_DIR, "procurement_requisition_draft.md")
    content = f"""# 國立大學請購申請單暨比價分析草稿 (LabSteward 生成)

**請購編號**：REQ-202611-001  
**請購單位**：資訊工程學系 人工智慧與系統實驗室  
**申請日期**：2026 年 11 月 11 日  
**主要用途**：支援碩士班深度學習模型訓練與科研實驗  

---

## 壹、庫存前置排查結論
依據本校資產管理規範，請購前已進行自有庫存與全校共享清查：
- 庫存狀態：**無閒置相符規格資產可供借用，確有實質新購需求**。

---

## 貳、採購金額與招標途徑判定
- **預計採購總額**：NT$ {plan.get('total_amount', 0):,d} 元
- **法規分類途徑**：{plan.get('route_desc', '小額採購')}
- **合規檢驗**：已通過 30 天拆單防禦檢驗，無化整為零情事。

---

## 參、市場比價與廠商報價清單 (依 TCO 排序)
"""
    for i, q in enumerate(plan.get("quotes", []), 1):
        content += f"""
### 廠商 {i}：{q['vendor']}
- **產品型號**：{q['product_name']}
- **報價金額**：NT$ {q['price']:,d} 元 (含營業稅)
- **保固條件**：{q['warranty_years']} 年原廠保固
- **交貨天數**：{q['lead_time_days']} 日工作天
- **總持有成本 (TCO)**：NT$ {q['tco']:,d} 元
"""
    content += """
---
## 肆、審查簽核欄
- **申請人 (學生/助理)**：____________________
- **實驗室設備長**：____________________
- **計畫主持人 (PI/指導教授)**：____________________
"""
    with open(filepath, mode="w", encoding="utf-8") as f:
        f.write(content)
    return filepath

def generate_disposal_draft(asset: Dict[str, Any], valuation: Dict[str, Any]) -> str:
    """Generate university asset disposal draft."""
    ensure_out_dir()
    filepath = os.path.join(OUT_DIR, f"disposal_application_{asset.get('asset_id', 'draft')}.md")
    content = f"""# 國立大學財產減損/報廢申請審查表草稿 (LabSteward 生成)

**財產編號**：{asset.get('asset_id')}  
**品名規格**：{asset.get('asset_name')}  
**取得成本**：NT$ {asset.get('cost', 0):,d} 元  
**購置日期**：{asset.get('purchase_date')} (已使用 {valuation.get('years_used', 0)} 年)  
**法定最低年限**：{valuation.get('statutory_min_life', 0)} 年  

---

## 壹、雙軌殘值評估與折舊現況
- **法定帳面價值 (直線法)**：NT$ {valuation.get('book_value', 0):,d} 元
- **市場公允估值 (指數衰減)**：NT$ {valuation.get('market_value', 0):,d} 元 (80% 區間: NT$ {valuation.get('market_interval', [0,0])[0]:,d} ~ {valuation.get('market_interval', [0,0])[1]:,d})
- **評估建議**：{valuation.get('advice')}
- **法規依據與說明**：{valuation.get('reason')}

---

## 貳、審核簽章
- **財產保管人**：____________________
- **系所財產承辦員**：____________________
- **指導教授 / 單位主管**：____________________
- **總務處保管組審核**：____________________
"""
    with open(filepath, mode="w", encoding="utf-8") as f:
        f.write(content)
    return filepath
