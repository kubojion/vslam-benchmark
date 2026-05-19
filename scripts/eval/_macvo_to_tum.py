#!/usr/bin/env python3
"""Convert a MAC-VO Sandbox folder into a TUM trajectory file.
MAC-VO stores estimated poses as 'poses.npy' (Nx7: tx ty tz qx qy qz qw)
and timestamps in 'timestamps.npy' (or in metadata). We try a few likely
locations and field names.
"""
import sys, os, glob, numpy as np
SBX, OUT = sys.argv[1], sys.argv[2]

candidates_pose = ["poses.npy", "trajectory.npy", "estimated_poses.npy",
                   "MACVO/poses.npy"]
candidates_time = ["timestamps.npy", "times.npy"]

def find(c):
    for p in c:
        full = os.path.join(SBX, p)
        if os.path.isfile(full): return full
    matches = []
    for p in c:
        matches += glob.glob(os.path.join(SBX, "**", os.path.basename(p)), recursive=True)
    return matches[0] if matches else None

ppath = find(candidates_pose)
tpath = find(candidates_time)
if ppath is None:
    sys.exit(f"no pose npy found under {SBX}; check Sandbox structure")
poses = np.load(ppath)
if poses.shape[1] == 7:
    trans, quat = poses[:, :3], poses[:, 3:]
elif poses.shape[1] == 8:
    # maybe (t, tx,ty,tz, qx,qy,qz,qw)
    times = poses[:, 0]; trans = poses[:, 1:4]; quat = poses[:, 4:8]
elif poses.shape[1:] == (4, 4):
    from scipy.spatial.transform import Rotation as R
    trans = poses[:, :3, 3]
    quat  = R.from_matrix(poses[:, :3, :3]).as_quat()
else:
    sys.exit(f"unexpected pose shape {poses.shape}")

if tpath is not None:
    times = np.load(tpath).astype(float)
else:
    if 'times' not in dir(): times = np.arange(len(poses), dtype=float) * 0.05  # fallback 20Hz
with open(OUT, "w") as f:
    for t, p, q in zip(times, trans, quat):
        f.write(f"{t:.9f} {p[0]:.6f} {p[1]:.6f} {p[2]:.6f} "
                f"{q[0]:.6f} {q[1]:.6f} {q[2]:.6f} {q[3]:.6f}\n")
print(f"wrote {OUT}  ({len(times)} poses)")
