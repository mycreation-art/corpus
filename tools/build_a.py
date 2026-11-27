import json
from decimal import Decimal
from common import *
import case_wide as W

CID = W.CASE_ID
D = "cases/" + CID

# ---------- exhibits ----------
EX = {}
for eid, (path, fn, _t) in W.EXHIBITS.items():
    EX[eid] = (path, write_member(path, fn()))


# ---------- solution computations (two methods) ----------
paise = lambda s: int((Decimal(s) * 100).to_integral_value())
taka = lambda p: Decimal(p) / 100

pairs = []
for b in W.BANK_ROWS:
    matches = [l for l in W.LEDGER_ROWS if l[3] == b[3]]
    pairs.append((b, matches))

dup_rows = [l for l in W.LEDGER_ROWS if l[0] == "L-307"]
missing_annex = [l for l in W.LEDGER_ROWS if l[5] == "missing_annex"]
charge_rows = [b for b in W.BANK_ROWS if b[3] == "BANK-CHG"]
july = [b for b in W.BANK_ROWS if b[3] == "INV-D-2025-0047"]
credit_note = paise("27300.00")

# bank total debits, two methods
total_bank_m1 = sum(taka(paise(b[4])) for b in W.BANK_ROWS)
total_bank_m2 = taka(sum(paise(b[4]) for b in W.BANK_ROWS))
assert total_bank_m1 == total_bank_m2

# ledger total (excluding duplicate L-307), two methods
led_valid = [l for l in W.LEDGER_ROWS if l[0] != "L-307"]
total_led_m1 = sum(taka(paise(l[4])) for l in led_valid)
total_led_m2 = taka(sum(paise(l[4]) for l in led_valid))
assert total_led_m1 == total_led_m2

dup_amount = taka(paise(dup_rows[0][4]))
cross_total = taka(paise("228600.00") + paise("115000.00"))

held_amount = taka(paise(missing_annex[0][4]))
charge_amount = taka(paise(charge_rows[0][4]))
july_amount = taka(paise(july[0][4]))
usd_check_m1 = Decimal("5200") * Decimal("123.00")
usd_check_m2 = taka(5200 * 12300)
assert usd_check_m1 == usd_check_m2 == taka(paise("639600.00"))
credit_check = taka(paise("228600.00")) - taka(credit_note)
assert credit_check == taka(paise("201300.00"))

unmatched_ledger = [l for l in led_valid if not any(b[3] == l[3] for b in W.BANK_ROWS)]
assert unmatched_ledger == [], unmatched_ledger
matched_pairs = [(b, m[0]) for b, m in pairs if m]
assert {b[3] for b, _ in matched_pairs} == {l[3] for _, l in matched_pairs}

SOLUTION = {
    "bank_debits_total_bdt": str(total_bank_m2),
    "ledger_valid_total_bdt": str(total_led_m2),
    "ledger_duplicate_excluded_bdt": str(dup_amount),
    "cross_pair_equal_totals_bdt": str(cross_total),
    "hold_missing_annex_bdt": str(held_amount),
    "unallocated_bank_charge_bdt": str(charge_amount),
    "july_forward_commitment_bdt": str(july_amount),
    "credit_note_receivable_bdt": str(taka(credit_note)),
    "methods": ["decimal_taka", "integer_paisa"],
    "method_agreement": True,
}

REG = []
for b, l in matched_pairs:
    if l[5] == "missing_annex":
        REG.append({"txn": b[0], "ref": b[3], "amount_bdt": b[4], "decision": "hold",
                    "reason": "সরবরাহ সনদ (ডেলিভারি সার্টিফিকেট) নথিভুক্ত নয়", "refs": [b[0], l[0]]})
    elif l[3] == "INV-D-2025-0047":
        REG.append({"txn": b[0], "ref": b[3], "amount_bdt": b[4], "decision": "release",
                    "reason": "চুক্তি হার ১২৩.০০ দিয়ে যাচাইকৃত (সংশোধনী-২)", "refs": [b[0], l[0], "A-2"]})
    elif l[3] == "INV-P-2025-0052":
        REG.append({"txn": b[0], "ref": b[3], "amount_bdt": b[4], "decision": "release",
                    "reason": "ক্রেডিট নোট CR-2025-0031 পরবর্তী পরিশোধে প্রযোজ্য (সংশোধনী-৩ পাদটীকা)",
                    "refs": [b[0], l[0], "A-3"]})
    else:
        REG.append({"txn": b[0], "ref": b[3], "amount_bdt": b[4], "decision": "release",
                    "reason": "রেফারেন্স ও মূল্য মিলেছে", "refs": [b[0], l[0]]})

released = sum(taka(paise(r["amount_bdt"])) for r in REG if r["decision"] == "release")
held = sum(taka(paise(r["amount_bdt"])) for r in REG if r["decision"] == "hold")
assert released + held == total_bank_m2 - charge_amount
SOLUTION["released_total_bdt"] = str(released)
SOLUTION["held_total_bdt"] = str(held)
SOLUTION["register_rows"] = len(REG)


