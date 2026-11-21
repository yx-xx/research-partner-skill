#!/usr/bin/env python3
"""Fetch bounded source files referenced by inspected entries, without installing skills."""
import concurrent.futures
import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('recovery', ROOT/'tools/recover_selected.py')
recovery=importlib.util.module_from_spec(spec);spec.loader.exec_module(recovery)
SELECTION={
'KalarisLabs/research-agent-skills': ['skills/'+x+'/SKILL.md' for x in ['experimental-design','citation-verification','reproducibility-statement','paper-card','autoresearch','fulltext-acquisition']],
'lllllllama/RigorPilot-Skills': ['skills/'+x+'/SKILL.md' for x in ['minimal-run-and-audit','safe-debug','ai-research-explore','explore-run']]+['skills/ai-research-reproduction/references/agent-runner.md','skills/ai-research-reproduction/references/agent-job.md','skills/ai-research-explore/references/research-campaign-spec.md','references/research-thinking-loop.md'],
'EvoScientist/EvoSkills': ['skills/paper-planning/SKILL.md','skills/paper-figures/scripts/validate_figure.py','skills/experiment-craft/references/experiment-log-template.md'],
'K-Dense-AI/science-superpowers': ['skills/investigating-anomalous-results/SKILL.md','scripts/prereg.sh'],
'WUBING2023/PaperSpine': ['dist/claude/skills/paper-spine/references/'+x+'.md' for x in ['scientific-evidence-ledger','paper-spine-production-protocol','results-validation','scientific-figure-workflow']],
'YufanDu-bjtu/paper-easy-reader': ['references/reader-data.md','scripts/render_reader.py','scripts/check_reader.py'],
'leo-lilinxiao/codex-autoresearch': ['scripts/autoresearch.py'],
}
if __name__=='__main__':
 records=json.loads((ROOT/'manifest.json').read_text())['repositories']
 jobs=[(r,p) for r in records for p in SELECTION.get(r['repository'],[])]
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
  futures=[pool.submit(recovery.fetch,r,p) for r,p in jobs]
  for f in concurrent.futures.as_completed(futures):
   v=f.result();results.append(v)
   print(json.dumps(v,ensure_ascii=False),flush=True)
 (ROOT/'discovery/followup-fetches.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
 recovery.refresh_manifest()
