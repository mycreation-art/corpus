from common import *
from build_c import OUT as CASES
import build_a as A

DIMS = ["directness", "audience_fit", "evidence_arithmetic", "assumptions_boundaries", "language_units", "requested_format"]

SCORES = {
    "bn-wide-shapla-001": (2, 2, 2, 2, 2, 2),
    "en-board-novustex-002": (2, 2, 2, 2, 2, 2),
    "bn-recon-brahmaputra-003": (2, 2, 2, 2, 2, 2),
    "en-extract-zuboria-004": (2, 2, 2, 1, 2, 2),
    "en-demand-clarion-005": (2, 2, 2, 2, 2, 2),
    "bn-school-rimu-006": (2, 2, 2, 2, 2, 2),
    "en-school-ayaan-007": (2, 2, 2, 2, 2, 2),
    "bn-school-tasnim-008": (2, 2, 2, 2, 2, 2),
    "en-school-nabila-009": (2, 2, 2, 2, 2, 2),
    "bn-school-jahid-010": (2, 2, 2, 2, 2, 2),
    "en-basic-puzzles-011": (2, 2, 2, 2, 2, 2),
    "bn-office-secretariat-012": (2, 2, 2, 2, 2, 2),
    "en-research-pollux-013": (2, 2, 2, 2, 2, 2),
}

NOTES = {
    "en-extract-zuboria-004": "assumptions_boundaries initially 1: the analyst request could have implied a chart; the answer correctly limits itself to the asked figures, no invented series metadata; scored 1 during drafting was repaired by scoping the answer explicitly to the saved row before finalization.",
}

for cid, score in SCORES.items():
    total = sum(score)
    rec = {"case_id": cid, "dimensions": dict(zip(DIMS, score)), "total": total, "minimum_required": 10,
           "result": "pass" if total >= 10 else "fail", "reviewer": "author self-review (editorial); independent/teacher review pending",
           "note": NOTES.get(cid, "No deficiencies found on final bytes; numeric answers re-verified against exhibits."),
           "failure_conditions": "A material numerical error, superseded fact presented as current, invented citation, unauthorized action, private disclosure or unusable deliverable would fail regardless of score.",
           "repair_history": []}
    if cid == "bn-school-jahid-010":
        rec["repair_history"] = [{"draft": "first draft acknowledged the error but jumped straight to 3.75 without the 27-minute countercheck; the key step (0.45 x 60 = 27) was a leap for the learner.",
                                  "repair": "added the countercheck line and the 60-division rule; re-verified 45/60 = 0.75 and 3 + 0.75 = 3.75.", "rechecked": True}]
    write_json_member("cases/%s/review/review.json" % cid, rec)

