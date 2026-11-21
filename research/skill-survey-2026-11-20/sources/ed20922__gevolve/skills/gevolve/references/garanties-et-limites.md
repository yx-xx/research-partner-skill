# What the locks guarantee, and what they do not guarantee

They stop honest mistakes and opportunistic cheating:
- the program cannot print a fake score, rewrite the judge in memory, or read
  the test through the judge (separate process, score read from a file it does not know about);
- once loaded, it can neither write a file, nor read outside the Python installation,
  nor launch a process, nor open the network: an audit hook in
  `executeur.py` refuses it, even if the static check (a blacklist) is bypassed.
  Both
  barriers have been broken through together (`match … case object(gi_frame=f)` for the static
  check, then `_posixsubprocess.fork_exec`, which launches a process without an audit event):
  the static check now reads class patterns, and the hook of evolutions created
  since then refuses to load modules that launch processes, open the network or create
  a sub-interpreter. Two blacklists remain two blacklists;
- an evolved program that does not decide the same way twice is discarded (`determinisme`): string
  hashing and global randomness are fixed in the executor, and each variant is run
  twice on `rapide`;
- the mutator has no terminal;
- modifications to the log, the results, the parents, the rules or the data
  are detected;
- with the witness capture and `verifier_instant()`, what the judge gives the program is
  compared with what was seen live. The locks protect the judge against the program;
  only this capture protects it against badly dated data, and only at the captured instants.

It is not a sandbox.
- **The models' memory**: on past public data, a mutator may
  know the results. Only a test later than its cutoff date, or paper
  trading, neutralises it. A mutator can read a data file, or `base.jsonl`
  and its validation scores, with Read: its instruction forbids it, nothing prevents it. What it
  might hard-code, `voir` helps to spot. And someone who has a
  terminal can rewrite everything, including the state outside the folder. The final guarantee remains
  the sealed test, with a threshold fixed in advance.
