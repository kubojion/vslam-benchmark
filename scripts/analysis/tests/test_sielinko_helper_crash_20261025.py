"""An incomplete attempt (post-native helper crash) is replaced only with an explicit helper-crash review."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import noise_execution_policy as policy  # noqa: E402

KEY = 'full__okvis2_zed2i__noise_x__field1_sielinko_h1_20261022__vio__rep1'


class HelperCrashRevisionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.record = dict(key=KEY, state='running', params={'a': 1}, run='/r/run1')
        self.review = dict(classification='post_native_helper_crash', revision='helpercrash-20261025',
                           helper_crash_attempts=[KEY], native_finished=True, scientific_score=None,
                           optimizer_feedback=False, replacement_count=1)

    def item(self):
        rec = self.root / 'record.json'; rec.write_text(json.dumps(self.record))
        digest = hashlib.sha256(rec.read_bytes()).hexdigest()
        self.review.setdefault('original_record_sha256', digest)
        rev = self.root / 'review.json'; rev.write_text(json.dumps(self.review))
        return dict(revision='helpercrash-20261025', record=str(rec), record_sha256=digest,
                    review=str(rev), review_sha256=hashlib.sha256(rev.read_bytes()).hexdigest())

    def revision(self):
        return policy.reviewed_attempt_revision({'physical_attempt_revisions': {KEY: self.item()}}, KEY)

    def test_exact_review_admits_the_incomplete_attempt(self):
        self.assertEqual(self.revision()['revision'], 'helpercrash-20261025')

    def test_any_deviation_is_refused(self):
        self.review['classification'] = 'resource_censored_guard_termination'
        with self.assertRaisesRegex(RuntimeError, 'reviewed failed attempt'):
            self.revision()
        for field, value in (('native_finished', False),
                             ('scientific_score', 0.1), ('optimizer_feedback', True), ('replacement_count', 2),
                             ('helper_crash_attempts', ['other']), ('original_record_sha256', '0' * 64)):
            with self.subTest(field=field):
                self.setUp(); self.review[field] = value
                with self.assertRaisesRegex(RuntimeError, 'helper-crash'):
                    self.revision()

    def test_a_replacement_that_never_started_its_estimator_may_be_superseded(self):
        self.review.update(revision='helpercrash-20261025', replacement_count=2,
                           superseded_replacements=[dict(revision='x', estimator_started=False, record_sha256='a' * 64)])
        self.assertEqual(self.revision()['revision'], 'helpercrash-20261025')
        for bad in (dict(estimator_started=True, record_sha256='a' * 64), dict(estimator_started=False)):
            with self.subTest(bad=bad):
                self.setUp()
                self.review.update(replacement_count=2, superseded_replacements=[dict(revision='x', **bad)])
                with self.assertRaisesRegex(RuntimeError, 'helper-crash'):
                    self.revision()
        self.setUp()
        self.review.update(replacement_count=1, superseded_replacements=[dict(revision='x', estimator_started=False, record_sha256='a' * 64)])
        with self.assertRaisesRegex(RuntimeError, 'helper-crash'):
            self.revision()

    def test_pre_estimation_failure_needs_its_own_exact_review(self):
        self.review = dict(classification='pre_estimation_infrastructure_failure', revision='helpercrash-20261025',
                           infrastructure_failed_attempts=[KEY], estimator_started=False, scientific_score=None,
                           optimizer_feedback=False, replacement_count=1)
        self.assertEqual(self.revision()['revision'], 'helpercrash-20261025')
        for field, value in (('estimator_started', True), ('scientific_score', 0.2), ('optimizer_feedback', True),
                             ('replacement_count', 2), ('infrastructure_failed_attempts', [])):
            with self.subTest(field=field):
                review = dict(classification='pre_estimation_infrastructure_failure', revision='helpercrash-20261025',
                              infrastructure_failed_attempts=[KEY], estimator_started=False, scientific_score=None,
                              optimizer_feedback=False, replacement_count=1)
                review[field] = value
                self.review = review
                with self.assertRaisesRegex(RuntimeError, 'pre-estimation'):
                    self.revision()

    def test_finished_records_keep_the_original_rule(self):
        self.record['state'] = 'finished'
        with self.assertRaises(RuntimeError):
            self.revision()

    def test_no_revision_means_none(self):
        self.assertIsNone(policy.reviewed_attempt_revision({}, KEY))


if __name__ == '__main__':
    unittest.main()
