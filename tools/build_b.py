import json
from decimal import Decimal
from fractions import Fraction
from common import *

OUT = {}


def register_case(meta):
    OUT[meta["id"]] = meta


# ================= CASE 2: en-board-novustex-002 =================
C2 = "en-board-novustex-002"
D2 = "cases/" + C2

write_member(D2 + "/exhibit-covenant.txt", """Summit Meridian Finance PLC - Facility Letter (extract), dated 2024-09-30, ref SMF/NVT/2024/118
Clause 7.1 (binding covenant): Total outstanding borrowings shall not at any time exceed 2.5 times EBITDA for the last twelve months, as certified in the audited financial statements.
Clause 7.2 (binding covenant): The facility is secured by a floating charge over inventories.
""")

write_member(D2 + "/exhibit-ebitda-ltm.csv", """quarter,period,ebitda_bdt,note
Q1,Jul-Sep 2024,15200000,
Q2,Oct-Dec 2024,16900000,
Q3,Jan-Mar 2025,17600000,
Q4,Apr-Jun 2025,18700000,includes one-off sale-leaseback gain of 6200000 - flagged by internal review; not yet audited
""")

write_member(D2 + "/exhibit-debt-schedule.csv", """facility,principal_outstanding_bdt,annual_interest_bdt,scheduled_principal_bdt
Term loan SMF-01,72000000,7920000,19750000
Overdraft KCB-OD,14500000,930000,0
note,CFO owner-stated definition (2025-07-01): DSCR = LTM EBITDA divided by (annual interest + scheduled principal) for the coming twelve months; CFO threshold 1.30; this threshold is the owner's stated standard; not a covenant.
""")

write_member(D2 + "/exhibit-term-sheets.txt", """Term sheet A - Summit Meridian Finance PLC, 2025-07-08: BDT 60,000,000; 11.75% p.a.; 5-year term; equal quarterly principal repayments of 3,000,000.
Term sheet B - Padma Capital Partners, 2025-07-09: BDT 60,000,000; 10.90% p.a.; 7-year term; annual principal repayment 7,500,000.
Term sheet B covenant (binding): Borrower leverage shall not exceed 2.2 times LTM EBITDA excluding one-off gains, tested quarterly.
Chair preference (stated 2025-07-10): a tenor of five years or less where all else is defensible.
""")

m = lambda x: Decimal(x) * 1000000
ebitda_ltm = m("68.4")
ebitda_excl = ebitda_ltm - m("6.2")
existing_debt = m("86.5")
total_debt = existing_debt + m("60")
lev = float(total_debt / ebitda_ltm)
lev_excl = float(total_debt / ebitda_excl)
lev_frac = Fraction(146500000, 68400000)
assert abs(lev - float(lev_frac)) < 1e-9
service_existing = m("28.6")
service_A = m("12.0") + m("7.05")
service_B = m("7.5") + m("6.54")
dscr_A = float(ebitda_ltm / (service_existing + service_A))
dscr_B = float(ebitda_ltm / (service_existing + service_B))
dscr_A_frac = Fraction(68400000, 28600000 + 19050000)
assert abs(dscr_A - float(dscr_A_frac)) < 1e-9
max_debt_B = Decimal("2.2") * ebitda_excl
max_loan_B = max_debt_B - existing_debt
min_ebitda_group = total_debt / Decimal("2.5")
covenant_margin = ebitda_excl - min_ebitda_group
margin_pct = covenant_margin / ebitda_excl * 100
S2 = {"ebitda_ltm": str(ebitda_ltm), "ebitda_excl_oneoff": str(ebitda_excl), "total_debt_proforma": str(total_debt),
      "leverage": str(round(lev, 4)), "leverage_excl_oneoff": str(round(lev_excl, 4)),
      "bankA_year1_service": str(service_A + service_existing), "dscr_A": str(round(dscr_A, 4)),
      "dscr_B": str(round(dscr_B, 4)), "max_loan_B_under_own_covenant": str(max_loan_B),
      "min_ebitda_for_group_covenant": str(min_ebitda_group), "covenant_margin_bdt": str(covenant_margin),
      "covenant_margin_pct": str(round(margin_pct, 2)), "methods": ["Decimal", "Fraction"], "agreement": True}

