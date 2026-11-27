import json
from decimal import Decimal
from fractions import Fraction
from common import *
from build_c import OUT, register_case

# ================= CASE 10: bn-school-jahid-010 =================
C10 = "bn-school-jahid-010"
D10 = "cases/" + C10
SOL10 = {"case_id": C10, "status": "solved", "obligations": ["O1_recheck_acknowledge", "O2_correction_and_rule"], "class_level": 6, "subject": "সময়/দশমিক",
         "answer": "৩ ঘণ্টা ৪৫ মিনিট = ৩.৭৫ ঘণ্টা", "correction": "টিউটরের ৩.৪৫ ভুল ছিল; ৪৫ মিনিট = ৩/৪ ঘণ্টা = ০.৭৫"}
wp10 = D10 + "/work_product/answer.txt"
write_member(wp10, """তুমি ঠিক ধরেছ, আমিই ভুল বলেছিলাম। আমি আবার হিসাব করে দেখলাম:
এক ঘণ্টায় ৬০ মিনিট, তাই ৪৫ মিনিট = ৪৫/৬০ ঘণ্টা = ৩/৪ ঘণ্টা = ০.৭৫ ঘণ্টা।
অর্থাৎ ৩ ঘণ্টা ৪৫ মিনিট = ৩ + ০.৭৫ = ৩.৭৫ ঘণ্টা — ৩.৪৫ নয়।
সহজ পরীক্ষা: ৩.৪৫ ঘণ্টা মানে ৩ ঘণ্টা ২৭ মিনিট (০.৪৫ × ৬০ = ২৭), যেটা আসলে ৪৫ মিনিট নয়।
মনে রাখার নিয়ম: মিনিটকে ঘণ্টায় ফেলতে ৬০ দিয়ে ভাগ করতে হয়; সংখ্যা পাশে বসিয়ে দিলে হয় না।
""")
write_json_member(D10 + "/solution/solution.json", SOL10)
write_json_member(D10 + "/checks/expected.json", {"case_id": C10, "expected_checks": [
    {"check": "tutor_recheck_and_correct", "detail": "acknowledges error, corrects to 3.75 with the 27-minute countercheck"}],
    "negative_controls": []})
register_case({
    "id": C10, "language": "bn", "domain": "education", "difficulty": "moderate", "family": "time_decimal_correction",
    "source_family": "none_conversation", "school_tag": {"class": 6, "subject": "গণিত"},
    "workplace": {"requester_role": "Class 6 learner", "trigger": "child correctly challenges the tutor's 3.45-hours claim",
                  "needed_deliverable": "recheck, acknowledged correction and a memorable rule", "next_use": "child converts 2 h 30 min alone"},
    "messages": [
        {"role": "user", "content": "স্যার, আপনি বলেছিলেন ৩ ঘণ্টা ৪৫ মিনিট মানে ৩.৪৫ ঘণ্টা। কিন্তু আমি ক্যালকুলেটরে ৪৫ ÷ ৬০ করে দেখলাম ০.৭৫ আসে। তাহলে কি ৩.৭৫ হবে? আমি কোথায় ভুল করলাম?"},
    ],
    "exhibits": [], "work_product": wp10, "solution": SOL10,
})

# ================= CASE 11: en-basic-puzzles-011 =================
C11 = "en-basic-puzzles-011"
D11 = "cases/" + C11
SOL11 = {"case_id": C11, "status": "solved", "obligations": ["O1_direct_answer", "O2_short_reason"], "answer": "42", "rule": "differences 4, 6, 8, 10 -> next +12; also n(n+1)"}
wp11 = D11 + "/work_product/answer.txt"
write_member(wp11, """Next number: 42. The gaps between the terms are 4, 6, 8 and 10 - each gap grows by 2 - so the next gap is 12, and 30 + 12 = 42. Another way to see it: each term is n x (n+1): 1x2, 2x3, 3x4, 4x5, 5x6, so the next is 6 x 7 = 42. Both routes agree.
""")
write_json_member(D11 + "/solution/solution.json", SOL11)
write_json_member(D11 + "/checks/expected.json", {"case_id": C11, "expected_checks": [
    {"check": "two_routes_agree", "detail": "difference rule and n(n+1) both give 42"}],
    "negative_controls": []})
