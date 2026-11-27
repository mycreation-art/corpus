import json
from decimal import Decimal
from fractions import Fraction
from common import *
from build_b import OUT, register_case

# ================= CASE 4: en-extract-zuboria-004 =================
C4 = "en-extract-zuboria-004"
D4 = "cases/" + C4
ROW4 = "Zuboria (ZBA) | SP.POP.TOTL | Population, total | 2021=5840000, 2022=5910000, 2023=5985000"
write_member(D4 + "/exhibit-indicator.txt", ROW4 + "\n")
assert 5985000 - 5840000 == 145000
SOL4 = {"case_id": C4, "status": "solved", "obligations": ["O1_header_atom", "O2_observation_atoms", "O3_separator_preserved", "O4_chat_answer"],
        "results": {"population_change_2021_to_2023": 145000}}
wp4 = D4 + "/work_product/extract_notes.txt"
write_member(wp4, """Extract notes (fictional Zuboria table)
- Header atom: text is the exact header prefix including the trailing " | "; targets carry the three literal pointers (country, series, unit).
- Observation atoms: text is "YYYY=value" plus the two-character ", " separator for every nonfinal observation. The final observation has no trailing separator.
- Missing values are unknown, never zero. All four atoms rebuilt programmatically from the saved line on disk and compared to the JSONL rows, including exact separators.
""")
write_json_member(D4 + "/solution/solution.json", SOL4)
write_json_member(D4 + "/checks/expected.json", {
    "case_id": C4,
    "expected_checks": [
        {"check": "extract_source_parity", "detail": "atoms and targets rebuilt from the cited line; exact equality"},
        {"check": "nonfinal_separator", "detail": "input.text of 2021/2022 atoms ends with ', '; P2 omits it"},
        {"check": "pointer_uniqueness", "detail": "each pointer occurs exactly once in its atom; <= 64 code points"},
    ],
    "negative_controls": [
        {"control": "decisive_change", "action": "strip trailing ', ' from the 2021 observation input", "expected": "parity check must reject the row"},
        {"control": "placebo", "action": "no change", "expected": "rows pass unchanged"},
        {"control": "missing_evidence", "action": "point evidence_ids at a foreign exhibit", "expected": "linkage check must reject"},
    ]})
register_case({
    "id": C4, "language": "en", "domain": "research", "difficulty": "moderate", "family": "indicator_extraction",
    "source_family": "zuboria_statistics_table",
    "workplace": {"requester_role": "policy analyst", "trigger": "saved indicator table must be turned into typed atoms for a slide",
                  "needed_deliverable": "header and observation atoms under the extract_legacy profile", "next_use": "chart drafting"},
    "messages": [
        {"role": "user", "content": "Here is our saved Zuboria population table. Extract it into the standard atoms and tell me how much the population grew from 2021 to 2023."},
    ],
    "exhibits": ["zuboria-indicator"],
    "work_product": wp4, "solution": SOL4,
})
EX4 = {"zuboria-indicator": (D4 + "/exhibit-indicator.txt", "Zuboria population indicator table (one literal row)")}

# ================= CASE 5: en-demand-clarion-005 =================
C5 = "en-demand-clarion-005"
D5 = "cases/" + C5
write_member(D5 + "/exhibit-indicator-rows.txt",
             "Clarion Islands (CRI) | EG.ELC.ACCS.UR.ZS | Access to electricity, urban (% of urban population) | 2018=96.4, 2019=97.1, 2020=97.8, 2021=98.2, 2022=98.6\n"
             "Clarion Islands (CRI) | EG.ELC.ACCS.RU.ZS | Access to electricity, rural (% of rural population) | 2018=41.2, 2019=48.7, 2020=57.9, 2021=66.4, 2022=74.1\n")
UR = {"2018": 96.4, "2019": 97.1, "2020": 97.8, "2021": 98.2, "2022": 98.6}
RU = {"2018": 41.2, "2019": 48.7, "2020": 57.9, "2021": 66.4, "2022": 74.1}
gaps = {y: round(UR[y] - RU[y], 1) for y in ["2018", "2019", "2020", "2021", "2022"]}
all_narrowing = gaps["2018"] > gaps["2019"] > gaps["2020"] > gaps["2021"] > gaps["2022"]
net = round(gaps["2018"] - gaps["2022"], 1)
assert net == 30.7 and all_narrowing
SOL5 = {"case_id": C5, "status": "solved", "obligations": ["O1_both_rows_saved", "O2_annual_gaps_pp", "O3_interval_directions", "O4_net_narrowing"],
        "results": {"gaps_pp": gaps, "every_interval_narrowing": True, "net_narrowing_pp": net}}