wp2 = D2 + "/work_product/decision_memo.txt"
write_member(wp2, """Decision memo - NovusTex Manufacturing Ltd: BDT 60,000,000 machinery loan
Decision owner: Board chair. Prepared for the chair; draft only - no facility is signed or executed from this memo.

Governing conditions
1. Binding covenant (facility letter clause 7.1, Summit Meridian Finance PLC): total borrowings <= 2.5x audited LTM EBITDA.
2. Owner-stated threshold (CFO, 2025-07-01): DSCR >= 1.30, DSCR = LTM EBITDA / (annual interest + scheduled principal).
3. Preference (chair, 2025-07-10): tenor <= 5 years where all else is defensible. A preference is not a constraint.

Verified facts
- LTM EBITDA (Jul 2024 - Jun 2025): BDT 68,400,000; includes a 6,200,000 sale-leaseback gain flagged by internal review and not yet audited; excluding it: BDT 62,200,000.
- Existing debt: BDT 86,500,000 (term loan 72,000,000 + overdraft 14,500,000). Existing annual debt service: BDT 28,600,000.

Feasible set (all conditions checked, two methods: Decimal and Fraction)
- Bank A (11.75%, 5-year): pro-forma leverage 2.1418 <= 2.5 (passes); year-1 combined debt service BDT 47,650,000, DSCR 1.4355 >= 1.30 (passes); tenor 5y (meets preference). FEASIBLE.
- Bank B at BDT 60,000,000 (10.90%, 7-year): group covenant passes; DSCR 1.6041 passes; BUT Bank B's own binding covenant caps leverage at 2.2x LTM EBITDA EXCLUDING one-off gains: 146,500,000 / 62,200,000 = 2.3553 > 2.2. INFEASIBLE at this size.
- Bank B at BDT 50,340,000 or less: 136,840,000 / 62,200,000 = 2.2 exactly - feasible only at a smaller loan (136,840,000 - 86,500,000 = 50,340,000).

Recommendation: Bank A, BDT 60,000,000, 5-year term at 11.75%. It is the only option that satisfies every binding condition at the requested size, and it also satisfies the chair's preference. Bank B is cheaper (10.90%) but infeasible at BDT 60,000,000 under its own exclusion-adjusted covenant; it becomes available only if the loan is cut to at most BDT 50,340,000.

Evidence that could reverse this recommendation: if auditors confirm the 6,200,000 gain is NOT a one-off (i.e., Bank B's exclusion test uses audited LTM EBITDA of 68,400,000), Bank B's leverage is 2.1418 <= 2.2 and B becomes feasible and cheaper; the recommendation would then depend on whether the chair's 5-year preference outweighs the interest saving.

Sensitivity: group covenant breach occurs if EBITDA falls below BDT 58,600,000 (a fall of 3,600,000, i.e. 5.79% from the exclusion-adjusted 62,200,000). No threshold was invented; both bounds are computed from the stated conditions.
""")
SOL2 = {"case_id": C2, "status": "solved", "obligations": ["O1_decision_owner", "O2_covenant_vs_threshold_vs_preference",
        "O3_feasible_set", "O4_recommendation", "O5_reversal_evidence", "O6_sensitivity"], "results": S2,
        "independent_review": "editorial_self_review; external review pending"}
write_json_member(D2 + "/solution/solution.json", SOL2)
write_json_member(D2 + "/checks/expected.json", {
    "case_id": C2,
    "expected_checks": [
        {"check": "two_method_ratios", "detail": "Decimal == Fraction for leverage and DSCR"},
        {"check": "bankB_own_covenant_breach", "detail": "2.3553 > 2.2 exclusion-adjusted"},
        {"check": "feasible_alternative_size", "detail": "Bank B feasible at <= 50,340,000"},
        {"check": "sensitivity_no_invented_threshold", "detail": "breach bound 58,600,000 computed"},
    ],
    "negative_controls": [
        {"control": "decisive_change", "action": "treat the 6,200,000 gain as recurring in Bank B's test", "expected": "Bank B becomes feasible; recommendation set changes; check must detect the altered premise"},
        {"control": "placebo", "action": "change Clause 7.2 security wording", "expected": "no numeric decision changes"},
        {"control": "missing_evidence", "action": "remove debt schedule", "expected": "DSCR unverifiable -> hold"},
    ]})
