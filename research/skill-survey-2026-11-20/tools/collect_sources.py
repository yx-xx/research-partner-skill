#!/usr/bin/env python3
"""Collect pinned public source snapshots for reading, without installing skills."""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
HEADERS = {"User-Agent": "research-partner-source-survey/1.0"}
MAX_ARCHIVE = 96 * 1024 * 1024
MAX_FILE = 2 * 1024 * 1024
TEXT_SUFFIXES = {'.md', '.mdx', '.rst', '.txt', '.py', '.sh', '.bash', '.json', '.jsonl', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.csv', '.tsv', '.tex', '.bib', '.sty', '.bst', '.cls', '.r', '.R', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.html', '.css', '.svg', '.xml', '.sql', '.cff', '.ipynb', '.lock', '.prompt', '.jinja', '.jinja2', '.j2', '.typ'}
SKIP_DIRS = {'node_modules', '.git', '__pycache__', '.venv', 'venv', '.next', '.pytest_cache', '.ruff_cache'}
NEW_REPOS = ['WUBING2023/PaperSpine', 'c3192095975-ship-it/research-flow', 'lhtrongai/research-direction-check', 'ed20922/gevolve', 'ray-caster/autoresearch-skill', 'leo-lilinxiao/codex-autoresearch', 'scanady/ds-mlops', 'onescience-ai/OneSkills', 'dahliasan/researchskills', 'javimarlop/scientific-paper-skill', 'YufanDu-bjtu/paper-easy-reader', 'Valdemar-Yu/mil-paper-advisor', 'w1-23/scientific-figure', 'shack/scientific-writing-review']

def read_json(url: str):
    last = None
    for attempt in range(2):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=25) as response:
                return json.load(response)
        except Exception as exc:
            last = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code in (403, 404, 429):
                break
    raise last

def metadata():
    result = {}
    for path in sorted((ROOT / 'discovery').glob('*.meta.json')):
        data = json.loads(path.read_text())
        result[data['full_name']] = data
    discovered = {}
    for path in sorted((ROOT / 'discovery').glob('*.json')):
        data = json.loads(path.read_text())
        for item in data.get('response', {}).get('items', []):
            discovered[item['full_name']] = item
    for repo in NEW_REPOS:
        if repo not in discovered:
            raise RuntimeError(f'Missing discovery metadata: {repo}')
        result[repo] = discovered[repo]
    return result

def pin(job):
    repo, branch, meta = job
    cache_path = ROOT / 'discovery' / 'pins.json'
    cached = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    saved = cached.get(repo + '@' + branch)
    if saved:
        sha, date, subject = saved['commit'], saved['commit_date_utc'], saved.get('commit_subject', '')
    else:
        url = f'https://api.github.com/repos/{repo}/branches/{urllib.parse.quote(branch, safe="")}'
        data = read_json(url)['commit']
        sha, date, subject = data['sha'], data['commit']['committer']['date'], data['commit']['message'].splitlines()[0]
    return {'repository': repo, 'branch': branch, 'commit': sha, 'commit_date_utc': date, 'commit_subject': subject, 'created_at_utc': meta['created_at'], 'pushed_at_utc': meta['pushed_at'], 'license_metadata': (meta.get('license') or {}).get('spdx_id'), 'repository_size_kib': meta.get('size'), 'observed_on': '2026-11-20', 'observation_timezone': 'Asia/Shanghai'}

def selected(path: PurePosixPath):
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    name = path.name.lower()
    return path.suffix in TEXT_SUFFIXES or name.startswith(('license', 'notice', 'copying', 'copyright', 'readme')) or name in {'makefile', 'dockerfile', 'justfile', 'procfile', 'version', 'changelog', '.gitignore', '.gitattributes'}

