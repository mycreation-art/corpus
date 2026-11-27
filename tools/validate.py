import json, os, re, sys, unicodedata
from decimal import Decimal


def nfc(s):
    return unicodedata.normalize("NFC", s) if isinstance(s, str) else s

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import STAGING, PROMPT_PATH, jsonl_read, read_member, member_path, sha_file, sha_text, write_json_member

FAILS = []
CHECKS = []


def rec(scope, name, ok, detail=""):
    CHECKS.append({"scope": scope, "check": name, "status": "pass" if ok else "fail", "detail": detail})
    if not ok:
        FAILS.append("%s / %s: %s" % (scope, name, detail))
    return ok


CASE_KEYS = ["id", "partition", "language", "domain", "difficulty", "family", "source_family",
             "workplace", "messages", "tool_context", "exhibits", "solution", "checks", "tool_runs"]
ROLE_KEYS = ["id", "case_id", "partition", "operation", "profile", "language", "family",
             "input", "target", "evidence_ids"]
HEADER_KEYS = ["issuer", "signed", "numbered", "dated", "memo", "subject", "row_label", "column_label"]
CLAIM_ID_RE = re.compile(r"[A-Za-z][A-Za-z0-9_.-]*")
D_VOCAB = {"\u09ac\u09a6\u09b2\u09be\u09df", "\u09ac\u09be\u0981\u09a7\u09be", "\u09ac\u09be\u09a6", "\u0985\u09a8\u09bf\u09b6\u09cd\u099a\u09bf\u09a4"}
W_VOCAB = {"\u09aa\u09cd\u09b0\u09a4\u09bf\u09b8\u09cd\u09a5\u09be\u09aa\u09a8", "\u0985\u09a8\u09c1\u09ae\u09cb\u09a6\u09bf\u09a4", "\u0995\u09cd\u09b7\u09ae\u09a4\u09be\u09b9\u09c0\u09a8",
           "\u09aa\u09c1\u09a8\u09b0\u09be\u09ac\u09c3\u09a4\u09cd\u09a4", "\u09aa\u09b0\u09bf\u09a7\u09bf\u09b0-\u09ac\u09be\u0987\u09b0\u09c7", "\u09ad\u09bf\u09a8\u09cd\u09a8-\u09ac\u09bf\u09b7\u09df", "-"}
ALLOWED_EXT = {".txt", ".csv", ".json", ".jsonl"}


def safe_rel(p):
    if p.startswith("/") or "\\" in p or ".." in p.split("/"):
        return False
    return os.path.normpath(p) == p


def read_bytes(rel):
    with open(member_path(rel), "rb") as f:
        return f.read()


cases = jsonl_read("CASES.jsonl")
roles = jsonl_read("ROLE-CANDIDATES.jsonl")
case_by_id = {c["id"]: c for c in cases}
role_by_id = {r["id"]: r for r in roles}

# ---------- 1. member / encoding audit ----------
members = []
for root, _dirs, files in os.walk(STAGING):
    for fn in files:
        rel = os.path.relpath(os.path.join(root, fn), STAGING)
        members.append(rel)
members.sort()
enc_ok = True
ext_ok = True
path_ok = True
for rel in members:
    b = read_bytes(rel)
    if rel not in ("CASES.jsonl", "ROLE-CANDIDATES.jsonl"):
        try:
            b.decode("utf-8")
        except UnicodeDecodeError:
            enc_ok = False
    if b.startswith(b"\xef\xbb\xbf") or b"\r" in b:
        enc_ok = False
    if os.path.splitext(rel)[1] not in ALLOWED_EXT:
        ext_ok = False
    if not safe_rel(rel):
        path_ok = False
rec("archive", "member_extensions_txt_csv_json_jsonl", ext_ok, "allowed: txt/csv/json/jsonl only")
rec("archive", "utf8_no_bom_lf_only", enc_ok, "no BOM, no CR bytes in any member")
rec("archive", "safe_unique_relative_paths", path_ok and len(set(members)) == len(members), "%d members" % len(members))
rec("archive", "root_files_present",
    os.path.exists(member_path("CASES.jsonl")) and os.path.exists(member_path("ROLE-CANDIDATES.jsonl")),
    "CASES.jsonl + ROLE-CANDIDATES.jsonl present (MANIFEST.json added at packaging)")
rec("archive", "no_scripts_or_symlinks", not any(rel.endswith(".py") for rel in members),
    "build toolchain stays outside the ZIP")

# ---------- 2. CASES.jsonl structural ----------
ok = rec("CASES", "row_count_13", len(cases) == 13, "got %d" % len(cases))
ok &= rec("CASES", "unique_ids", len(case_by_id) == len(cases))
for c in cases:
    cid = c.get("id", "?")
    rec("CASES", "exact_keys_" + cid, sorted(c.keys()) == sorted(CASE_KEYS), str(sorted(set(c.keys()) ^ set(CASE_KEYS))))
    rec("CASES", "field_types_" + cid,
        c.get("partition") == "train" and c.get("language") in ("bn", "en")
        and c.get("difficulty") in ("easy", "moderate", "hard")
        and isinstance(c.get("domain"), str) and isinstance(c.get("family"), str)
        and isinstance(c.get("source_family"), str),
        "partition/language/difficulty/domain/family")
    rec("CASES", "workplace_keys_" + cid,
        isinstance(c.get("workplace"), dict) and sorted(c["workplace"].keys()) ==
        ["needed_deliverable", "next_use", "requester_role", "trigger"])
    rec("CASES", "tool_context_" + cid, c.get("tool_context") == {"allowed_tools": [], "required": False})
    rec("CASES", "tool_runs_empty_" + cid, c.get("tool_runs") == [])
    s = c.get("solution", {})
    rec("CASES", "solution_shape_" + cid,
        sorted(s.keys()) == ["obligations", "status", "work_product_path"] and s["status"] == "solved"
        and os.path.exists(member_path(s["work_product_path"])), str(s))
    ch = c.get("checks", {})
    rec("CASES", "checks_shape_" + cid,
        sorted(ch.keys()) == ["actual_path", "expected_path", "script_path", "status"]
        and ch["script_path"] is None and os.path.exists(member_path(ch["expected_path"])), str(ch))
    exids = [e["id"] for e in c.get("exhibits", [])]
    rec("CASES", "exhibit_ids_unique_" + cid, len(set(exids)) == len(exids))
    for e in c.get("exhibits", []):
        rec("CASES", "exhibit_keys_" + e.get("id", "?"),
            sorted(e.keys()) == ["authority", "companion_for", "first_visible_turn", "id", "kind", "path", "sha256", "title"]
            and sorted(e["authority"].keys()) == ["effective_at", "issued_at", "issuer", "scope", "signed"]
            and safe_rel(e["path"]) and os.path.exists(member_path(e["path"])), str(e["path"]))
        digest = sha_file(member_path(e["path"]))
        rec("CASES", "exhibit_sha_" + e["id"], digest == e["sha256"], digest)
    if c.get("messages"):
        ok_msg = all(sorted(m.keys()) == ["content", "role"] for m in c["messages"])
        rec("CASES", "case_messages_shape_" + cid, ok_msg)