register_case({
    "id": C11, "language": "en", "domain": "reasoning", "difficulty": "easy", "family": "sequence_next_term",
    "source_family": "none_conversation",
    "workplace": {"requester_role": "casual user", "trigger": "sequence puzzle",
                  "needed_deliverable": "direct answer with a short reason", "next_use": "none"},
    "messages": [
        {"role": "user", "content": "What comes next in 2, 6, 12, 20, 30 - and why?"},
    ],
    "exhibits": [], "work_product": wp11, "solution": SOL11,
})

# ================= CASE 12: bn-office-secretariat-012 =================
C12 = "bn-office-secretariat-012"
D12 = "cases/" + C12
write_member(D12 + "/exhibit-approval-memo.txt", """গণপ্রজাতন্ত্রী বাংলাদেশ সরকার — কাল্পনিক দৃশ্যপট (প্রশিক্ষণের জন্য নির্মিত)
জেলা পরিষদ শাখা; স্মারক নং: ১৭.০৬৮.০৪২.১০১.২৩.০৩৭.২০২৫/০৮; তারিখ: ২০২৫-০৩-১২
"সবুজ পথ" উপজেলা সড়ক মেরামত কর্মসূচি (২য় পর্যায়) অনুমোদিত হয়েছে।
বাজেট: ৪৮,৫০,০০০ টাকা; মেয়াদ: ২০২৫-০৬-৩০ পর্যন্ত; বাস্তবায়নকারী: উপজেলা প্রকৌশল বিভাগ।
অনুমোদনকারী: জেলা প্রশাসক (কাল্পনিক নাম: মো. আরিফুল ইসলাম)।
""")
SOL12 = {"case_id": C12, "status": "solved", "obligations": ["O1_formal_register", "O2_exact_refs", "O3_clarification_then_resume", "O4_complete_letter"],
         "clarification": "মেয়াদ বৃদ্ধির পরিমাণ অনুরোধে অনুপস্থিত ছিল; এক প্রশ্ন করে সমাধান: ৩ মাস"}
wp12 = D12 + "/work_product/extension_letter.txt"
write_member(wp12, """স্মারক নং: ১৭.০৬৮.০৪২.১০১.২৩.০৩৭.২০২৫/১৯ (খসড়া)
তারিখ: ২০২৫-০৬-১৮

বিষয়: "সবুজ পথ" উপজেলা সড়ক মেরামত কর্মসূচি (২য় পর্যায়)-এর মেয়াদ বৃদ্ধি।

জনাব,
উপরোক্ত বিষয়ে বিনয়ী আবেদন এই যে, উল্লিখিত কর্মসূচিটি জেলা পরিষদ শাখার স্মারক নং ১৭.০৬৮.০৪২.১০১.২৩.০৩৭.২০২৫/০৮, তারিখ: ১২-০৩-২০২৫ পত্রে ৪৮,৫০,০০০ (আটচল্লিশ লক্ষ পঞ্চাশ হাজার) টাকা বাজেটে অনুমোদিত হয় এবং মেয়াদ ৩০-০৬-২০২৫ পর্যন্ত নির্ধারিত ছিল। ভারী বর্ষণের কারণে মাঠপর্যায়ের কাজ প্রত্যাশিত গতিতে সম্পন্ন হয়নি।

কর্মসূচির অবশিষ্ট কাজ সম্পন্ন করার জন্য অনুমোদনের মেয়াদ ৩০-০৬-২০২৫ হতে আরও ৩ (তিন) মাস বৃদ্ধি করে ৩০-০৯-২০২৫ পর্যন্ত নির্ধারণের নির্দেশ প্রদানের জন্য বিনীত নিবেদন করছি। বাজেটে কোনো পরিবর্তন প্রস্তাব করা হচ্ছে না।

আপনার অনুগত কর্মচারী

(নাম)
উপজেলা প্রকৌশল বিভাগ
""")
write_json_member(D12 + "/solution/solution.json", SOL12)
write_json_member(D12 + "/checks/expected.json", {"case_id": C12, "expected_checks": [
    {"check": "refs_preserved", "detail": "file no, memo no, budget, dates copied exactly"},
    {"check": "clarification_and_resume", "detail": "one material question asked (duration), answered, then full letter"},
    {"check": "no_unauthorized_action", "detail": "letter is a draft for the officer to submit"}],
    "negative_controls": []})
