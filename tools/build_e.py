import json
from common import *
from build_b import OUT as CASES, EX2, EX3
from build_c import EX4, EX5
from build_d import EX12, EX13
import case_wide as W
import build_a as A

CID1 = W.CASE_ID
RELEASED_PAISA = str(int(A.released * 100))
RELEASED_DISP = bdt(int(A.released * 100)) + " টাকা"
EX1 = {eid: (path, title) for eid, (path, _fn, title) in W.EXHIBITS.items()}

RC = []


def rc(rid, case_id, operation, profile, language, family, input_obj, target, evidence_ids):
    RC.append({"id": rid, "case_id": case_id, "partition": "train", "operation": operation,
               "profile": profile, "language": language, "family": family,
               "input": input_obj, "target": target, "evidence_ids": evidence_ids})


# ---------- TRACE rows ----------
def hdr(issuer, signed, numbered, dated, memo, subject):
    return {"issuer": issuer, "signed": signed, "numbered": numbered, "dated": dated,
            "memo": memo, "subject": subject, "row_label": None, "column_label": None}


rc("rc-shapla-trace-a3", CID1, "TRACE", "trace_legacy", "bn", "wide_reconciliation_dossier",
   {"operation": "TRACE", "atom_id": "shapla-amendments-009",
    "header": hdr("শাপলা ট্রেড হাউস লিমিটেড — বিত্ত পরিচালক", True, True, "2025-05-20", "এসটিএইচ/এএসি/২০২৫-২১", "সংশোধনী-৩"),
    "text": "বে ট্রেডার্সের INV-P-2025-0052-এর বিপরীতে ২৭,৩০০.০০ টাকার ক্রেডিট নোট অনুমোদিত।",
    "claims": [{"claim_id": "claim.shapla.credit_note_claim", "slot": "receivable", "value": "2730000",
                "display": "২৭,৩০০.০০ টাকা", "operand_atoms": ["shapla-amendments-009"], "kind": "value"}]},
   "D বদলায়\nC claim.shapla.credit_note_claim\nV ২৭,৩০০.০০ টাকার ক্রেডিট নোট অনুমোদিত\nW অনুমোদিত",
   ["shapla-amendments"])

rc("rc-shapla-trace-picnic", CID1, "TRACE", "trace_legacy", "bn", "wide_reconciliation_dossier",
   {"operation": "TRACE", "atom_id": "shapla-emails-012",
    "header": hdr("নুসরাত জাহান (এডমিন)", False, False, "2025-06-26", None, "অফিস পিকনিক"),
    "text": "শুক্রবারের অফিস পিকনিকের জন্য কে বাস ভাড়া আনবে, দয়া করে জানান।",
    "claims": [{"claim_id": "claim.shapla.released_total", "slot": "total", "value": RELEASED_PAISA,
                "display": RELEASED_DISP, "operand_atoms": ["shapla-emails-012"], "kind": "value"}]},
   "D বাদ\nC claim.shapla.released_total\nV অফিস পিকনিকের জন্য কে বাস ভাড়া আনবে\nW ভিন্ন-বিষয়",
   ["shapla-emails"])

rc("rc-shapla-trace-dup", CID1, "TRACE", "trace_legacy", "bn", "wide_reconciliation_dossier",
   {"operation": "TRACE", "atom_id": "shapla-ledger-q2-008",
    "header": hdr("শাপলা ট্রেড হাউস লিমিটেড — হিসাব বিভাগ", False, False, "2025-05-19", None, None),
    "text": "L-307,Rafiqul Islam (Sales),2025-05-19,ADV-Q-2025-0088,125000.00,certificate_on_file",
    "claims": [{"claim_id": "claim.shapla.released_total", "slot": "total", "value": RELEASED_PAISA,
                "display": RELEASED_DISP, "operand_atoms": ["shapla-ledger-q2-008"], "kind": "value"}]},
   "D বাদ\nC claim.shapla.released_total\nV Rafiqul Islam (Sales)\nW পুনরাবৃত্ত",
   ["shapla-ledger-q2"])

rc("rc-brahma-trace-opening", "bn-recon-brahmaputra-003", "TRACE", "trace_legacy", "bn", "supplier_reconciliation",
   {"operation": "TRACE", "atom_id": "brahmaputra-statement-003",
    "header": hdr("ব্রহ্মপুত্র হার্ডওয়্যার (কাল্পনিক)", False, False, "2025-05-01", None, None),
    "text": "বকেয়া প্রারম্ভিক (০১-০৫-২০২৫) ৫,০০,০০০.০০ ড",
    "claims": [{"claim_id": "claim.brahma.opening_balance", "slot": "opening_balance", "value": "458200.00",
                "display": "৪,৫৮,২০০.০০ টাকা", "operand_atoms": ["brahmaputra-statement-003"], "kind": "value"}]},
   "D বদলায়\nC claim.brahma.opening_balance\nV ৫,০০,০০০.০০ ড\nW অনুমোদিত",
   ["brahmaputra-statement"])