def reg_txt():
    L = []
    L.append("শাপলা ট্রেড হাউস লিমিটেড — কোয়ার্টার-শেষ মিলকরণ ও রিলিজ/হোল্ড রেজিস্টার")
    L.append("সময়কাল: ২০২৫ সালের এপ্রিল-জুন (কিউ২); এ/সি ৫০২.১১৩০.৮৮৪৫, কর্ণফুলী বাণিজ্যিক ব্যাংক")
    L.append("অনুরোধকারী: ফারহানা রহমান (বিত্ত পরিচালক); প্রস্তুত: হিসাব বিভাগ; সংস্করণ: rev3")
    L.append("সময়সীমা: ২০২৫-০৬-৩০ ১৭:০০ UTC (ঢাকা সময় রাত ১১টা) — ইমেইল থ্রেড অনুযায়ী চূড়ান্ত")
    L.append("")
    L.append("রেজিস্টার সারি (৫০,০০০ টাকার সমান বা বেশি মূল্যের পরিশোধ):")
    for r in REG:
        L.append("%s | %s | %s টাকা | %s | %s | উৎস: %s" % (
            r["txn"], r["ref"], bdt(paise(r["amount_bdt"])), r["decision"], r["reason"], ", ".join(r["refs"])))
    L.append("")
    L.append("সারসংক্ষেপ লাইন (৫০,০০০ টাকার নিচে): ব্যাংক চার্জ %s টাকা (এলোকেশনহীন, এসক্যালেশন চলছে)" % bdt(paise(charge_rows[0][4])))
    L.append("মোট ব্যাংক ডেবিট (কিউ২): %s টাকা" % bdt(int(total_bank_m2 * 100)))
    L.append("রিলিজড (মোট): %s টাকা" % bdt(int(released * 100)))
    L.append("হোল্ড (মোট): %s টাকা" % bdt(int(held * 100)))
    L.append("বাদ (ডুপ্লিকেট খাতা সারি L-307, Rafiqul Islam (Sales)): %s টাকা" % bdt(paise(dup_rows[0][4])))
    L.append("জুলাই পরিশোধ রানের প্রতিশ্রুত (সংশোধনী-৪, rev2 অনুযায়ী যোগ): %s টাকা" % bdt(paise(july[0][4])))
    L.append("ক্রেডিট নোট দাবি (বে ট্রেডার্স, CR-2025-0031): %s টাকা" % bdt(credit_note))
    L.append("")
    L.append("উল্লেখযোগ্য ব্যতিক্রম:")
    L.append("১) L-307: ADV-Q-2025-0088 দুই ব্যক্তির নামে পোস্ট হয়েছে; ক্রয় বিভাগের রফিকুল ইসলাম সঠিক; বিক্রয় বিভাগের সারি ডুপ্লিকেট।")
    L.append("২) B-105/L-305 ও B-114/L-313: দুই কলামের মোট সমান (৩,৪৩,৬০০ টাকা) হলেও রেফারেন্স-ভিত্তিক জোড়াই শাসনকারী।")
    L.append("৩) L-310/B-109: সনদ অনুপস্থিত — হোল্ড; সনদ পেলে পুনঃমূল্যায়ন হবে।")
    L.append("৪) B-113: ১৮,৬০০ টাকা ব্যাংক চার্জ, খাতায় চালান নেই — এলোকেশনহীন, ব্যাংকে জিজ্ঞাসা জারি।")
    L.append("৫) ইউএসডি হার: ইমেইলে ১২২.৫০ দেখানো হলেও চুক্তি হার ১২৩.০০ শাসনকারী (সংশোধনী-২)।")
    L.append("এই রেজিস্টার খসড়া; কোনো পরিশোধ নির্বাহ এখান থেকে করা হয়নি।")
    return "\n".join(L) + "\n"


wp_register = D + "/work_product/register_q2.txt"
write_member(wp_register, reg_txt())
wp_register_json = D + "/work_product/register_q2.json"
write_json_member(wp_register_json, {"schema": "shapla.release-register.v1", "case_id": CID,
                                     "request_revision": "rev3", "currency": "BDT",
                                     "rows": REG,
                                     "totals": {"bank_debits": str(total_bank_m2), "released": str(released),
                                                "held": str(held), "duplicate_excluded": str(dup_amount),
                                                "july_forward": str(july_amount), "credit_note_claim": str(taka(credit_note)),
                                                "unallocated_charge": str(charge_amount)}})
wp_summary = D + "/work_product/board_summary_en.txt"
write_member(wp_summary, """Shapla Trade House Ltd - Q2 2025 reconciliation: executive summary for the group audit committee

Prepared for: Finance Director (Farhana Rahman); source register: register_q2 (rev3, Bangla)
Scope: bank account 502.1130.8845, April-June 2025, payments of BDT 50,000 and above itemised.

Position
- Total Q2 bank debits reconciled: BDT %s.
- Released after evidence checks: BDT %s across %d items.
- Held pending evidence: BDT %s (INV-S-2025-0312, Meghna Cement Traders Ltd: delivery certificate absent from the file).
- Unallocated bank charge of BDT %s escalated to the bank; not posted to any vendor.
- One duplicate ledger posting (ADV-Q-2025-0088, "Rafiqul Islam (Sales)") excluded; the Procurement posting is the correct one.

Key judgments
- Two pairs share equal column totals (BDT %s); reference-based pairing, not totals, governs.
- The contract USD rate of 123.00 (amendment A-2) governs over the 122.50 market rate quoted in email.
- Credit note CR-2025-0031 (BDT 27,300.00) applies to the next settlement: recorded as a receivable claim, no payment restated.
- July 1 payment run (amendment A-4): BDT %s shown as a forward commitment, not a Q2 payable.

Controls: totals verified by two independent methods (Decimal taka and integer paisa); all atoms and typed facts disposed; no open tensions at release. This document is a draft for review; no payment was executed from it.
""" % (bdt(int(total_bank_m2 * 100), False), bdt(int(released * 100), False), sum(1 for r in REG if r["decision"] == "release"),
       bdt(int(held * 100), False), bdt(paise(charge_rows[0][4]), False), bdt(int(cross_total * 100), False), bdt(paise(july[0][4]), False)))


