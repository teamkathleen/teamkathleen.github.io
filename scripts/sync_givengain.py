#!/usr/bin/env python3
"""Pull Kathleen's fundraising total and donor names from GivenGain into data/campaign.json.

Run it any time:   python3 scripts/sync_givengain.py
It also runs daily on GitHub Actions (.github/workflows/sync-givengain.yml).

What gets published, on purpose:
  - the amount raised and the goal
  - donor names exactly as GivenGain shows them publicly, each name once
What never gets published:
  - anonymous donors, individual gift amounts, messages, fees, timestamps

Uses only the Python standard library.
"""
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ID = 129854
API = "https://api.givengain.com/v4/project"
USER_AGENT = "TeamKathleen.com donor sync (github.com/teamkathleen)"
OUT = Path(__file__).resolve().parent.parent / "data" / "campaign.json"
PAGE_SIZE = 100


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def fetch_timeline():
    """All timeline items, following GivenGain's cursor until nothing new comes back."""
    items, seen, cursor = [], set(), None
    while True:
        params = {"page": 0, "pageSize": PAGE_SIZE}
        if cursor:
            params["cursor"] = cursor
        data = get_json(f"{API}/{PROJECT_ID}/timeline?{urllib.parse.urlencode(params)}")
        new = [i for i in data.get("items", []) if i.get("id") not in seen]
        for i in new:
            seen.add(i.get("id"))
        items.extend(new)
        cursor = data.get("lastCursor")
        if not new or len(data.get("items", [])) < PAGE_SIZE or not cursor:
            return items


def main():
    project = get_json(f"{API}/{PROJECT_ID}")
    raised = project.get("amountRaised", project.get("stats", {}).get("raised"))
    target = project.get("target")
    if not isinstance(raised, (int, float)) or not isinstance(target, (int, float)):
        sys.exit("GivenGain's project data changed shape; not overwriting campaign.json.")

    donations = [i["payload"] for i in fetch_timeline() if i.get("type") == "donation" and "payload" in i]
    names, seen = [], set()
    # Newest first, each person once.
    for d in sorted(donations, key=lambda d: d.get("id", 0), reverse=True):
        name = (d.get("donor") or "").strip()
        if d.get("anonymous") or not name or name.lower().startswith("anonymous"):
            continue
        key = name.casefold()
        if key not in seen:
            seen.add(key)
            names.append(name)

    out = {
        "raised": raised,
        "target": target,
        "donorCount": len(donations),
        "donors": names,
        "source": f"https://www.givengain.com/project/{PROJECT_ID}",
        "updated": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }

    # Only rewrite the file when something real changed, so the daily job doesn't commit noise.
    if OUT.exists():
        old = json.loads(OUT.read_text())
        if {k: v for k, v in old.items() if k != "updated"} == {k: v for k, v in out.items() if k != "updated"}:
            print(f"No change: ${raised:,} of ${target:,}, {len(names)} named donors.")
            return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"Updated: ${raised:,} of ${target:,}, {len(donations)} gifts, {len(names)} named donors.")


if __name__ == "__main__":
    main()