register_case({
    "id": C2, "language": "en", "domain": "finance", "difficulty": "hard", "family": "board_covenant_decision",
    "source_family": "novustex_credit_file",
    "workplace": {"requester_role": "board chair", "trigger": "machinery loan approval with a binding leverage covenant and a competing cheaper term sheet",
                  "needed_deliverable": "decision memo with feasible set, recommendation and reversal evidence", "next_use": "board resolution drafting"},
    "messages": [
        {"role": "user", "content": "We have two term sheets for the 60 million machinery loan. Which one should I put to the board, and what would make me wrong? Keep it short enough for the board pack."},
        {"role": "assistant", "content": "I can answer from the covenant extract, EBITDA file, debt schedule and both term sheets on file. One check first: should I treat the 6.2m sale-leaseback gain as excluded, per Bank B's own covenant wording, while it is still unaudited?"},
        {"role": "user", "content": "Yes - use the exclusion-adjusted EBITDA for feasibility, and say clearly what would reverse the recommendation."},
    ],
    "exhibits": ["novustex-covenant", "novustex-ebitda", "novustex-debt", "novustex-termsheets"],
    "work_product": wp2, "solution": SOL2,
})
EX2 = {}
for eid, path, title in [("novustex-covenant", D2 + "/exhibit-covenant.txt", "Facility letter extract (binding covenant)"),
                         ("novustex-ebitda", D2 + "/exhibit-ebitda-ltm.csv", "LTM EBITDA quarterly file"),
                         ("novustex-debt", D2 + "/exhibit-debt-schedule.csv", "Debt schedule and CFO DSCR definition"),
                         ("novustex-termsheets", D2 + "/exhibit-term-sheets.txt", "Two term sheets and chair preference")]:
    EX2[eid] = (path, title)

write_json_member(D2 + "/presentation/presentation-rich.json", {
    "schema": "craftly.alphabet.presentation.reference.v1", "case_id": C2, "request_revision": "rev1",
    "language": "en", "audience": "board_chair", "purpose": "loan_approval_decision",
    "result_state": "recommendation_delivered_no_execution", "obligation_ids": ["O3_feasible_set", "O4_recommendation"],
    "canonical_data_ref": D2 + "/solution/solution.json",
    "blocks": [
        {"id": "b1", "type": "heading", "claim_ids": [], "obligation_ids": [], "source_refs": [], "layout": "full",
         "content": {"text": "Machinery loan: recommendation for the board"}},
        {"id": "b2", "type": "metric_group", "claim_ids": [], "obligation_ids": ["O3_feasible_set"], "source_refs": ["solution.json"], "layout": "full",
         "content": {"metrics": [
             {"label": "Pro-forma leverage", "value": S2["leverage"], "unit": "x EBITDA", "period": "pro-forma"},
             {"label": "Bank A DSCR", "value": S2["dscr_A"], "unit": "ratio", "period": "year 1"},
             {"label": "Bank B leverage excl. one-off", "value": S2["leverage_excl_oneoff"], "unit": "x EBITDA (limit 2.2)", "period": "LTM"},
             {"label": "Covenant margin", "value": S2["covenant_margin_pct"], "unit": "percent fall to breach", "period": "LTM"}]}},
        {"id": "b3", "type": "callout", "claim_ids": [], "obligation_ids": ["O4_recommendation"], "source_refs": ["exhibit-term-sheets.txt"], "layout": "full",
         "content": {"kind": "decision", "text": "Recommend Bank A (11.75%, 5y). Bank B breaches its own 2.2x exclusion-adjusted covenant at BDT 60,000,000; it is feasible only at <= BDT 50,340,000."}},
        {"id": "b4", "type": "status", "claim_ids": [], "obligation_ids": ["O5_reversal_evidence"], "source_refs": ["exhibit-ebitda-ltm.csv"], "layout": "full",
         "content": {"state": "reversal_evidence_named", "text": "If auditors treat the 6.2m gain as recurring, Bank B becomes feasible and cheaper; the decision then turns on the chair's tenor preference."}},
    ],
    "fallback_markdown_path": wp2,
    "accessibility": {"alt_text_present": True, "text_fallback": True},
    "validation": {"schema_ok": True, "values_match_canonical": True, "render_inspection": "pending_no_renderer"},
})