# ---------- reference ledger ----------
def atoms_from_text(ex_id, text, shape):
    out = []
    pos = 0
    lines = text.split("\n")
    for i, line in enumerate(lines):
        b = len(line.encode("utf-8"))
        if line == "" and i == len(lines) - 1:
            break
        out.append({"atom_id": "%s-%03d" % (ex_id, i + 1), "source": ex_id, "version": 1,
                    "sha256": sha_text(line), "byte_start": pos, "byte_end": pos + b,
                    "sequence": i + 1, "text": line, "shape": shape,
                    "planned_role": "TRACE", "profile": "trace_legacy" if shape == "memo_or_email_line" else "coordinator"})
        pos += b + 1
    recon = "\n".join(a["text"] for a in out) + ("\n" if out else "")
    assert recon == text, ex_id
    return out


ATOMS = []
for eid in ["shapla-bank-q2", "shapla-ledger-q2"]:
    ATOMS += atoms_from_text(eid, W.EXHIBITS[eid][1](), "csv_row")
for eid in ["shapla-amendments", "shapla-emails"]:
    ATOMS += atoms_from_text(eid, W.EXHIBITS[eid][1](), "memo_or_email_line")

FACTS = []
for b in W.BANK_ROWS:
    FACTS.append({"fact_id": "FB-" + b[0], "atom_id": "shapla-bank-q2-%03d" % (int(b[0][2:])), "attribute": "bank_debit",
                  "pointer": "txn_id=" + b[0], "raw_literal": b[4], "type": "money",
                  "value": str(paise(b[4])), "unit": "BDT paisa", "status": "in_force", "validation": "verified"})
    FACTS.append({"fact_id": "FBd-" + b[0], "atom_id": None, "attribute": "value_date",
                  "pointer": "txn_id=" + b[0] + ":date", "raw_literal": b[1], "type": "date",
                  "value": b[1], "unit": "ISO date", "status": "in_force", "validation": "verified"})
    FACTS.append({"fact_id": "FBr-" + b[0], "atom_id": None, "attribute": "instrument_ref",
                  "pointer": "txn_id=" + b[0] + ":ref", "raw_literal": b[3], "type": "string",
                  "value": b[3], "unit": None, "status": "in_force", "validation": "verified"})
for l in W.LEDGER_ROWS:
    dup = l[0] == "L-307"
    st = "void" if dup else "in_force"
    FACTS.append({"fact_id": "FL-" + l[0], "atom_id": None, "attribute": "ledger_entry",
                  "pointer": "entry_id=" + l[0], "raw_literal": l[4], "type": "money",
                  "value": str(paise(l[4])), "unit": "BDT paisa", "status": st, "validation": "verified"})
    FACTS.append({"fact_id": "FLr-" + l[0], "atom_id": None, "attribute": "invoice_ref",
                  "pointer": "entry_id=" + l[0] + ":ref", "raw_literal": l[3], "type": "string",
                  "value": l[3], "unit": None, "status": st, "validation": "verified"})
    FACTS.append({"fact_id": "FLa-" + l[0], "atom_id": None, "attribute": "annex_status",
                  "pointer": "entry_id=" + l[0] + ":annex_status", "raw_literal": l[5], "type": "string",
                  "value": l[5], "unit": None, "status": st, "validation": "verified"})