rc("rc-pollux-trace-supersede", "en-research-pollux-013", "TRACE", "trace_legacy", "en", "definition_conflict_hold",
   {"operation": "TRACE", "atom_id": "pollux-handbook-3rd-004",
    "header": hdr("Pollux Academic Press (fictional)", False, True, "2019", None, "Entry 12.4"),
    "text": "Entry 12.4: working capital ratio = current assets divided by current liabilities",
    "claims": [{"claim_id": "claim.eastwind.wc_ratio_definition", "slot": "definition", "value": "current assets divided by current liabilities",
                "display": "current assets / current liabilities (3rd ed.)", "operand_atoms": ["pollux-handbook-3rd-004"], "kind": "value"}]},
   "D বাদ\nC claim.eastwind.wc_ratio_definition\nV current assets divided by current liabilities\nW প্রতিস্থাপন",
   ["pollux-handbook-3rd"])

rc("rc-pollux-trace-covenant", "en-research-pollux-013", "TRACE", "trace_legacy", "en", "definition_conflict_hold",
   {"operation": "TRACE", "atom_id": "eastwind-covenant-003",
    "header": hdr("Eastwind Imports lender (fictional)", True, True, "2023-05-04", None, None),
    "text": "\"The working capital ratio shall not fall below 1.75.\"",
    "claims": [{"claim_id": "claim.eastwind.wc_ratio_governing", "slot": "governing_definition", "value": "unresolved",
                "display": "governing definition not established", "operand_atoms": ["eastwind-covenant-003"], "kind": "value"}]},
   "D অনিশ্চিত\nC -\nV -\nW -",
   ["eastwind-covenant"])

rc("rc-novustex-trace-overdraft", "en-board-novustex-002", "TRACE", "trace_legacy", "en", "board_covenant_decision",
   {"operation": "TRACE", "atom_id": "novustex-debt-003",
    "header": hdr(None, False, False, "2025-06-30", None, None),
    "text": "Overdraft KCB-OD,14500000,930000,0",
    "claims": [{"claim_id": "claim.novustex.existing_debt", "slot": "existing_debt", "value": "86500000",
                "display": "BDT 86,500,000", "operand_atoms": ["novustex-debt-002", "novustex-debt-003"], "kind": "value"}]},
   "D বাঁধা\nC claim.novustex.existing_debt\nV Overdraft KCB-OD,14500000,930000,0\nW -",
   ["novustex-debt"])

# ---------- EXTRACT rows ----------
NEUTRAL6 = {"issuer": None, "signed": None, "numbered": None, "dated": None, "memo": None, "subject": None}
ROWLABEL = "Zuboria (ZBA) | SP.POP.TOTL | Population, total"

rc("rc-zuboria-extract-header", "en-extract-zuboria-004", "EXTRACT", "extract_legacy", "en", "indicator_extraction",
   {"operation": "EXTRACT", "atom_id": "zuboria-header",
    "header": dict(NEUTRAL6, row_label=ROWLABEL, column_label=None),
    "text": "Zuboria (ZBA) | SP.POP.TOTL | Population, total | "},
   "T1 source|*|country\nP1 Zuboria (ZBA)\nQ1 in_force\n"
   "T2 source|*|series\nP2 SP.POP.TOTL\nQ2 in_force\n"
   "T3 source|*|unit\nP3 Population, total\nQ3 in_force",
   ["zuboria-indicator"])

for yr, val, final in [("2021", "5840000", False), ("2022", "5910000", False), ("2023", "5985000", True)]:
    rc("rc-zuboria-extract-obs-" + yr, "en-extract-zuboria-004", "EXTRACT", "extract_legacy", "en", "indicator_extraction",
       {"operation": "EXTRACT", "atom_id": "zuboria-obs-" + yr,
        "header": dict(NEUTRAL6, row_label=ROWLABEL, column_label=yr + "; Population, total"),
        "text": "%s=%s%s" % (yr, val, "" if final else ", ")},
       "T1 source|*|year\nP1 %s\nQ1 in_force\nT2 source|*|value\nP2 %s=%s\nQ2 in_force" % (yr, yr, val),
       ["zuboria-indicator"])

# ---------- DEMAND row ----------
REQ5 = "Using the saved Clarion Islands access table, give me the annual urban-rural gap in percentage points for 2018 through 2022 and tell me whether the gap narrowed over the period."
rc("rc-clarion-demand-gap", "en-demand-clarion-005", "DEMAND", "demand_routing", "en", "indicator_gap_request",
   {"operation": "DEMAND", "request": REQ5},
   "TYPE public_statistics.gap",
   ["clarion-rows"])

ROLE_PART1 = RC
