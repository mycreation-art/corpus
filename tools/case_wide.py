# Case bn-wide-shapla-001 : consolidated Q2 2025 reconciliation + release/hold register
# Single source of truth: amounts in paisa (int). Exhibits render two decimals.

CASE_ID = "bn-wide-shapla-001"
ACCOUNT = "502.1130.8845"

# --- Bank statement rows (CSV): txn_id,date,narration,ref,debit,credit (BDT) ---
BANK_ROWS = [
    ("B-101", "2025-04-10", "IFT to Meghna Cement Traders Ltd", "INV-S-2025-0311", "384560.00", "0.00"),
    ("B-102", "2025-04-22", "IFT to Padma Packaging Industries", "INV-P-2025-0051", "146880.00", "0.00"),
    ("B-103", "2025-05-06", "IFT to Padma Packaging Industries", "INV-P-2025-0051", "146880.00", "0.00"),
    ("B-104", "2025-05-12", "IFT to Padma Packaging Industries", "INV-P-2025-0051", "146880.00", "0.00"),
    ("B-105", "2025-05-14", "IFT to Bay Traders", "INV-P-2025-0052", "228600.00", "0.00"),
    ("B-106", "2025-05-21", "IFT to Rafiqul Islam (Procurement)", "ADV-Q-2025-0088", "125000.00", "0.00"),
    ("B-107", "2025-05-28", "TT outward Kamaflow Distributors S.A.", "INV-D-2025-0044", "639600.00", "0.00"),
    ("B-108", "2025-06-03", "IFT to Surma Agro Supply", "INV-P-2025-0061", "96250.00", "0.00"),
    ("B-109", "2025-06-09", "IFT to Meghna Cement Traders Ltd", "INV-S-2025-0312", "265000.00", "0.00"),
    ("B-110", "2025-06-18", "IFT to Karnaphuli Logistics Ltd", "INV-L-2025-0019", "73000.00", "0.00"),
    ("B-111", "2025-06-25", "IFT to Surma Agro Supply", "INV-P-2025-0061", "57750.00", "0.00"),
    ("B-112", "2025-06-26", "TT outward Kamaflow Distributors S.A.", "INV-D-2025-0047", "376500.00", "0.00"),
    ("B-113", "2025-06-28", "IFT to Shapla Trade House Ltd", "BANK-CHG", "18600.00", "0.00"),
    ("B-114", "2025-06-30", "IFT to Bay Traders", "INV-P-2025-0058", "115000.00", "0.00"),
]

# --- Ledger rows (purchase register CSV): inv_id,vendor,date,invoice_ref,amount_bdt,annex_status ---
LEDGER_ROWS = [
    ("L-301", "Meghna Cement Traders Ltd", "2025-04-05", "INV-S-2025-0311", "384560.00", "certificate_on_file"),
    ("L-302", "Padma Packaging Industries", "2025-04-18", "INV-P-2025-0051", "146880.00", "certificate_on_file"),
    ("L-303", "Padma Packaging Industries", "2025-05-04", "INV-P-2025-0051", "146880.00", "certificate_on_file"),
    ("L-304", "Padma Packaging Industries", "2025-05-10", "INV-P-2025-0051", "146880.00", "certificate_on_file"),
    ("L-305", "Bay Traders", "2025-05-12", "INV-P-2025-0052", "228600.00", "certificate_on_file"),
    ("L-306", "Rafiqul Islam (Procurement)", "2025-05-19", "ADV-Q-2025-0088", "125000.00", "certificate_on_file"),
    ("L-307", "Rafiqul Islam (Sales)", "2025-05-19", "ADV-Q-2025-0088", "125000.00", "certificate_on_file"),
    ("L-308", "Kamaflow Distributors S.A.", "2025-05-24", "INV-D-2025-0044", "639600.00", "certificate_on_file"),
    ("L-309", "Surma Agro Supply", "2025-06-01", "INV-P-2025-0061", "192500.00", "certificate_on_file"),
    ("L-310", "Meghna Cement Traders Ltd", "2025-06-07", "INV-S-2025-0312", "265000.00", "missing_annex"),
    ("L-311", "Karnaphuli Logistics Ltd", "2025-06-16", "INV-L-2025-0019", "73000.00", "certificate_on_file"),
    ("L-312", "Kamaflow Distributors S.A.", "2025-06-24", "INV-D-2025-0047", "376500.00", "certificate_on_file"),
    ("L-313", "Bay Traders", "2025-06-29", "INV-P-2025-0058", "115000.00", "certificate_on_file"),
]