FACTS += [
    {"fact_id": "FM-A1", "atom_id": None, "attribute": "amendment_uplift", "pointer": "A-1", "raw_literal": "১.৫%",
     "type": "percent", "value": "1.5", "unit": "percent", "status": "in_force", "validation": "verified"},
    {"fact_id": "FM-A1e", "atom_id": None, "attribute": "effective_date", "pointer": "A-1", "raw_literal": "২০২৫-০৫-২০",
     "type": "date", "value": "2025-05-20", "unit": "ISO date", "status": "in_force", "validation": "verified"},
    {"fact_id": "FM-A2", "atom_id": None, "attribute": "contract_fx_rate", "pointer": "A-2", "raw_literal": "১২৩.০০",
     "type": "rate", "value": "123.00", "unit": "BDT/USD", "status": "in_force", "validation": "verified"},
    {"fact_id": "FM-A3", "atom_id": None, "attribute": "credit_note_amount", "pointer": "A-3/CR-2025-0031", "raw_literal": "২৭,৩০০.০০",
     "type": "money", "value": "2730000", "unit": "BDT paisa", "status": "in_force", "validation": "verified"},
    {"fact_id": "FM-A4", "atom_id": None, "attribute": "july_effective_date", "pointer": "A-4", "raw_literal": "২০২৫-০৭-০১",
     "type": "date", "value": "2025-07-01", "unit": "ISO date", "status": "in_force", "validation": "verified"},
    {"fact_id": "FE-1", "atom_id": None, "attribute": "submission_deadline", "pointer": "email: Farhana 09:15 UTC", "raw_literal": "১৭:০০ UTC",
     "type": "datetime", "value": "2025-06-30T17:00:00Z", "unit": "UTC", "status": "in_force", "validation": "verified"},
    {"fact_id": "FE-2", "atom_id": None, "attribute": "itemisation_threshold", "pointer": "email: Farhana 12:00 UTC", "raw_literal": "৫০,০০০ টাকা",
     "type": "money", "value": "5000000", "unit": "BDT paisa", "status": "in_force", "validation": "verified"},
    {"fact_id": "FE-3", "atom_id": None, "attribute": "market_fx_quote", "pointer": "A-2 context", "raw_literal": "১২২.৫০",
     "type": "rate", "value": "122.50", "unit": "BDT/USD", "status": "in_force", "validation": "not_governing"},
]

CLAIMS = [
    {"claim_id": "claim.shapla.q2_bank_total", "slot": "total", "value": str(int(total_bank_m2 * 100)),
     "display": bdt(int(total_bank_m2 * 100)) + " টাকা", "operands": ["FB-B-%03d" % i for i in range(101, 115)],
     "rule": "sum of Q2 bank debits", "calc_refs": ["calc-m1-decimal", "calc-m2-paisa"], "deliverables": ["register_q2"]},
    {"claim_id": "claim.shapla.released_total", "slot": "total", "value": str(int(released * 100)),
     "display": bdt(int(released * 100)) + " টাকা", "operands": ["FB-B-%03d" % i for i in range(101, 115) if i not in (109, 113)],
     "rule": "sum of released rows", "calc_refs": ["calc-m2-paisa"], "deliverables": ["register_q2", "board_summary_en"]},
    {"claim_id": "claim.shapla.held_total", "slot": "total", "value": str(int(held * 100)),
     "display": bdt(int(held * 100)) + " টাকা", "operands": ["FB-B-109"], "rule": "sum of held rows",
     "calc_refs": ["calc-m2-paisa"], "deliverables": ["register_q2", "board_summary_en"]},
    {"claim_id": "claim.shapla.usd_payable", "slot": "payable_amount", "value": "63960000",
     "display": bdt(63960000) + " টাকা", "operands": ["FM-A2"], "rule": "USD 5200 x contract rate 123.00",
     "calc_refs": ["calc-usd-decimal", "calc-usd-integer"], "deliverables": ["register_q2"]},
    {"claim_id": "claim.shapla.credit_note_claim", "slot": "receivable", "value": "2730000",
     "display": bdt(2730000) + " টাকা", "operands": ["FM-A3"], "rule": "credit note applies to next settlement",
     "calc_refs": ["calc-credit"], "deliverables": ["register_q2"]},
    {"claim_id": "claim.shapla.july_forward", "slot": "forward_commitment", "value": str(paise(july[0][4])),
     "display": bdt(paise(july[0][4])) + " টাকা", "operands": ["FM-A4"], "rule": "rev2 scope addition",
     "calc_refs": [], "deliverables": ["register_q2", "board_summary_en"]},
]

DISPOSITIONS = []
for a in ATOMS:
    text = a["text"]
    if a["source"] == "shapla-emails" and "পিকনিক" in text:
        DISPOSITIONS.append({"id": a["atom_id"], "kind": "atom", "state": "ruled_out",
                             "reason": "touches_no_claim", "witness": "TRACE proposal rc-shapla-trace-picnic; no claim references admin logistics"})
    elif text in (W.BANK_CSV_HEADER, W.LEDGER_CSV_HEADER):
        DISPOSITIONS.append({"id": a["atom_id"], "kind": "atom", "state": "ruled_out",
                             "reason": "touches_no_claim", "witness": "structural header; back-references from row facts cover data rows only"})
    else:
        DISPOSITIONS.append({"id": a["atom_id"], "kind": "atom", "state": "bound",
                             "bound_claims": ["claim.shapla.q2_bank_total"]})
for f in FACTS:
    if f["fact_id"] in ("FL-L-307", "FLr-L-307", "FLa-L-307"):
        DISPOSITIONS.append({"id": f["fact_id"], "kind": "fact", "state": "ruled_out", "reason": "duplicate",
                             "witness": "same invoice_ref ADV-Q-2025-0088 already carried by L-306; bank paid one debit B-106 only"})
    else:
        DISPOSITIONS.append({"id": f["fact_id"], "kind": "fact", "state": "bound",
                             "bound_claims": ["claim.shapla.q2_bank_total"] if f["fact_id"].startswith("FB-") else ["claim.shapla.released_total"]})