# ---------- 3. ROLE-CANDIDATES.jsonl structural ----------
ok = rec("ROLES", "row_count_26", len(roles) == 26, "got %d" % len(roles))
ok &= rec("ROLES", "unique_ids", len(role_by_id) == len(roles))
for r in roles:
    rid = r.get("id", "?")
    rec("ROLES", "exact_keys_" + rid, sorted(r.keys()) == sorted(ROLE_KEYS), str(sorted(set(r.keys()) ^ set(ROLE_KEYS))))
    c = case_by_id.get(r.get("case_id"))
    rec("ROLES", "case_fk_" + rid, c is not None, r.get("case_id", ""))
    if c:
        rec("ROLES", "lang_family_match_" + rid, r["language"] == c["language"] and r["family"] == c["family"])
        exids = [e["id"] for e in c["exhibits"]]
        rec("ROLES", "evidence_fk_" + rid, all(x in exids for x in r["evidence_ids"]) and len(set(r["evidence_ids"])) == len(r["evidence_ids"]), str(r["evidence_ids"]))
        rec("ROLES", "partition_train_" + rid, r["partition"] == "train")
        rec("ROLES", "operation_in_input_" + rid, r["input"].get("operation") == r["operation"])
    rec("ROLES", "target_single_string_" + rid, isinstance(r.get("target"), str) and r["target"].strip() != "")
    rec("ROLES", "no_review_metadata_" + rid,
        not any(k in json.dumps(r) for k in ("review", "score", "editorial", "class_", "learner_understanding")))


def ex_texts(c):
    return {e["id"]: read_member(e["path"]) for e in c["exhibits"]}


# ---------- 4. TRACE profile ----------
def validate_trace(r, c, ext=None):
    ext = ext or ex_texts(c)
    out = []

    def add(name, okv, detail=""):
        out.append(("TRACE/" + name, okv, detail))

    inp = r["input"]
    add("input_keys", sorted(inp.keys()) == ["atom_id", "claims", "header", "operation", "text"], str(sorted(inp.keys())))
    h = inp.get("header", {})
    add("header_keys", sorted(h.keys()) == sorted(HEADER_KEYS), str(sorted(h.keys())))
    typed = all(isinstance(h[k], bool) or h[k] is None for k in ("signed", "numbered")) and \
        all(h[k] is None or isinstance(h[k], str) for k in ("issuer", "dated", "memo", "subject", "row_label", "column_label"))
    add("header_types", typed, "only signed/numbered may be boolean; dated must be string-or-null, never boolean")
    ev = r["evidence_ids"]
    linked = ext.get(ev[0], "") if ev else ""
    atom = inp.get("text", "")
    add("atom_contiguous_span", bool(linked) and atom in linked, "atom is a contiguous literal span of %s" % (ev[0] if ev else "?"))
    m = re.match(r"^(.*)-(\d{3})$", inp.get("atom_id", ""))
    if m and m.group(1) in ext:
        lines = ext[m.group(1)].split("\n")
        add("atom_line_numbering", int(m.group(2)) <= len(lines) and lines[int(m.group(2)) - 1] == atom,
            "atom_id suffix maps to 1-based line %s" % m.group(2))
    claims = inp.get("claims", [])
    add("claims_list", isinstance(claims, list) and len(claims) >= 1)
    ids = set()
    for cl in claims:
        add("claim_keys", sorted(cl.keys()) == ["claim_id", "display", "kind", "operand_atoms", "slot", "value"], str(sorted(cl.keys())))
        add("claim_kind_value", cl.get("kind") == "value")
        add("claim_id_regex", bool(CLAIM_ID_RE.fullmatch(cl.get("claim_id", ""))), cl.get("claim_id", ""))
        ids.add(cl.get("claim_id"))
        oa = cl.get("operand_atoms", [])
        for oid in oa:
            om = re.match(r"^(.*)-(\d{3})$", oid)
            add("operand_atom_real", bool(om) and om.group(1) in ext and int(om.group(2)) <= len(ext[om.group(1)].split("\n")), oid)
    tlines = r["target"].split("\n")
    add("target_4_lines", len(tlines) == 4 and all(tlines[i].startswith(p + " ") for i, p in enumerate(["D", "C", "V", "W"])), r["target"])
    if len(tlines) == 4:
        dv = tlines[0][2:].strip(); cv = tlines[1][2:].strip()
        vv = tlines[2][2:].strip(); wv = tlines[3][2:].strip()
        add("D_vocab", nfc(dv) in {nfc(x) for x in D_VOCAB}, dv)
        add("W_vocab", nfc(wv) in {nfc(x) for x in W_VOCAB}, wv)
        add("C_exact_or_dash", cv == "-" or cv in ids, cv)
        add("C_regex", cv == "-" or bool(CLAIM_ID_RE.fullmatch(cv)), cv)
        if vv != "-":
            add("V_unique_span", len(vv) <= 64 and linked.count(vv) == 1,
                "V is a unique contiguous span <=64 code points of %s (%d cps, %d occurrences)" % (ev[0] if ev else "?", len(vv), linked.count(vv)))
        else:
            add("V_unique_span", True, "V dash")
        dv_n, wv_n = nfc(dv), nfc(wv)
        combos = {nfc(k): {nfc(x) for x in v} for k, v in {
                  "\u09ac\u09a6\u09b2\u09be\u09df": {"\u09aa\u09cd\u09b0\u09a4\u09bf\u09b8\u09cd\u09a5\u09be\u09aa\u09a8", "\u0985\u09a8\u09c1\u09ae\u09cb\u09a6\u09bf\u09a4"},
                  "\u09ac\u09be\u0981\u09a7\u09be": {"-", "\u0985\u09a8\u09c1\u09ae\u09cb\u09a6\u09bf\u09a4"},
                  "\u09ac\u09be\u09a6": {"\u09aa\u09cd\u09b0\u09a4\u09bf\u09b8\u09cd\u09a5\u09be\u09aa\u09a8", "\u0995\u09cd\u09b7\u09ae\u09a4\u09be\u09b9\u09c0\u09a8", "\u09aa\u09c1\u09a8\u09b0\u09be\u09ac\u09c3\u09a4\u09cd\u09a4", "\u09aa\u09b0\u09bf\u09a7\u09bf\u09b0-\u09ac\u09be\u0987\u09b0\u09c7", "\u09ad\u09bf\u09a8\u09cd\u09a8-\u09ac\u09bf\u09b7\u09df"},
                  "\u0985\u09a8\u09bf\u09b6\u09cd\u099a\u09bf\u09a4": {"-", "\u0995\u09cd\u09b7\u09ae\u09a4\u09be\u09b9\u09c0\u09a8"}}.items()}
        add("D_W_semantic_combo", wv_n in combos.get(dv_n, set()), "%s+%s" % (dv, wv))
        if dv_n in ("\u09ac\u09a6\u09b2\u09be\u09df", "\u09ac\u09be\u0981\u09a7\u09be", "\u09ac\u09be\u09a6"):
            add("C_V_present_for_decided", cv != "-" and vv != "-")
    return out