def download(record):
    repo, branch, sha = record['repository'], record['branch'], record['commit']
    folder = ROOT / 'sources' / (repo.replace('/', '__') + ('__' + branch if branch != 'main' else ''))
    if (folder / 'SNAPSHOT.json').exists():
        old = json.loads((folder / 'SNAPSHOT.json').read_text())
        if old.get('commit') == sha and old.get('status') == 'downloaded':
            return old | {'reused': True}
    folder.mkdir(parents=True, exist_ok=True)
    archive = ROOT / 'sources' / ('.' + repo.replace('/', '__') + '-' + branch + '.tar.gz')
    url = f'https://codeload.github.com/{repo}/tar.gz/{sha}'
    result = subprocess.run(['curl', '--fail', '--location', '--max-time', '60', '--silent', '--show-error', '--output', str(archive), url], capture_output=True, text=True, timeout=65)
    if result.returncode:
        # Even a partial tar stream carries the full Git commit in its PAX header.
        try:
            with tarfile.open(archive, 'r|gz') as partial:
                full_sha = partial.pax_headers.get('comment', '')
            if len(full_sha) == 40:
                pin_path = ROOT / 'discovery' / ('resolved-' + repo.replace('/', '__') + '-' + branch + '.json')
                pin_path.write_text(json.dumps(record | {'commit': full_sha}, indent=2))
        except Exception:
            pass
        raise RuntimeError(result.stderr.strip()[:400] or f'curl exit {result.returncode}')
    total = archive.stat().st_size
    if total > MAX_ARCHIVE:
        raise RuntimeError(f'Archive exceeded {MAX_ARCHIVE} bytes')
    digest = hashlib.sha256(archive.read_bytes())
    files, skipped = [], []
    with tarfile.open(archive, 'r:gz') as tar:
        full_sha = tar.pax_headers.get('comment', '')
        if len(full_sha) == 40 and full_sha.startswith(sha):
            record = record | {'commit': full_sha}
        for member in tar:
            if not member.isfile():
                continue
            parts = PurePosixPath(member.name).parts[1:]
            if not parts or any(part in ('..', '') for part in parts):
                continue
            relative = PurePosixPath(*parts)
            if not selected(relative) or member.size > MAX_FILE:
                skipped.append({'path': str(relative), 'bytes': member.size})
                continue
            data = tar.extractfile(member).read()
            if b'\x00' in data[:8192]:
                skipped.append({'path': str(relative), 'bytes': member.size})
                continue
            target = folder / str(relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            files.append({'path': str(relative), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    archive.unlink(missing_ok=True)
    record = record | {'status': 'downloaded', 'source_url': f'https://github.com/{repo}', 'archive_url': url, 'archive_sha256': digest.hexdigest(), 'archive_bytes': total, 'selection_policy': 'Text/source files up to 2 MiB each; non-regular files, binaries, and dependency caches omitted. Snapshot is for reading, not installed.', 'retained_files': len(files), 'retained_bytes': sum(x['bytes'] for x in files), 'skill_entry_files': [x['path'] for x in files if PurePosixPath(x['path']).name == 'SKILL.md'], 'skipped_files': skipped, 'file_manifest': files}
    (folder / 'SNAPSHOT.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    return record

def main():
    metas = metadata()
    jobs = [(repo, meta['default_branch'], meta) for repo, meta in metas.items()]
    jobs.append(('Galaxy-Dawn/claude-scholar', 'codex', metas['Galaxy-Dawn/claude-scholar']))
    pins, errors = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(pin, job): job for job in jobs}
        for future in concurrent.futures.as_completed(futures):
            job = futures[future]
            try:
                record = future.result(); pins.append(record)
                print(json.dumps({'phase': 'pinned', 'repo': record['repository'], 'branch': record['branch'], 'commit': record['commit'][:12], 'date': record['commit_date_utc']}, ensure_ascii=False), flush=True)
            except Exception as exc:
                errors.append({'repository': job[0], 'branch': job[1], 'phase': 'pin', 'error': str(exc)})
                print(json.dumps(errors[-1]), flush=True)
    (ROOT / 'discovery' / 'pinned-records.json').write_text(json.dumps(pins, ensure_ascii=False, indent=2) + '\n')
    pins.sort(key=lambda x: x.get('repository_size_kib') or 0)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(download, record): record for record in pins}
        for future in concurrent.futures.as_completed(futures):
            record = futures[future]
            try:
                result = future.result(); results.append(result)
                print(json.dumps({'phase': 'downloaded', 'repo': result['repository'], 'branch': result['branch'], 'files': result['retained_files'], 'skills': len(result['skill_entry_files']), 'source_mib': round(result['retained_bytes'] / 1048576, 2)}, ensure_ascii=False), flush=True)
            except Exception as exc:
                errors.append({'repository': record['repository'], 'branch': record['branch'], 'phase': 'download', 'error': str(exc)})
                print(json.dumps(errors[-1]), flush=True)
    manifest = {'observed_on': '2026-11-20', 'timezone': 'Asia/Shanghai', 'method': 'GitHub repository discovery, commit pinning, filtered source archive extraction', 'repositories': sorted(results, key=lambda x: (x['repository'].lower(), x['branch'])), 'errors': errors}
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'phase': 'complete', 'snapshots': len(results), 'repositories': len({x['repository'] for x in results}), 'errors': len(errors)}, ensure_ascii=False), flush=True)

if __name__ == '__main__':
    main()
