# Rules: structure and organization

How to read the rules:

- Each rule opens with its name in bold. Cite that name and its section number in every finding, for example "Old before new (1.11)".
- *Check:* says how to test the text where the test is not obvious.
- The letters in brackets name the sources behind a rule. Use them to point the student to further reading. A rule without letters has no source; the supervisor added it.
- The rules are settled. Where the sources disagree, the rule states the position this review takes. Do not replace it with a source's different position or with your own preference.

Sources:

- **H**: Hack, "Writing a Thesis/Paper"
- **D**: Dreyer, "How to Write Papers So People Can Read Them"
- **PJ**: Peyton Jones, "How to write a great research paper"
- **W**: Williams and Bizup, *Style: Lessons in Clarity and Grace*
- **Z**: Zobel, *Writing for Computer Science*
- **S**: Strunk and White, *The Elements of Style*, 4th edition
- **E**: Berger, Blackburn, Hauswirth and Hicks, *SIGPLAN Empirical Evaluation Checklist*, 2018

Sections:

- 1.1 The document as a whole
- 1.2 Abstract
- 1.3 Introduction
- 1.4 Background
- 1.5 Main part
- 1.6 Evaluation
- 1.7 Related work
- 1.8 Conclusion
- 1.9 Chapters and sections
- 1.10 Paragraphs
- 1.11 Flow between sentences
- 1.12 Thesis versus paper

## Premises

1. **The reader has little time and does not know what the author knows.** The author knows the details and wants to report them. The reader does not yet know what the work is for. [H D W]
2. **One pattern holds at every scale, from the sentence to the document.** Familiar, short and general material comes first; new, long and detailed material comes last. The point is stated first and then supported. [W D PJ]
3. **A text is an argument for a skeptical reader.** It says early what it claims and backs each claim with evidence. [Z PJ]
4. **The principles are diagnostics, not laws.** They explain why a passage is hard to follow. A passage that reads well needs no change, even if it departs from one. [W Z]
5. **Careless presentation makes readers doubt the work itself.** [H Z W]

## 1 Structure and organization

### 1.1 The document as a whole

- **One aim, stated.** The text has one research question or key idea, and a sentence that states it outright. Several contributions are linked by an explicit overall goal. *Check:* quote the sentence that states the question and the one that states the contribution. [PJ Z]
- **An argument, not a chronicle.** The order follows the logic of the argument, not the history of the project. A failed attempt appears only as evidence for a claim. *Check:* look for "first we tried …, then we realized …" and for chapters organized by project phase. [PJ W Z]
- **A research report, not a build report.** The text says what was found out and why it matters. It describes what was built only as far as the question requires. [Z PJ]
- **The expected parts.** Abstract and introduction open the document, and a conclusion closes it. Between them come background (optional), the main part, an evaluation (unless the work is purely theoretical) and related work. [H Z]
- **Top-down, in layers.** Every mechanism gets a high-level explanation before its details, and no section needs details that come later. [D PJ]
- **Every claim has evidence.** Each claim in the abstract and introduction is supported in the body and taken up again in the conclusion. *Check:* build a claim-to-evidence table. Flag claims without evidence, chapters that support no claim, and conclusions without a matching result. [PJ Z H]
- **Survives skimming.** Introduction and conclusion together tell an outsider what the work is about and how well it worked. *Check:* read only these two parts, then state the problem, the contribution and the result. [H Z PJ]
- **Written for a defined reader.** The text contains neither unexplained specialist terms nor pages of textbook basics. Each part has its own reader, and what the part may assume and must explain depends on that reader. A concept that this reader does not know and the text does not explain is a gap. Pages spent on what this reader knows are a fault as well; a few lines that fix the terminology are not. *Check* for the main part of a thesis: could the author, on the day the work began, have followed this passage? [H Z D]

  | Part | Thesis | Paper |
  |---|---|---|
  | Abstract | Anyone deciding whether to read on | An expert reviewer who chooses among hundreds of submissions |
  | Introduction and conclusion | Anyone with a bachelor's degree in the same discipline, possibly from another field | The same |
  | Conclusion, in addition | Someone who wants to apply the technique | The same |
  | Key ideas or overview | As the introduction, in more technical depth | The same |
  | Background | The second reviewer | The typical reader of the venue |
  | Main part and evaluation | The second reviewer, having read the background | The typical reader of the venue |
  | Related work | The second reviewer | An expert in the field |

  The second reviewer is a member of the same discipline from another subfield, for example a computer scientist who works in a different area. They know the standard curriculum of the degree thoroughly, but not the concepts, tools and jargon of the subfield. The typical reader of the venue is a researcher in the area of the conference or journal who does not work on this problem.

