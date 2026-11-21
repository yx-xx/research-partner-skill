# Reviewer response

A rebuttal or response letter is a second manuscript with its own evidence rules. It wins by resolving the concerns that decide the outcome, with the least text that settles each one.

## Before drafting

Collect the paper, the verbatim reviews with reviewer IDs, and the venue's response rules: length limit in words or characters, whether a revised PDF is allowed, and whether the response is one shared document or a separate thread per reviewer. Ask for the rules if they are missing, because they change the shape of the whole response. Keep the reviews verbatim in a working file so nothing is paraphrased away.

## Break the reviews into concerns

Split each review into atomic concerns and give each an ID such as `R2-C3`, with a short quote as its anchor. For each concern, record:

- **Type.** Misreading of the paper, legitimate weakness, request for new evidence, novelty or nearest-work dispute, assumption or rigor question, clarity, reproducibility, or out of scope.
- **Severity.** Whether it could decide the outcome, affect the score, or is cosmetic.
- **Reviewer position.** Supportive, borderline, or negative, and how much their view is likely to move the decision. Borderline reviewers with addressable concerns deserve the most drafting effort.

Concerns raised by more than one reviewer come first. Group them into two to four shared themes the response can resolve once.

## Three gates

Do not finalize while any concern fails a gate.

| Gate | Every item must map to |
| --- | --- |
| Provenance | Each factual sentence traces to the paper, the reviews, a result or derivation the author has confirmed, or a clearly labeled plan |
| Commitment | Each promise is already done, approved by the author for this response, or framed as future work |
| Coverage | Each concern ends as answered, deliberately deferred with a reason, or flagged as needing the author's input |

Never invent an experiment, number, derivation, citation, or link to fill a gap. When the evidence is thin, say less. A missing result becomes a request to the author or a narrow concession, never a plausible paragraph.

## Choose a response mode per concern

| Mode | Use when | Shape |
| --- | --- | --- |
| Direct clarification | The reviewer misread something the paper states | Point to the exact section, equation, or table, and fix the wording that allowed the misreading |
| Grounded evidence | The concern needs a result | Give the one number or analysis that answers this reviewer's ask, with its conditions |
| Nearest-work delta | Novelty is disputed | Name the closest work and the exact difference in mechanism, assumption, or result |
| Structural distinction | "This reduces to X" | Accept the local reduction, then show the feature the method keeps that X does not, backed by a theorem step, derivation, or measured consequence |
| Assumption hierarchy | Theory assumptions are questioned | Separate the assumptions the result needs from technical conveniences, and say what relaxing each costs |
| Narrow concession | The reviewer is right | Accept the specific point, then state what remains true and why the contribution survives |
| Scope boundary | The request is outside the paper's question | Say why it is outside, and add it to limitations or future work if it is a fair gap |

Pick the minimum sufficient evidence. One figure that maps directly to the reviewer's question beats three that serve other reviewers. If a design choice could look like cherry-picking, such as a threshold, seed protocol, compute matching, or a held-out split, state when and how it was fixed. Say so only when it is true.

## Write each answer

Lead with the direct answer in one sentence. Give the evidence in the next two to four. End with the consequence for the paper and where the manuscript changed: "Section 4.2 now reports both splits." Quantify where the number carries the point.

- **Shared document.** Open with a short note on the shared themes and how they were resolved. Then give numbered per-reviewer answers. Close with what is resolved, what remains, and the case for the contribution. A rough budget is a tenth for the opener, most of the space for answers, and a short close.
- **Per-reviewer threads.** Each response must stand alone. Do not write "see our reply to Reviewer 1". Reuse one canonical setup or metric paragraph across threads so details cannot drift.

Answer supportive reviewers too, briefly. Never set reviewers against each other. Where one praised clarity and another found it unclear, the second reader's confusion is real and worth fixing.

## Tie the response to the manuscript

Keep a revision checklist with one line per manuscript edit, each tagged with its concern ID and commitment state. Every edit the response promises appears on the list, and the list holds nothing the response does not justify. Record concerns that trigger no edit, with a one-line reason, so nothing silently disappears. Check that the revised manuscript delivers each item before the author submits it.

## Before sending

- Count the exact characters or words against the limit. Compress redundancy, then pleasantries, then the opener. Never cut an answer to a decisive concern.
- Read for tone. Flag defensive, evasive, or apologetic phrasing and rewrite it as plain statements of what is true.
- Check that answers to different reviewers do not contradict each other or the paper.
- Read it once as the meta-reviewer would. Mark the paragraph most likely to backfire, and fix or cut it.

## Follow-up rounds

Answer only the new points. Link each to its earlier concern ID or open a new one. Escalate with evidence, not rhetoric. Concede when the reviewer is right. When a reviewer will not move and there is no new evidence, answer once and stop.

Adapted in part from the rebuttal workflow in [ARIS (auto-claude-code-research-in-sleep)](https://github.com/wanshuiyin/auto-claude-code-research-in-sleep), MIT license.