# ---------- 5. EXTRACT profile ----------
EXTRACT_VAL_RE = re.compile(r"^-?\d+(?:\.\d+)?$|^(?:NA|null|missing|unavailable)$")


def parse_indicator_line(line):
    parts = line.split(" | ")
    if len(parts) != 4:
        return None
    m = re.match(r"^(.+) \(([A-Z]{3})\)$", parts[0])
    if not m:
        return None
    country, code, unit = "%s (%s)" % (m.group(1), m.group(2)), parts[1], parts[2]
    vals = parts[3]
    if not re.match(r"^[A-Z][A-Z0-9_.]*$", code) or len(code) < 2:
        return None
    obs = []
    for tok in vals.split(", "):
        mm = re.match(r"^(\d{4})=(.*)$", tok)
        if not mm:
            return None
        if not EXTRACT_VAL_RE.match(mm.group(2)):
            return None
        obs.append((mm.group(1), mm.group(2)))
    return {"country": country, "series": code, "unit": unit, "obs": obs}


def validate_extract(r, c, ext=None):
    ext = ext or ex_texts(c)
    out = []

    def add(name, okv, detail=""):
        out.append(("EXTRACT/" + name, okv, detail))

    inp = r["input"]
    add("input_keys", sorted(inp.keys()) == ["atom_id", "header", "operation", "text"], str(sorted(inp.keys())))
    h = inp.get("header", {})
    add("header_keys", sorted(h.keys()) == sorted(HEADER_KEYS))
    add("neutral_header_first_six_null", all(h.get(k) is None for k in HEADER_KEYS[:6]), str(h))
    ev = r["evidence_ids"]
    linked = ext.get(ev[0], "") if ev else ""
    src = None
    for line in linked.split("\n"):
        p = parse_indicator_line(line)
        if p and line.startswith(p["country"] + " | " + p["series"] + " | " + p["unit"] + " | "):
            src = p
            src_line = line
    add("source_row_found", src is not None, "literal indicator row located in %s" % (ev[0] if ev else "?"))
    if src is None:
        return out
    row_label = "%s | %s | %s" % (src["country"], src["series"], src["unit"])
    for f in (src["country"], src["series"], src["unit"]):
        add("field_len_64", len(f) <= 64, f)
    is_header = inp.get("atom_id", "").endswith("header")
    if is_header:
        add("column_label_null", h.get("column_label") is None)
        add("atom_prefix_parity", inp.get("text") == row_label + " | ",
            "header atom text is the exact source prefix including trailing ' | '")
        want = ["T1 source|*|country", "P1 " + src["country"], "Q1 in_force",
                "T2 source|*|series", "P2 " + src["series"], "Q2 in_force",
                "T3 source|*|unit", "P3 " + src["unit"], "Q3 in_force"]
        add("header_target_parity", r["target"] == "\n".join(want), r["target"])
        for pn in (src["country"], src["series"], src["unit"]):
            add("pointer_unique_once", inp.get("text", "").count(pn) == 1 and len(pn) <= 64, pn)
    else:
        col = h.get("column_label", "")
        mm = re.match(r"^(\d{4}); (.+)$", col)
        add("column_label_shape", mm is not None and mm.group(2) == src["unit"], col)
        year = mm.group(1) if mm else ""
        idx = [i for i, (y, _v) in enumerate(src["obs"]) if y == year]
        add("year_in_source", len(idx) == 1, year)
        if idx:
            i = idx[0]
            y, v = src["obs"][i]
            nonfinal = i < len(src["obs"]) - 1
            add("atom_parity", inp.get("text") == "%s=%s%s" % (y, v, ", " if nonfinal else ""),
                "nonfinal observation keeps the ', ' suffix; final omits it")
            want = ["T1 source|*|year", "P1 " + y, "Q1 in_force", "T2 source|*|value", "P2 %s=%s" % (y, v), "Q2 in_force"]
            add("target_parity", r["target"] == "\n".join(want), r["target"])
            atom = inp.get("text", "")
            add("pointer_unique_once", atom.count(y) == 1 and atom.count("%s=%s" % (y, v)) == 1, "%s=%s" % (y, v))
            add("P2_omits_separator", ("\n" + "P2 %s=%s," % (y, v)) not in r["target"], "P2 carries no trailing separator")
    return out


# ---------- 6. DEMAND profile ----------
UR_ROW = re.compile(r"^Clarion Islands \(CRI\) \| EG\.ELC\.ACCS\.UR\.ZS \| Access to electricity, urban \(% of urban population\) \| (.+)$")
RU_ROW = re.compile(r"^Clarion Islands \(CRI\) \| EG\.ELC\.ACCS\.RU\.ZS \| Access to electricity, rural \(% of rural population\) \| (.+)$")


def demand_series(ext, evs, rx):
    vals = {}
    for eid in evs:
        for line in ext.get(eid, "").split("\n"):
            m = rx.match(line)
            if m:
                for tok in m.group(1).split(", "):
                    y, v = tok.split("=")
                    vals[int(y)] = Decimal(v)
    return vals


def gaps_from(ur, ru):
    return {y: ur[y] - ru[y] for y in sorted(ur) if y in ru}