- **Proportion.** Space is proportional to importance, every passage serves the stated aim, and nothing is covered twice. [Z W H]
- **Title.** Specific, accurate about scope and outcome, no hype. [Z]

### 1.2 Abstract

- **Five moves, in order:** context and motivation, the specific problem or gap, the approach, the results, and what follows from them. *Check:* assign each sentence to a move. Flag missing moves and background that serves none. [H D PJ Z]
- **It does not open with the contribution.** The first sentence gives context, not "We present X". [D]
- **Specific and self-contained.** It names the technique and gives the number. It contains no citations, undefined acronyms, mathematics or outline of the document. The introduction does not depend on it. [Z]
- **Length.** About five sentences for a paper. A thesis abstract may be longer but remains a brief summary. [H PJ D Z]

### 1.3 Introduction

- **Four moves, in order:** motivation, problem, contribution, results. The contributions list carries the last two together. *Check:* label each paragraph with a move. Flag missing moves, moves out of order, and paragraphs that fit none, such as a literature survey, project history or general background. The outline paragraph of the structure overview is exempt. [H PJ D W]
- **Opening.** Brief context that is specific to the work, then the turn to the problem. Flag an opening that would fit any thesis in the area ("X is increasingly important") and "In this thesis we …" before any context. A thesis motivates briefly and at a high level; a paper for a specialized venue needs little general motivation. [PJ D Z H W]
- **The problem has a cost.** After stating the gap, the text answers "so what?": what stays unanswered or impossible. [W PJ]
- **A concrete example** shows the problem and returns when the approach is presented. [H PJ D]
- **Contributions are explicit and refutable.** They are stated as a list, preferably bulleted, that closes the introduction; only an outline paragraph may follow it. Each item says what is new and how it improves on the state of the art, states its result, could turn out false, and points to the chapter with the evidence. Flag "we describe X" and "we study Y". [H PJ W E]
- **Results are reported.** The introduction says how well the work succeeded, with numbers where there is an evaluation. The results stand in the items of the contributions list and need no paragraph of their own. Nothing is held back for suspense. [H Z W]
- **Old versus new.** Each assertion is recognizable as cited prior knowledge or as a result of this work. [Z]
- **Prior work only to establish the gap.** A sentence or two, at most a paragraph. Citations attach to specific techniques. [H D PJ]
- **No heavy machinery.** No formal notation, undefined jargon or detailed literature discussion. [Z H]
- **Structure overview.** The introduction contains a short description of the document's structure. This is either an outline paragraph or a contributions list whose forward references cover the document comprehensively. [PJ Z]

### 1.4 Background

- **Only what the later text needs, at the depth it needs.** The material is standard in the field but beyond an introductory course. *Check:* for each background section, find where it is used. Flag material that is never used, textbook basics, concepts the main part uses but nobody introduced, and the author's own contribution hidden in the background. [H D Z]
- **Thesis versus paper.** A background chapter is normal in a thesis. A paper preferably keeps background minimal and at the point of use. A background section is acceptable in a paper that depends on terminology outside the expertise of its typical reader. [D H Z]
- **Difficult concepts are motivated or recalled at the point of use.** [D]
- **Background is not related work.** Background is what the reader needs to understand the contribution. Related work is the alternatives the contribution competes with. [Z]

### 1.5 Main part

- **It opens with an overview** that guides the reader through the findings. [H]
- **Key ideas before details.** The reader meets the main idea in plain language and on a concrete example before the first formal definition. This happens in an overview chapter or at the start of each technical chapter. *Check:* could a reader stop before the details and still state the idea? [D PJ]
- **Incremental build-up.** A complicated system or model is not presented in one step. A simplified version comes first, then one extension at a time, each with a motivation. [D]
- **Examples before the general case.** Central abstractions come with a concrete instance, and each example illustrates one concept. [PJ D Z]
- **Why, not only what.** Each design decision has a stated reason and, where relevant, the rejected alternatives. Each definition, theorem or algorithm is introduced with what it is needed for. [Z]
- **The line of thought is laid out.** Each step follows from what is already on the page. Flag "obviously" and "clearly" without a reason, and steps that only the author can fill in. [H Z]
- **Precise, complete, reproducible.** A competent reader could redo the work. Flag missing parameters, skipped steps and promotional language. [H Z]
- **Bulky detail goes to the appendix.** Every main result, and enough justification to judge it, stays in the body. [D Z PJ]

### 1.6 Evaluation

The review checks what the text says about the evaluation. It does not judge whether the experiments are well designed or sufficient. The rules for describing the setup and for reporting results are in Section 3.2.