# ================= CASE 3: bn-recon-brahmaputra-003 =================
C3 = "bn-recon-brahmaputra-003"
D3 = "cases/" + C3

write_member(D3 + "/exhibit-statement.txt", """ব্রহ্মপুত্র হার্ডওয়্যার — গ্রাহক বিবরণী (ফিকশনাল নমুনা)
গ্রাহক: কর্ণফুলী হার্ডওয়্যার এজেন্সি; মাস: মে ২০২৫
বকেয়া প্রারম্ভিক (০১-০৫-২০২৫) ৫,০০,০০০.০০ ড
০২-০৫-২০২৫ বিল BHD-1183 ২,৪০,০০০.০০ ড
০৯-০৫-২০২৫ বিল BHD-1191 ১,৮৫,০০০.০০ ড
১৫-০৫-২০২৫ পরিশোধ (ব্যাংক) ৩,২৫,০০০.০০ ক্র
২২-০৫-২০২৫ বিল BHD-1204 ৯৬,৪৫০.০০ ড
২৪-০৫-২০২৫ ক্যারেজ ১,৬৮০.০০ ড
২৯-০৫-২০২৫ পরিশোধ (ব্যাংক) ৪,১০,০০০.০০ ক্র
সমাপনী বকেয়া: ২,৮৮,১৩০.০০ ড
""")

write_member(D3 + "/exhibit-cashbook.csv", """entry,date,particulars,debit_dr,credit_cr
CB-01,2025-05-01,opening balance as recorded,458200.00,0.00
CB-02,2025-05-02,purchase bill BHD-1183,240000.00,0.00
CB-03,2025-05-09,purchase bill BHD-1191,226800.00,0.00
CB-04,2025-05-15,payment to supplier,0.00,325000.00
CB-05,2025-05-22,purchase bill BHD-1204,96450.00,0.00
CB-06,2025-05-24,carriage inward,1680.00,0.00
CB-07,2025-05-29,payment to supplier,0.00,410000.00
""")

paise = lambda s: int((Decimal(s) * 100).to_integral_value())
stmt_owed = paise("500000.00") + (paise("240000.00") + paise("185000.00") + paise("96450.00") + paise("1680.00")) - (paise("325000.00") + paise("410000.00"))
cb_owed = paise("458200.00") + (paise("240000.00") + paise("226800.00") + paise("96450.00") + paise("1680.00")) - (paise("325000.00") + paise("410000.00"))
assert stmt_owed == cb_owed == paise("288130.00")
err_open = paise("500000.00") - paise("458200.00")
err_bill = paise("226800.00") - paise("185000.00")
assert err_open == err_bill == paise("41800.00")
S3 = {"statement_closing_bdt": "288130.00", "cashbook_closing_bdt": "288130.00",
      "totals_match_but_composition_wrong": True, "error_opening_bdt": "41800.00 understated",
      "error_bill_BHD-1191_bdt": "41800.00 overstated (offsetting, so totals match)",
      "methods": ["integer paisa", "Decimal"], "agreement": True}
