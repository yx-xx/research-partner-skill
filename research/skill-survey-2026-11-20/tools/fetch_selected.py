#!/usr/bin/env python3
"""Complete selected skill entrypoints and helper files at pinned commits."""
import concurrent.futures
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('recovery', ROOT / 'tools/recover_selected.py')
recovery = importlib.util.module_from_spec(spec); spec.loader.exec_module(recovery)

SELECTION = {
'EvoScientist/EvoSkills': ['skills/' + name + '/SKILL.md' for name in ['research-ideation','research-survey','paper-planning','experiment-pipeline','experiment-craft','experiment-iterative-coder','paper-writing','paper-review','paper-rebuttal','paper-figures','evo-memory','paper-navigator','paper-graph','evomath-tao']] + ['skills/README.md'],
'K-Dense-AI/science-superpowers': ['skills/' + name + '/SKILL.md' for name in ['framing-research-questions','surveying-prior-work','establishing-feasibility-first','designing-the-analysis','preregistering-analysis','subagent-driven-analysis','executing-analysis','dispatching-parallel-investigations','investigating-anomalous-results','verifying-results-before-claiming','requesting-red-team-review','receiving-critical-review','setting-up-reproducible-analysis','reporting-and-archiving-findings','writing-science-skills','using-science-superpowers']],
'K-Dense-AI/scientific-agent-skills': ['skills/' + name + '/SKILL.md' for name in ['paper-lookup','experimental-design','statistical-analysis','statistical-power','scientific-visualization','hypothesis-generation','scientific-critical-thinking','scientific-brainstorming','peer-review','citation-management','sympy','uncertainty-and-units']] + ['skills/experimental-design/scripts/randomization.py','skills/experimental-design/scripts/doe_designs.py','skills/statistical-analysis/scripts/assumption_checks.py'],
'KalarisLabs/research-agent-skills': ['README.md','skills/research-manager/SKILL.md','skills/research-persona/SKILL.md','skills/research-methodology/SKILL.md','skills/office/SKILL.md','skills/verification-before-completion/SKILL.md','skills/scientific-critical-thinking/SKILL.md','skills/statistical-analysis/SKILL.md','skills/paper-lookup/SKILL.md','skills/scientific-writing/SKILL.md','skills/office-agent/office-docs/SKILL.md'],
'wanshuiyin/Auto-claude-code-research-in-sleep': ['docs/SKILLS_CATALOG.md','skills/idea-discovery-robot/SKILL.md','skills/idea-creator/SKILL.md','skills/novelty-check/SKILL.md','skills/research-refine/SKILL.md','skills/research-review/SKILL.md','skills/experiment-bridge/SKILL.md','skills/experiment-audit/SKILL.md','skills/result-to-claim/SKILL.md','skills/paper-writing/SKILL.md','skills/proof-orchestrator/SKILL.md','tools/evidence_check.py'],
'Imbad0202/academic-research-skills': ['VERSION','deep-research/SKILL.md','academic-paper/SKILL.md','academic-paper-reviewer/SKILL.md','academic-pipeline/SKILL.md','experiment-agent/SKILL.md'],
'lllllllama/RigorPilot-Skills': ['skills/ai-research-reproduction/SKILL.md','skills/paper-context-resolver/SKILL.md','skills/novelty-check/SKILL.md','skills/experiment-audit/SKILL.md','skills/research-review/SKILL.md'],
'Google-DeepMind/science-skills': [],
'Orchestra-Research/AI-Research-SKILLs': ['20-ml-paper-writing/ml-paper-writing/SKILL.md','21-research-ideation/brainstorming-research-ideas/SKILL.md','21-research-ideation/creative-thinking-for-research/SKILL.md','22-agent-native-research-artifact/research-manager/SKILL.md','22-agent-native-research-artifact/rigor-reviewer/SKILL.md','18-multimodal/openpi/SKILL.md','18-multimodal/openvla-oft/SKILL.md','18-multimodal/cosmos-policy/SKILL.md'],
'Galaxy-Dawn/claude-scholar': ['skills/research-ideation/SKILL.md','skills/results-analysis/SKILL.md','skills/results-report/SKILL.md','skills/paper-self-review/SKILL.md','skills/citation-verification/SKILL.md'],
}

if __name__ == '__main__':
    records = json.loads((ROOT / 'manifest.json').read_text())['repositories']
    jobs = []
    for record in records:
        for path in SELECTION.get(record['repository'], []): jobs.append((record,path))
        folder = ROOT / 'sources' / (record['repository'].replace('/','__') + ('__'+record['branch'] if record['branch']!='main' else ''))
        if not any(p.name.lower().startswith('license') for p in folder.iterdir() if p.is_file()):
            jobs.extend([(record,'LICENSE'),(record,'LICENSE.md')])
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        futures=[pool.submit(recovery.fetch, record,path) for record,path in jobs]
        for future in concurrent.futures.as_completed(futures):
            result=future.result();results.append(result)
            if result['status']=='unavailable' or len(results)%15==0:
                print(json.dumps({'completed':len(results),'total':len(jobs),'last':result},ensure_ascii=False),flush=True)
    (ROOT/'discovery/selected-fetches.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    records=recovery.refresh_manifest()
    print(json.dumps({'completed':len(results),'downloaded':sum(x['status']=='downloaded' for x in results),'unavailable':sum(x['status']=='unavailable' for x in results),'snapshots':len(records),'skill_entries':sum(len(r['skill_entry_files']) for r in records)},ensure_ascii=False),flush=True)
