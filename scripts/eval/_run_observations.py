"""Execution observations from saved logs and resource records.

Log matches are evidence of messages, not proof of absent failures or valid loops.
"""
import os
import re
import sys

import numpy as np

LOG_PATTERNS = {
    "orbslam3": {
        "init_success":    re.compile(r"New Map created with \d+ points"),
        # Count explicit messages, not unique episodes; local-map failures can
        # recover without entering the terminal LOST state.
        "tracking_loss":   re.compile(r"^(?:Fail to track local map!|Track Lost\.\.\.|IMU\. State LOST|Timestamp jump detected\. State set to LOST\.)"),
        "loop_closure":    re.compile(r"\*Loop detected"),
        "map_reset":       re.compile(r"^(?:Active map Reseting|System Reseting)\s*$"),
    },
    "fasttrack_partial_gpu": {
        "init_success":    re.compile(r"New Map created with \d+ points"),
        "tracking_loss":   re.compile(r"\bLOST\b"),
        "loop_closure":    re.compile(r"\*Loop detected"),
        "map_reset":       re.compile(r"Map id:\s*\d+"),
    },
    "droidslam": {
        "init_success":    None,
        "tracking_loss":   None,
        "loop_closure":    None,
        "map_reset":       None,
    },
    "macvo": {
        "init_success":    None,
        "tracking_loss":   None,
        "loop_closure":    None,
        "map_reset":       None,
    },
    "basalt": {
        # Basalt prints frame count updates and marginalisation info.
        # "Initialized!" signals the first successful stereo triangulation.
        "init_success":    re.compile(r"Initialized!|initialized"),
        "tracking_loss":   re.compile(r"Tracking lost|tracking lost|LOST"),
        "loop_closure":    None,
        "map_reset":       None,
    },
    "airslam": {
        # visual_odometry.cpp prints "dataset done" once all frames are loaded,
        # then "i ====== 0" for the first frame processed.
        # No tracking-loss or loop-closure output (stereo VO only).
        "init_success":    None,
        "tracking_loss":   None,
        "loop_closure":    re.compile(r"Loop closure detected|loop detected"),
        "map_reset":       None,
    },
    "ov2slam": {
        "init_success":    None,
        "tracking_loss":   re.compile(r"RESET REQUIRED"),
        "loop_closure":    re.compile(r"\[PoseGraph\].*Closing a loop between"),
        "map_reset":       re.compile(r"RESET APPLIED"),
    },
    "megasam": {
        # MegaSaM prints per-frame depth+pose progress and a final
        # "Saved trajectory" banner.
        "init_success":    None,
        "tracking_loss":   None,
        "loop_closure":    None,
        "map_reset":       None,
    },
    "mast3r_slam": {
        # MASt3R-SLAM uses the MASt3R retrieval head for loop closures; the
        # demo prints "Loop closure" when one is accepted.
        "init_success":    re.compile(r"Initialised"),
        "tracking_loss":   re.compile(r"Tracking lost"),
        "loop_closure":    re.compile(r"Loop closure"),
        "map_reset":       None,
    },
    "okvis2": {
        # okvis_app_synchronous prints "Initialised!" after IMU init,
        # "Marginalisation... SLAM frame" for ongoing tracking,
        # and "Finishing..." before writing the trajectory.
        # Loop closures: Frontend.cpp logs one "LOOP CLOSURE: current frame N,
        # matching to keyframe M, ..." line per detected closure. NOTE: do NOT
        # match bare "loop closure" -- that hits the per-frame timing-profile
        # rows ("loop closure query", "attempt loop closure") and overcounts by
        # ~100x (e.g. 6337 timing rows vs 76 real closures on Rosario seq1).
        "init_success":    re.compile(r"Initialised!|Initialized!|SLAM started"),
        "tracking_loss":   re.compile(r"Tracking LOST|tracking lost"),
        "loop_closure":    re.compile(r"LOOP CLOSURE: current frame"),
        "map_reset":       None,
    },
    "okvis2x": {
        # Frontend.cpp logs "Initialized!" (INFO) once the IMU-aided front-end
        # bootstraps, and "3d2d tracking lost. Number of 3d2d-matches: N"
        # (WARNING) when it loses the map.
        # Loop closures: OKVIS2-X shares OKVIS2's Frontend.cpp and logs the same
        # "LOOP CLOSURE: current frame N, matching to keyframe M, ..." events
        # (the earlier "OKVIS2-X never logs an accepted closure" assumption was
        # wrong -- it does, e.g. 27 on Rosario seq1, 29 on EuRoC MH_01; the only
        # thing it never logs here is a GPS loop closure).
        "init_success":    re.compile(r"Initialized!"),
        "tracking_loss":   re.compile(r"3d2d tracking lost"),
        "loop_closure":    re.compile(r"LOOP CLOSURE: current frame"),
        "map_reset":       None,
    },
    "openvins": {
        # OpenVINS' MSCKF prints "[init]: successful initialization in ..."
        # once the static-IMU/dynamic init succeeds. "Reset System" appears
        # if the filter explicitly resets. No built-in loop closure.
        "init_success":    re.compile(r"successful initialization|Initialized System"),
        "tracking_loss":   re.compile(r"failed to track|Reset System|TRACKING LOST"),
        "loop_closure":    None,
        "map_reset":       re.compile(r"Reset System"),
    },
}



_MAP_ID_RE = re.compile(r"Map id:\s*(\d+)")
ORB_DETAIL_PATTERNS = {
    'local_tracking_failure_messages': re.compile(r'^Fail to track local map!\s*$'),
    'local_mapping_reset_messages': re.compile(r'^LM: Reseting (?:current map|Atlas) in Local Mapping\.\.\.\s*$'),
    'imu_initialization_reset_requests': re.compile(r'^Not enough motion for initializing\. Reseting\.\.\.\s*$'),
    'map_creation_messages': re.compile(r'^Creation of new map with id:\s*\d+\s*$'),
}