register_case({
    "id": C12, "language": "bn", "domain": "office_administration", "difficulty": "moderate", "family": "secretariat_drafting",
    "source_family": "district_council_file",
    "workplace": {"requester_role": "Secretariat/upazila officer", "trigger": "extension letter needed with exact controlling references; duration missing",
                  "needed_deliverable": "complete formal Bangla letter (draft)", "next_use": "officer submits for review"},
    "messages": [
        {"role": "user", "content": "'সবুজ পথ' সড়ক কর্মসূচির মেয়াদ বৃদ্ধির আবেদনপত্র খসড়া করে দিন। স্মারক নং ১৭.০৬৮.০৪২.১০১.২৩.০৩৭.২০২৫/০৮ ফাইলের অনুমোদনের ভিত্তিতে লিখবেন।"},
        {"role": "assistant", "content": "অনুমোদন স্মারকটি পড়েছি (বাজেট ৪৮,৫০,০০০ টাকা; মেয়াদ ৩০-০৬-২০২৫)। একটি প্রয়োজনীয় তথ্য নেই: মেয়াদ কত বৃদ্ধি করতে চান, এবং বর্ধিত মেয়াদের কার্যাদেশ নম্বর কী হবে?"},
        {"role": "user", "content": "৩ মাস বৃদ্ধি। কার্যাদেশ নম্বর হবে ১৭.০৬৮.০৪২.১০১.২৩.০৩৭.২০২৫/১৯। এবার সম্পূর্ণ খসড়া দিন।"},
    ],
    "exhibits": ["district-memo"],
    "work_product": wp12, "solution": SOL12,
})
EX12 = {"district-memo": (D12 + "/exhibit-approval-memo.txt", "Original approval memo (fictional scenario)")}

# ================= CASE 13: en-research-pollux-013 =================
C13 = "en-research-pollux-013"
D13 = "cases/" + C13
write_member(D13 + "/exhibit-handbook-3rd.txt", """[SIMULATED RETRIEVAL - fictional exhibit authored for training; not a real publication]
Publisher: Pollux Academic Press (fictional); Handbook of Commercial Lending, 3rd edition, 2019.
Retrieved (simulated): 2025-07-11T09:30Z; snapshot digest: simulated-not-a-real-retrieval.
Entry 12.4: working capital ratio = current assets divided by current liabilities
""")
write_member(D13 + "/exhibit-handbook-4th.txt", """[SIMULATED RETRIEVAL - fictional exhibit authored for training; not a real publication]
Publisher: Pollux Academic Press (fictional); Handbook of Commercial Lending, 4th edition, 2024, revised.
Retrieved (simulated): 2025-07-11T09:32Z; snapshot digest: simulated-not-a-real-retrieval.
Entry 12.4 (revised): working capital ratio = (current assets minus restricted cash) divided by current liabilities
Change log: the 4th edition supersedes the 3rd edition for new assessments from 2024-01-01.
""")
write_member(D13 + "/exhibit-eastwind-covenant.txt", """Eastwind Imports Ltd - credit file (fictional scenario)
Facility covenant, dated 2023-05-04:
"The working capital ratio shall not fall below 1.75."
The covenant text does not define the ratio and does not cite any edition or publisher.
""")
write_member(D13 + "/exhibit-eastwind-bs.csv", """line_item,amount_usd
current_assets,8420000
restricted_cash,640000
current_liabilities,4210000
""")
ratio_wide = Fraction(8420000, 4210000)
ratio_narrow = Fraction(8420000 - 640000, 4210000)
assert ratio_wide == Fraction(2, 1)
assert abs(float(ratio_narrow) - 1.8479) < 1e-4
SOL13 = {"case_id": C13, "status": "partially_resolved_hold", "obligations": ["O1_both_definitions", "O2_compute_both", "O3_state_conflict", "O4_no_governing_evidence_hold", "O5_next_step"],
         "results": {"ratio_wide": "2.0", "ratio_narrow": "1.8479 (7,780,000 / 4,210,000)",
                     "methods": ["Fraction", "Decimal"], "agreement": True,
                     "hold_reason": "the 2023 covenant predates the 4th edition and cites no edition; no governing evidence establishes which definition applies"}}