TENSIONS = [
    {"id": "T-1", "type": "rival", "implicated": ["FM-A2", "FE-3"], "trigger": "USD rate 123.00 (memo A-2) vs 122.50 (email quote)",
     "history": "open 2025-06-26, resolved 2025-06-27", "resolution": "contract rate governs (amendment A-2 states the market rate is not governing)",
     "obligations_affected": ["O2"]},
    {"id": "T-2", "type": "orphan", "implicated": ["FB-B-113"], "trigger": "bank debit with no ledger invoice",
     "history": "open 2025-06-27", "resolution": "kept out of vendor claims; escalated to bank; summary-line treatment per threshold rule",
     "obligations_affected": ["O5"]},
    {"id": "T-3", "type": "misread", "implicated": ["FL-L-306", "FL-L-307"], "trigger": "two nearly identical names with different responsibilities",
     "history": "resolved", "resolution": "bank narration confirms Procurement; Sales row ruled_out duplicate", "obligations_affected": ["O1"]},
    {"id": "T-4", "type": "qualifier", "implicated": ["FM-A1e", "FBd-B-101"], "trigger": "A-1 uplift effective 2025-05-20 vs payment on 2025-04-10",
     "history": "resolved", "resolution": "uplift forward-looking only; paid amount stands at ledger value", "obligations_affected": ["O2"]},
    {"id": "T-5", "type": "dangling", "implicated": ["FLa-L-310"], "trigger": "annex_status=missing_annex with bank debit already settled",
     "history": "resolved as hold", "resolution": "register holds the item; not released without certificate", "obligations_affected": ["O3"]},
]

OBLIGATIONS = [
    {"id": "O1", "request_revision": "rev1", "clause": "প্রতিটি কিউ২ ব্যাংক ডেবিট খাতার সারির সাথে মিলিয়ে দেখান", "kind": "reconciliation", "slot": "matched_pairs", "state": "delivered", "ref": "register_q2 rows"},
    {"id": "O2", "request_revision": "rev1", "clause": "অনুমোদিত সংশোধনী অনুযায়ী মূল্য সমন্বয়", "kind": "computation", "slot": "adjusted_amounts", "state": "delivered", "ref": "claims usd_payable, credit_note_claim"},
    {"id": "O3", "request_revision": "rev1", "clause": "রিলিজ/হোল্ড সিদ্ধান্তসহ রেজিস্টার", "kind": "deliverable", "slot": "register", "state": "delivered", "ref": "register_q2.txt/json"},
    {"id": "O4", "request_revision": "rev1", "clause": "প্রতিটি সারিতে উৎসের রেফারেন্স", "kind": "format", "slot": "source_refs", "state": "delivered", "ref": "register rows refs field"},
    {"id": "O5", "request_revision": "rev1", "clause": "অমিল ব্যাংক আইটেম আলাদা করে দেখান", "kind": "exception_report", "slot": "unmatched", "state": "delivered", "ref": "register exceptions ৪"},
    {"id": "O6", "request_revision": "rev1", "clause": "সময়সীমার ঘড়ি নিশ্চিত করা", "kind": "judgement", "slot": "deadline_clock", "state": "delivered", "ref": "email confirmation 17:00 UTC"},
    {"id": "O7", "request_revision": "rev1", "clause": "৫০,০০০ টাকার নিচের আইটেম এক লাইনে সারসংক্ষেপ", "kind": "format", "slot": "threshold_rule", "state": "delivered", "ref": "register summary line"},
    {"id": "O8", "request_revision": "rev2", "clause": "জুলাই পরিশোধ রানের প্রতিশ্রুত অংক আলাদা অংশে", "kind": "deliverable", "slot": "forward_commitments", "state": "delivered", "ref": "register july_forward; rev2"},
    {"id": "O9", "request_revision": "rev3", "clause": "গ্রুপ অডিট কমিটির জন্য ইংরেজি এক্সিকিউটিভ সামারি", "kind": "deliverable", "slot": "board_summary", "state": "delivered", "ref": "board_summary_en.txt; rev3"},
    {"id": "O10", "request_revision": "rev1", "clause": "সংশোধনীর ফলে অপরিবর্তিত অংশ অক্ষুণ্ণ রাখা", "kind": "constraint", "slot": "revision_integrity", "state": "delivered", "ref": "rev2/rev3 diffs; unchanged rows preserved"},
    {"id": "O11", "request_revision": "rev1", "clause": "কোনো পরিশোধ নির্বাহ করা যাবে না; খসড়াই চূড়ান্ত", "kind": "prohibition", "slot": "no_execution", "state": "delivered", "ref": "register footer"},
    {"id": "O12", "request_revision": "rev1", "clause": "মোট দুটি স্বাধীন পদ্ধতিতে যাচাই", "kind": "verification", "slot": "two_method_totals", "state": "delivered", "ref": "calc-m1/calc-m2; agreement true"},
]

DEPENDENCIES = [
    {"from": "source:shapla-bank-q2", "to": "fact:FB-*"},
    {"from": "fact:FB-*", "to": "claim:claim.shapla.q2_bank_total"},
    {"from": "fact:FM-A2", "to": "claim:claim.shapla.usd_payable"},
    {"from": "claim:claim.shapla.released_total", "to": "deliverable:register_q2"},
    {"from": "claim:claim.shapla.held_total", "to": "deliverable:register_q2"},
    {"from": "claim:claim.shapla.july_forward", "to": "deliverable:register_q2"},
    {"from": "revision:rev2", "to": "obligation:O8"},
    {"from": "revision:rev3", "to": "obligation:O9"},
    {"from": "claim:claim.shapla.released_total", "to": "deliverable:board_summary_en"},
]