def parse_log(log_path, algo):
    """Parse a timestamped run log. Returns dict of robustness fields.

    Semantics (fixed 2026-08-05):
      * A field is None (not 0) when the algorithm has NO log pattern for it —
        "not instrumented" must be distinguishable from "genuinely zero".
        (Previously DPVO/Voxel-SVIO/all GNSS runners silently reported 0 loop
        closures / 0 tracking losses.)
      * map_resets uses the algorithm's OWN configured pattern. The old
        code fetched it and then re-grepped ORB's "Map id:" regex regardless,
        so OV2SLAM's "RESET APPLIED" and OpenVINS' "Reset System" never
        counted. Legacy id-style patterns use (distinct ids - 1). ORB-SLAM3
        uses explicit Tracking reset messages; LocalMapping resets, IMU init
        requests and map creation messages are separate, overlapping counters.
        These are message counts, not deduplicated failure episodes.
    """
    patterns = LOG_PATTERNS.get(algo, {})

    def _has(key):
        return patterns.get(key) is not None

    result = {
        "init_success":      None,
        "init_time_s":       None,
        "tracking_losses":   0 if _has("tracking_loss") else None,
        "loop_closures":     0 if _has("loop_closure") else None,
        "map_resets":        0 if _has("map_reset") else None,
        "output_valid":      None,
        "first_failure_s":   None,
        "log_instrumented":  bool(patterns),
        "event_semantics":   "configured log-pattern matches; absence does not prove no failure; loop matches do not certify accepted/correct closures",
        "log_available":     os.path.isfile(log_path),
    }
    details = ORB_DETAIL_PATTERNS if algo == 'orbslam3' else {}
    result.update({key: 0 if key in details else None for key in ORB_DETAIL_PATTERNS})
    if details:
        result['event_semantics'] += ('; ORB tracking_losses includes recoverable local-map failure messages, not unique lost episodes; '
            'map_resets counts explicit Tracking resets only; local mapping/init reset messages are separate overlapping observations')

    if not os.path.isfile(log_path):
        for key in ("tracking_losses", "loop_closures", "map_resets", *ORB_DETAIL_PATTERNS):
            result[key] = None
        return result

    map_ids_seen = set()
    map_event_count = 0
    pat_map = patterns.get("map_reset")
    map_is_id_style = bool(pat_map and "Map id" in pat_map.pattern)

    with open(log_path) as f:
        for raw_line in f:
            raw_line = raw_line.rstrip()
            # Try to strip leading float timestamp added by run script
            m_ts = re.match(r"^(\d+\.\d+)\s+(.*)", raw_line)
            if m_ts:
                rel_t = float(m_ts.group(1))
                line = m_ts.group(2)
            else:
                rel_t = None
                line = raw_line
            line = line.strip()

            for key, pattern in details.items():
                if pattern.search(line):
                    result[key] += 1

            pat_init = patterns.get("init_success")
            if pat_init and pat_init.search(line) and not result["init_success"]:
                result["init_success"] = True
                result["init_time_s"] = rel_t

            pat_loss = patterns.get("tracking_loss")
            if pat_loss and pat_loss.search(line):
                result["tracking_losses"] += 1
                if result["first_failure_s"] is None and rel_t is not None:
                    result["first_failure_s"] = rel_t

            pat_loop = patterns.get("loop_closure")
            if pat_loop and pat_loop.search(line):
                result["loop_closures"] += 1

            if pat_map:
                if map_is_id_style:
                    mm = _MAP_ID_RE.search(line)
                    if mm:
                        map_ids_seen.add(int(mm.group(1)))
                elif pat_map.search(line):
                    map_event_count += 1

    if pat_map:
        if map_is_id_style:
            result["map_resets"] = max(0, len(map_ids_seen) - 1) if map_ids_seen else 0
        else:
            result["map_resets"] = map_event_count

    return result


# ──────────────────────────────────────────────────────────────────────────────
# Resource stats from CSV
# ──────────────────────────────────────────────────────────────────────────────
def parse_resources(csv_path):
    """Parse scoped resources.csv, retaining legacy files as explicitly unscoped."""
    if not os.path.isfile(csv_path):
        return None
    try:
        import csv as _csv
        rows = list(_csv.DictReader(open(csv_path)))
        if not rows:
            return None

        def col(name):
            vals = []
            for r in rows:
                try:
                    raw = r.get(name)
                    if raw not in (None, ""):
                        vals.append(float(raw))
                except (TypeError, ValueError):
                    pass
            return vals

        def summary(values, fn):
            return round(float(fn(values)), 1) if values else None

        vram = col("vram_mib")
        gpu  = col("gpu_util_pct")
        cpu  = col("cpu_pct")
        ram  = col("ram_mib")
        cpu_time = col("cpu_time_s")
        scopes = sorted({row.get("scope") for row in rows if row.get("scope")})

        return {
            "resource_scope": scopes[0] if len(scopes) == 1 else "legacy_whole_system",
            "vram_mean_mib": summary(vram, np.mean),
            "vram_peak_mib": summary(vram, np.max),
            "gpu_mean_pct": summary(gpu, np.mean),
            "gpu_peak_pct": summary(gpu, np.max),
            "cpu_mean_pct": summary(cpu, np.mean),
            "cpu_peak_pct": summary(cpu, np.max),
            "cpu_time_s": summary(cpu_time, np.max),
            "ram_mean_mib": summary(ram, np.mean),
            "ram_peak_mib": summary(ram, np.max),
        }
    except Exception as e:
        print(f"[eval] resource parse failed: {e}", file=sys.stderr)
        return None