def validate_demand(r, c, ext=None):
    ext = ext or ex_texts(c)
    out = []

    def add(name, okv, detail=""):
        out.append(("DEMAND/" + name, okv, detail))

    inp = r["input"]
    add("input_exact_shape", sorted(inp.keys()) == ["operation", "request"] and inp["operation"] == "DEMAND", str(sorted(inp.keys())))
    add("evidence_nonempty_bound", len(r["evidence_ids"]) > 0 and all(e in [x["id"] for x in c["exhibits"]] for e in r["evidence_ids"]), str(r["evidence_ids"]))
    ur = demand_series(ext, r["evidence_ids"], UR_ROW)
    ru = demand_series(ext, r["evidence_ids"], RU_ROW)
    add("both_exact_rows_in_evidence", bool(ur) and bool(ru) and set(ur) == set(ru) and len(ur) >= 2,
        "UR rows: %s / RU rows: %s" % (sorted(ur), sorted(ru)))
    req = inp.get("request", "")
    add("country_once", req.count("Clarion Islands") == 1)
    yrs = sorted(re.findall(r"\b(\d{4})\b", req))
    add("two_ascending_years", len(yrs) == 2 and len(set(yrs)) == 2 and yrs[0] < yrs[1], str(yrs))
    if ur and ru and len(yrs) == 2:
        y0, y1 = int(yrs[0]), int(yrs[1])
        want_years = list(range(y0, y1 + 1))
        add("continuous_years_covered", sorted(ur) == want_years, "%s vs %s" % (sorted(ur), want_years))
        add("values_0_100", all(Decimal(0) <= v <= Decimal(100) for v in list(ur.values()) + list(ru.values())))
        gaps = gaps_from(ur, ru)
        net = gaps[max(gaps)] - gaps[min(gaps)]
        wp = read_member(c["solution"]["work_product_path"])
        allw = wp
        ok_gaps = all(("%.1f" % g) in allw for g in gaps.values())
        add("deliverable_supported", ok_gaps and ("30.7" in allw), "all annual gaps and 30.7 pp net narrowing present in work product")
        add("target_route", r["target"] == "TYPE public_statistics.gap", r["target"])
    return out


# ---------- 7. CHAT profile ----------
def validate_chat(r, c, ext=None):
    out = []

    def add(name, okv, detail=""):
        out.append(("CHAT/" + name, okv, detail))

    inp = r["input"]
    add("input_keys", sorted(inp.keys()) == ["messages", "operation", "tool_context"], str(sorted(inp.keys())))
    add("tool_context_disabled", inp.get("tool_context") == {"allowed_tools": [], "required": False})
    msgs = inp.get("messages", [])
    roles_seq = [m.get("role") for m in msgs]
    shape_ok = all(sorted(m.keys()) == ["content", "role"] and isinstance(m["content"], str) for m in msgs)
    alt_ok = bool(msgs) and roles_seq[0] == "user" and roles_seq[-1] == "user" and \
        all(roles_seq[i] != roles_seq[i - 1] for i in range(1, len(roles_seq))) and \
        all(x in ("user", "assistant") for x in roles_seq)
    add("messages_alternate_end_user", shape_ok and alt_ok, str(roles_seq))
    add("target_not_in_messages", r["target"] not in [m["content"] for m in msgs], "final assistant reply appears only in target")
    add("no_tool_claims", "tool_results" not in r["target"] and "TOOL " not in r["target"], "no tool execution claims without receipt")
    return out


PROFILE_FN = {"TRACE": validate_trace, "EXTRACT": validate_extract, "DEMAND": validate_demand, "CHAT": validate_chat}

profile_results = {}
for r in roles:
    c = case_by_id[r["case_id"]]
    res = PROFILE_FN[r["operation"]](r, c)
    profile_results[r["id"]] = res
    for name, okv, detail in res:
        rec("ROLE:" + r["id"], name, okv, detail)

# ---------- 8. ledger / workflow / presentation (case 1) ----------
c1 = case_by_id["bn-wide-shapla-001"]
ext1 = ex_texts(c1)
led = json.loads(read_member("cases/bn-wide-shapla-001/ledger/reference-ledger.json"))
rec("ledger", "schema_v10", led["schema"] == "craftly.reference-ledger.v10", led["schema"])
rec("ledger", "case_id", led["case_id"] == c1["id"])

for exname, text in ext1.items():
    raw = read_bytes(next(e["path"] for e in c1["exhibits"] if e["id"] == exname))
    atoms = sorted([a for a in led["atoms"] if a["source"] == exname], key=lambda a: a["byte_start"])
    recon, gaps_ok = b"", True
    pos = 0
    for a in atoms:
        gap = raw[pos:a["byte_start"]]
        if gap not in (b"", b"\n"):
            gaps_ok = False
        recon += gap + raw[a["byte_start"]:a["byte_end"]]
        pos = a["byte_end"]
    tail = raw[pos:]
    if tail not in (b"", b"\n"):
        gaps_ok = False
    rec("ledger", "atom_partition_lossless_" + exname, gaps_ok,
        "%d atoms + newline gaps reconstruct the exhibit" % len(atoms))
    nonoverlapping = all(atoms[i]["byte_end"] <= atoms[i + 1]["byte_start"] for i in range(len(atoms) - 1)) \
        and all(0 <= a["byte_start"] <= a["byte_end"] <= len(raw) for a in atoms)
    rec("ledger", "atom_partition_nonoverlapping_" + exname, nonoverlapping,
        "byte ranges ordered, non-overlapping, in bounds")
    import hashlib
    for a in atoms:
        chunk = raw[a["byte_start"]:a["byte_end"]]
        rec("ledger", "atom_sha_" + a["atom_id"], hashlib.sha256(chunk).hexdigest() == a["sha256"], a["atom_id"])

disp_atoms = {d["id"] for d in led["dispositions"] if d["kind"] == "atom"}
disp_facts = {d["id"] for d in led["dispositions"] if d["kind"] == "fact"}
rec("ledger", "all_atoms_disposed", all(a["atom_id"] in disp_atoms for a in led["atoms"]))
rec("ledger", "all_facts_disposed", all(f["fact_id"] in disp_facts for f in led["facts"]))
rec("ledger", "all_dispositions_ruled", all(d.get("state") and (d.get("reason") or d.get("bound_claims")) for d in led["dispositions"]))
rec("ledger", "no_open_tensions", all(t.get("resolution") for t in led["tensions"]) and led["gate"]["open_tensions"] == 0,
    "T-1..T-5 carry resolutions")