SENSITIVITY = [
    {"id": "S1", "target": "A-1 uplift 1.5% -> 2.5%", "effect": "forward contract price changes to 390,428.40 -> 394,174.00 BDT; paid amounts unchanged", "changes_decision": False},
    {"id": "S2", "target": "USD rate 123.00 -> 122.50", "effect": "INV-D-2025-0044 payable changes by 2,600.00 BDT (5200 x 0.50)", "changes_decision": True},
    {"id": "S3", "target": "itemisation threshold 50,000 -> 25,000", "effect": "no additional Q2 item falls in the 25,000-50,000 band; register rows unchanged", "changes_decision": False},
]

LEDGER = {
    "schema": "craftly.reference-ledger.v10", "case_id": CID, "source_version": "2025-06-30",
    "request_revision": "rev3", "route": "evidence_ledger",
    "contract_status": "reference_sidecar_not_deployed",
    "atoms": ATOMS, "facts": FACTS, "claims": CLAIMS, "dispositions": DISPOSITIONS,
    "tensions": TENSIONS, "obligations": OBLIGATIONS, "dependencies": DEPENDENCIES,
    "sensitivity": SENSITIVITY,
    "gate": {"atoms_all_disposed": True, "facts_all_disposed": True, "open_tensions": 0,
             "sensitivity_required": True, "independent_calculations": ["calc-m1-decimal", "calc-m2-paisa"],
             "obligations_delivered": [o["id"] for o in OBLIGATIONS], "obligations_held": [],
             "result": "release", "note": "reference sidecar; authoring-time checks, not a deployed system"},
}
write_json_member(D + "/ledger/reference-ledger.json", LEDGER)


def jobs():
    J = []
    n = 0
    for b in W.BANK_ROWS:
        n += 1
        J.append(("J%02d" % n, "extract/verify bank row " + b[0], ["source:shapla-bank-q2"], "FB-" + b[0]))
    for l in W.LEDGER_ROWS:
        n += 1
        J.append(("J%02d" % n, "extract/verify ledger row " + l[0], ["source:shapla-ledger-q2"], "FL-" + l[0]))
    for tag in ["A-1", "A-2", "A-3", "A-4"]:
        n += 1
        J.append(("J%02d" % n, "read amendment memo " + tag + " and type its obligations", ["source:shapla-amendments"], "FM-" + tag))
    for i, tag in enumerate(["E1", "E2", "E3"]):
        n += 1
        J.append(("J%02d" % n, "read material email " + tag, ["source:shapla-emails"], "FE-" + str(i + 1)))
    assert n == 34, n
    matches = [("match INV-S-2025-0311", ["J01", "J14"]), ("match INV-P-2025-0051 (3 installments)", ["J02", "J15", "J16", "J17"]),
               ("resolve duplicate ADV-Q-2025-0088", ["J06", "J19", "J20"]), ("pair equal-totals cross INV-P-2025-0052/0058", ["J05", "J14", "J19", "J27"]),
               ("match INV-D-2025-0044 at contract rate", ["J07", "J22", "J29"]), ("match INV-S-2025-0312 + annex check", ["J09", "J24"]),
               ("match INV-L-2025-0019", ["J10", "J25"]), ("match INV-P-2025-0061", ["J08", "J23"])]
    for m, deps in matches:
        n += 1
        J.append(("J%02d" % n, m, deps, "T-3" if "duplicate" in m else "match"))
    n += 1
    J.append(("J43", "compute USD payable at contract rate (two methods)", ["J39", "J29"], "claim.shapla.usd_payable"))
    n += 1
    J.append(("J44", "apply credit note CR-2025-0031 to next settlement", ["J38", "J30"], "claim.shapla.credit_note_claim"))
    n += 1
    J.append(("J45", "classify missing-annex item as hold", ["J40"], "T-5"))
    n += 1
    J.append(("J46", "classify bank charge B-113 as unallocated + escalate", ["J13", "J34"], "T-2"))
    n += 1
    J.append(("J47", "decide release set and hold set", ["J35", "J36", "J37", "J38", "J39", "J40", "J41", "J42", "J43", "J44", "J45", "J46"], "O3"))
    n += 1
    J.append(("J48", "two-method total verification + assemble Bangla register (rev1)", ["J47", "J32", "J33"], "O12"))
    n += 1
    J.append(("J49", "rev2+rev3: July forward section; English executive summary; unchanged rows preserved", ["J48", "J31"], "O8"))
    n += 1
    J.append(("J50", "editorial review, regression checks, final gate: obligations delivered, no open tension, seal", ["J49"], "gate"))
    assert n == 50, n
    return J


JOBS = [{"id": j[0], "description": j[1], "dependencies": j[2], "status": "done", "result_ref": j[3]} for j in jobs()]


def snap(rev, note, extra):
    s = {"revision": rev, "note": note, "jobs_done": len(JOBS), "stage": "register_final" if rev == "rev3" else "work_active"}
    s.update(extra)
    return {"snapshot": s, "snapshot_hash": sha_text(json.dumps(s, ensure_ascii=False, sort_keys=True))}


