#!/usr/bin/env python3
"""既存の探索的テスト（tests/test.py〜test13.py）を、この環境のビルド成果物に対して実行するランナー。

既存スクリプトは file:///home/claude/proto/... を直書きしているため、実行時だけパスを一時ディレクトリへ
置き換えて実行する（元のスクリプトは変更しない）。test6 用の http.server(8765) も自動で起動する。

  python3 build.py && python3 tests/run_legacy.py [test2 test8 ...] [--locale en]

- 既存スクリプトはブラウザの言語を指定していない（日本語の表示・スポット名を前提に書かれている）ため、
  既定では日本語ロケール（LANGUAGE=ja）でブラウザを起動する。--locale en で英語ロケールにもできる。
- test.py は規約同意（v1.0-beta）より前に書かれたもので、同意前はボタンが無効のため完走しない。
  既定の実行対象から外している（名前を指定すれば実行する）。
判定: スクリプトが例外で落ちたら FAIL。出力は目視確認用にそのまま表示する。
"""
import os, pathlib, re, shutil, subprocess, sys, tempfile, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUILD = ROOT / 'sling-spot-ar-prototype.html'
LEGACY = ['test2', 'test3', 'test4', 'test5', 'test6', 'test7', 'test8', 'test9', 'test10', 'test11', 'test12', 'test13']
OUTDATED = {'test': '規約同意の導入前のテスト（同意チェックが無いため #bDemo が無効のまま）'}


def main(args):
    locale = 'ja'
    if '--locale' in args:
        i = args.index('--locale'); locale = args[i + 1]; args = args[:i] + args[i + 2:]
    if not BUILD.exists():
        sys.exit('build first: python3 build.py')
    names = args or LEGACY
    env = dict(os.environ, LANGUAGE=locale, LANG={'ja': 'ja_JP.UTF-8', 'en': 'en_US.UTF-8'}.get(locale, 'C.UTF-8'))
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='ssar-legacy-'))
    shutil.copy(BUILD, tmp / BUILD.name)
    shutil.copy(ROOT / 'tests' / 'test_photo.jpg', tmp / 'test_photo.jpg')
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', '8765', '--bind', '127.0.0.1'], cwd=tmp,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.8)
    fails = []
    try:
        for n in names:
            if n in OUTDATED and not args:
                continue
            src = (ROOT / 'tests' / f'{n}.py').read_text()
            src = src.replace('/home/claude/proto', str(tmp))
            p = tmp / f'_{n}.py'
            p.write_text(src)
            t0 = time.time()
            r = subprocess.run([sys.executable, str(p)], cwd=tmp, capture_output=True, text=True, timeout=240, env=env)
            ok = r.returncode == 0
            print(f'===== {n}: {"OK" if ok else "FAIL"} ({time.time() - t0:.1f}s)' + (f'  ※{OUTDATED[n]}' if n in OUTDATED else ''))
            print(r.stdout.rstrip())
            if not ok:
                print(r.stderr.rstrip()[-3000:])
                fails.append(n)
            if re.search(r"errs\W+\[[^\]]", r.stdout) or "pageerrors ['" in r.stdout:
                print(f'  !! {n}: page errors were reported')
                fails.append(n + '(pageerror)')
    finally:
        srv.terminate()
    print('locale:', locale, ' screenshots:', tmp)
    print('FAILED:', fails if fails else 'none')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