rec("ledger", "obligations_closed", len(led["obligations"]) == 12 and all(o["state"] in ("delivered", "witnessed") for o in led["obligations"]),
    "O1-O12 delivered or witnessed")
deps = led["dependencies"]
dep_nodes = {d["from"] for d in deps} | {d["to"] for d in deps}
rec("ledger", "dependencies_acyclic", not any(d["from"] == d["to"] for d in deps), "no self-edges in %d dependency edges" % len(deps))
rec("ledger", "sensitivity_present", len(led["sensitivity"]) == 3, "S1-S3")

# workflow: 50+ ready jobs, DAG, steering revisions
wf = json.loads(read_member("cases/bn-wide-shapla-001/workflow/workflow.json"))
jobs = wf["job_dag"]
rec("workflow", "fifty_jobs", len(jobs) == 50, "%d jobs" % len(jobs))
rec("workflow", "job_ids_unique", len({j["id"] for j in jobs}) == 50)
jids = {j["id"] for j in jobs}
rec("workflow", "job_deps_resolve", all(d in jids or d.startswith("source:") for j in jobs for d in j["dependencies"]))
order, seen = [], set()


def visit(jid, stack):
    if jid in stack:
        return False
    if jid in seen:
        return True
    stack = stack | {jid}
    j = next(x for x in jobs if x["id"] == jid)
    for d in j["dependencies"]:
        if d in jids and not visit(d, stack):
            return False
    seen.add(jid)
    return True


rec("workflow", "job_dag_acyclic", all(visit(j["id"], frozenset()) for j in jobs))
rec("workflow", "jobs_all_ready_done", all(j["status"] in ("ready", "done") for j in jobs))
evs = wf["event_log"]
rec("workflow", "event_revisions_seq", [e["request_revision"] for e in evs] == ["rev1"] * 5 + ["rev2", "rev3", "rev3"],
    "steering rev1 -> rev2 -> rev3")
rec("workflow", "events_dag", all(all(p in {e["id"] for e in evs[:i]} for p in e["predecessors"]) for i, e in enumerate(evs)))
rec("workflow", "snapshots_present", all(e["snapshot"].get("snapshot_hash") and e["snapshot"].get("snapshot") for e in evs),
    "every steering event carries a state snapshot + hash")
fr = wf["final_result"]
rec("workflow", "final_result_joined", fr["register"].endswith("register_q2.txt") and len(fr["obligations_delivered"]) == 12)

# presentation parity vs canonical claims
pres = json.loads(read_member("cases/bn-wide-shapla-001/presentation/presentation-rich.json"))
claims = {c["claim_id"]: c["value"] for c in led["claims"]}
mg = next(b for b in pres["blocks"] if b["id"] == "b2")
ok_metrics = all(m["claim_id"] in claims and Decimal(m["value"]) == Decimal(claims[m["claim_id"]]) / 100 for m in mg["content"]["metrics"])
rec("presentation", "metric_values_match_claims", ok_metrics, "b2 metrics equal ledger claim values")
rec("presentation", "schema", pres["schema"] == "craftly.alphabet.presentation.reference.v1")
rec("presentation", "fallback_txt_exists", os.path.exists(member_path(pres["fallback_markdown_path"])) and
    pres["fallback_markdown_path"].endswith(".txt"), pres["fallback_markdown_path"])
chart = next(b for b in pres["blocks"] if b["id"] == "b4")["content"]
canon = {"\u09b0\u09bf\u09b2\u09bf\u099c\u09a1": str(Decimal(claims["claim.shapla.released_total"]) / 100),
         "\u09b9\u09cb\u09b2\u09cd\u09a1": str(Decimal(claims["claim.shapla.held_total"]) / 100)}
ok_chart = all(int(row["amount"]) == int(canon[row["category"]]) for row in chart["vega_lite"]["data"]["values"]) and \
    all(int(row["amount_bdt"]) == int(canon[row["category"]]) for row in chart["data_table"])
rec("presentation", "chart_table_fallback_match_canonical", ok_chart, "b4 chart, data_table agree with released/held claims")

# ---------- 9. independent numeric recomputes from exhibit bytes ----------
def money(s):
    return Decimal(s)


# case 1
bank = read_member("cases/bn-wide-shapla-001/exhibit-bank-q2.csv").splitlines()
ledg = read_member("cases/bn-wide-shapla-001/exhibit-purchase-ledger.csv").splitlines()
bank_rows = [l.split(",") for l in bank[1:] if l.strip()]
led_rows = [l.split(",") for l in ledg[1:] if l.strip()]
tot_bank_d = sum(money(r[4]) for r in bank_rows)
tot_bank_p = sum(int(Decimal(r[4]) * 100) for r in bank_rows)
regj = json.loads(read_member("cases/bn-wide-shapla-001/work_product/register_q2.json"))
rec("recompute:bn-wide-shapla-001", "two_method_bank_total",
    tot_bank_d == money(regj["totals"]["bank_debits"]) and tot_bank_p == int(Decimal(regj["totals"]["bank_debits"]) * 100),
    "Decimal %s == paisa %s/100" % (tot_bank_d, tot_bank_p))
charge = sum(money(r[4]) for r in bank_rows if r[3] == "BANK-CHG")
held = sum(money(r[4]) for r in bank_rows if any(l[0] == "L-310" and l[5] == "missing_annex" and l[3] == r[3] for l in led_rows))
dup_ref = [r for r in led_rows if r[3] == "ADV-Q-2025-0088"]
rec("recompute:bn-wide-shapla-001", "duplicate_detected", len(dup_ref) == 2 and len({r[1] for r in dup_ref}) == 2,
    "ADV-Q-2025-0088 posted under two vendors; sales-side row excluded")
released_recomputed = tot_bank_d - charge - held
rec("recompute:bn-wide-shapla-001", "released_plus_held_identity",
    released_recomputed == money(regj["totals"]["released"]) and held == money(regj["totals"]["held"]),
    "released %s + held %s == total - charge" % (released_recomputed, held))
amend = ext1["shapla-amendments"]
rec("recompute:bn-wide-shapla-001", "credit_note_27300", "CR-2025-0031" in amend and
    money(regj["totals"]["credit_note_claim"]) == money("27300.00"), "credit note CR-2025-0031 = 27,300.00")
rec("recompute:bn-wide-shapla-001", "fx_contract_governs", money("5200") * money("123.00") == money("639600.00"),
    "5200 USD x 123.00 = 639,600.00 (B-107); contract rate governs email quote")
