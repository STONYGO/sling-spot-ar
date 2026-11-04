#!/usr/bin/env python3
"""全テストの実行: ビルド → assert 付きテスト4本 → 既存の探索的テスト（run_legacy.py）。

  cd vendor && npm install && cd ..
  python3 tests/run_all.py            # 失敗があれば終了コード 1
  python3 tests/run_all.py --no-legacy
"""
import pathlib, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
SUITES = ['test_ipad_layout.py', 'test_i18n.py', 'test_offline.py', 'test_dex.py']


def main(args):
    r = subprocess.run([sys.executable, str(ROOT / 'build.py')], cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr); return 1
    results = {}
    for s in SUITES:
        t0 = time.time()
        p = subprocess.run([sys.executable, s], cwd=ROOT / 'tests', capture_output=True, text=True, timeout=1500)
        out = p.stdout.rstrip().split('\n')
        fails = [l for l in out if l.startswith('  FAIL')]
        print(f'##### {s}: {"OK" if p.returncode == 0 else "FAIL"} ({time.time() - t0:.0f}s) {out[-1] if out else ""}')
        for l in fails: print(l)
        if p.returncode and not fails: print(p.stderr[-2000:])
        results[s] = p.returncode == 0
    if '--no-legacy' not in args:
        p = subprocess.run([sys.executable, 'run_legacy.py'], cwd=ROOT / 'tests', capture_output=True, text=True, timeout=1500)
        print(f'##### run_legacy.py: {"OK" if p.returncode == 0 else "FAIL"}  {p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ""}')
        results['legacy'] = p.returncode == 0
    ok = all(results.values())
    print('ALL OK' if ok else f'FAILED: {[k for k, v in results.items() if not v]}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
