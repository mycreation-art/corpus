import json, os, shutil
from common import STAGING

if os.path.isdir(STAGING):
    shutil.rmtree(STAGING)
os.makedirs(STAGING)

from common import *
from build_b import OUT as CASES, EX2, EX3
from build_c import EX4, EX5
from build_d import EX12, EX13
from build_e import ROLE_PART1
import case_wide as W
import build_a as A

CID1 = W.CASE_ID
D1 = "cases/" + CID1

TC = {"allowed_tools": [], "required": False}
ROLE_PART2 = []


def chat(rid, case_id, language, family, messages, target, evidence):
    ROLE_PART2.append({"id": rid, "case_id": case_id, "partition": "train", "operation": "CHAT",
                       "profile": "chat_text", "language": language, "family": family,
                       "input": {"operation": "CHAT", "messages": messages, "tool_context": TC},
                       "target": target, "evidence_ids": evidence})


# ---------- case 1 ----------
chat("rc-shapla-chat-hold", CID1, "bn", "wide_reconciliation_dossier",
     [{"role": "user", "content": "রেজিস্টারে INV-S-2025-0312 (মেঘনা সিমেন্ট ট্রেডার্স) কেন হোল্ড করা হলো?"}],
     "INV-S-2025-0312 (২,৬৫,০০০ টাকা, B-109) হোল্ড করা হয়েছে কারণ খাতায় এর সরবরাহ সনদ (ডেলিভারি সার্টিফিকেট) নথিভুক্ত নয়—ক্রয় খাতার L-310 সারিতে annex_status = missing_annex। ব্যাংক ডেবিট ২০২৫-০৬-০৯-এ হয়েছে, অর্থাৎ টাকা গেছে, কিন্তু প্রমাণপত্র ছাড়া রিলিজ দেওয়া ঝুঁকিপূর্ণ। সনদ ফাইলে যুক্ত হলে আমরা সারিটি পুনঃমূল্যায়ন করে রিলিজ করব। সূত্র: B-109, L-310।",
     ["shapla-ledger-q2", "shapla-bank-q2"])

CHAT1_MESSAGES = [
    {"role": "user", "content": "কিউ২ শেষে ব্যাংক আর খাতার মিলকরণ রেজিস্টার বানিয়ে দিন; ৩০ জুন ১৭:০০ UTC-এর মধ্যে দরকার।"},
    {"role": "assistant", "content": "পেয়েছি। চারটি উৎস (ব্যাংক এক্সপোর্ট, ক্রয় খাতা, সংশোধনী স্মারক, ইমেইল) জমে নিয়ে সারি-স্তরে মিলিয়ে রিলিজ/হোল্ড রেজিস্টার তৈরি করছি; সময়সীমা ঢাকা সময়ে রাত ১১টা।"},
    {"role": "user", "content": "জুলাই ১ তারিখের পরিশোধ রানের প্রতিশ্রুত অংকও আলাদা অংশে দেখান; বাকি রেজিস্টার অপরিবর্তিত রাখুন।"},
    {"role": "assistant", "content": "ঠিক আছে—সংশোধনী-৪ অনুযায়ী জুলাই পরিশোধ রানের ৩,৭৬,৫০০ টাকা (INV-D-2025-0047) আলাদা 'প্রতিশ্রুত অংশ' হিসেবে যোগ হবে; এ পর্যন্ত অনুমোদিত রেজিস্টার সারি কোনোটাই বদলাবে না।"},
    {"role": "user", "content": "গ্রুপ অডিট কমিটির জন্য ইংরেজি এক্সিকিউটিভ সামারি যোগ করুন।"},
]
chat("rc-shapla-chat-delivery", CID1, "bn", "wide_reconciliation_dossier", CHAT1_MESSAGES,
     "ইংরেজি এক্সিকিউটিভ সামারি প্রস্তুত (board_summary_en.txt): মোট কিউ২ ব্যাংক ডেবিট ২৮,২০,৫০০ টাকা; রিলিজড ২৫,৩৫,৯০০ টাকা; হোল্ড ২,৬৫,০০০ টাকা (সনদ অনুপস্থিত); ব্যাংক চার্জ ১৮,৬০০ টাকা এলোকেশনহীন; জুলাই প্রতিশ্রুত ৩,৭৬,৫০০ টাকা। সমস্ত তথ্য বাংলা রেজিস্টারের অনুমোদিত সারি থেকে নেওয়া, কোনো সংখ্যা পুনঃগণনা ছাড়া অপরিবর্তিত। খসড়া পর্যালোচনার জন্য প্রস্তুত; কোনো পরিশোধ নির্বাহ হয়নি।",
     ["shapla-bank-q2", "shapla-ledger-q2", "shapla-amendments", "shapla-emails"])

