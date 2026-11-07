#!/usr/bin/env python3
"""Bundle video files into an Aerial (app.orchard.tv) APK under assets/videos/.

The source APK is copied entry-by-entry so every existing file keeps its exact
uncompressed bytes. Existing v1 signature files (META-INF/*.SF, *.RSA/DSA, and
MANIFEST.MF) are dropped because they cannot cover the added entries -- the APK
must be re-signed afterwards.

Usage:
    python bundle_videos.py --apk input.apk --videos ./myvideos --out output-unsigned.apk

Videos are stored with ZIP_STORED (no compression). That keeps the APK small on
disk relative to recompression effort (H.264 barely compresses) and, more
importantly, leaves them addressable with AssetManager.openFd().
"""
from __future__ import annotations

import argparse
import os
import sys
import zipfile

SIG_PREFIXES = ('META-INF/CERT', 'META-INF/AERIAL', 'META-INF/ANDROID')
SIG_EXACT = {'META-INF/MANIFEST.MF'}
VIDEO_EXT = ('.mp4', '.mov', '.mkv', '.webm')


def is_signature(name: str) -> bool:
    if name in SIG_EXACT:
        return True
    if name.startswith(SIG_PREFIXES):
        return True
    # any *.SF / *.RSA / *.DSA / *.EC directly under META-INF
    if name.startswith('META-INF/'):
        rest = name[len('META-INF/'):]
        if '/' not in rest and rest.upper().endswith(('.SF', '.RSA', '.DSA', '.EC')):
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--apk', required=True, help='source APK')
    ap.add_argument('--videos', required=True, help='folder containing video files')
    ap.add_argument('--out', required=True, help='output (unsigned) APK')
    ap.add_argument('--asset-dir', default='assets/videos',
                    help='asset folder inside the APK (default: assets/videos)')
    args = ap.parse_args()

    if not os.path.isfile(args.apk):
        print('error: no such APK: %s' % args.apk, file=sys.stderr)
        return 2
    if not os.path.isdir(args.videos):
        print('error: no such folder: %s' % args.videos, file=sys.stderr)
        return 2

    names = sorted(f for f in os.listdir(args.videos)
                   if f.lower().endswith(VIDEO_EXT)
                   and os.path.isfile(os.path.join(args.videos, f)))
    if not names:
        print('error: no %s files in %s' % ('/'.join(VIDEO_EXT), args.videos),
              file=sys.stderr)
        return 2

    asset_dir = args.asset_dir.strip('/')
    with zipfile.ZipFile(args.apk) as zin:
        with zipfile.ZipFile(args.out, 'w', allowZip64=True) as out:
            out.comment = zin.comment
            copied = dropped = 0
            for info in zin.infolist():
                if is_signature(info.filename):
                    dropped += 1
                    continue
                zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
                zi.compress_type = info.compress_type
                zi.external_attr = info.external_attr
                zi.internal_attr = info.internal_attr
                zi.create_system = info.create_system
                out.writestr(zi, zin.read(info.filename))
                copied += 1

            for name in names:
                data = open(os.path.join(args.videos, name), 'rb').read()
                zi = zipfile.ZipInfo(asset_dir + '/' + name)
                zi.compress_type = zipfile.ZIP_STORED
                zi.external_attr = 0o644 << 16
                out.writestr(zi, data)
                print('  + %-40s %8.1f MB' % (name, len(data) / 1048576))

    print('copied %d entries, dropped %d signature files' % (copied, dropped))
    print('written %s (%.1f MB)' % (args.out, os.path.getsize(args.out) / 1048576))
    print('\nNow sign it -- see scripts/sign_apk.ps1. An APK targeting SDK 30+')
    print('MUST carry a v2 or v3 signature to install on Android 11+.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
