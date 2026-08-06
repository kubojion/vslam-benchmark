# OKVIS2 build patches (the one prerequisite forks can't carry)

Slimmed 2026-08-06: the AirSLAM launch files and the OpenVINS `Dockerfile.benchmark` that used
to live here are now carried by our forks and arrive via `git submodule update`
([kubojion/AirSLAM](https://github.com/kubojion/AirSLAM/tree/vslam-benchmark-patches),
[kubojion/open_vins](https://github.com/kubojion/open_vins/tree/vslam-benchmark-patches),
wired in `.gitmodules`).

What remains — and why it must stay: OKVIS2's build needs CMake fixes inside its **nested**
upstream submodules (`src/okvis2/external/DBoW2`, `src/okvis2/external/opengv`; OKVIS2-X uses
the same externals). Carrying those via forks would require forking DBoW2, opengv AND
okvis2/okvis2x just to re-pin them — a patch directory is the standard, cheaper solution.

**After `git submodule update --init --recursive`, run:**

```bash
bash vendor/prerequisites/install.sh
```

It applies (idempotently):

| patch | target |
|---|---|
| `okvis2/dbow2-cmake.patch` | `src/okvis2/external/DBoW2` |
| `okvis2/opengv-cmake.patch` | `src/okvis2/external/opengv` |
