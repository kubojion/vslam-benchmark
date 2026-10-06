#!/usr/bin/env python3
"""Read-only delivery diagnosis from native log and publisher sidecar, no estimator execution."""
import argparse
import json
from pathlib import Path
import re


def audit(log, delivery):
    # Native ROS2Visualizer.cpp reports lag with *100 rather than *1000.
    samples=re.findall(r'\[TIME\]: ([0-9.eE+-]+) seconds total \([^\n]*?, ([0-9.eE+-]+) ms behind\)',log)
    lags=[float(lag)*10 for _,lag in samples]
    times=[float(t) for t,_ in samples]
    published=min(delivery['published_left'],delivery['published_right'])
    return dict(schema=1,publisher=delivery,processed_camera_callbacks=len(samples),
                processed_over_published=len(samples)/published if published else None,
                max_native_lag_ms=max(lags) if lags else None,
                mean_callback_seconds=sum(times)/len(times) if times else None,
                estimator_received_imu=None,
                limitations=['INFO TIME lines count completed camera callbacks including initialisation, not successful state updates.',
                             'Published counts and output pose counts do not measure internal IMU receipt.',
                             'Missing/truncated native logs make callback counts a lower bound.',
                             'Select playback by delivery evidence; never by ATE.'])


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('run',type=Path);a=ap.parse_args()
    print(json.dumps(audit((a.run/'openvins_node.log').read_text(errors='replace'),
                          json.loads((a.run/'openvins_delivery.json').read_text())),indent=2))
if __name__=='__main__':main()
