"""Session comparison utilities."""

from __future__ import annotations

from typing import Any


def _single_compare(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    li = left.get("interpretation_payload", {})
    ri = right.get("interpretation_payload", {})
    lf = left.get("facts_payload", {})
    rf = right.get("facts_payload", {})

    lflags = (lf.get("reason_flags", {}) or {})
    rflags = (rf.get("reason_flags", {}) or {})
    reason_flag_changes = {
        key: {"left": lflags.get(key), "right": rflags.get(key)}
        for key in sorted(set(lflags.keys()) | set(rflags.keys()))
        if lflags.get(key) != rflags.get(key)
    }

    llevels = (lf.get("levels", {}) or {})
    rlevels = (rf.get("levels", {}) or {})
    level_changes = {
        tf: {"left": llevels.get(tf), "right": rlevels.get(tf)}
        for tf in sorted(set(llevels.keys()) | set(rlevels.keys()))
        if llevels.get(tf) != rlevels.get(tf)
    }

    return {
        "left_id": left["id"],
        "right_id": right["id"],
        "ticker": left.get("ticker") or right.get("ticker"),
        "changes": {
            "action_changed": li.get("action") != ri.get("action"),
            "entry_stage_changed": li.get("entry_stage") != ri.get("entry_stage"),
            "confidence_delta": round(float(ri.get("confidence", 0.0)) - float(li.get("confidence", 0.0)), 4),
            "ranking_score_delta": None,
            "reason_flag_changes": reason_flag_changes,
            "level_changes": level_changes,
            "summary": f"Moved from {li.get('entry_stage')} to {ri.get('entry_stage')}."
            if li.get("entry_stage") != ri.get("entry_stage")
            else "No major stage transition.",
        },
    }


def _watchlist_compare(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    litems = {i.get("ticker"): i for i in left.get("metadata", {}).get("items", []) if i.get("ticker")}
    ritems = {i.get("ticker"): i for i in right.get("metadata", {}).get("items", []) if i.get("ticker")}

    lt = set(litems.keys())
    rt = set(ritems.keys())
    shared = sorted(lt & rt)

    changed_rankings: dict[str, Any] = {}
    changed_actions: dict[str, Any] = {}
    changed_priorities: dict[str, Any] = {}
    for ticker in shared:
        lrow = litems[ticker]
        rrow = ritems[ticker]
        ls = ((lrow.get("ranking") or {}).get("score"))
        rs = ((rrow.get("ranking") or {}).get("score"))
        if ls != rs:
            changed_rankings[ticker] = {"left": ls, "right": rs}
        la = ((lrow.get("interpretation") or {}).get("action"))
        ra = ((rrow.get("interpretation") or {}).get("action"))
        if la != ra:
            changed_actions[ticker] = {"left": la, "right": ra}
        lp = ((lrow.get("ranking") or {}).get("priority"))
        rp = ((rrow.get("ranking") or {}).get("priority"))
        if lp != rp:
            changed_priorities[ticker] = {"left": lp, "right": rp}

    return {
        "left_id": left["id"],
        "right_id": right["id"],
        "changes": {
            "added_tickers": sorted(rt - lt),
            "removed_tickers": sorted(lt - rt),
            "changed_rankings": changed_rankings,
            "changed_actions": changed_actions,
            "changed_priorities": changed_priorities,
        },
    }


def compare_sessions(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    if left.get("session_type") == "watchlist_batch_analysis" or right.get("session_type") == "watchlist_batch_analysis":
        return _watchlist_compare(left, right)
    return _single_compare(left, right)