# ---------- case 2 ----------
chat("rc-novustex-chat-rec", "en-board-novustex-002", "en", "board_covenant_decision",
     [{"role": "user", "content": "We have two term sheets for the 60 million machinery loan. Which one should I put to the board, and what would make me wrong? Keep it short enough for the board pack."},
      {"role": "assistant", "content": "I can answer from the covenant extract, EBITDA file, debt schedule and both term sheets on file. One check first: should I treat the 6.2m sale-leaseback gain as excluded, per Bank B's own covenant wording, while it is still unaudited?"},
      {"role": "user", "content": "Yes - use the exclusion-adjusted EBITDA for feasibility, and say clearly what would reverse the recommendation."}],
     "Recommend Bank A: BDT 60,000,000, 11.75%, 5-year. On exclusion-adjusted EBITDA of BDT 62,200,000, pro-forma leverage is 2.1418 against the 2.5x group covenant (passes), DSCR 1.4355 against the 1.30 threshold (passes), and the 5-year tenor matches your stated preference. Bank B is cheaper at 10.90% but breaches its own binding 2.2x exclusion-adjusted covenant at this size (2.3553); it only becomes feasible at BDT 50,340,000 or less. What would reverse this: auditors confirming the 6.2m gain is not one-off - then B's leverage is 2.1418 and the choice is between B's cheaper rate and your 5-year preference. Draft only; nothing signed.",
     ["novustex-covenant", "novustex-ebitda", "novustex-debt", "novustex-termsheets"])

# ---------- case 3 ----------
chat("rc-brahma-chat-why", "bn-recon-brahmaputra-003", "bn", "supplier_reconciliation",
     [{"role": "user", "content": "সরবরাহকারীর বিবরণী আর আমার ক্যাশ বুকের মোট দুটোই ২,৮৮,১৩০ টাকা দেখাচ্ছে, তাহলে মিলকরণ তো ঠিক আছে?"},
      {"role": "assistant", "content": "মোট মিলে গেলেও সারি ধরে মিলিয়ে দেখা দরকার — আমি উভয় ফাইল খুলে সারি-স্তরে যাচাই করছি।"},
      {"role": "user", "content": "ঠিক আছে, সারি ধরে মিলিয়ে বলুন কোথায় সমস্যা।"}],
     "মোট মিললেও সমস্যা আছে—দুটি ত্রুটি ঠিক একে অপরকে প্রতিহত করেছে: (১) প্রারম্ভিক বকেয়া খাতায় ৪,৫৮,২০০.০০ টাকা, বিবরণীতে ৫,০০,০০০.০০ টাকা—৪১,৮০০ টাকা কম; (২) বিল BHD-1191 খাতায় ২,২৬,৮০০.০০ টাকা, বিবরণীতে ১,৮৫,০০০.০০ টাকা—৪১,৮০০ টাকা বেশি। ফলে সমাপনী ২,৮৮,১৩০.০০ টাকা কাকতালীয়ভাবে সঠিক, কিন্তু CB-01 ও CB-03 সংশোধন করতে হবে, নইলে আগস্টে বিল মিলবে না। পূর্ণ স্মারক: reconciliation_memo।",
     ["brahmaputra-statement", "brahmaputra-cashbook"])