wp5 = D5 + "/work_product/gap_answer.txt"
write_member(wp5, """Clarion Islands (fictional) - urban-rural electricity access gap, 2018-2022
Annual gap (urban minus rural, percentage points), from the two saved indicator rows:
2018: 96.4 - 41.2 = 55.2 pp
2019: 97.1 - 48.7 = 48.4 pp
2020: 97.8 - 57.9 = 39.9 pp
2021: 98.2 - 66.4 = 31.8 pp
2022: 98.6 - 74.1 = 24.5 pp
Every interval narrowed, and the gap narrowed by 30.7 percentage points net over the period (55.2 -> 24.5).
Values are fictional and were verified against the saved rows; both rows cover exactly 2018-2022 with no missing values.
""")
write_json_member(D5 + "/solution/solution.json", SOL5)
write_json_member(D5 + "/checks/expected.json", {
    "case_id": C5,
    "expected_checks": [
        {"check": "two_exact_rows", "detail": "UR.ZS and RU.ZS rows with exact units, continuous 2018-2022, values 0-100"},
        {"check": "gap_computation", "detail": "annual gaps recomputed from saved rows"},
        {"check": "demand_input_shape", "detail": "input has exactly operation and request"},
        {"check": "request_shape", "detail": "country name once; two ascending four-digit year endpoints"},
    ],
    "negative_controls": [
        {"control": "decisive_change", "action": "swap one urban value with the rural value", "expected": "gap direction check must fail"},
        {"control": "placebo", "action": "no change", "expected": "case unaffected"},
        {"control": "missing_evidence", "action": "empty evidence_ids on the DEMAND row", "expected": "source-binding check must reject"},
    ]})
register_case({
    "id": C5, "language": "en", "domain": "public_statistics", "difficulty": "moderate", "family": "indicator_gap_request",
    "source_family": "clarion_statistics_table",
    "workplace": {"requester_role": "program officer", "trigger": "urban-rural access gap needed for a briefing",
                  "needed_deliverable": "annual gaps in percentage points with direction and net narrowing", "next_use": "briefing slide"},
    "messages": [
        {"role": "user", "content": "Using the saved Clarion Islands access table, give me the annual urban-rural gap in percentage points for 2018 through 2022 and tell me whether the gap narrowed over the period."},
    ],
    "exhibits": ["clarion-rows"],
    "work_product": wp5, "solution": SOL5,
})
EX5 = {"clarion-rows": (D5 + "/exhibit-indicator-rows.txt", "Clarion Islands access indicator rows (two literal rows)")}

# ================= CASE 6: bn-school-rimu-006 =================
C6 = "bn-school-rimu-006"
D6 = "cases/" + C6
SOL6 = {"case_id": C6, "status": "solved", "obligations": ["O1_direct_answer", "O2_check"], "class_level": 2, "subject": "গণিত (ভাগ)",
        "answer": "১৪টা লিচু ৪ জনে ভাগ করলে সবাই ৩টা করে পাবে, ২টা বাকি থাকবে",
        "check": "4 x 3 = 12; 12 + 2 = 14"}
wp6 = D6 + "/work_product/answer.txt"
write_member(wp6, "১৪টা লিচুকে ৪ জনের মধ্যে সমান ভাগ করতে হবে। ৪ জন প্রত্যেকে ৩টা করে পেলে মোট ১২টা যায় (৪ × ৩ = ১২)। "
                 "১৪ − ১২ = ২, তাই ২টা লিচু বাকি থাকবে—ওগুলো পরে মা-বাবাকে দেওয়া যাবে। যাচাই: ৩ + ৩ + ৩ + ৩ = ১২, আর ১২ + ২ = ১৪।\n")
write_json_member(D6 + "/solution/solution.json", SOL6)
write_json_member(D6 + "/checks/expected.json", {"case_id": C6, "expected_checks": [
    {"check": "answer_from_problem", "detail": "14 = 4x3 + 2 verified"},
    {"check": "class_level_language", "detail": "Class 2 wording, no formal terms"}],
    "negative_controls": []})