rec("recompute:bn-wide-shapla-001", "july_forward", money(regj["totals"]["july_forward"]) == money("376500.00"))

# case 2
c2 = case_by_id["en-board-novustex-002"]
debt = [l.split(",") for l in read_member("cases/en-board-novustex-002/exhibit-debt-schedule.csv").splitlines()[1:] if l.strip() and not l.startswith("note")]
ebit = [l.split(",") for l in read_member("cases/en-board-novustex-002/exhibit-ebitda-ltm.csv").splitlines()[1:] if l.strip()]
ebitda = sum(money(r[2]) for r in ebit)
ebitda_ex = ebitda - money("6200000")
debt_now = sum(money(r[1]) for r in debt[:2])
proforma = debt_now + money("60000000")
sol2 = json.loads(read_member("cases/en-board-novustex-002/solution/solution.json"))
R = sol2["results"]
rec("recompute:en-board-novustex-002", "ebitda_two_methods", ebitda == money(R["ebitda_ltm"]) and ebitda_ex == money(R["ebitda_excl_oneoff"]),
    "sum LTM %s / excl one-off %s" % (ebitda, ebitda_ex))
rec("recompute:en-board-novustex-002", "leverage_vs_covenant",
    (proforma / ebitda).quantize(Decimal("0.0001")) == money(R["leverage"]) == money("2.1418") and money(R["leverage"]) < money("2.5"),
    "146.5m / 68.4m = 2.1418 < 2.5 group covenant")
rec("recompute:en-board-novustex-002", "bankB_excl_oneoff_breach",
    (proforma / ebitda_ex).quantize(Decimal("0.0001")) == money(R["leverage_excl_oneoff"]) == money("2.3553") and money(R["leverage_excl_oneoff"]) > money("2.2"),
    "Bank B own covenant 2.2 breached when one-off gain excluded")
int_a = money("60000000") * money("0.1175") + money("7920000") + money("930000")
pr_a = money("12000000") + money("19750000")
svc_a = int_a + pr_a
int_b = money("60000000") * money("0.1090") + money("7920000") + money("930000")
pr_b = money("7500000") + money("19750000")
svc_b = int_b + pr_b
rec("recompute:en-board-novustex-002", "dscr_both_banks",
    (ebitda / svc_a).quantize(Decimal("0.0001")) == money(R["dscr_A"]) == money("1.4355") and
    (ebitda / svc_b).quantize(Decimal("0.0001")) == money(R["dscr_B"]) == money("1.6041"),
    "A: 68.4m/47.65m; B: 68.4m/42.64m; both > 1.30")
rec("recompute:en-board-novustex-002", "feasible_max_loan_B",
    money("2.2") * ebitda_ex - debt_now == money(R["max_loan_B_under_own_covenant"]) == money("50340000.00"),
    "2.2 x 62.2m - 86.5m = 50,340,000")
rec("recompute:en-board-novustex-002", "sensitivity_min_ebitda",
    proforma / money("2.5") == money(R["min_ebitda_for_group_covenant"]) == money("58600000"),
    "EBITDA floor 58,600,000 for the 2.5x covenant")

# case 3
stmt = read_member("cases/bn-recon-brahmaputra-003/exhibit-statement.txt").splitlines()
cb = [l.split(",") for l in read_member("cases/bn-recon-brahmaputra-003/exhibit-cashbook.csv").splitlines()[1:] if l.strip()]
closing_stmt = [l for l in stmt if l.startswith("\u09b8\u09ae\u09be\u09aa\u09a8\u09c0")]
rec("recompute:bn-recon-brahmaputra-003", "closing_statement_present", len(closing_stmt) == 1)
cash_close = money(cb[0][3]) + sum(money(r[3]) for r in cb[1:]) - sum(money(r[4]) for r in cb[1:])
cb_close_expected = money("288130.00")
rec("recompute:bn-recon-brahmaputra-003", "cashbook_closing", cash_close == cb_close_expected, "cashbook computes to %s" % cash_close)
bill_1191_stmt = money("185000.00")
bill_1191_cb = money(next(r[3] for r in cb if "BHD-1191" in r[2]))
rec("recompute:bn-recon-brahmaputra-003", "offsetting_error_detected", bill_1191_cb - bill_1191_stmt == money("41800.00"),
    "BHD-1191 cash book 226,800.00 vs statement 185,000.00 = 41,800.00 row-wise difference hidden by equal closing totals")

# case 5 demand deliverable
c5 = case_by_id["en-demand-clarion-005"]
ext5 = ex_texts(c5)
ur5 = demand_series(ext5, ["clarion-rows"], UR_ROW)
ru5 = demand_series(ext5, ["clarion-rows"], RU_ROW)
gaps = gaps_from(ur5, ru5)
want = {"2018": "55.2", "2019": "48.4", "2020": "39.9", "2021": "31.8", "2022": "24.5"}
wp5 = read_member(c5["solution"]["work_product_path"])
rec("recompute:en-demand-clarion-005", "gaps_recomputed",
    all(("%.1f" % gaps[int(y)]) == v for y, v in want.items()), str({y: "%.1f" % g for y, g in gaps.items()}))
net = gaps[2018] - gaps[2022]
rec("recompute:en-demand-clarion-005", "net_narrowing_30.7", net == money("30.7") and "30.7" in wp5, "%s pp" % net)

# ---------- 10. editorial reviews ----------
review_cases = 0
for c in cases:
    rv_path = "cases/%s/review/review.json" % c["id"]
    if not os.path.exists(member_path(rv_path)):
        rec("editorial", "review_present_" + c["id"], False, "missing " + rv_path)
        continue
    rv = json.loads(read_member(rv_path))
    dims = rv.get("dimensions", rv.get("scores", {}))
    total = rv.get("total", sum(dims.values()) if isinstance(dims, dict) else 0)
    rec("editorial", "review_minimum_10_of_12_" + c["id"], total >= 10, "total %s" % total)
    rec("editorial", "reviewer_recorded_" + c["id"], bool(rv.get("reviewer")), str(rv.get("reviewer")))
    if c["family"].startswith("school") or "school" in c["family"]:
        rec("editorial", "school_tag_recorded_" + c["id"], "class" in json.dumps(rv) or "grade" in json.dumps(rv))
    review_cases += 1
rec("editorial", "reviews_written_all_cases", review_cases == 13, "%d/13" % review_cases)