# ---------- case 4 ----------
chat("rc-zuboria-chat-growth", "en-extract-zuboria-004", "en", "indicator_extraction",
     [{"role": "user", "content": "Here is our saved Zuboria population table. How much did the population grow from 2021 to 2023, and which series is it?"}],
     "Per the saved row, the series is SP.POP.TOTL (Population, total) for Zuboria (ZBA). The population grew from 5,840,000 in 2021 to 5,985,000 in 2023 - an increase of 145,000.",
     ["zuboria-indicator"])

# ---------- case 5 ----------
chat("rc-clarion-chat-gaps", "en-demand-clarion-005", "en", "indicator_gap_request",
     [{"role": "user", "content": "Using the saved Clarion Islands access table, give me the annual urban-rural gap in percentage points for 2018 through 2022 and tell me whether the gap narrowed over the period."}],
     "From the two saved Clarion Islands rows (fictional values), the urban-rural gap in percentage points is: 2018: 55.2; 2019: 48.4; 2020: 39.9; 2021: 31.8; 2022: 24.5. Every interval narrowed, and the gap narrowed by 30.7 percentage points net over the period (55.2 down to 24.5). Both rows cover exactly 2018-2022 with no missing values.",
     ["clarion-rows"])

# ---------- school / basic / office chats ----------
chat("rc-rimu-chat-14", "bn-school-rimu-006", "bn", "primary_sharing_division",
     [{"role": "user", "content": "আম্মু ১২টা লিচু দিয়েছে। আমি, তুহিন, সাদিয়া আর রাফি—মোট ৪ জন—সমান ভাগ করে নিলে কে কয়টা পাবে?"},
      {"role": "assistant", "content": "১২টা লিচু ৪ জনে সমান ভাগ করলে প্রত্যেকে ৩টা করে পাবে, কারণ ১২ ÷ ৪ = ৩। যাচাই করো: ৩ + ৩ + ৩ + ৩ = ১২।"},
      {"role": "user", "content": "থামো! আম্মু আরো ২টা লিচু দিয়েছে। এখন কে কয়টা পাবে?"}],
     "এখন ১২ + ২ = ১৪টা লিচু। ৪ জন প্রত্যেকে ৩টা করে পেলে ১২টা যায় (৪ × ৩ = ১২), তাই ২টা বাকি থাকবে—ওগুলো মা-বাবাকে দেওয়া যাবে। যাচাই: ৩ + ৩ + ৩ + ৩ = ১২, আর ১২ + ২ = ১৪।",
     [])

chat("rc-ayaan-chat-fractions", "en-school-ayaan-007", "en", "fraction_misconception_tutoring",
     [{"role": "user", "content": "Ayaan cut one roti into 8 equal pieces and another same-size roti into 6 equal pieces. He says one piece of the 8-piece roti is bigger because 8 is bigger than 6. Is he right?"},
      {"role": "assistant", "content": "Good challenge to test. Picture the two whole rotis being exactly the same size, then compare one piece from each - I will walk through it with you."},
      {"role": "user", "content": "Okay. Then which is bigger: one-fifth of a roti or one-seventh?"}],
     "One-fifth is bigger. Cut the same-size roti into 5 equal pieces and another into 7: more pieces means each piece is smaller, so one piece out of 7 is smaller than one piece out of 5. The same idea answers Ayaan's rotis - one-sixth is bigger than one-eighth, even though 8 is a bigger number, because cutting into more pieces makes each piece smaller when the whole roti is the same size.",
     [])

chat("rc-tasnim-chat-percent", "bn-school-tasnim-008", "bn", "percentage_composition",
     [{"role": "user", "content": "একটি ক্লাসে ছাত্রছাত্রী মিলিয়ে ৪০ জন। ছাত্রী ৬০%। কয়জন ছাত্রী, কয়জন ছাত্র? পরে ৫ জন নতুন ছাত্রী ভর্তি হলে ছাত্রীর নতুন শতকরা হবে কত?"}],
     "ছাত্রী = ৪০ × ৬০/১০০ = ২৪ জন; ছাত্র = ৪০ − ২৪ = ১৬ জন। যাচাই: ২৪ + ১৬ = ৪০ এবং ২৪/৪০ = ৬০%। ৫ জন নতুন ছাত্রী ভর্তি হলে মোট ৪৫ জন, ছাত্রী ২৯ জন—নতুন শতকরা ২৯/৪৫ × ১০০ = ৬৪.৪৪...% ≈ ৬৪.৪%। খেয়াল: হর (৪৫) বদলেছে, তাই পুরনো ৬০% আর কাজ করবে না।",
     [])

