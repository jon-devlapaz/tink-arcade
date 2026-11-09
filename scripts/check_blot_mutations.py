import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
MUTATIONS = (
    ('growth', 'this.radius += 4;', 'this.radius += 0;', 'each word grows radius'),
    ('slowdown', 'this.speed *= 0.87;', 'this.speed *= 1;', 'each word reduces speed'),
    ('contact', 'word.marked = true;', 'word.marked = false;', 'contact marks word'),
    ('drying', 'this.elapsed + dt', 'this.elapsed + 0', 'continuous active drying'),
)


def main():
    for name, original, replacement, expected in MUTATIONS:
        with tempfile.TemporaryDirectory(prefix='.blot-mutation-', dir=ROOT) as directory:
            checkout = pathlib.Path(directory)
            shutil.copytree(ROOT / 'blot', checkout / 'blot')
            (checkout / 'tests').mkdir()
            for filename in ('test_blot_browser.py', 'blot_browser.html', 'blot_browser.js', 'run_blot_browser.cjs'):
                shutil.copy2(ROOT / 'tests' / filename, checkout / 'tests' / filename)
            shutil.copy2(ROOT / 'tinkery.preview', checkout)
            engine = checkout / 'blot/game.js'
            source = engine.read_text()
            if source.count(original) != 1:
                raise RuntimeError('Mutation target must be unique: ' + name)
            engine.write_text(source.replace(original, replacement))
            run = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_blot_browser.py'],
                                 cwd=checkout, capture_output=True, text=True, timeout=30)
            if run.returncode == 0 or expected not in run.stdout + run.stderr:
                print(run.stdout + run.stderr)
                raise AssertionError('Mutation was not caught by its assertion: ' + name)
            print('PASS targeted reversion rejected: ' + name)
    return 0


if __name__ == '__main__':
    sys.exit(main())