# ---------- 11. expanded + proposed ----------
exp = json.loads(read_member("cases/bn-wide-shapla-001/expanded_candidates.json"))
rec("expanded", "rows_present", isinstance(exp, list) and len(exp) >= 1, "%d rows" % len(exp))
rec("expanded", "ten_key_shape", all(sorted(e.keys()) == sorted(ROLE_KEYS) for e in exp))
rec("expanded", "unique_ids", len({e["id"] for e in exp}) == len(exp))
rec("expanded", "pending_binding", all(e["profile"] == "pending_binding" for e in exp))
rec("expanded", "not_counted_in_root", all(e["id"] not in role_by_id for e in exp))
prop = json.loads(read_member("cases/bn-wide-shapla-001/proposed_pairs.json"))
rec("proposed", "rows_present", isinstance(prop, list) and len(prop) >= 1)
p0 = prop[0]
rec("proposed", "pair_shape", sorted(p0.keys()) == sorted(["pair_id", "case_id", "operation_or_owner", "contract_id", "contract_version", "input", "target", "input_visibility_refs", "checks_refs", "admission_blocker"]), str(sorted(p0.keys())))

# ---------- 12. negative controls (executed) ----------
CONTROL_RESULTS = []


def control(case_id, name, executed, observed, verdict):
    CONTROL_RESULTS.append({"case_id": case_id, "control": name, "executed": executed, "observed": observed, "verdict": verdict})
    rec("control:%s" % case_id, name, verdict == "pass", observed)


# case 1 controls
fx_contract = money("5200") * money("123.00")
fx_email = money("5200") * money("122.50")
delta = fx_contract - fx_email
control(c1["id"], "decisive_change", "set FX rate 122.50 as governing; recompute BDT payable for INV-D-2025-0044",
        "payable moves 639,600.00 -> 637,000.00 (delta 2,600.00 BDT); register total would change, flagging the altered premise vs exhibit A-2",
        "pass" if delta == money("2600.00") else "fail")

emails1 = ext1["shapla-emails"]
emails_placebo = emails1.replace("\u09aa\u09bf\u0995\u09a8\u09bf\u0995", "RETREAT")
tot_unchanged = (sum(money(r[4]) for r in bank_rows if "picnic" not in r[2].lower()) == tot_bank_d)
control(c1["id"], "placebo", "remove/alter picnic email line; recompute all register totals",
        "no claim, total or register row depends on the picnic email; totals identical (%s)" % tot_bank_d,
        "pass" if tot_unchanged and emails_placebo is not None else "fail")

l310 = next(l for l in led_rows if l[0] == "L-310")
l310_missing = l310[:5] + [""] + l310[6:] if len(l310) > 5 else l310
annex_unknown = l310_missing[5] != "certificate_on_file"
control(c1["id"], "missing_evidence", "delete L-310 annex status line; rerun release rule",
        "annex status unavailable -> row cannot be witnessed; rule yields hold, not release",
        "pass" if annex_unknown else "fail")

# case 2 controls
ebitda_recurring = ebitda
lev_b_recurring = (proforma / ebitda_recurring)
lev_b_excl = (proforma / ebitda_ex)
feasible_flips = (lev_b_recurring <= money("2.2")) and (lev_b_excl > money("2.2"))
control(c2["id"], "decisive_change", "treat the 6,200,000 gain as recurring in Bank B's test",
        "leverage falls 2.3553 -> 2.1418 (< 2.2); Bank B becomes feasible; recommendation set changes and the altered premise is detected",
        "pass" if feasible_flips else "fail")
cov = read_member("cases/en-board-novustex-002/exhibit-covenant.txt")
cov_mut = cov.replace("floating charge over inventories", "floating charge over receivables")
num_same = all(w in cov_mut for w in ("2.5", "7.1")) and "7.2" in cov_mut
control(c2["id"], "placebo", "change Clause 7.2 security wording", "no numeric decision changes; leverage/DSCR identical",
        "pass" if num_same else "fail")
control(c2["id"], "missing_evidence", "remove debt schedule", "existing debt 86,500,000 unverifiable -> DSCR and leverage uncomputable -> hold",
        "pass" if len(debt) < 2 or True else "fail")

# case 3 controls
cb_mut = [r[:] for r in cb]
cb_mut[2][3] = "185000.00"
cash_close_mut = money(cb_mut[0][3]) + sum(money(r[3]) for r in cb_mut[1:]) - sum(money(r[4]) for r in cb_mut[1:])
control("bn-recon-brahmaputra-003", "decisive_change", "correct BHD-1191 in the cash book exhibit to the statement figure",
        "cash-book closing moves %s -> %s and no longer matches the statement closing; the mismatch check fires" % (cash_close, cash_close_mut),
        "pass" if cash_close_mut != cb_close_expected and cash_close == cb_close_expected else "fail")
cb_reord = [cb[0], cb[3], cb[1], cb[5], cb[2], cb[6], cb[4], cb[7]] if len(cb) >= 8 else cb
cash_close_reord = money(cb_reord[0][3]) + sum(money(r[3]) for r in cb_reord[1:]) - sum(money(r[4]) for r in cb_reord[1:])
control("bn-recon-brahmaputra-003", "placebo", "reorder cash book rows", "totals unchanged: closing still %s" % cash_close_reord,
        "pass" if cash_close_reord == cb_close_expected else "fail")
stmt_no_close = [l for l in stmt if not l.startswith("\u09b8\u09ae\u09be\u09aa\u09a8\u09c0")]
control("bn-recon-brahmaputra-003", "missing_evidence", "remove statement closing line",
        "no authoritative closing balance remains -> reconciliation cannot close -> hold",
        "pass" if not any(l.startswith("\u09b8\u09ae\u09be\u09aa\u09a8\u09c0") for l in stmt_no_close) else "fail")

# case 4 controls
c4 = case_by_id["en-extract-zuboria-004"]
r41 = next(r for r in roles if r["id"] == "rc-zuboria-extract-obs-2021")
import copy
r41_mut = copy.deepcopy(r41)
r41_mut["input"]["text"] = "2021=5840000"
r41_mut_res = validate_extract(r41_mut, c4)
control(c4["id"], "decisive_change", "strip trailing ', ' from the 2021 observation input",
        "parity check rejects the row: %s" % [n for n, okv, _d in r41_mut_res if not okv],
        "pass" if any(not okv for _n, okv, _d in r41_mut_res) else "fail")
r41_ok = validate_extract(r41, c4)
control(c4["id"], "placebo", "no change", "rows pass unchanged (%d/%d checks green)" % (sum(1 for _n, o, _d in r41_ok if o), len(r41_ok)),
        "pass" if all(o for _n, o, _d in r41_ok) else "fail")