chat("rc-nabila-chat-trip", "en-school-nabila-009", "en", "algebra_fixed_cost",
     [{"role": "user", "content": "A school trip costs 25,000 taka fixed plus 350 taka per student. The cost per student comes to 850 taka. I guessed 60 students but the teacher said it is wrong. How many students are going, and why was my guess wrong? Please show it so I can redo it myself."}],
     "Let n be the number of students. Total cost = 25,000 + 350n, and per student = (25,000 + 350n)/n = 850. So 25,000 + 350n = 850n, giving 25,000 = 500n and n = 50. Check: 25,000 + 350 x 50 = 42,500, and 42,500/50 = 850 - both sides agree. Your guess of 60 fails because 46,000/60 = 766.67, not 850: the fixed 25,000 spreads over more students, so MORE students means LOWER per-student cost. That fixed-cost-spreading step is the one to reuse next time.",
     [])

chat("rc-jahid-chat-time", "bn-school-jahid-010", "bn", "time_decimal_correction",
     [{"role": "user", "content": "স্যার, আপনি বলেছিলেন ৩ ঘণ্টা ৪৫ মিনিট মানে ৩.৪৫ ঘণ্টা। কিন্তু আমি ক্যালকুলেটরে ৪৫ ÷ ৬০ করে দেখলাম ০.৭৫ আসে। তাহলে কি ৩.৭৫ হবে? আমি কোথায় ভুল করলাম?"}],
     "তুমি ঠিক, আমিই ভুল বলেছিলাম—ভালো ধরেছ। ৪৫ মিনিট = ৪৫/৬০ = ৩/৪ ঘণ্টা = ০.৭৫ ঘণ্টা, তাই ৩ ঘণ্টা ৪৫ মিনিট = ৩.৭৫ ঘণ্টা। পরীক্ষা করে দেখো: ৩.৪৫ ঘণ্টা হলে মিনিট হয় ০.৪৫ × ৬০ = ২৭ মিনিট, অর্থাৎ ৩ ঘণ্টা ২৭ মিনিট—যেটা আমাদের ৪৫ মিনিট নয়। নিয়ম: মিনিটকে ঘণ্টায় রূপান্তরে ৬০ দিয়ে ভাগ করতে হয়; সংখ্যা পাশে বসিয়ে দিলে হয় না।",
     [])

chat("rc-puzzle-chat-seq", "en-basic-puzzles-011", "en", "sequence_next_term",
     [{"role": "user", "content": "What comes next in 2, 6, 12, 20, 30 - and why?"}],
     "42. The gaps are 4, 6, 8, 10 - each one grows by 2 - so the next gap is 12 and 30 + 12 = 42. Another view: the terms are 1x2, 2x3, 3x4, 4x5, 5x6, so the next is 6x7 = 42. Both routes agree.",
     [])

chat("rc-secretariat-chat-letter", "bn-office-secretariat-012", "bn", "secretariat_drafting",
     [{"role": "user", "content": "'সবুজ পথ' সড়ক কর্মসূচির মেয়াদ বৃদ্ধির আবেদনপত্র খসড়া করে দিন। স্মারক নং ১৭.০৬৮.০৪২.১০১.২৩.০৩৭.২০২৫/০৮ ফাইলের অনুমোদনের ভিত্তিতে লিখবেন।"},
      {"role": "assistant", "content": "অনুমোদন স্মারকটি পড়েছি (বাজেট ৪৮,৫০,০০০ টাকা; মেয়াদ ৩০-০৬-২০২৫)। একটি প্রয়োজনীয় তথ্য নেই: মেয়াদ কত বৃদ্ধি করতে চান, এবং বর্ধিত মেয়াদের কার্যাদেশ নম্বর কী হবে?"},
      {"role": "user", "content": "৩ মাস বৃদ্ধি। কার্যাদেশ নম্বর হবে ১৭.০৬৮.০৪২.১০১.২৩.০৩৭.২০২৫/১৯। এবার সম্পূর্ণ খসড়া দিন।"}],
     read_member("cases/bn-office-secretariat-012/work_product/extension_letter.txt").rstrip("\n"),
     ["district-memo"])

