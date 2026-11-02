"""Provenance helpers run on the system interpreter, not a wrapper's activated conda env (Rule C 283)."""
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[3]
PATHS = REPO/'scripts/_paths.sh'
HELPERS = ('_capture_implementation.py', '_capture_inputs.py', '_capture_runtime.py', '_enrich_run_meta.py',
           '_gnss_input.py')


class HelperInterpreterTests(unittest.TestCase):
    def test_every_helper_call_uses_the_pinned_system_interpreter(self):
        text = PATHS.read_text()
        self.assertIn('VSLAM_HELPER_PYTHON=/usr/bin/python3\n', text)
        calls = re.findall(r'^\s*(?:run_post_native_helper )?(\S+) "\$WS/scripts/run/(_\w+\.py)"', text, re.M)
        self.assertEqual({name for _, name in calls}, set(HELPERS))
        self.assertEqual({interpreter for interpreter, _ in calls}, {'"$VSLAM_HELPER_PYTHON"'})

    def test_an_activated_env_python3_on_path_is_not_used(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            decoy = root/'conda-env/bin'; decoy.mkdir(parents=True)
            (decoy/'python3').write_text('#!/bin/sh\necho decoy-env-python\nexit 3\n'); (decoy/'python3').chmod(0o755)
            workspace = root/'ws'; (workspace/'scripts/run').mkdir(parents=True)
            (workspace/'scripts/_paths.sh').write_text(PATHS.read_text())
            (workspace/'scripts/run/_enrich_run_meta.py').write_text(
                'import sys\nprint(sys.executable, *sys.argv[1:])\n')
            script = 'source "$WS/scripts/_paths.sh"; enrich_run_meta meta.json --measurement-mode x'
            result = subprocess.run(['bash', '-c', script], capture_output=True, text=True, check=True,
                                    env=dict(os.environ, WS=str(workspace), PATH=f"{decoy}:{os.environ['PATH']}"))
            self.assertNotIn('decoy', result.stdout)
            self.assertTrue(result.stdout.startswith('/usr/bin/python3 meta.json --require-implementation-capture'),
                            result.stdout)


if __name__ == '__main__':
    unittest.main()


class PostNativeHelperRetryTests(unittest.TestCase):
    """A post-native helper SIGSEGV is retried once in a fresh process; nothing else is retried."""

    def run_helper(self, exits):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); counter = root/'count'; counter.write_text('0')
            fake = root/'fake.sh'
            fake.write_text('#!/bin/bash\nn=$(cat "%s"); n=$((n+1)); echo $n > "%s"\n'
                            'echo "fh=$PYTHONFAULTHANDLER"\ncodes=(%s)\nexit ${codes[$((n-1))]}\n'
                            % (counter, counter, ' '.join(map(str, exits))))
            fake.chmod(0o755)
            script = f'source "{PATHS}"; run_post_native_helper "{fake}" x; echo "rc=$?"'
            out = subprocess.run(['bash', '-c', script], capture_output=True, text=True)
            return out.stdout, int(counter.read_text())

    def test_one_segfault_is_retried_and_succeeds(self):
        out, calls = self.run_helper([139, 0])
        self.assertEqual(calls, 2); self.assertIn('rc=0', out); self.assertIn('fh=1', out)

    def test_two_segfaults_fail(self):
        out, calls = self.run_helper([139, 139])
        self.assertEqual(calls, 2); self.assertIn('rc=139', out)

    def test_other_failures_are_never_retried(self):
        for code in (1, 2, 134, 137):
            out, calls = self.run_helper([code, 0])
            self.assertEqual(calls, 1, code); self.assertIn(f'rc={code}', out)

    def test_only_post_native_enrichment_uses_the_retry(self):
        text = PATHS.read_text()
        self.assertEqual(text.count('run_post_native_helper "$VSLAM_HELPER_PYTHON" "$WS/scripts/run/_enrich_run_meta.py"'), 2)
        for helper in ('_capture_implementation.py', '_capture_inputs.py', '_capture_runtime.py'):
            self.assertIn(f'    "$VSLAM_HELPER_PYTHON" "$WS/scripts/run/{helper}"', text)
