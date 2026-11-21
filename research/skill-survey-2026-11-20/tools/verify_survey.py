#!/usr/bin/env python3
"""Check local survey integrity; never execute downloaded third-party code."""
from __future__ import annotations
import ast,csv,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
 errors=[];m=json.loads((ROOT/'manifest.json').read_text());records=m['repositories'];file_checks=0
 for r in records:
  folder=r['repository'].replace('/','__')+('__'+r['branch'] if r['branch']!='main' else '')
  d=ROOT/'sources'/folder
  snapshot=json.loads((d/'SNAPSHOT.json').read_text())
  if snapshot!=r:errors.append(f'Snapshot differs: {folder}')
  if not re.fullmatch('[0-9a-f]{40}',r['commit']):errors.append(f'Non-full commit: {folder}')
  expected={x['path'] for x in r['file_manifest']};actual={str(p.relative_to(d)) for p in d.rglob('*') if p.is_file() and p.name!='SNAPSHOT.json'}
  if actual!=expected:errors.append(f'Inventory differs: {folder}')
  for x in r['file_manifest']:
   p=d/x['path']
   if not p.is_file():errors.append(f'Missing file: {p}');continue
   b=p.read_bytes();file_checks+=1
   if len(b)!=x['bytes'] or hashlib.sha256(b).hexdigest()!=x['sha256']:errors.append(f'Hash or size differs: {p}')
  if r['retained_files']!=len(expected):errors.append(f'File count differs: {folder}')
  skills=sorted(x['path'] for x in r['file_manifest'] if Path(x['path']).name=='SKILL.md')
  if set(skills)!=set(r['skill_entry_files']) or len(skills)!=len(r['skill_entry_files']):errors.append(f'Skill list differs: {folder}')
 reading=json.loads((ROOT/'analysis/reading-log.json').read_text())['records']
 for x in reading:
  p=ROOT/x['file']
  if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=x['sha256']:errors.append(f'Reading record mismatch: {p}')
 with (ROOT/'analysis/skill-index.csv').open(encoding='utf-8',newline='') as f:index=list(csv.DictReader(f))
 if len(index)!=sum(len(r['skill_entry_files']) for r in records):errors.append('Skill index count differs')
 for x in index:
  if not (ROOT/x['file']).is_file():errors.append('Missing indexed skill: '+x['file'])
 docs=[ROOT/'README.md',ROOT/'analysis/reading-notes.md',ROOT/'analysis/adoption-map.md',ROOT/'analysis/catalog.md']
 links=0
 for p in docs:
  for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',p.read_text()):
   if re.match(r'\w+://',target):continue
   dest=target.split('#')[0].strip('<>')
   if not dest:continue
   # verification.json is this check's output, so verify its destination directory here.
   linked=p.parent/dest
   if linked==ROOT/'analysis/verification.json':exists=linked.parent.is_dir()
   else:exists=linked.exists()
   if not exists:errors.append(f'Broken report link in {p.name}: {target}')
   links+=1
 scripts=list((ROOT/'tools').glob('*.py'))
 for p in scripts:
  try:ast.parse(p.read_text(),filename=str(p))
  except SyntaxError as e:errors.append(str(e))
 results={'observed_on':'2026-11-20','timezone':'Asia/Shanghai','status':'passed' if not errors else 'failed','repositories':len({r['repository'] for r in records}),'branch_snapshots':len(records),'full_commit_pins_checked':len(records),'source_files_sha256_checked':file_checks,'skill_index_rows':len(index),'reading_log_records_checked':len(reading),'report_links_checked':links,'own_python_scripts_ast_checked':len(scripts),'partial_archives_remaining':len(list((ROOT/'sources').glob('.*.tar.gz'))),'third_party_runtime_tests_performed':False,'main_skill_edited':False,'errors':errors}
 (ROOT/'analysis/verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(results,ensure_ascii=False,indent=2))
 raise SystemExit(bool(errors))
if __name__=='__main__':main()