chat("rc-pollux-chat-hold", "en-research-pollux-013", "en", "definition_conflict_hold",
     [{"role": "user", "content": "Our covenant says the working capital ratio cannot fall below 1.75. The old handbook and the new one define it differently. Which number should I put in the compliance report for 2025-06-30?"},
      {"role": "assistant", "content": "I can compute both readings from the saved balance sheet, but which edition governs a covenant dated 2023-05-04 is not settled by anything in the file. I will show both numbers and hold the governing question with a next step, rather than pick silently."},
      {"role": "user", "content": "Do that - show both numbers and what is missing."}],
     read_member("cases/en-research-pollux-013/work_product/covenant_note.txt").rstrip("\n"),
     ["pollux-handbook-3rd", "pollux-handbook-4th", "eastwind-covenant", "eastwind-bs"])

ROLE = ROLE_PART1 + ROLE_PART2

# ---------- CASES.jsonl ----------
AUTHORITY = {
    "shapla-bank-q2": {"issuer": "কর্ণফুলী বাণিজ্যিক ব্যাংক", "signed": False, "issued_at": "2025-06-30", "effective_at": None, "scope": "Q2 2025 statement export, A/C 502.1130.8845"},
    "shapla-ledger-q2": {"issuer": "শাপলা ট্রেড হাউস হিসাব বিভাগ", "signed": False, "issued_at": "2025-06-30", "effective_at": None, "scope": "internal purchase register copy"},
    "shapla-amendments": {"issuer": "ফারহানা রহমান (বিত্ত পরিচালক)", "signed": True, "issued_at": None, "effective_at": None, "scope": "signed amendment memos A-1..A-4, 2025"},
    "shapla-emails": {"issuer": None, "signed": False, "issued_at": None, "effective_at": None, "scope": "internal email thread copy, 2025-06-26"},
    "novustex-covenant": {"issuer": "Summit Meridian Finance PLC", "signed": True, "issued_at": "2024-09-30", "effective_at": None, "scope": "facility letter extract"},
    "novustex-ebitda": {"issuer": "NovusTex finance (internal)", "signed": False, "issued_at": "2025-07-01", "effective_at": None, "scope": "LTM EBITDA, unaudited"},
    "novustex-debt": {"issuer": "NovusTex finance (internal)", "signed": False, "issued_at": "2025-06-30", "effective_at": None, "scope": "debt schedule + CFO DSCR definition"},
    "novustex-termsheets": {"issuer": None, "signed": False, "issued_at": None, "effective_at": None, "scope": "term sheets A and B + chair preference"},
    "brahmaputra-statement": {"issuer": "ব্রহ্মপুত্র হার্ডওয়্যার (কাল্পনিক)", "signed": False, "issued_at": "2025-05-31", "effective_at": None, "scope": "customer statement May 2025"},
    "brahmaputra-cashbook": {"issuer": "কর্ণফুলী হার্ডওয়্যার এজেন্সি (কাল্পনিক)", "signed": False, "issued_at": "2025-05-31", "effective_at": None, "scope": "internal cash book May 2025"},
    "zuboria-indicator": {"issuer": None, "signed": False, "issued_at": None, "effective_at": None, "scope": "saved indicator table row (fictional)"},
    "clarion-rows": {"issuer": None, "signed": False, "issued_at": None, "effective_at": None, "scope": "saved indicator rows (fictional)"},
    "district-memo": {"issuer": "জেলা পরিষদ শাখা (কাল্পনিক দৃশ্যপট)", "signed": True, "issued_at": "2025-03-12", "effective_at": None, "scope": "approval memo for Shobuj Path programme"},
    "pollux-handbook-3rd": {"issuer": "Pollux Academic Press (fictional)", "signed": False, "issued_at": "2019", "effective_at": None, "scope": "simulated retrieval, 3rd edition entry"},
    "pollux-handbook-4th": {"issuer": "Pollux Academic Press (fictional)", "signed": False, "issued_at": "2024", "effective_at": None, "scope": "simulated retrieval, 4th edition entry"},
    "eastwind-covenant": {"issuer": "Eastwind Imports lender (fictional)", "signed": True, "issued_at": "2023-05-04", "effective_at": None, "scope": "facility covenant"},
    "eastwind-bs": {"issuer": "Eastwind Imports (fictional)", "signed": False, "issued_at": "2025-06-30", "effective_at": None, "scope": "balance sheet extract"},
}

