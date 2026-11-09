import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BlotBrowserTests(unittest.TestCase):
    def test_browser_behavior_and_requests(self):
        chrome = os.environ.get('BLOT_CHROME') or shutil.which('chromium') or shutil.which('google-chrome')
        if not chrome:
            chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        self.assertTrue(Path(chrome).is_file(), 'A Chromium browser is required; set BLOT_CHROME')
        node = shutil.which('node')
        self.assertIsNotNone(node, 'Node.js is required for the dependency-free browser bridge')
        with tempfile.TemporaryDirectory(prefix='.blot-browser-', dir=ROOT) as profile:
            process = subprocess.Popen([node, str(ROOT / 'tests/run_blot_browser.cjs'), chrome, profile],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                       start_new_session=True)
            try:
                stdout, stderr = process.communicate(timeout=25)
            finally:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
        self.assertEqual(process.returncode, 0, stdout + stderr)
        self.assertIn('PASS ', stdout, stdout + stderr)

    def test_static_delivery_and_preview(self):
        self.assertEqual(json.loads((ROOT / 'tinkery.preview').read_text()), {
            'command': 'python3 -m http.server 5173 --bind 127.0.0.1 --directory blot',
            'url': 'http://127.0.0.1:5173/',
        })
        self.assertEqual({path.name for path in (ROOT / 'blot').iterdir()},
                         {'index.html', 'style.css', 'game.js', 'ui.js'})
        css = (ROOT / 'blot/style.css').read_text()
        for color in ('#fffcf0', '#100f0f', '#1f7a72'):
            self.assertIn(color, css)
        for path in (ROOT / 'blot').iterdir():
            source = path.read_text()
            for forbidden in ('https://', 'http://', '@import', 'fetch(', 'WebSocket', 'XMLHttpRequest'):
                self.assertNotIn(forbidden, source)


if __name__ == '__main__':
    unittest.main()
