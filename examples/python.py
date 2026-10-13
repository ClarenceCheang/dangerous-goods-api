"""One call to each of the six Fortitude21 dangerous goods endpoints.

Standard library only (Python 3.8+). No key needed.
The API allows about 10 requests per 10 seconds per IP, so the script
pauses between calls and waits 10 seconds if it gets HTTP 429.

Usage: python examples/python.py
Terms of use: https://fortitude21.com/terms
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://fortitude21.com/api"
PAUSE = 1.5
# Set your own User-Agent. The CDN in front of the API refuses urllib's
# default one ("Python-urllib/3.x") with HTTP 403, Cloudflare error 1010.
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "fortitude21-api-example/1.0 (python)",
}


def call(endpoint, params):
    """GET an endpoint. Returns (HTTP status, parsed JSON)."""
    url = f"{BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status, json.load(resp)
        except urllib.error.HTTPError as err:
            if err.code == 429 and attempt == 0:
                time.sleep(10)  # the limit resets after 10 seconds
                continue
            # A 400 still carries JSON: ok is false and error says why.
            body = err.read().decode("utf-8")
            try:
                data = json.loads(body)
            except ValueError:
                data = {}
            if "ok" not in data:
                data = {"ok": False, "error": data.get("title") or body[:200]}
            return err.code, data
    raise RuntimeError("rate limited twice")


def show(name, status, data, summary):
    print(f"== {name}: HTTP {status}, ok={data.get('ok')}")
    if data.get("ok"):
        print("  " + summary(data))
    else:
        print("  error: " + str(data.get("error")))
    for line in data.get("assumed", []):
        print("  assumed: " + line)
    # Show the credit line wherever you show a result (terms, section 3).
    print("  cite: " + str(data.get("cite")))
    print()


def containers(d):
    entry = d["entries"][0]
    sizes = ", ".join(f"{c['type']} up to {c['largest_litres']} L" for c in entry["containers"][:3])
    return f"{entry['proper_shipping_name']} (PG {entry['packing_group']}): {sizes}"


CALLS = [
    ("un-packaging", {"un": "1203"}, containers),
    (
        "un-decode",
        {"mark": "UN 3H1/Y1.9/150/26/D/BAM 12345", "un": "1203"},
        lambda d: f"{d['noun']}; may carry UN {d['check']['un']}: {d['check']['entries'][0]['may_carry']}",
    ),
    (
        "ibc-dates",
        {"code": "31HA1", "made": "06/25"},
        lambda d: f"status {d['status']}, fill only before {d['fill_only_before']}, end of use {d['end_of_use']}",
    ),
    (
        "adr-points",
        {"l": "1203:20:10,1263:II:20:5"},
        lambda d: f"exempt={d['exempt']}, used {d['used']} of {d['limit']} ({d['test']})",
    ),
    (
        "bund-size",
        {"region": "gb-eng", "drums": 4, "ibcs": 1},
        lambda d: f"minimum {d['minimum_capacity_l']} L under {d['rule']['instrument']}",
    ),
    (
        "jerry-cans",
        {"mode": "water", "people": 4, "days": 14, "scenario": "survival"},
        lambda d: f"{d['total_l']} L = {d['cans']} x {d['can']['name']}",
    ),
]

if __name__ == "__main__":
    for endpoint, params, summary in CALLS:
        status, data = call(endpoint, params)
        show(endpoint, status, data, summary)
        time.sleep(PAUSE)