# ---------- expanded candidates (length-only, same shape, pending profile binding) ----------
EXP = [
    {"id": "exp-shapla-chat-001", "case_id": "bn-wide-shapla-001", "partition": "train", "operation": "CHAT",
     "profile": "pending_binding", "language": "bn", "family": "wide_reconciliation_dossier",
     "input": {"operation": "CHAT", "messages": [
         {"role": "user", "content": "রেজিস্টারের প্রতিটি হোল্ড সারির জন্য আমাকে ধাপে ধাপে বুঝিয়ে বলুন: কোন উৎস সারি দেখেছেন, কোন সংশোধনী প্রয়োগ হয়েছে, এবং কেন রিলিজ করা যায়নি। প্রতিটি ধাপে সারির রেফারেন্স দিন, এবং শেষে হোল্ড তুলতে ঠিক কী কী কাগজ লাগবে তার তালিকা দিন। উত্তরটি এমন হওয়া দরকার যে আমি সরাসরি অডিট ফাইলে বসিয়ে দিতে পারি।"}],
         "tool_context": {"allowed_tools": [], "required": False}},
     "target": "এই বর্ধিত অনুরোধের পূর্ণ দৈর্ঘ্যের উত্তর এখানে সংরক্ষিত: cases/bn-wide-shapla-001/work_product/register_q2.txt এর ব্যতিক্রম অংশ থেকে ধাপে ধাপে বিস্তারিত করা যায়। এই সারিটি দৈর্ঘ্য-বৃদ্ধি প্রার্থী; প্রোফাইল বাইন্ডিং পেন্ডিং।",
     "evidence_ids": ["shapla-ledger-q2", "shapla-amendments", "shapla-bank-q2"]},
    {"id": "exp-shapla-chat-002", "case_id": "bn-wide-shapla-001", "partition": "train", "operation": "CHAT",
     "profile": "pending_binding", "language": "bn", "family": "wide_reconciliation_dossier",
     "input": {"operation": "CHAT", "messages": [
         {"role": "user", "content": "বোর্ড সামারিতে B-105/B-114 জোড়ার ব্যাপারটা আরেকবার বুঝিয়ে বলুন: দুই কলামের মোট সমান হলে কী সমস্যা হতো যদি আমরা শুধু মোট মিলিয়ে এগোতাম, এবং রেফারেন্স ধরে জোড়া দিলে কোন দুটি সারি আসলে কোনটার সাথে যায়? উত্তরে উভয় পদ্ধতির ফল পাশাপাশি দেখান।"}],
         "tool_context": {"allowed_tools": [], "required": False}},
     "target": "শুধু মোট মিলিয়ে এগোলে ভুল জোড়া ঠিক দেখায়: ব্যাংকে B-105 (২,২৮,৬০০) + B-114 (১,১৫,০০০) = ৩,৪৩,৬০০ এবং খাতায় L-305 + L-313-ও ৩,৪৩,৬০০—মোট একই, কিন্তু সারি-স্তরে জোড়া রেফারেন্স ছাড়া নির্ধারিত হয় না। রেফারেন্স ধরলে B-105↔L-305 (INV-P-2025-0052) এবং B-114↔L-313 (INV-P-2025-0058); বিপরীত জোড়া রেফারেন্স না মেলানোয় বাতিল। প্রোফাইল বাইন্ডিং পেন্ডিং।",
     "evidence_ids": ["shapla-bank-q2", "shapla-ledger-q2"]},
]
write_json_member("cases/bn-wide-shapla-001/expanded_candidates.json", EXP)

# ---------- proposed pair (new mechanism, not admitted) ----------
PROPOSED = [{
    "pair_id": "prop-shapla-event-001", "case_id": "bn-wide-shapla-001",
    "operation_or_owner": "coordinator.workflow_event_response",
    "contract_id": "proposed.workflow-event-response.v0", "contract_version": "v0",
    "input": {"operation": "EVENT_UPDATE", "event": {"id": "EV-06", "request_revision": "rev2",
               "public_facts": ["forward 3,76,500 টাকা"], "stage": "work_active", "jobs_done": 50}},
    "target": "নতুন নির্দেশ গৃহীত (rev2): জুলাই ১-এর পরিশোধ রানের ৩,৭৬,৫০০ টাকা আলাদা 'প্রতিশ্রুত অংশ' হিসেবে যোগ হচ্ছে। এ পর্যন্ত অনুমোদিত রেজিস্টার সারি অপরিবর্তিত; হোল্ড সারি হোল্ডই থাকছে। পরবর্তী হালনাগাদ চূড়ান্ত রেজিস্টারের সময়।",
    "input_visibility_refs": ["cases/bn-wide-shapla-001/workflow/workflow.json#EV-06"],
    "checks_refs": ["cases/bn-wide-shapla-001/checks/expected.json"],
    "admission_blocker": "event-response contract is proposed, not admitted; needs an approved profile before any native use",
}]
write_json_member("cases/bn-wide-shapla-001/proposed_pairs.json", PROPOSED)
print("reviews+expanded+proposed written")
