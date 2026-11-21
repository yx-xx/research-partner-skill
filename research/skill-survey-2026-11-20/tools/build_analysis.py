#!/usr/bin/env python3
"""Build the survey catalog and an explicit static-reading log from pinned local sources."""
from __future__ import annotations
import csv
import hashlib
import importlib.util
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('recovery',ROOT/'tools/recover_selected.py')
REC=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(REC)
# These are reading records, not statements that the programs were executed.
READINGS={
'EvoScientist/EvoSkills': [('skills/experiment-craft/SKILL.md','全文','五步诊断、失败样本、下一步动作'),('skills/evo-memory/SKILL.md','全文','方向记忆与执行策略；有条件复用'),('skills/experiment-pipeline/SKILL.md','重点段落；部分中段未逐行读','分阶段实验与固定阈值风险'),('skills/paper-figures/SKILL.md','全文','图意规格、语义检查、交付状态'),('skills/paper-figures/scripts/validate_figure.py','88–179 行与函数索引','检查器实际只做部分结构/代码模式检查')],
'Galaxy-Dawn/claude-scholar':[('README.md','目录和定位筛选；另与 codex 分支日期比较','平台分支不可等同最新版本')],
'Imbad0202/academic-research-skills':[('README.md','版本、定位、v3.24.4 更新说明（397 行起）','本地3.22.0与上游3.24.4区分；更新不等于已实证'),('academic-pipeline/SKILL.md','入口与路由、完整性检查相关段落','审计分母、生成输出与脚本检查边界')],
'K-Dense-AI/science-superpowers':[('skills/establishing-feasibility-first/SKILL.md','重点段落1–176行；部分输出曾截断','真实规模探测、限制触发、独立正确性检查、人工退出门'),('skills/preregistering-analysis/SKILL.md','重点段落1–215行；部分输出曾截断','事先计划与结果后探索；不泛化为所有研究必须完整预注册'),('skills/preregistering-analysis/prereg.sh','1–42、149–280行的审计逻辑及函数/调用索引','Git首提交、当前内容、结果路径顺序；不证明从未改过或从未看过数据')],
'KalarisLabs/research-agent-skills':[('README.md','能力目录、实际路径和定位','只将独特模块作为新增价值'),('skills/experimental-design/SKILL.md','1–75行与同名文本比较','实验设计选择、伪重复、分块'),('skills/fulltext-acquisition/SKILL.md','流程和状态表重点段落','全文身份与文件名分开；脚本未实测'),('skills/citation-verification/SKILL.md','1–80行重点段落','标识匹配和支持句子分开'),('skills/citation-verification/scripts/verify_citations.py','函数和状态分类索引；非全文','不作运行有效性保证'),('skills/autoresearch/SKILL.md','1–55行','内外双循环；强制后台连续运行不适用'),('skills/reproducibility-statement/SKILL.md','1–65行','可用性声明应指向实际可访问资源')],
'Norman-bury/research-writing-skill':[('skills/evidence-driven-writing/SKILL.md','全文','段落论点、证据与过渡；不照搬硬文件门')],
'TheSyBuilder/research-skills':[('research-idea-finder/SKILL.md','原则、瓶颈、机制与dry-run重点段落；非全文','朴素机制审计、可执行小例子；定量配额和作者引述未验证')],
'UCL-ERL/skills':[('skills/evaluation/experiment-dossier-builder/SKILL.md','全文','远端实验到本地写作的证据交接'),('skills/evaluation/paper-code-consistency-auditor/SKILL.md','全文','配置实际值、激活路径与论文漂移')],
'Valdemar-Yu/mil-paper-advisor':[('SKILL.md','全文','论证链与主动隐藏弱点的冲突')],
'WUBING2023/PaperSpine':[('dist/claude/skills/paper-spine/SKILL.md','主体重点段落，非逐字全文','实际产物进入下游、渲染验收、运行服务依赖'),('dist/claude/skills/paper-spine/references/scientific-evidence-ledger.md','1–100行及后续局部','claim/result/number/source关联；不强制套旧Runner格式'),('dist/claude/skills/paper-spine/references/results-validation.md','1–60行','按科学问题回写结果；明确legacy表格不构成当前流程前提')],
'YufanDu-bjtu/paper-easy-reader':[('SKILL.md','全文','逐句对齐、来源定位、独立覆盖清单'),('scripts/check_reader.py','1–75、95–143行','结构自检不能证明对原论文的覆盖完整性')],
'c3192095975-ship-it/research-flow':[('SKILL.md','入口前100行和目录；非全文','能力槽、路由、停止门'),('references/capability-model.md','1–110行','能力与技能名分离、fallback'),('scripts/discover_skills.py','330–360、388–437行及函数/依赖索引','关键词启发式；ready不是运行探测')],
'ed20922/gevolve':[('skills/gevolve/SKILL.md','全文','固定评价、噪声、假设轨迹和封存测试'),('skills/gevolve/references/garanties-et-limites.md','全文','明确不构成沙箱；约束与保证边界')],
'javimarlop/scientific-paper-skill':[('scientific-paper/SKILL.md','全文','数字账本、跨章节一致性'),('scientific-paper/scripts/check_dois.py','全文','DOI解析与元数据匹配；不能证明支持句子')],
'leo-lilinxiao/codex-autoresearch':[('SKILL.md','全文','控制器拥有测量、停止状态、状态询问不启动运行')],
'lhtrongai/research-direction-check':[('research-direction-check/SKILL.md','主体重点段落，非逐字全文','benchmark×模型×机制查新、混淆表、何种证据解除阻塞')],
'lllllllama/RigorPilot-Skills':[('skills/ai-research-reproduction/SKILL.md','全文','README-first、过程成功与结果复现分开、语义偏离记录'),('skills/paper-context-resolver/SKILL.md','全文','仅补复现关键缺口'),('skills/minimal-run-and-audit/SKILL.md','全文','科学含义变更与可比性报告'),('references/research-thinking-loop.md','全文','一次改变、候选胜出与晋升确认分离'),('skills/ai-research-explore/references/research-campaign-spec.md','1–90行','固定评价合同和预算；不是文献查新保证'),('skills/ai-research-reproduction/references/agent-job.md','主体与保证表重点段落','completed可包含有效失败；状态不明不自动重放')],
'onescience-ai/OneSkills':[('SKILL.md','入口主体','平台资源/专家/执行器分工；重运行时依赖')],
'ray-caster/autoresearch-skill':[('SKILL.md','主体重点段落；中段少量配方未读','外部控制器、噪声与独立确认'),('scripts/driver.py','207–218、567–598、803–857行及状态索引','fresh确认均值、候选哈希、越界改动检查')],
'scanady/ds-mlops':[('.agents/skills/dsflow-autoresearch/SKILL.md','前约100行重点段落；非全文','内部搜索集与正式验证分开')],
'shack/scientific-writing-review':[('skills/scientific-writing-review/SKILL.md','1–65、127–153行及完整章节索引','审稿意见也要反证、保留限定词；语言编辑不等同科研审查'),('skills/scientific-writing-review/references/verifier-brief.md','全文','keep/amend/drop、核对原文和规则')],
'w1-23/scientific-figure':[('SKILL.md','定位、工作流和语义关键词筛选；非全文','可编辑部件、当前版本绑定、工程测试与科学审查分开')],
'wanshuiyin/Auto-claude-code-research-in-sleep':[('skills/experiment-bridge/SKILL.md','1–90行与结构筛选','实验计划到执行、sanity先行、固定模型/GPU部署默认'),('skills/result-to-claim/SKILL.md','1–100行及其证据预检说明','先确定性核对再昂贵审查'),('tools/evidence_check.py','88–125行及函数索引','数字出现检查，不是科学支持关系验证'),('skills/shared-references/evidence-precheck.md','随入口核对用途；非全文','预检与最终科学判决分开')],
}
POSITION={
'EvoScientist/EvoSkills':('优先借鉴','实验诊断与有条件研究记忆'),
'Galaxy-Dawn/claude-scholar':('后续按需','综合研究工具链；注意分支时效'),
'Imbad0202/academic-research-skills':('选择性借鉴','审稿/引用/修订审计；不引入全套审批'),
'K-Dense-AI/claude-scientific-writer':('低优先级','较重的应用/工作流，非轻量主skill替换'),
'K-Dense-AI/science-superpowers':('优先借鉴','可行性探测、软件资源上限和事前约束'),
'K-Dense-AI/scientific-agent-skills':('按需工具库','统计、文献、领域工具；避免重装重叠模块'),
'KalarisLabs/research-agent-skills':('按需补件','全文身份核对、引文核验、复现声明'),
'Norman-bury/research-writing-skill':('选择性借鉴','段落级论点—证据—过渡'),
'Orchestra-Research/AI-Research-SKILLs':('按需工具库','ML工具和领域技能；仓库push不等于主分支新提交'),
'TheSyBuilder/research-skills':('近期重点观察','瓶颈定义、朴素机制审计和可执行小例子'),
'UCL-ERL/skills':('优先借鉴','最匹配机器人/AI；证据交接和论文代码一致性'),
'Valdemar-Yu/mil-paper-advisor':('局部借鉴','方法组件论证衔接；拒绝回避不利结果'),
'VincenzoImp/academic-research-skills':('目录候选','学术流程集合；本轮未深入其实现'),
'WUBING2023/PaperSpine':('选择性借鉴','结果回写、数字来源、实际渲染交付'),
'YufanDu-bjtu/paper-easy-reader':('专题补件','双语深读、来源定位；核对器不证明全文覆盖'),
'c3192095975-ship-it/research-flow':('局部借鉴','能力槽与真实就绪状态；不替代总推进器'),
'dahliasan/researchskills':('领域候选','R/写作协作与远程HPC；本轮目录筛选'),
'ed20922/gevolve':('近期重点观察','评价冻结、噪声、假设轨迹和封存最终测试'),
'google-deepmind/science-skills':('低直接相关','生命科学模型工具用法；非通用科研合作伙伴'),
'javimarlop/scientific-paper-skill':('小而可借鉴','数字账本和跨章节一致性'),
'leo-lilinxiao/codex-autoresearch':('运行器候选','控制器拥有测量和完成状态；宿主依赖需适配'),
'lhtrongai/research-direction-check':('优先借鉴','机器人方向体检、近邻文献与对照边界'),
'lllllllama/RigorPilot-Skills':('优先借鉴','复现身份、科学含义变更、过程/证据/结果多层状态'),
'meiyou666/research-skills-system':('目录候选','中文研究流程集合；本轮未深入其实现'),
'onescience-ai/OneSkills':('领域候选','资源与科学计算平台，依赖较重'),
'ray-caster/autoresearch-skill':('近期重点观察','独立确认复测、控制器判定和失败状态'),
'scanady/ds-mlops':('局部借鉴','搜索/正式验证分层；领域工作流很重'),
'shack/scientific-writing-review':('小而可借鉴','逐条复核审稿意见，降低误报'),
'w1-23/scientific-figure':('专题候选','可编辑SVG部件和版本化视觉验收'),
'wanshuiyin/Auto-claude-code-research-in-sleep':('选择性借鉴','研究合同、结果到主张、确定性预检'),
}
def folder_name(r):
 return r['repository'].replace('/','__')+('__'+r['branch'] if r['branch']!='main' else '')