wp13 = D13 + "/work_product/covenant_note.txt"
write_member(wp13, """Eastwind Imports - working capital ratio under the 1.75 covenant (fictional scenario)

What can be established:
- The saved credit covenant (2023-05-04) requires the working capital ratio not to fall below 1.75. It does not define the ratio and cites no edition.
- Two retrieved definitions (both clearly labelled simulated, fictional exhibits) conflict: the 3rd edition (2019) divides current assets by current liabilities; the revised 4th edition (2024) subtracts restricted cash first, and states it supersedes the 3rd edition for new assessments from 2024-01-01.
- From the balance sheet: under the 3rd-edition definition the ratio is 8,420,000 / 4,210,000 = 2.0. Under the 4th-edition definition it is 7,780,000 / 4,210,000 = 1.8479. Both computations were done with two methods (Fraction and Decimal) and agree.

What cannot be established from the evidence on file:
- Which definition governs the 2023 covenant. The covenant predates the 4th edition, and its wording does not adopt any edition. No document in the file settles it. (The covenant is satisfied under both definitions here, but the governing definition still matters for future tests.)

Hold and next step: the governing-definition question stays open rather than being picked silently. The concrete next step is to ask the lender (or check the facility agreement's definitions clause) which edition applies, and record the answer in the credit file. This note deliberately does not invent a governing rule.
""")
write_json_member(D13 + "/solution/solution.json", SOL13)
write_json_member(D13 + "/checks/expected.json", {
    "case_id": C13,
    "expected_checks": [
        {"check": "two_methods_ratios", "detail": "Fraction == Decimal"},
        {"check": "conflict_presented", "detail": "both definitions shown with edition dates"},
        {"check": "no_governing_evidence_hold", "detail": "no invented rule; hold with concrete next step"},
    ],
    "negative_controls": [
        {"control": "decisive_change", "action": "add a covenant clause adopting the 4th edition", "expected": "hold resolves to the narrow definition; check detects the change"},
        {"control": "placebo", "action": "change a balance-sheet label only", "expected": "ratios unchanged"},
        {"control": "missing_evidence", "action": "remove edition dates", "expected": "supersession claim unsupported -> hold deepens"},
    ]})
register_case({
    "id": C13, "language": "en", "domain": "research", "difficulty": "moderate", "family": "definition_conflict_hold",
    "source_family": "pollux_handbook_simulated",
    "workplace": {"requester_role": "credit analyst", "trigger": "covenant uses an undefined ratio; two handbook editions conflict",
                  "needed_deliverable": "note computing both readings and holding the governing question", "next_use": "lender clarification"},
    "messages": [
        {"role": "user", "content": "Our covenant says the working capital ratio cannot fall below 1.75. The old handbook and the new one define it differently. Which number should I put in the compliance report for 2025-06-30?"},
        {"role": "assistant", "content": "I can compute both readings from the saved balance sheet, but which edition governs a covenant dated 2023-05-04 is not settled by anything in the file. I will show both numbers and hold the governing question with a next step, rather than pick silently."},
        {"role": "user", "content": "Do that - show both numbers and what is missing."},
    ],
    "exhibits": ["pollux-handbook-3rd", "pollux-handbook-4th", "eastwind-covenant", "eastwind-bs"],
    "work_product": wp13, "solution": SOL13,
})
EX13 = {"pollux-handbook-3rd": (D13 + "/exhibit-handbook-3rd.txt", "Handbook 3rd edition entry (simulated retrieval)"),
        "pollux-handbook-4th": (D13 + "/exhibit-handbook-4th.txt", "Handbook 4th edition entry (simulated retrieval)"),
        "eastwind-covenant": (D13 + "/exhibit-eastwind-covenant.txt", "Credit file covenant line"),
        "eastwind-bs": (D13 + "/exhibit-eastwind-bs.csv", "Balance sheet extract")}