register_case({
    "id": C6, "language": "bn", "domain": "education", "difficulty": "easy", "family": "primary_sharing_division",
    "source_family": "none_conversation", "school_tag": {"class": 2, "subject": "গণিত"},
    "workplace": {"requester_role": "Class 2 learner", "trigger": "sharing lychees equally, then the count changes",
                  "needed_deliverable": "warm direct answer with a check", "next_use": "child retries with own numbers"},
    "messages": [
        {"role": "user", "content": "আম্মু ১২টা লিচু দিয়েছে। আমি, তুহিন, সাদিয়া আর রাফি—মোট ৪ জন—সমান ভাগ করে নিলে কে কয়টা পাবে?"},
        {"role": "assistant", "content": "১২টা লিচু ৪ জনে সমান ভাগ করলে প্রত্যেকে ৩টা করে পাবে, কারণ ১২ ÷ ৪ = ৩। যাচাই করো: ৩ + ৩ + ৩ + ৩ = ১২।"},
        {"role": "user", "content": "থামো! আম্মু আরো ২টা লিচু দিয়েছে। এখন কে কয়টা পাবে?"},
    ],
    "exhibits": [], "work_product": wp6, "solution": SOL6,
})

# ================= CASE 7: en-school-ayaan-007 =================
C7 = "en-school-ayaan-007"
D7 = "cases/" + C7
SOL7 = {"case_id": C7, "status": "solved", "obligations": ["O1_misconception_correction", "O2_transfer_check"], "class_level": 4, "subject": "fractions",
        "answer": "Ayaan is not right; one-sixth of an equal roti is bigger than one-eighth, and one-fifth is bigger than one-seventh",
        "transfer_check": "1/5 vs 1/7: more pieces means smaller pieces"}
wp7 = D7 + "/work_product/answer.txt"
write_member(wp7, """Ayaan is not right. Take two rotis of exactly the same size. Cut one into 8 equal pieces and the other into 6 equal pieces. Now hold up one piece from each roti: because the first roti was cut into more pieces, each piece has to be smaller. One piece out of 6 is bigger than one piece out of 8, so one-sixth of a roti is more roti than one-eighth.

Try the same idea with new numbers: which is bigger, one-fifth or one-seventh? Seven pieces of the same roti are smaller than five pieces, so one-fifth is bigger. When the bottom number grows, each piece shrinks - as long as the whole is the same size.
""")
write_json_member(D7 + "/solution/solution.json", SOL7)
write_json_member(D7 + "/checks/expected.json", {"case_id": C7, "expected_checks": [
    {"check": "misconception_addressed", "detail": "8>6 misconception refuted with equal-whole comparison"},
    {"check": "transfer_check", "detail": "1/5 vs 1/7 included"}],
    "negative_controls": []})
register_case({
    "id": C7, "language": "en", "domain": "education", "difficulty": "easy", "family": "fraction_misconception_tutoring",
    "source_family": "none_conversation", "school_tag": {"class": 4, "subject": "Mathematics"},
    "workplace": {"requester_role": "Class 4 learner", "trigger": "believes 1/8 > 1/6 because 8 > 6",
                  "needed_deliverable": "concrete correction plus a transfer check", "next_use": "child compares new fraction pairs"},
    "messages": [
        {"role": "user", "content": "Ayaan cut one roti into 8 equal pieces and another same-size roti into 6 equal pieces. He says one piece of the 8-piece roti is bigger because 8 is bigger than 6. Is he right?"},
        {"role": "assistant", "content": "Good challenge to test. Picture the two whole rotis being exactly the same size, then compare one piece from each - I will walk through it with you."},
        {"role": "user", "content": "Okay. Then which is bigger: one-fifth of a roti or one-seventh?"},
    ],
    "exhibits": [], "work_product": wp7, "solution": SOL7,
})

# ================= CASE 8: bn-school-tasnim-008 =================
C8 = "bn-school-tasnim-008"
D8 = "cases/" + C8
girls = 40 * 60 // 100
boys = 40 - girls
assert (girls, boys) == (24, 16)
new_pct = Fraction(29, 45) * 100
assert abs(float(new_pct) - 64.4444) < 1e-3
SOL8 = {"case_id": C8, "status": "solved", "obligations": ["O1_both_parts", "O2_check_and_rounding"], "class_level": 7, "subject": "শতকরা ও অনুপাত",
        "answers": {"girls_boys": "২৪ জন ছাত্রী, ১৬ জন ছাত্র", "new_percent": "৬৪.৪% (২৯/৪৫ = ৬৪.৪৪...%)"},
        "methods": ["percentage x integer division", "Fraction"], "agreement": True}
