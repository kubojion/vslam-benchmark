"""Regression for real absolute image links missing inside OpenVINS Docker."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'run'))
from _openvins_image_mounts import image_mounts


class ImageMounts(unittest.TestCase):
    def test_resolves_external_per_file_links_without_writing_sources(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            seq = root / 'prefix'
            for camera in ('cam0', 'cam1'):
                source = root / 'original' / camera
                source.mkdir(parents=True)
                (source / '1.png').write_bytes(b'original-image')
                target = seq / 'mav0' / camera
                (target / 'data').mkdir(parents=True)
                (target / 'data/1.png').symlink_to(source / '1.png')
                (target / 'data.csv').write_text('#timestamp,filename\n100,1.png\n')
            report = image_mounts(seq)
            self.assertEqual(report['directories'], [str(root/'original'/c) for c in ('cam0','cam1')])
            self.assertEqual(report['frames'], {'cam0':1, 'cam1':1})
            self.assertEqual((root/'original/cam0/1.png').read_bytes(), b'original-image')
            (root/'original/cam0/1.png').unlink()
            with self.assertRaises(FileNotFoundError):
                image_mounts(seq)


if __name__ == '__main__':
    unittest.main()
