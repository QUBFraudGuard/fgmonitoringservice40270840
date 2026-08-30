import os
import time
import requests
import threading
from flask import Flask, jsonify

app = Flask(__name__)

PROXY_URLS = ["http://proxy1.40270840.qpc.qubcloud.uk/", "http://proxy2.40270840.qpc.qubcloud.uk/"]

def call_via_proxy(path, backend_name, params, timeout=10):
    last_error = None
    for base in PROXY_URLS:
        try:
            url = f"{base}{path}/{backend_name}"
            resp = requests.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            last_error = e
            continue
    raise last_error or Exception("all proxy endpoints unreachable")


def merge_results(easy_results, rep_results):
    merged = []
    for easy, rep in zip(easy_results, rep_results):
        if easy["decision"] == "ERROR":
            merged.append(easy)
        elif rep and rep.get("decision") == "ERROR":
            merged.append(rep)
        elif easy["decision"] == "SUSPICIOUS":
            merged.append(easy)
        elif rep and rep.get("decision") == "SUSPICIOUS":
            merged.append(rep)
        else:
            merged.append(easy)
    return merged


def run_check():

    try:
        test_batch = "5000-1234-UK,50000-1234-UK,500-9999-UK,500-1234-ES"
        expected = ["OK", "SUSPICIOUS", "SUSPICIOUS", "SUSPICIOUS"]  # known expected outcomes

        start = time.time()
        screening = call_via_proxy("screen", "screening", {"items": test_batch})
        reputation = call_via_proxy("screen", "reputation", {"items": test_batch})
        duration = time.time() - start

        merged = merge_results(screening["results"], reputation["results"])
        actual = [r["decision"] for r in merged]

        passed = actual == expected
        return {"passed": passed, "duration": duration, "actual": actual, "expected": expected}

    except Exception as e:
        return {"passed": False, "error": str(e), "duration": None}

    # On-demand
@app.route("/check", methods=["GET"])
def check_now():
    result = run_check()
    return jsonify(result)

# Periodic

def periodic_loop():
    while True:
        result = run_check()
        if not result["passed"]:
            print(f"[ALERT] Monitor check FAILED: {result}", flush=True)
        time.sleep(60) 

threading.Thread(target=periodic_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5001")))