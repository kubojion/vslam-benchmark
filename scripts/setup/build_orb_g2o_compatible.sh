#!/usr/bin/env bash
# Build the bundled g2o with the generic Eigen ABI used by this ORB build.
# Use a fresh output directory; never replace the historical native library.
set -euo pipefail
WS=$(cd "$(dirname "$0")/../.." && pwd)
DEST=${1:?usage: build_orb_g2o_compatible.sh /absolute/fresh/output}
[[ "$DEST" == /* && ! -e "$DEST" ]] || { echo 'output must be a fresh absolute path' >&2; exit 2; }
python3 - "$WS" "$DEST" <<'PY'
from pathlib import Path
import hashlib, json, shutil, sys
root, target = map(Path, sys.argv[1:])
flags = root/'src/ORB_SLAM3/build/CMakeFiles/ORB_SLAM3.dir/flags.make'
text = flags.read_text()
if '-march' in text or '-mavx' in text or 'EIGEN_MAX_ALIGN' in text:
    raise SystemExit('ORB build flags changed: review Eigen ABI before building')
target.mkdir(parents=True)
source = root/'src/ORB_SLAM3/Thirdparty/g2o'
shutil.copytree(source, target/'g2o-source', ignore=shutil.ignore_patterns('build','lib','.git'))
record = {str(p.relative_to(target)): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in (target/'g2o-source').rglob('*') if p.is_file()}
record['ORB_flags_sha256'] = hashlib.sha256(flags.read_bytes()).hexdigest()
(target/'source-inputs.json').write_text(json.dumps(record, indent=2)+'\n')
PY
# RelWithDebInfo avoids g2o's Release-only -march=native, matching ORB's
# existing RelWithDebInfo build. No optimizer source/parameter changes.
cmake -S "$DEST/g2o-source" -B "$DEST/build" -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build "$DEST/build" --parallel 4
sha256sum "$DEST/g2o-source/lib/libg2o.so"
