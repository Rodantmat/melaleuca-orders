#!/usr/bin/env python3
"""leakcheck.py - refuses to let anything that looks like a credential reach a commit.
usage: python tools/leakcheck.py <dir> [<dir> ...]   (exit 1 + loud message when something is found; prints file names only, never the value)"""
import os, re, sys
NAMES = re.compile(r"(^|/)(credentials(?![^/]*\.example$)[^/]*|\.env[^/]*|.*\.pem|.*\.key|id_rsa.*)$", re.I)
CONTENT = [re.compile(p) for p in (
    r"shippo_(live|test)_[0-9a-f]{20,}", r"github_pat_[A-Za-z0-9_]{20,}", r"gh[pousr]_[A-Za-z0-9]{30,}",
    r"Atzr\|[A-Za-z0-9_\-]{20,}", r"amzn1\.oa2-cs\.v1\.[0-9a-f]{20,}", r"AKIA[0-9A-Z]{16}", r"(?i)\bMELA_(USER|PASS)_\d+=(?![%$<{\"'\\s])\S{3,}",
    r"(?i)\b(GMAIL_APP_PASSWORD|PROXY_URL|DATABASE_URL|CLIENT_SECRET|REFRESH_TOKEN)=(?![%$<{\"'\\s])\S{6,}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"(?i)postgres(ql)?://[^\s:@]+:[^\s@]+@", r"https?://[^\s:/@%$]+:(?![%$])[^\s@/%$]+@[A-Za-z0-9.\-]+")]
bad = []
for root_dir in sys.argv[1:] or ["."]:
    for dp, dn, fn in os.walk(root_dir):
        dn[:] = [d for d in dn if d != ".git"]
        for f in fn:
            p = os.path.join(dp, f)
            if f.endswith(".example"): continue
            if NAMES.search(p.replace("\\", "/")):
                bad.append((p, "file name")); continue
            try:
                if os.path.getsize(p) > 5_000_000: continue
                t = open(p, "r", encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            for c in CONTENT:
                if c.search(t):
                    bad.append((p, "pattern " + c.pattern[:30])); break
if bad:
    print("::error::LEAK GUARD - nothing was published. Suspicious files (values NOT shown):")
    for p, why in bad: print("  -", p, "(%s)" % why)
    sys.exit(1)
print("leakcheck: clean")
