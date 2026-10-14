import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from file_safety import ensure_backup, atomic_save


class FileSafetyTests(unittest.TestCase):
    def test_backup_is_created_once_and_never_replaced(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"campaign.sav"
            path.write_bytes(b"original")
            backup = Path(ensure_backup(path))
            path.write_bytes(b"edited")
            self.assertEqual(ensure_backup(path), str(backup))
            self.assertEqual(backup.read_bytes(), b"original")
            self.assertEqual(path.read_bytes(), b"edited")

    def test_existing_save_as_target_is_preserved_before_replace(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"other.sav"
            path.write_bytes(b"destination original")
            ensure_backup(path)
            save = Mock()
            save.to_bytes.return_value = b"new save"
            atomic_save(save, path)
            self.assertEqual(path.read_bytes(), b"new save")
            self.assertEqual(Path(str(path)+".bak").read_bytes(), b"destination original")
            self.assertEqual(len(list(Path(folder).glob('*.tmp'))), 0)

    def test_serialization_failure_does_not_truncate_destination(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"campaign.sav"
            path.write_bytes(b"original")
            save = Mock()
            save.to_bytes.side_effect = ValueError("bad model")
            with self.assertRaises(ValueError):
                atomic_save(save, path)
            self.assertEqual(path.read_bytes(), b"original")

    def test_replace_failure_leaves_original_and_cleans_temporary(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"campaign.sav"
            path.write_bytes(b"original")
            save = Mock()
            save.to_bytes.return_value = b"new save"
            with patch('file_safety.os.replace', side_effect=PermissionError()):
                with self.assertRaises(PermissionError):
                    atomic_save(save, path)
            self.assertEqual(path.read_bytes(), b"original")
            self.assertEqual(list(Path(folder).glob('*.tmp')), [])


if __name__ == '__main__':
    unittest.main()