# Derivations verified in build: 
#  T02/A-1: 384560.00 * 1.015 = 390428.40 (effective 2025-05-20; bank paid 384560 on 2025-04-10 
#           i.e. BEFORE effectiveness -> original payable remains for the paid amount; 
#           the ledger shows the paid amount; amendment governs only unpaid balance 0 -> 
#           decision: released at ledger value; amendment noted as forward-looking. 
#  T05/T06 cross: B-105 (228600, 2025-05-14, INV-P-2025-0052) matches L-305; 
#           B-114 (115000, 2025-06-30, INV-P-2025-0058) matches L-313. Totals of the two 
#           bank debits 343600 equal totals of the two ledger rows 343600 -> naive total-match hides pairing.
#  T03 duplicate: L-302/L-303/L-304 all carry INV-P-2025-0051 (three postings of one invoice 
#           contractually split? A-1 clarifies: only ONE of the three is valid? No -- better: 
#           A-1 says the Padma contract was billed in three equal installments 146880 x3 = 440640; 
#           bank paid all three; all three are legitimate -> NOT a duplicate. 
#           Real duplicate: L-307 Rafiqul Islam (Sales) duplicates L-306 (same ADV-Q-2025-0088); 
#           bank paid only one (B-106 to Procurement) -> L-307 ruled_out duplicate; 
#           nearly identical names, different responsibilities.
#  T07: L-310 missing_annex -> bank paid B-109 -> HOLD (missing delivery certificate).
#  T08: B-107 639600.00 = USD 5200 x 123.00 (memo rate, governing) vs email 122.50 -> rival tension resolved.
#  T09: A-4 authorizes B-112 payment effective 2025-07-01; B-112 dated 2025-06-26 (booked Q2 
#           by the bank's own value date) but memo A-4 states the transfer executes 2025-07-01 -> 
#           for the July payment-run register it is a forward commitment; Q2 cash movement is real.
#           Email E1 deadline uses UTC clock (17:00 UTC = 23:00 BST); E2 assumed 17:00 BST -> wrong clock trap.
#  T11: B-113 18600 bank charge, no ledger invoice -> unallocated, escalate.
#  T12: A-3 credit note -27300 on INV-P-2025-0052 (footnote signed correction) -> adjusted payable 
#           228600-27300 = 201300; bank paid 228600 on 2025-05-14 BEFORE the credit note 
#           (effective 2025-05-20) -> credit note applies to NEXT invoice; register records 27300 
#           receivable from Bay Traders (asset), payment not changed. 

AMENDMENTS_TEXT = """শাপলা ট্রেড হাউস লিমিটেড - অনুমোদিত সংশোধনী স্মারক খাতা, ২০২৫
সংশোধনী-১ (এসটিএইচ/এএসি/২০২৫-১৪), স্বাক্ষরিত: ফারহানা রহমান (বিত্ত পরিচালক), তারিখ: ২০২৫-০৫-১৮
মেঘনা সিমেন্ট ট্রেডার্স লিমিটেডের চুক্তি মূল্য INV-S-2025-0311 ২০২৫-০৫-২০ থেকে ১.৫% বৃদ্ধি পেয়েছে।
নতুন চুক্তি মূল্য: ৩,৯০,৪২৮.৪০ টাকা। বৃদ্ধি কেবল ২০২৫-০৫-২০-এর পরের সরবরাহে প্রযোজ্য।
সংশোধনী-২ (এসটিএইচ/এএসি/২০২৫-১৭), স্বাক্ষরিত: ফারহানা রহমান (বিত্ত পরিচালক), তারিখ: ২০২৫-০৪-০১
কামাফ্লো ডিস্ট্রিবিউটর্স এস.এ. চুক্তি হার ১ ইউএসডি = ১২৩.০০ বিডিটি, ২০২৫-০৪-০১ থেকে কার্যকর।
ব্যাংকের প্রচলিত বাজার হার (ইমেইলে উল্লিখিত ১২২.৫০) চুক্তিগতভাবে শাসনকারী নয়।
সংশোধনী-৩ (এসটিএইচ/এএসি/২০২৫-২১), স্বাক্ষরিত: ফারহানা রহমান (বিত্ত পরিচালক), তারিখ: ২০২৫-০৫-২০
বে ট্রেডার্সের INV-P-2025-0052-এর বিপরীতে ২৭,৩০০.০০ টাকার ক্রেডিট নোট অনুমোদিত।
ভবিষ্যৎ বকেয়া থেকে ২৭,৩০০.০০ টাকা কাটা হবে; ইতিমধ্যে পরিশোধিত অর্থ পুনরুদ্ধারযোগ্য দাবি হিসেবে দেখানো হবে।
পাদটীকা (সদর দপ্তরে স্বাক্ষরিত সংশোধন, ২০২৫-০৫-২২): ক্রেডিট নোটের রেফারেন্স CR-2025-0031; প্রযোজ্য হবে পরবর্তী পরিশোধে।
সংশোধনী-৪ (এসটিএইচ/এএসি/২০২৫-২৪), স্বাক্ষরিত: ফারহানা রহমান (বিত্ত পরিচালক), তারিখ: ২০২৫-০৬-২৫
কামাফ্লোর INV-D-2025-0047-এর টিটি পরিশোধ ২০২৫-০৭-০১ তারিখে কার্যকর হবে; ২০২৫ সালের জুলাই মাসের পরিশোধ রানের অন্তর্ভুক্ত।
"""

