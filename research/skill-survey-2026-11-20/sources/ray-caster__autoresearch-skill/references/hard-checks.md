# Hard checks (gates in the evaluator)

Read this when writing the evaluator (Setup step 4), or when the morning diff shows gaming (Report step 5).
Each check runs inside `eval_cmd`, before the score. If it fails, print the reason and set `"pass": false`.
The files that define a check (statements, properties, allowed lists, test data) must **not** be
`editable`: the driver's tamper check then voids any round that weakens them.

**Simple checks first**: they're cheap and catch most gaming.
- **Copying test data:** fail if an editable file contains long word-for-word chunks of eval cases (prompt
  optimisation), or hard-coded expected answers.
- **Allowed values:** fail on any value outside the allowed list or range (E24 series, part stock, parameter
  bounds), instead of asking for it in program.md.
- **Banned patterns:** use a regex or AST check on the editable files for things that look like shortcuts
  (`if input == <test case>`, disabled assertions, `try: ... except: pass`, reading the held-out path).
- **Complexity:** cap the editable files' size or how much they may grow, if "simpler wins ties" matters.
- **Existing tests, linters and type checkers:** run them as gates, never as the score.

**Ready-made gates:** copy `templates/checks/lean_gate.py` and `templates/checks/tla_gate.py` into
`<project>/autoresearch/checks/` (tracked, not editable). Each is stdlib Python: call
`lean_gate(dir, theorem)` or `tla_gate(dir, module, cfg)` from evaluate.py, get `(ok, reason)`, print the
reason and set `"pass": ok`. Installed on this machine: Lean 4.36 / Lake 5 via elan (`~/.elan/bin`),
Java 21 (`~/tools/jre`) and `~/tools/tla2tools.jar`; the helpers find them there.

**Lean: proven correctness as a gate.** Use it when the loop optimises an algorithm whose correctness
can be stated as a theorem (sorting, a numeric routine, a scheduler). The score is something else
(speed, size), and the proof must still compile after every change.
- Setup: `lake new <name>`, or a `lakefile.toml` with one `lean_lib`. A check is `lake build`.
- Layout, so the agent can't weaken the claim:
  - `Spec.lean` (protected) defines the claim, e.g. `def Claim (f : List Nat → List Nat) : Prop := ...`.
  - `Impl.lean` (editable) holds the code and its proof, `theorem claim_proof : Spec.Claim f`.
  - `Check.lean` (protected) contains `example : Spec.Claim Impl.f := Impl.claim_proof` and
    `#print axioms Impl.claim_proof`. A weakened theorem then fails the build (type mismatch).
- `lean_gate` passes only if `lake build` exits 0 AND the `#print axioms` line is present AND every axiom
  is one of `propext`, `Classical.choice`, `Quot.sound`. Tested: `sorry` (shows as `sorryAx`), a smuggled
  `axiom`, and `native_decide` (an auxiliary `..._native.native_decide.ax_*` axiom) all **build with exit
  code 0**, so the exit code alone is not a gate; the axiom check rejects all three. Lake replays the
  axiom line from cache, so repeated evals of an unchanged file still pass.
- Limits:
  - It proves the claim as written in Spec.lean, so review Spec.lean yourself: a wrong claim gets proven
    happily.
  - It's about the Lean code. If the real code is in another language, the proof covers only a model of
    it.

**TLA+: design checked for every interleaving.** Use it when the loop optimises a protocol or state
machine: sync, retries, locking, notifications across devices. The score is e.g. messages or latency
from a simulation; TLC is the gate.
- A check is `java -cp tla2tools.jar tlc2.TLC -workers auto -metadir <temp dir> -config Model.cfg Props.tla`.
  `-metadir` outside the repo matters: otherwise TLC writes a `states/` folder into the project.
- Layout (three modules):
  - `Base.tla` (protected): `CONSTANT`s, `VARIABLES`, `vars`.
  - `Protocol.tla` (editable): `EXTENDS Base`, defines only the protocol's actions (e.g. `Proto == ...`).
  - `Props.tla` (protected): `EXTENDS Protocol`, and defines `Init`, the **environment's** actions (the
    user, the network), `Next`, `Spec` with its fairness, the invariants and the liveness properties.
  - `Model.cfg` (protected): bounds (e.g. `CONSTANT Devices = {d1, d2}`), `SPECIFICATION Spec`, `INVARIANT`,
    `PROPERTY`.
- Keep the environment, `Spec` and fairness in the protected file, include a liveness property, and keep
  TLC's deadlock check on. Otherwise "do nothing" is a perfectly safe protocol and the loop will find it.
  Tested: a `Proto == FALSE` candidate is caught as a deadlock, and with `-deadlock` as a liveness
  violation.
- `tla_gate` passes only if TLC exits 0 AND prints `Model checking completed. No error has been found.`
  TLC's exit codes (tested, tla2tools 1.8): 11 deadlock, 12 invariant violated, 13 liveness violated. On
  failure the reason includes TLC's counterexample trace (each state, step by step), which is exactly the
  feedback the next round needs.
- Limits:
  - It checks the design, not your implementation.
  - It's bounded: passing with 3 devices usually, not always, means passing with 10. Use larger bounds in
    `holdout_cmd`.

Neither tool helps when the score itself is statistical (Sharpe, prompt accuracy): you can't prove
those properties.