EVENTS = [
    {"id": "EV-01", "seq": 1, "request_revision": "rev1", "predecessors": [], "change": "request received (register by 2025-06-30 17:00 UTC)",
     "public_facts": ["scope: Q2 2025", "account 502.1130.8845"], "snapshot": snap("rev1", "intake", {"accepted_facts": 0})},
    {"id": "EV-02", "seq": 2, "request_revision": "rev1", "predecessors": ["EV-01"], "change": "sources frozen; 4 exhibits admitted",
     "public_facts": ["4 exhibits", "atoms %d" % len(ATOMS)], "snapshot": snap("rev1", "sources_frozen", {"accepted_facts": len(FACTS)})},
    {"id": "EV-03", "seq": 3, "request_revision": "rev1", "predecessors": ["EV-02"], "change": "matching completed; duplicate excluded",
     "public_facts": ["13 matched pairs", "1 duplicate ruled out (L-307)"], "snapshot": snap("rev1", "matched", {"accepted_facts": len(FACTS)})},
    {"id": "EV-04", "seq": 4, "request_revision": "rev1", "predecessors": ["EV-03"], "change": "tension T-1 resolved: contract FX rate governs",
     "public_facts": ["rate 123.00 governs"], "snapshot": snap("rev1", "tension_resolved", {"accepted_facts": len(FACTS)})},
    {"id": "EV-05", "seq": 5, "request_revision": "rev1", "predecessors": ["EV-04"], "change": "register drafted; hold for missing certificate",
     "public_facts": ["released %s" % bdt(int(released * 100)), "held %s" % bdt(int(held * 100))], "snapshot": snap("rev1", "draft_ready", {"accepted_facts": len(FACTS)})},
    {"id": "EV-06", "seq": 6, "request_revision": "rev2", "predecessors": ["EV-05"], "change": "steering: add July forward commitments; register rows unchanged",
     "public_facts": ["forward %s" % bdt(paise(july[0][4]))], "snapshot": snap("rev2", "scope_added", {"accepted_facts": len(FACTS), "added_obligation": "O8"})},
    {"id": "EV-07", "seq": 7, "request_revision": "rev3", "predecessors": ["EV-06"], "change": "steering: English executive summary requested; facts preserved, rerendered",
     "public_facts": ["board_summary_en produced"], "snapshot": snap("rev3", "rerender", {"accepted_facts": len(FACTS), "added_obligation": "O9"})},
    {"id": "EV-08", "seq": 8, "request_revision": "rev3", "predecessors": ["EV-07"], "change": "checks passed; obligations delivered; register sealed",
     "public_facts": ["gate: release", "no open tensions"], "snapshot": snap("rev3", "sealed", {"accepted_facts": len(FACTS)})},
]

WORKFLOW = {"schema": "shapla.workflow.v1", "case_id": CID, "job_dag": JOBS, "event_log": EVENTS,
            "final_result": {"released": str(released), "held": str(held), "register": wp_register,
                             "board_summary": wp_summary, "obligations_delivered": [o["id"] for o in OBLIGATIONS]},
            "note": "events locally authored/replayed; live telemetry not applicable"}
write_json_member(D + "/workflow/workflow.json", WORKFLOW)