- **The elements are present.** The evaluation says which claim or question each experiment tests, describes the setup, presents the results and discusses them. Fixed headings such as "Methods", "Results" and "Discussion" are not required. *Check:* for each experiment, find the sentence that says what it is meant to show. [Z]
- **Results are selected.** The results that carry the argument get a graph or table and a discussion. The others are reported in a line or two, and bulky ones go to the appendix. [Z]
- **A side experiment gets a sentence or two.** A preliminary or dead-end experiment that explains a design decision is sketched with its outcome, not reported in full. [Z]

### 1.7 Related work

- **It compares; it does not list.** For each work or group of works, the text says what it does and how the present work differs from it or builds on it. It is organized by topic, not paper by paper. Flag "A did X. B did Y." [H D Z PJ]
- **In one place.** The comparison is not scattered over the chapters. [Z D]
- **Position.** In a paper it comes after the main part and before the conclusion. In a thesis it may come early or late. [D PJ H Z]
- **Fair and generous.** The text says what each work achieved. Criticism is reasoned and never dismissive. The comparison is with the current state of the art, not with a straw man. [PJ Z D]
- **Adequate.** Directly related work is covered, the seminal papers are cited, and the sources are current. Textbook notions need no citation. [H Z]

### 1.8 Conclusion

- **Content.** It restates contributions and results concretely and in terms consistent with the introduction. It says what others can expect when they apply the technique, and it names limitations and future work. [H W Z E]
- **Brief, with no new material.** It is still more than a repetition of the abstract or a walk through the chapters. [PJ H W Z]

### 1.9 Chapters and sections

- **Framed.** Each chapter and section opens with a short passage that says what it establishes and how it connects to what came before. It does not start in the details or directly with a subheading. A thesis chapter also closes by saying what was established. *Check:* read only the openings in sequence. They should give a coherent outline of the document. [W Z H D]
- **A visible ordering principle,** such as problem then solution, general to specific, or simple to complex. Parallel sections (one per experiment or per method) follow the same template. *Check:* name the principle. [W Z]
- **Headings show the logic** when read as a table of contents. They are specific to the work, parallel in wording and limited to a few levels. [Z W]
- **The reader's state of knowledge suffices.** At every point, what the reader has learned so far is enough for what follows. No term is used before it is defined. [Z D H]
- **Key terms recur.** The concepts announced in the introduction and in section openings reappear in headings and body under the same names. [W]

### 1.10 Paragraphs

- **One point per paragraph,** stated in one sentence at or near the beginning. The other sentences support it. *Check:* mark the point sentence of each paragraph, and read the first sentences of a section's paragraphs as its outline. Flag paragraphs whose point cannot be located, that carry several topics, or that begin on one topic and end on another. [D W Z S]
- **Every paragraph has a role** relative to the point of its section: background, sub-point, reason, evidence, method or another view. [W D]
- **Length is a signal, not a fault.** A one-sentence paragraph that is not a transition usually lacks support for its point. A paragraph that fills most of a page usually holds several points, and a run of one- or two-sentence paragraphs usually spreads one point over several. *Check:* where the length stands out, apply the one-point test. [S]
- **Lists and asides.** A list is used only for content that is important and naturally enumerable, with grammatically parallel items. Footnotes and parentheses hold nothing essential. [Z PJ]

### 1.11 Flow between sentences

- **Old before new.** A sentence begins with information the reader already has and ends with the new information. A new term first appears at the end of a sentence, and the next sentence picks it up. *Check:* look at the opening words of each sentence. Flag sentences that open with a term the reader has not seen. [D W]
- **Consistent topics.** Across a paragraph, the sentence subjects name a small set of related things. Subjects are not varied for variety. [W]
- **Connectives state real relations.** "Therefore", "however" and "thus" appear only where that relation holds. Additive connectives ("moreover", "furthermore") are rare, and connectives do not open several sentences in a row. [W Z]
- **Paragraph breaks.** A new paragraph names its subject again instead of opening with "This" or "It". [Z]

### 1.12 Thesis versus paper

| Aspect | Thesis | Paper |
|---|---|---|
| Abstract | May be longer | About five sentences |
| Motivation | Brief and high-level, but present | Little general motivation |
| Background | Own chapter, enough for the second reviewer | Preferably minimal and at the point of use; a section of its own if the paper needs terminology outside the typical reader's expertise |
| Key ideas | Overview chapter or chapter openings | A section between introduction and main part |
| Related work | Early or late | After the main part |
| What is judged | The candidate's competence, shown by critical analysis of the results [Z] | The contribution |
