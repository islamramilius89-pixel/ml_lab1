import json
import sys
import time
import requests

BASE_URL = "http://localhost:8000"
RETRIES = 15


def wait_for_api():
    for i in range(RETRIES):
        try:
            r = requests.get(f"{BASE_URL}/", timeout=3)
            if r.status_code == 200:
                print("[OK] API готов к работе")
                return True
        except requests.exceptions.RequestException:
            pass
        print(f"[..] Ждём API ({i + 1}/{RETRIES})")
        time.sleep(2)
    return False


def main():
    if not wait_for_api():
        print("[FAIL] API не поднялся за отведённое время")
        sys.exit(1)

    with open("scenario.json", encoding="utf-8") as f:
        scenarios = json.load(f)["scenarios"]

    failed = 0
    for s in scenarios:
        url = f"{BASE_URL}{s['path']}"
        try:
            r = requests.request(s["method"], url, timeout=10)
            ok = r.status_code == s["expect_status"]
            body = r.text[:200]
            print(f"[{'OK' if ok else 'FAIL'}] {s['name']} -> {r.status_code} | {body}")
        except Exception as e:
            ok = False
            print(f"[ERROR] {s['name']}: {e}")
        if not ok:
            failed += 1

    print(f"\nИтог: {len(scenarios) - failed}/{len(scenarios)} сценариев пройдено")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()