EXALL = {}
for eid, (path, _fn, title) in W.EXHIBITS.items():
    EXALL[eid] = (path, title)
for d in (EX2, EX3, EX4, EX5, EX12, EX13):
    for eid, (path, t) in d.items():
        EXALL[eid] = (path, t)


def exhibit_objs(eids):
    return [{"id": eid, "path": EXALL[eid][0], "title": EXALL[eid][1],
             "kind": "csv" if EXALL[eid][0].endswith(".csv") else "txt",
             "sha256": sha_file(member_path(EXALL[eid][0])), "first_visible_turn": 0, "companion_for": None,
             "authority": AUTHORITY[eid]} for eid in eids]


EX1 = {eid: (path, title) for eid, (path, _fn, title) in W.EXHIBITS.items()}

CASE1 = {
    "id": CID1, "partition": "train", "language": "bn", "domain": "finance", "difficulty": "hard",
    "family": "wide_reconciliation_dossier", "source_family": "karnaphuli_bank_plus_internal_ledger",
    "workplace": {"requester_role": "বিত্ত পরিচালক", "trigger": "কোয়ার্টার-শেষ ব্যাংক-বনাম-খাতা মিলকরণ ও রিলিজ/হোল্ড রেজিস্টার, দুটি পৃথক উৎস ধারা ও সংঘর্ষসহ",
                  "needed_deliverable": "মিলকরণ রেজিস্টার + বোর্ড সামারি; ৫০টি সমসাময়িক কাজ", "next_use": "জুলাই পরিশোধ রান ও অডিট কমিটি"},
    "messages": CHAT1_MESSAGES, "tool_context": TC,
    "exhibits": exhibit_objs(list(EX1)),
    "solution": {"status": "solved", "work_product_path": A.wp_register, "obligations": [o["id"] for o in A.OBLIGATIONS]},
    "checks": {"script_path": None, "expected_path": D1 + "/checks/expected.json", "actual_path": D1 + "/checks/actual.json", "status": "pass"},
    "tool_runs": [],
}

CASES_ROWS = [CASE1]
for meta in CASES.values():
    CASES_ROWS.append({
        "id": meta["id"], "partition": "train", "language": meta["language"], "domain": meta["domain"],
        "difficulty": meta["difficulty"], "family": meta["family"], "source_family": meta["source_family"],
        "workplace": meta["workplace"], "messages": meta["messages"], "tool_context": TC,
        "exhibits": exhibit_objs(meta["exhibits"]),
        "solution": {"status": "solved", "work_product_path": meta["work_product"], "obligations": meta["solution"]["obligations"]},
        "checks": {"script_path": None, "expected_path": "cases/%s/checks/expected.json" % meta["id"],
                   "actual_path": "cases/%s/checks/actual.json" % meta["id"], "status": "pass"},
        "tool_runs": [],
    })

jsonl_write("CASES.jsonl", CASES_ROWS)
jsonl_write("ROLE-CANDIDATES.jsonl", ROLE)
print("cases:", len(CASES_ROWS), "role rows:", len(ROLE))