FALLBACK_MD = D + "/work_product/register_fallback.txt"
write_member(FALLBACK_MD, reg_txt())
RICH = {
    "schema": "craftly.alphabet.presentation.reference.v1", "case_id": CID, "request_revision": "rev3",
    "language": "bn", "audience": "finance_director", "purpose": "quarter_end_release_hold_register",
    "result_state": "draft_delivered_no_execution", "obligation_ids": ["O3", "O4", "O8", "O9"],
    "canonical_data_ref": wp_register_json,
    "blocks": [
        {"id": "b1", "type": "heading", "claim_ids": [], "obligation_ids": [], "source_refs": [],
         "content": {"text": "শাপলা ট্রেড হাউস — কিউ২ ২০২৫ মিলকরণ ও রিলিজ/হোল্ড রেজিস্টার"}, "layout": "full"},
        {"id": "b2", "type": "metric_group", "claim_ids": ["claim.shapla.q2_bank_total", "claim.shapla.released_total", "claim.shapla.held_total", "claim.shapla.july_forward"],
         "obligation_ids": ["O3"], "source_refs": ["register_q2"], "layout": "full",
         "content": {"metrics": [
             {"label": "মোট ব্যাংক ডেবিট (কিউ২)", "value": str(total_bank_m2), "unit": "BDT", "claim_id": "claim.shapla.q2_bank_total"},
             {"label": "রিলিজড", "value": str(released), "unit": "BDT", "claim_id": "claim.shapla.released_total"},
             {"label": "হোল্ড", "value": str(held), "unit": "BDT", "claim_id": "claim.shapla.held_total"},
             {"label": "জুলাই প্রতিশ্রুত (rev2)", "value": str(july_amount), "unit": "BDT", "claim_id": "claim.shapla.july_forward"}]}},
        {"id": "b3", "type": "table", "claim_ids": [], "obligation_ids": ["O4"], "source_refs": ["register_q2"],
         "layout": "full",
         "content": {"columns": [{"id": "txn", "type": "string"}, {"id": "ref", "type": "string"}, {"id": "amount_bdt", "type": "money"}, {"id": "decision", "type": "enum"}, {"id": "reason", "type": "string"}],
                     "rows": [{"row_id": r["txn"], "cells": {"txn": r["txn"], "ref": r["ref"], "amount_bdt": r["amount_bdt"], "decision": r["decision"], "reason": r["reason"]}} for r in REG]}},
        {"id": "b4", "type": "chart", "claim_ids": ["claim.shapla.released_total", "claim.shapla.held_total"],
         "obligation_ids": ["O3"], "source_refs": ["register_q2"], "layout": "half",
         "content": {"vega_lite": {"$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                     "mark": "bar", "encoding": {"x": {"field": "category", "type": "nominal"},
                     "y": {"field": "amount", "type": "quantitative", "title": "BDT"}},
                     "data": {"values": [{"category": "রিলিজড", "amount": int(released)},
                                          {"category": "হোল্ড", "amount": int(held)}]},
                     "title": "রিলিজ বনাম হোল্ড (টাকা)"},
                     "alt_text": "রিলিজড %s টাকা বনাম হোল্ড %s টাকা" % (bdt(int(released * 100)), bdt(int(held * 100))),
                     "data_table": [{"category": "রিলিজড", "amount_bdt": str(released)}, {"category": "হোল্ড", "amount_bdt": str(held)}]}},
        {"id": "b5", "type": "callout", "claim_ids": [], "obligation_ids": ["O5"], "source_refs": ["B-113"], "layout": "full",
         "content": {"text": "১৮,৬০০ টাকার ব্যাংক চার্জ (B-113) খাতায় অমিল — ব্যাংকে জিজ্ঞাসা জারি হয়েছে; রেজিস্টারে এলোকেশনহীন দেখানো হয়েছে।", "kind": "exception"}},
        {"id": "b6", "type": "status", "claim_ids": [], "obligation_ids": ["O3", "O10", "O11"], "source_refs": ["EV-08"], "layout": "full",
         "content": {"state": "released_gate", "text": "সব দায়বদ্ধতা পূরণ, কোনো খোলা টেনশন নেই; খসড়া পর্যালোচনার জন্য প্রস্তুত — কোনো পরিশোধ নির্বাহ হয়নি।"}},
        {"id": "b7", "type": "artifact", "claim_ids": [], "obligation_ids": ["O3"], "source_refs": [], "layout": "full",
         "content": {"kind": "register_json", "handle": wp_register_json, "state": "authoring_artifact_staged_in_case_directory"}},
    ],
    "fallback_markdown_path": FALLBACK_MD,
    "accessibility": {"alt_text_present": True, "text_fallback": True, "bangla_typography": True},
    "validation": {"schema_ok": True, "values_match_canonical": True, "render_inspection": "pending_no_renderer"},
}
write_json_member(D + "/presentation/presentation-rich.json", RICH)

SOL = {"case_id": CID, "status": "solved", "source_version": "2025-06-30", "request_revisions": ["rev1", "rev2", "rev3"],
       "obligations": [o["id"] for o in OBLIGATIONS], "solutions": SOLUTION,
       "methods": ["Decimal taka", "integer paisa"], "independent_review": "editorial_self_review; external review pending",
       "steering": ["rev2: add July forward commitments (register rows unchanged)",
                    "rev3: English executive summary from accepted facts (no new source reads)"],
       "notes": "Duplicate L-307 excluded; missing annex held; bank charge escalated; contract FX rate governs."}
write_json_member(D + "/solution/solution.json", SOL)

EXPECTED = {
    "case_id": CID,
    "expected_checks": [
        {"check": "two_method_totals_agree", "detail": "Decimal(taka) == integer paisa for all totals"},
        {"check": "register_totals_identity", "detail": "released + held == bank total - unallocated charge"},
        {"check": "duplicate_row_excluded", "detail": "L-307 absent from released set"},
        {"check": "missing_annex_held", "detail": "L-310/B-109 marked hold"},
        {"check": "cross_pairing_by_ref", "detail": "equal column totals do not drive pairing"},
        {"check": "fx_rate_precedence", "detail": "contract 123.00 governs email 122.50"},
        {"check": "obligations_closed", "detail": "O1-O12 delivered or witnessed"},
        {"check": "no_open_tensions", "detail": "T-1..T-5 resolved"},
        {"check": "steering_revisions_preserve_unchanged", "detail": "rev2/rev3 do not alter released rows"},
        {"check": "atoms_partition_lossless", "detail": "atom texts + newlines reconstruct each exhibit"},
    ],
    "negative_controls": [
        {"control": "decisive_change", "action": "set FX rate 122.50 as governing", "expected": "usd payable changes by 2600.00 BDT; register total changes; check must flag discrepancy vs exhibit A-2"},
        {"control": "placebo", "action": "remove picnic email line", "expected": "no claim, total or register row changes"},
        {"control": "missing_evidence", "action": "delete L-310 annex status line", "expected": "hold witness unresolvable; affected obligation must hold, not release"},
    ],
}
write_json_member(D + "/checks/expected.json", EXPECTED)