wp3 = D3 + "/work_product/reconciliation_memo.txt"
write_member(wp3, """ব্রহ্মপুত্র হার্ডওয়্যার — মে ২০২৫ মিলকরণ স্মারক (কাল্পনিক নমুনা)
প্রস্তুত: কর্ণফুলী হার্ডওয়্যার এজেন্সির হিসাব সহকারীর জন্য।

ফলাফল আগে: সরবরাহকারীর বিবরণী অনুযায়ী সমাপনী বকেয়া ২,৮৮,১৩০.০০ টাকা — এটিই সঠিক।
দুটি ত্রুটি একে অপরকে প্রতিহত করেছে, তাই দুই পক্ষের মোট মিলে গেছে; কিন্তু খাতার সারিগুলো ভুল।

ব্যতিক্রম ১: প্রারম্ভিক বকেয়া খাতায় ৪,৫৮,২০০.০০ টাকা, বিবরণীতে ৫,০০,০০০.০০ টাকা — ৪১,৮০০.০০ টাকা কম।
ব্যতিক্রম ২: বিল BHD-1191 খাতায় ২,২৬,৮০০.০০ টাকা, বিবরণীতে ১,৮৫,০০০.০০ টাকা — ৪১,৮০০.০০ টাকা বেশি।
দুই ত্রুটির প্রভাব সমান ও বিপরীতমুখী; মোট মিলে থাকায় শুধু মোট মিলিয়ে দেখলে ধরা পড়ে না।

সংশোধন: CB-01 সমন্বয় +৪১,৮০০.০০ টাকা (ড); CB-03 সমন্বয় −৪১,৮০০.০০ টাকা (ড)। সমাপনী বকেয়া অপরিবর্তিত ২,৮৮,১৩০.০০ টাকা।
যাচাই: পুরো হিসাব দুই পদ্ধতিতে করা হয়েছে (টাকা-পয়সা পূর্ণসংখ্যা এবং দশমিক) — ফলাফল এক।
সতর্কতা: সংশোধন না করলে আগস্টে বিল মিলবে না; এই মাসের "মিলে যাওয়া" ভুল নিরাপত্তা দেয়।
""")
SOL3 = {"case_id": C3, "status": "solved", "obligations": ["O1_row_level_reconciliation", "O2_exception_list", "O3_correction_entries", "O4_warn_offsetting_errors"], "results": S3,
        "independent_review": "editorial_self_review; external review pending"}
write_json_member(D3 + "/solution/solution.json", SOL3)
write_json_member(D3 + "/checks/expected.json", {
    "case_id": C3,
    "expected_checks": [
        {"check": "two_method_totals", "detail": "integer paisa == Decimal"},
        {"check": "offsetting_errors_detected", "detail": "opening -41800 and bill +41800 found row-wise"},
        {"check": "closing_balance_unchanged", "detail": "288130.00 before and after correction"},
    ],
    "negative_controls": [
        {"control": "decisive_change", "action": "correct BHD-1191 in the cash book exhibit", "expected": "cash-book closing no longer matches; check detects the mismatch"},
        {"control": "placebo", "action": "reorder cash book rows", "expected": "totals unchanged"},
        {"control": "missing_evidence", "action": "remove statement closing line", "expected": "no authoritative balance -> hold"},
    ]})
register_case({
    "id": C3, "language": "bn", "domain": "finance", "difficulty": "moderate", "family": "supplier_reconciliation",
    "source_family": "brahmaputra_ledger",
    "workplace": {"requester_role": "accounts assistant", "trigger": "monthly supplier statement vs cash book with offsetting errors hidden by matching totals",
                  "needed_deliverable": "reconciliation memo with exceptions and correction entries", "next_use": "next month's reconciliation"},
    "messages": [
        {"role": "user", "content": "সরবরাহকারীর বিবরণী আর আমার ক্যাশ বুকের মোট দুটোই ২,৮৮,১৩০ টাকা দেখাচ্ছে, তাহলে মিলকরণ তো ঠিক আছে?"},
        {"role": "assistant", "content": "মোট মিলে গেলেও সারি ধরে মিলিয়ে দেখা দরকার — আমি উভয় ফাইল খুলে সারি-স্তরে যাচাই করছি।"},
        {"role": "user", "content": "ঠিক আছে, সারি ধরে মিলিয়ে বলুন কোথায় সমস্যা।"},
    ],
    "exhibits": ["brahmaputra-statement", "brahmaputra-cashbook"],
    "work_product": wp3, "solution": SOL3,
})
EX3 = {"brahmaputra-statement": (D3 + "/exhibit-statement.txt", "Supplier customer statement (May 2025)"),
       "brahmaputra-cashbook": (D3 + "/exhibit-cashbook.csv", "Internal cash book (May 2025)")}
