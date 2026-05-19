#!/usr/bin/env python3
"""Thin wrapper around DROID-SLAM's demo.py logic that ALSO writes a TUM
trajectory at the end. Mirrors demo.py CLI; adds --trajectory_out and
--rightimagedir / --timestamps for stereo with paired left/right folders.
"""
import argparse, os, sys, glob, numpy as np, cv2, torch

# __file__ is scripts/run/_droid_demo_wrapper.py → three dirnames to reach WS root
_WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, os.path.join(_WS, "src", "DROID-SLAM", "droid_slam"))
sys.path.insert(0, os.path.join(_WS, "src", "DROID-SLAM"))
from droid import Droid


def load_calib(path):
    vals = list(map(float, open(path).read().split()))
    fx, fy, cx, cy = vals[:4]
    # distortion coefficients are optional; default to zero (no distortion)
    k = np.zeros(4)
    if len(vals) > 4:
        extra = vals[4:8]
        k[:len(extra)] = extra
    K = np.eye(3)
    K[0, 0] = fx; K[1, 1] = fy; K[0, 2] = cx; K[1, 2] = cy
    return K, k


def image_stream(left_dir, right_dir, K, k, t_file, stride=1, max_frames=None):
    lefts = sorted(glob.glob(os.path.join(left_dir, "*.png")))
    rights = sorted(glob.glob(os.path.join(right_dir, "*.png"))) if right_dir else None
    times = None
    if t_file and os.path.isfile(t_file):
        times = [float(x) for x in open(t_file).read().split()]
        # times.txt may store nanoseconds (e.g. Rosario v2); TUM format needs seconds
        if times and times[0] > 1e12:
            times = [t / 1e9 for t in times]

    n_yielded = 0
    for i in range(0, len(lefts), stride):
        if max_frames is not None and n_yielded >= max_frames:
            break
        img = cv2.imread(lefts[i])
        if img is None:
            continue
        h0, w0 = img.shape[:2]

        if np.any(k != 0):
            img = cv2.undistort(img, K, k)

        # Aspect-ratio preserving resize targeting ~384×512 px, 8-pixel aligned
        # (same formula as demo.py; network expects images aligned to 8 pixels)
        scale = np.sqrt((384 * 512) / (h0 * w0))
        h1 = int(h0 * scale)
        w1 = int(w0 * scale)
        img = cv2.resize(img, (w1, h1))
        h1 = h1 - h1 % 8
        w1 = w1 - w1 % 8
        img = img[:h1, :w1]

        imgs = [img]
        if rights:
            r = cv2.imread(rights[i])
            if r is not None:
                if np.any(k != 0):
                    r = cv2.undistort(r, K, k)
                r = cv2.resize(r, (w1, h1))[:h1, :w1]
                imgs.append(r)

        # (N_cams, C, H, W) float tensor
        ten = torch.as_tensor(
            np.stack([cv2.cvtColor(im, cv2.COLOR_BGR2RGB) for im in imgs])
        ).float().permute(0, 3, 1, 2)

        # Scale intrinsics to match resized image dimensions
        intr = torch.as_tensor([
            K[0, 0] * w1 / w0,  # fx
            K[1, 1] * h1 / h0,  # fy
            K[0, 2] * w1 / w0,  # cx
            K[1, 2] * h1 / h0,  # cy
        ])

        t = times[i] if times else float(i)
        n_yielded += 1
        yield t, ten, intr


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--imagedir", required=True)
    p.add_argument("--rightimagedir", default=None)
    p.add_argument("--calib", required=True)
    p.add_argument("--timestamps", default=None)
    p.add_argument("--stereo", action="store_true")
    p.add_argument("--disable_vis", action="store_true")
    p.add_argument("--reconstruction_path", default=None)
    p.add_argument("--trajectory_out", required=True)
    p.add_argument("--stride", type=int, default=1)
    p.add_argument("--buffer", type=int, default=512)
    p.add_argument("--weights", default=None)
    # DROID-SLAM tuning params — defaults match demo.py
    p.add_argument("--beta", type=float, default=0.3)
    p.add_argument("--filter_thresh", type=float, default=2.4)
    p.add_argument("--warmup", type=int, default=8)
    p.add_argument("--keyframe_thresh", type=float, default=4.0)
    p.add_argument("--frontend_thresh", type=float, default=16.0)
    p.add_argument("--frontend_window", type=int, default=25)
    p.add_argument("--frontend_radius", type=int, default=2)
    p.add_argument("--frontend_nms", type=int, default=1)
    p.add_argument("--backend_thresh", type=float, default=22.0)
    p.add_argument("--backend_radius", type=int, default=2)
    p.add_argument("--backend_nms", type=int, default=3)
    p.add_argument("--upsample", action="store_true")
    p.add_argument("--skip_backend", action="store_true",
                   help="skip global bundle adjustment (saves ~1 GB VRAM; "
                        "use when backend OOMs on long sequences)")
    p.add_argument("--max_frames", type=int, default=None,
                   help="stop after this many source frames (e.g. 2700 = first 3 min at 15 fps)")
    args = p.parse_args()

    if args.weights is None:
        for cand in (
            "droid.pth",
            os.path.join(_WS, "src", "DROID-SLAM", "droid.pth"),
        ):
            if os.path.isfile(cand):
                args.weights = cand
                break
    if args.weights is None:
        raise FileNotFoundError("droid.pth not found; pass --weights /path/to/droid.pth")

    K, k = load_calib(args.calib)
    right_dir = args.rightimagedir if args.stereo else None

    def stream():
        return image_stream(args.imagedir, right_dir, K, k, args.timestamps,
                            args.stride, args.max_frames)

    droid = None
    times = []
    for t, image, intr in stream():
        if droid is None:
            args.image_size = list(image.shape[-2:])
            droid = Droid(args)
        droid.track(t, image, intrinsics=intr)
        times.append(t)

    # terminate() runs backend global BA then fills non-keyframe poses.
    # On 8 GB VRAM the backend OOMs for long sequences; --skip_backend
    # bypasses it and calls traj_filler directly (frontend trajectory only).
    print(f"[droid] keyframes in buffer: {droid.video.counter.value} / {args.buffer}")
    if args.skip_backend:
        import torch
        del droid.frontend
        torch.cuda.empty_cache()
        traj = droid.traj_filler(stream()).inv().data.cpu().numpy()
    else:
        # terminate() returns camera_trajectory.inv().data.cpu().numpy()
        # lietorch SE3 data layout: [tx, ty, tz, qx, qy, qz, qw] — matches TUM format
        traj = droid.terminate(stream())

    os.makedirs(os.path.dirname(os.path.abspath(args.trajectory_out)), exist_ok=True)
    with open(args.trajectory_out, "w") as f:
        for t, pose in zip(times, traj):
            f.write(f"{t:.9f} " + " ".join(f"{v:.9f}" for v in pose) + "\n")
    print(f"wrote {args.trajectory_out}")


if __name__ == "__main__":
    main()
