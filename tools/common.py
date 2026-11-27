import hashlib, json, os

STAGING = "/workspace/corpus_build/staging"
PROMPT_PATH = "/mnt/vibefs/uploads/7435077d-19d0-4403-94eb-11ae3c1b6c04/CUDObZup-Craftly-Alphabet-R9-Corpus-Generator-Prompt-V16.md"


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(path):
    with open(path, "rb") as f:
        return sha_bytes(f.read())


def sha_text(t):
    return sha_bytes(t.encode("utf-8"))


def write_member(path, text):
    full = os.path.join(STAGING, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb") as f:
        f.write(text.encode("utf-8"))
    return sha_bytes(text.encode("utf-8"))


def write_member_bytes(path, data):
    full = os.path.join(STAGING, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb") as f:
        f.write(data)
    return sha_bytes(data)


def member_path(path):
    return os.path.join(STAGING, path)


def read_bytes(rel):
    with open(member_path(rel), "rb") as f:
        return f.read()


def read_member(path):
    with open(member_path(path), "rb") as f:
        return f.read().decode("utf-8")


def read_json(path):
    return json.loads(read_member(path))


def write_json_member(path, obj):
    return write_member(path, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def jsonl_write(path, rows):
    lines = [json.dumps(r, ensure_ascii=False) for r in rows]
    return write_member(path, "\n".join(lines) + "\n")


def jsonl_read(path):
    text = read_member(path)
    return [json.loads(l) for l in text.splitlines() if l.strip()]


def bdt(x_paise, grouped=True):
    x = int(x_paise)
    sign = "-" if x < 0 else ""
    x = abs(x)
    taka, paise = divmod(x, 100)
    if grouped:
        s = str(taka)
        if len(s) > 3:
            head, tail = s[:-3], s[-3:]
            parts = []
            while len(head) > 2:
                parts.insert(0, head[-2:])
                head = head[:-2]
            if head:
                parts.insert(0, head)
            s = ",".join(parts + [tail])
        out = sign + s
    else:
        out = sign + str(taka)
    if paise:
        out += "." + ("%02d" % paise)
    return out


def expect(cond, msg, failures):
    if not cond:
        failures.append(msg)
    return cond
