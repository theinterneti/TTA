import subprocess
import sys
import unittest
from pathlib import Path

core_path = Path(__file__).parent.parent / "tools"
if str(core_path) not in sys.path:
    sys.path.insert(0, str(core_path))

from pathlib import Path as _P


class TestAdminCliHttpSmoke(unittest.TestCase):
    def test_cli_help(self):
        # ensure CLI loads
        cli = _P(__file__).parent.parent / 'tools' / 'admin_cli.py'
        self.assertTrue(cli.exists())
        # We don't execute external processes here beyond a --help smoke due to environment constraints
        out = subprocess.run(["python", str(cli), "--help"], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0)
        self.assertIn("Admin CLI", out.stdout)


if __name__ == '__main__':
    unittest.main()