def shanghai(s):
 return datetime.fromisoformat(s.replace('Z','+00:00')).astimezone(ZoneInfo('Asia/Shanghai')).isoformat() if s else None

def main():
 records=REC.refresh_manifest()
 manifest_path=ROOT/'manifest.json';manifest=json.loads(manifest_path.read_text())
 manifest['method']='GitHub discovery and metadata; immutable commit pinning; filtered text archives or recovered/targeted source subsets; static reading only'
 summary={'repositories':len({r['repository'] for r in records}),'branch_snapshots':len(records),'retained_source_files':sum(r['retained_files'] for r in records),'skill_entry_files':sum(len(r['skill_entry_files']) for r in records),'retained_source_bytes':sum(r['retained_bytes'] for r in records),'filtered_text_archives':sum(r['status']=='downloaded' for r in records),'selected_source_subsets':sum(r['status']=='selected_sources' for r in records)}
 manifest['summary']=summary;manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 catalog=[];reading=[];index=[]
 for r in records:
  repo=r['repository'];folder=folder_name(r);chosen=READINGS.get(repo,[]) if r['branch']!='codex' else [('README.md','分支定位与日期筛选','没有把codex分支当成最新分支')]
  pos,role=POSITION[repo]
  detail=any(x[1]=='全文' for x in chosen)
  depth='重点模块细读（含源码或参考）' if detail else '局部细读/入口筛选' if chosen else '仓库定位/目录筛选，未细读模块'
  cat={k:r.get(k) for k in ['repository','branch','commit','created_at_utc','pushed_at_utc','commit_date_utc','status','retained_files','retained_bytes','license_metadata']}
  cat.update({'created_at_shanghai':shanghai(r.get('created_at_utc')),'selected_head_at_shanghai':shanghai(r.get('commit_date_utc')),'skill_entries':len(r['skill_entry_files']),'reading_depth':depth,'recommendation':pos,'role':role,'local_snapshot':'sources/'+folder+'/SNAPSHOT.json'})
  catalog.append(cat)
  for rel,scope,focus in chosen:
   p=ROOT/'sources'/folder/rel
   if not p.exists(): raise RuntimeError(f'Reading log points to missing source: {p}')
   reading.append({'repository':repo,'branch':r['branch'],'commit':r['commit'],'file':'sources/'+folder+'/'+rel,'scope':scope,'focus':focus,'line_count':len(p.read_text().splitlines()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'runtime_tested':False})
  for rel in r['skill_entry_files']:
   p=ROOT/'sources'/folder/rel;text=p.read_text(errors='replace');lines=text.splitlines()
   name=next((s.split(':',1)[1].strip().strip('"\'') for s in lines[:35] if s.startswith('name:')),p.parent.name)
   desc=next((s.split(':',1)[1].strip() for s in lines[:40] if s.startswith('description:')),'')
   index.append({'repository':repo,'branch':r['branch'],'commit':r['commit'],'skill_name':name,'file':'sources/'+folder+'/'+rel,'lines':len(lines),'description_excerpt':desc[:500],'in_reading_log':any(x[0]==rel for x in chosen)})
 out=ROOT/'analysis';out.mkdir(exist_ok=True)
 (out/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
 (out/'reading-log.json').write_text(json.dumps({'method':'Explicit static reading scope; downloaded does not mean read; scripts not executed. Index extraction is metadata screening only.','observed_on':'2026-11-20','records':reading},ensure_ascii=False,indent=2)+'\n')
 with (out/'skill-index.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(index[0]));w.writeheader();w.writerows(index)
 table=['# 本地来源目录','', '时间以 Asia/Shanghai（UTC+8）显示。创建日是仓库创建日，提交日是所下载分支 HEAD 的提交日；二者均不等于某个 skill 首次发布或最后修改日。`downloaded` 为按类型和大小过滤的文本归档，`selected_sources` 为恢复/补取的源码子集。阅读深度不代表运行有效性。','','| 项目 / 分支 | 创建日 | 所选分支提交日 | 读取范围 | SKILL入口 | 本轮阅读 | 建议用途 |','|---|---|---|---|---:|---|---|']
 for c in catalog:
  f=folder_name(c);created=(c['created_at_shanghai'] or '未知')[:10];head=(c['selected_head_at_shanghai'] or '未知')[:10]
  scope='过滤文本归档' if c['status']=='downloaded' else '选取源码子集'
  table.append(f"| [{c['repository']} / {c['branch']}](../sources/{f}/SNAPSHOT.json) | {created} | {head} | {scope} | {c['skill_entries']} | {c['reading_depth']} | {c['recommendation']}：{c['role']} |")
 table+=['','同名技能的重叠比较见 [same-name-comparison.json](same-name-comparison.json)。所有入口（含分支重复及模板入口）的元数据索引见 [skill-index.csv](skill-index.csv)。逐文件阅读范围见 [reading-log.json](reading-log.json)。']
 (out/'catalog.md').write_text('\n'.join(table)+'\n')
 print(json.dumps(summary,ensure_ascii=False));print('reading_log_files',len(reading))
if __name__=='__main__':main()