wp8 = D8 + "/work_product/answer.txt"
write_member(wp8, """প্রথম অংশ: মোট ৪০ জন, ছাত্রী ৬০%।
ছাত্রী = ৪০ × ৬০/১০০ = ২৪ জন। ছাত্র = ৪০ − ২৪ = ১৬ জন।
যাচাই: ২৪ + ১৬ = ৪০ এবং ২৪/৪০ = ৬০%।

দ্বিতীয় অংশ: ৫ জন নতুন ছাত্রী ভর্তি হলে মোট = ৪০ + ৫ = ৪৫ জন, ছাত্রী = ২৪ + ৫ = ২৯ জন।
নতুন শতকরা = ২৯/৪৫ × ১০০ = ৬৪.৪৪...% ≈ ৬৪.৪%।
খেয়াল: ২৯/৪৫ আর ৬৪.৪৪% একই কথা; শুধু "৬৪ শতাংশ" লিখলে ভুল হবে, দশমিকের পরের অংশ রাখতে হবে।
""")
write_json_member(D8 + "/solution/solution.json", SOL8)
write_json_member(D8 + "/checks/expected.json", {"case_id": C8, "expected_checks": [
    {"check": "two_methods", "detail": "integer division == Fraction for both parts"},
    {"check": "units_and_rounding", "detail": "64.4% shown with the exact fraction"}],
    "negative_controls": []})
register_case({
    "id": C8, "language": "bn", "domain": "education", "difficulty": "moderate", "family": "percentage_composition",
    "source_family": "none_conversation", "school_tag": {"class": 7, "subject": "গণিত"},
    "workplace": {"requester_role": "Class 7 learner", "trigger": "percentage of a class, then admission changes the denominator",
                  "needed_deliverable": "full worked solution with a check and a rounding caution", "next_use": "exam practice"},
    "messages": [
        {"role": "user", "content": "একটি ক্লাসে ছাত্রছাত্রী মিলিয়ে ৪০ জন। ছাত্রী ৬০%। কয়জন ছাত্রী, কয়জন ছাত্র? পরে ৫ জন নতুন ছাত্রী ভর্তি হলে ছাত্রীর নতুন শতকরা হবে কত?"},
    ],
    "exhibits": [], "work_product": wp8, "solution": SOL8,
})

# ================= CASE 9: en-school-nabila-009 =================
C9 = "en-school-nabila-009"
D9 = "cases/" + C9
assert Fraction(25000, 500) == 50
check_total = 25000 + 350 * 50
assert check_total == 850 * 50 == 42500
SOL9 = {"case_id": C9, "status": "solved", "obligations": ["O1_solution", "O2_verification", "O3_diagnosis"], "class_level": 10, "subject": "algebra",
        "answer": 50, "method": "25000 + 350n = 850n", "check": "both sides equal 42,500 taka at n = 50"}
wp9 = D9 + "/work_product/answer.txt"
write_member(wp9, """Setting it up: the trip has a fixed cost of 25,000 taka plus 350 taka per student, and the cost per student is 850 taka.
Let n be the number of students. Total cost = 25,000 + 350n. Cost per student = (25,000 + 350n) / n = 850.
So 25,000 + 350n = 850n, which gives 25,000 = 500n, so n = 50.
Check: at 50 students the total is 25,000 + 350 x 50 = 42,500, and 42,500 / 50 = 850 taka per student. Both sides agree.

Why 60 is wrong: with 60 students the total is 25,000 + 21,000 = 46,000, and 46,000 / 60 = 766.67 taka per student, not 850. The fixed 25,000 spreads over more students, so more students means a LOWER per-student cost - that is the exact step to reuse on any fixed-cost problem.
""")
write_json_member(D9 + "/solution/solution.json", SOL9)
write_json_member(D9 + "/checks/expected.json", {"case_id": C9, "expected_checks": [
    {"check": "equation_solution", "detail": "n = 50 verified at 42,500"},
    {"check": "misconception_diagnosis", "detail": "60-student error explained via fixed-cost spread"}],
    "negative_controls": []})
register_case({
    "id": C9, "language": "en", "domain": "education", "difficulty": "hard", "family": "algebra_fixed_cost",
    "source_family": "none_conversation", "school_tag": {"class": 10, "subject": "Mathematics"},
    "workplace": {"requester_role": "Class 10 learner", "trigger": "word problem with a guessed wrong answer (60)",
                  "needed_deliverable": "full solution, verification, and diagnosis of the wrong method", "next_use": "learner rewrites the solution in own words"},
    "messages": [
        {"role": "user", "content": "A school trip costs 25,000 taka fixed plus 350 taka per student. The cost per student comes to 850 taka. I guessed 60 students but the teacher said it is wrong. How many students are going, and why was my guess wrong? Please show it so I can redo it myself."},
    ],
    "exhibits": [], "work_product": wp9, "solution": SOL9,
})