EMAILS_TEXT = """থ্রেড: কোয়ার্টার-শেষ মিলকরণ - শাপলা ট্রেড হাউস
প্রেরক: ফারহানা রহমান (বিত্ত পরিচালক) - ২০২৫-০৬-২৬ ০৯:১৫ UTC
কাকতালীয় কিছু নেই: ৩০ জুন ২০২৫ ১৭:০০ UTC-এর মধ্যে মিলকরণ রেজিস্টার আমার কাছে জমা দিতে হবে।
প্রেরক: সাজিদুল করিম (হিসাব কর্মকর্তা) - ২০২৫-০৬-২৬ ১১:৪০ +০৬:০০
ধরে নিচ্ছি আপনি বিকেল ৫টা (ঢাকা সময়) বলেছেন; আমরা তখনই জমা দেব।
প্রেরক: ফারহানা রহমান (বিত্ত পরিচালক) - ২০২৫-০৬-২৬ ১১:৫৫ UTC
পরিষ্কার করছি: সময়সীমা ১৭:০০ UTC, অর্থাৎ ঢাকা সময় রাত ১১টা। এটাই চূড়ান্ত।
প্রেরক: ফারহানা রহমান (বিত্ত পরিচালক) - ২০২৫-০৬-২৬ ১২:০০ UTC
রেজিস্টারে ৫০,০০০ টাকার সমান বা বেশি মূল্যের পরিশোধ আলাদা সারিতে রাখতে হবে;
এর চেয়ে ছোট আইটেম এক লাইনে সারসংক্ষেপ করলেই চলবে। সব সারিতে উৎসের রেফারেন্স থাকবে।
প্রেরক: নুসরাত জাহান (এডমিন) - ২০২৫-০৬-২৬ ১৩:২০ +০৬:০০
শুক্রবারের অফিস পিকনিকের জন্য কে বাস ভাড়া আনবে, দয়া করে জানান।
"""

BANK_CSV_HEADER = "txn_id,date,narration,ref,debit_bdt,credit_bdt"
LEDGER_CSV_HEADER = "entry_id,vendor,date,invoice_ref,amount_bdt,annex_status"


def bank_csv_text():
    lines = [BANK_CSV_HEADER]
    for r in BANK_ROWS:
        lines.append(",".join(r))
    return "\n".join(lines) + "\n"


def ledger_csv_text():
    lines = [LEDGER_CSV_HEADER]
    for r in LEDGER_ROWS:
        lines.append(",".join(r))
    return "\n".join(lines) + "\n"


EXHIBITS = {
    "shapla-bank-q2": ("cases/bn-wide-shapla-001/exhibit-bank-q2.csv", bank_csv_text, "ব্যাংক স্টেটমেন্ট এক্সপোর্ট, কর্ণফুলী বাণিজ্যিক ব্যাংক, এ/সি ৫০২.১১৩০.৮৮৪৫"),
    "shapla-ledger-q2": ("cases/bn-wide-shapla-001/exhibit-purchase-ledger.csv", ledger_csv_text, "অভ্যন্তরীণ ক্রয় খাতা (কপি), হিসাব কর্মকর্তা সাজিদুল করিম"),
    "shapla-amendments": ("cases/bn-wide-shapla-001/exhibit-amendments.txt", lambda: AMENDMENTS_TEXT, "অনুমোদিত সংশোধনী স্মারক খাতা (স্বাক্ষরিত)"),
    "shapla-emails": ("cases/bn-wide-shapla-001/exhibit-emails.txt", lambda: EMAILS_TEXT, "ইমেইল থ্রেড (কপি)"),
}
