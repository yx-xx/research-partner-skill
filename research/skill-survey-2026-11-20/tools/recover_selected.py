#!/usr/bin/env python3
"""Recover complete source members from timed-out archives, then fetch selected files."""
from __future__ import annotations
import concurrent.futures
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('collector', ROOT / 'tools/collect_sources.py')
collector = importlib.util.module_from_spec(spec); spec.loader.exec_module(collector)
HEADERS = {'User-Agent': 'research-partner-source-survey/1.0'}

def recover():
    pins = json.loads((ROOT / 'discovery/pinned-records.json').read_text())
    recovered = []
    for record in pins:
        repo, branch = record['repository'], record['branch']
        folder = ROOT / 'sources' / (repo.replace('/', '__') + ('__' + branch if branch != 'main' else ''))
        if (folder / 'SNAPSHOT.json').exists():
            continue
        archive = ROOT / 'sources' / ('.' + repo.replace('/', '__') + '-' + branch + '.tar.gz')
        if not archive.exists():
            continue
        folder.mkdir(parents=True, exist_ok=True)
        count = 0
        try:
            with tarfile.open(archive, 'r|gz') as tar:
                full_sha = tar.pax_headers.get('comment', '')
                if len(full_sha) == 40:
                    record['commit'] = full_sha
                for member in tar:
                    if not member.isfile(): continue
                    parts = PurePosixPath(member.name).parts[1:]
                    if not parts or '..' in parts: continue
                    relative = PurePosixPath(*parts)
                    if not collector.selected(relative) or member.size > collector.MAX_FILE: continue
                    data = tar.extractfile(member).read()
                    if len(data) != member.size or b'\x00' in data[:8192]: continue
                    target = folder / str(relative); target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
                    count += 1
        except (EOFError, OSError, tarfile.TarError) as exc:
            record['archive_recovery_stop'] = type(exc).__name__
        record.update({'status': 'selected_sources', 'source_url': f'https://github.com/{repo}', 'selection_policy': 'Complete source members recovered from a partial archive; selected missing files fetched by immutable raw URL. This is a reading subset, not a complete checkout.', 'recovered_files': count})
        recovered.append(record)
        (folder / 'SNAPSHOT.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'phase': 'recovered', 'repo': repo, 'branch': branch, 'files': count, 'skills': len(list(folder.rglob('SKILL.md')))}, ensure_ascii=False), flush=True)
    return recovered

def fetch(record, path):
    repo, branch, sha = record['repository'], record['branch'], record['commit']
    folder = ROOT / 'sources' / (repo.replace('/', '__') + ('__' + branch if branch != 'main' else ''))
    target = folder / path
    if target.exists(): return {'repository': repo, 'path': path, 'status': 'already_present'}
    url = f'https://raw.githubusercontent.com/{repo}/{sha}/{path}'
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=18) as response:
            data = response.read(collector.MAX_FILE + 1)
        if len(data) > collector.MAX_FILE: raise RuntimeError('File exceeds source limit')
        target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
        return {'repository': repo, 'path': path, 'status': 'downloaded', 'source_url': url, 'sha256': hashlib.sha256(data).hexdigest()}
    except Exception as exc:
        return {'repository': repo, 'path': path, 'status': 'unavailable', 'error': str(exc)}

def refresh_manifest():
    path = ROOT / 'manifest.json'
    previous = json.loads(path.read_text())
    records = []
    for metadata in sorted((ROOT / 'sources').glob('*/SNAPSHOT.json')):
        record = json.loads(metadata.read_text()); folder = metadata.parent
        files = []
        for p in sorted(folder.rglob('*')):
            if p.is_file() and p.name != 'SNAPSHOT.json':
                data = p.read_bytes(); files.append({'path': p.relative_to(folder).as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
        record.update({'retained_files': len(files), 'retained_bytes': sum(x['bytes'] for x in files), 'skill_entry_files': [x['path'] for x in files if PurePosixPath(x['path']).name == 'SKILL.md'], 'file_manifest': files})
        metadata.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n'); records.append(record)
    previous['archive_attempt_errors'] = previous.pop('errors', previous.get('archive_attempt_errors', []))
    previous['repositories'] = records
    previous['errors'] = [e for e in previous['archive_attempt_errors'] if not any(e['repository'] == r['repository'] and e['branch'] == r['branch'] for r in records)]
    path.write_text(json.dumps(previous, ensure_ascii=False, indent=2) + '\n')
    return records

if __name__ == '__main__':
    records = recover()
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for record in records:
            futures.append(pool.submit(fetch, record, 'README.md'))
        outcomes = [f.result() for f in concurrent.futures.as_completed(futures)]
    (ROOT / 'discovery/recovery-fetches.json').write_text(json.dumps(outcomes, ensure_ascii=False, indent=2) + '\n')
    all_records = refresh_manifest()
    print(json.dumps({'snapshots': len(all_records), 'repositories': len({r['repository'] for r in all_records}), 'retained_files': sum(r['retained_files'] for r in all_records), 'skill_entries': sum(len(r['skill_entry_files']) for r in all_records)}, ensure_ascii=False), flush=True)