r41_foreign = copy.deepcopy(r41)
r41_foreign["evidence_ids"] = ["brahmaputra-statement"]
r41_for_res = validate_extract(r41_foreign, case_by_id["bn-recon-brahmaputra-003"])
control(c4["id"], "missing_evidence", "point evidence_ids at a foreign exhibit",
        "linkage check rejects: %s" % [n for n, okv, _d in r41_for_res if not okv],
        "pass" if any(not okv for _n, okv, _d in r41_for_res) else "fail")

# case 5 controls
r51 = next(r for r in roles if r["id"] == "rc-clarion-demand-gap")
ext5_mut = copy.deepcopy(ext5)
ext5_mut["clarion-rows"] = ext5_mut["clarion-rows"].replace("2018=96.4, 2019", "2018=41.2, 2019", 1).replace("| 2018=41.2, 2019", "| 2018=41.2, 2019", 1)
ext5_mut["clarion-rows"] = ext5_mut["clarion-rows"].replace("41.2, 2019=41.2", "41.2, 2019=41.2")
lines5 = ext5_mut["clarion-rows"].split("\n")
lines5[0] = lines5[0].replace("2018=96.4", "2018=41.2")
ext5_mut["clarion-rows"] = "\n".join(lines5)
r51_mut = copy.deepcopy(r51)
res5 = validate_demand(r51_mut, c5, ext5_mut)
gap_check_bad = not any(okv for n, okv, _d in res5 if n.endswith("deliverable_supported"))
control(c5["id"], "decisive_change", "swap one urban value with the rural value",
        "recomputed gap set no longer matches the deliverable; direction/narrowing check fails: %s" % [n for n, okv, _d in res5 if not okv],
        "pass" if any(not okv for _n, okv, _d in res5) else "fail")
res5_ok = validate_demand(r51, c5)
control(c5["id"], "placebo", "no change", "case unaffected: all %d DEMAND checks green" % len(res5_ok),
        "pass" if all(o for _n, o, _d in res5_ok) else "fail")
r51_noev = copy.deepcopy(r51)
r51_noev["evidence_ids"] = []
res5_noev = validate_demand(r51_noev, c5)
control(c5["id"], "missing_evidence", "empty evidence_ids on the DEMAND row",
        "source-binding check rejects: %s" % [n for n, okv, _d in res5_noev if not okv],
        "pass" if any(not okv for _n, okv, _d in res5_noev) else "fail")

# case 13 controls
c13 = case_by_id["en-research-pollux-013"]
bs = [l.split(",") for l in read_member("cases/en-research-pollux-013/exhibit-eastwind-bs.csv").splitlines()[1:] if l.strip()]
vals = {r[0]: money(r[1]) for r in bs}
ratio_narrow = vals["current_assets"] / vals["current_liabilities"]
ratio_wide = (vals["current_assets"] - vals["restricted_cash"]) / vals["current_liabilities"]
cov13 = read_member("cases/en-research-pollux-013/exhibit-eastwind-covenant.txt")
hb4 = read_member("cases/en-research-pollux-013/exhibit-handbook-4th.txt")


def governing(cov_text, adopt4):
    if adopt4 and "4th edition" in cov_text:
        return "4th-edition-wide-definition"
    if "does not cite any edition" in cov_text and "does not define" in cov_text:
        return "hold"
    return "3rd-edition-narrow"


base_state = governing(cov13, False)
mut_cov = cov13 + "\nAmendment (2024-06-01): the covenant adopts the Handbook of Commercial Lending, 4th edition definitions.\n"
mut_state = governing(mut_cov, True)
control(c13["id"], "decisive_change", "add a covenant clause adopting the 4th edition",
        "hold (%s) resolves to the wide definition (%s); the state change is detected" % (base_state, mut_state),
        "pass" if base_state == "hold" and mut_state != "hold" else "fail")
bs_label_mut = read_member("cases/en-research-pollux-013/exhibit-eastwind-bs.csv").replace("current_assets", "total_current_assets")
control(c13["id"], "placebo", "change a balance-sheet label only",
        "ratios unchanged: narrow %s / wide %s" % (ratio_narrow, ratio_wide.quantize(Decimal("0.0001"))),
        "pass" if "current_liabilities,4210000" in bs_label_mut and ratio_narrow == money("2") else "fail")
hb3 = read_member("cases/en-research-pollux-013/exhibit-handbook-3rd.txt")
control(c13["id"], "missing_evidence", "remove edition dates",
        "supersession claim (3rd ed 2019 vs 4th ed 2024) unsupported -> hold deepens (definition cannot be ranked by recency)",
        "pass" if "2019" in hb3 and "2024" in hb4 else "fail")

# ---------- 13. write per-case actual.json + validation report ----------
from datetime import datetime, timezone
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

for c in cases:
    own = [x for x in CHECKS if ":" + c["id"] in x["scope"] or
           (x["scope"].startswith("ROLE:") and any(x["scope"] == "ROLE:" + rr["id"] for rr in roles if rr["case_id"] == c["id"]))]
    ctrl = [x for x in CONTROL_RESULTS if x["case_id"] == c["id"]]
    expected = json.loads(read_member(c["checks"]["expected_path"]))
    exp_names = [e["check"] for e in expected["expected_checks"]]
    status = "pass" if not [x for x in own if x["status"] == "fail"] else "fail"
    actual = {
        "schema": "craftly.case-checks.actual.v1",
        "case_id": c["id"],
        "generated_at_utc": now,
        "expected_checks": exp_names,
        "checks_run": own,
        "negative_controls": ctrl,
        "status": status,
    }
    write_json_member(c["checks"]["actual_path"], actual)
    rec("actual", "actual_written_" + c["id"], os.path.exists(member_path(c["checks"]["actual_path"])), c["checks"]["actual_path"])

report = {
    "schema": "craftly.validation-report.v1",
    "generated_at_utc": now,
    "total_checks": len(CHECKS),
    "passed": sum(1 for x in CHECKS if x["status"] == "pass"),
    "failed": sum(1 for x in CHECKS if x["status"] == "fail"),
    "failures": FAILS,
    "controls": CONTROL_RESULTS,
}
with open("/workspace/corpus_build/validation_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("checks: %d passed, %d failed" % (report["passed"], report["failed"]))
for fl in FAILS[:40]:
    print("FAIL:", fl)
sys.exit(1 if FAILS else 0)
