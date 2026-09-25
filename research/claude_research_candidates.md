# Three candidate experiments on learners that choose experiments: independent assessment (draft)

**Status: DRAFT, pending independent Codex review.** Author: Claude (Opus 5.5). This round was read and search only: nothing was implemented, run or written, and no git commands were used. v1/v2 are treated as frozen references. Seeds 0..4 and 100..119 are inspected development data. Reserved seeds 1000..1049 stay unused.

## 0. Can the probe scripts be recovered?

**Yes, as exact text.** In the earlier session I created three scripts with a quoted heredoc (`cat > …/scratchpad/aN.py <<'EOF'`), so the shell substituted nothing and the file contents equal the command text. The original paths were `/private/tmp/claude-501/-Users-marmon-Documents-Projects-artificial-scientist/917f4e50-0fc8-4801-934b-58c6782e9622/scratchpad/{a1,a2,a3}.py`. That scratchpad is no longer available to me, so **I cannot confirm the files still exist on disk.** The appendix copies the text verbatim from my session transcript. It is not a reconstruction.

Run conditions:
- Launched from the repository root, at clean commit `7660d32`, with Python 3.9.6.
- a1 covers §§1–2.1 of the earlier report, a2 covers §§2.2–2.3, and a3 covers §2.4.
- The first launch of a2 failed with `timeout: command not found` before running anything. It was re-run unchanged without `timeout`.

Two notes on interpreting the earlier probes:
- **a3 did not record whether v2 was sparse before tick 1200.** Checks fall at ticks 1216, 1280 and 1344, so possible delays are 16, 80 or 144. The observed minimum was 80, so no world had contracted by 1216. v2 only changes at checks, and the last check before the return was at 1152. So all 80 worlds were sparse at the return. This is an inference; Codex's reconstruction records the state directly.
- **Correction to my earlier wording.** The correct-lag expert's roughly 0.01-nat advantage over the mixture is an **empirical reference comparison**. It is not an upper bound on every possible selector. A selector that switches experts over time could in principle beat a static correct-lag expert. "Bounds what a perfect hard selector … could gain" overstated it.

## 1. A shared, identifiable test world

All three candidates use one world family chosen to make actions necessary:
- **World:** three observed binary variables. The structure is one of the 25 DAGs on 3 labeled nodes, with conditional probability tables (CPTs) drawn from a family prior.
- **Actions** (7 per step, each costing one step and returning one joint 3-bit sample): observe passively, or set one variable to a value with do(X_i = v), for i = 1..3 and v ∈ {0,1}.
- **Evaluation:** exact, independent of the policy. It is the mean KL divergence between the true distribution and the learner's posterior predictive across all 7 regimes, computed from evaluator-only CPTs at fixed budgets N.
- **Learner:** exact Bayes over the 25 DAGs with Dirichlet CPTs. The intervened node's likelihood is dropped (the standard Cooper–Yoo treatment, not re-verified this session). This is a known model, not a new learner.
- **Seeds:** a new generator with a fresh development range, e.g. 200..249. Held-out seeds are chosen later and must differ from 0..4, 100..119 and 1000..1049.

## 2. Candidates

### E1. Does choosing interventions by expected information gain beat random interventions? (Replication and harness validation)

- **Question.** At N ∈ {5, 10, 20, 40}, does picking the action with the highest expected information gain about the graph reduce the 7-regime KL compared with random interventions and passive observation? How does the gap depend on mechanism strength?
- **Closest work.** Tong & Koller (2001) actively choose interventions and beat random sampling and random queries. ABCI (Toth et al., 2022) chooses interventions to target a specific query and beats observational and random designs. CAASL (2024) amortizes the design policy. The problem is solved in principle.
- **Unresolved distinction.** None methodological. The only open item is mapping where the advantage disappears in this harness.
- **Strongest counterargument.** When the learner's prior equals the generator's prior, Bayes-optimal inference plus information-gain design is expected to win. A positive result would only confirm the code.
- **Baselines** (all use the same exact learner and N samples):
  - passive observation only;
  - random intervention;
  - round-robin over the 7 actions;
  - an oracle that knows the true DAG and learns only the CPTs, labeled privileged.
  - Cost per step of the information-gain policy is disclosed.
- **Thresholds, set before measuring:**
  - Pass: information gain beats random intervention by ≥ 0.02 nats at N = 20, with a 95% seed-bootstrap interval excluding 0.
  - Harness validity: passive observation is worse than both by ≥ 0.02 nats at N = 40.
- **Falsifier.** If random intervention comes within 0.02 nats of information gain in every regime, report that random interventions suffice here.
- **Pre-check, no policy code.**
  - (a) Compute analytically the loss that remains with infinite passive data, where the posterior spreads over each Markov-equivalence class. If it is < 0.02 nats, interventions cannot matter, so revise the family.
  - (b) Monte Carlo the exact learner under random design against the privileged oracle at N = 20. If the gap is < 0.02 nats, there is no headroom left for design.
- **Verdict: TEST, as a replication only, and only as the control harness for E3.** It has no novelty value on its own.

### E2. Does transfer across worlds help through experiment choice, or only through inference? (Evaluation)

- **Question.** Worlds come from a family with shared structure, e.g. edge probabilities and a range of mechanism strengths. A prior is estimated from K ∈ {5, 20} previous worlds. Does it reduce loss in a new world at fixed N? The key factorial is 2×2: prior used for inference {broad, transferred} × prior used for design {broad, transferred}. The question is whether the benefit comes from the design channel or the inference channel, and what it costs when the new world comes from a shifted family.
- **Closest work.**
  - Hierarchical Bayesian transfer in sequential decisions (Wilson, Fern & Tadepalli, 2012).
  - Amortized design policies (CAASL 2024) and test-time-refined semi-amortized policies (Step-DAD, ICML 2025).
  - ACE (2026), which learns intervention strategies but by its own account does not evaluate on held-out systems.
- **Unresolved distinction.** The design-versus-inference split. I found no explicit decomposition. That is weak evidence, not novelty.
- **Strongest counterargument.** With exact Bayes, the within-family gain from a transferred prior is just the value of prior knowledge, and the shifted-family penalty is ordinary prior misspecification. Both are expected.
- **Baselines.**
  - A fresh broad prior.
  - The true family prior, as a privileged upper reference.
  - A transferred prior applied to inference only.
- **Budgets.** Each world gets the same N. Report the K×N earlier observations explicitly. The fresh control sees none of them.
- **Thresholds.** The design-channel effect, measured with the inference prior held fixed, must be ≥ 0.02 nats at N = 10 with an interval excluding 0. The shift penalty is reported at every K.
- **Falsifier.** If the design effect is < 0.02 nats, transfer acts through inference only. That is standard hierarchical Bayes, so stop.
- **Pre-check, exact learner under random design.**
  - (a) Headroom at N = 10 between the true family prior and the broad prior. If it is < 0.02 nats, reject.
  - (b) Along simulated histories, how often information-gain design under the broad prior and under the family prior pick the same action. If they agree on ≥ 90% of steps, drop the design factor.
- **Verdict: REVISE.** Defer until E3's harness exists. Reject if either pre-check fails.

### E3. Can the learner find out, by experimenting, that its model class is wrong? (Evaluation; closest to "awareness of limits")

- **Question.** Some worlds contain a hidden binary confounder U → X1, X2, which lies outside the no-confounder class. Can the learner detect that at a fixed false-alarm rate, using an anytime-valid test, within N ≤ 400 samples? Does a falsification-seeking design detect sooner than information gain aimed at identification, random intervention, or passive observation?
- **Why actions are necessary (reasoning, not yet verified).** The complete DAG is saturated over three binary variables, so passive data can never reject the class. Rejection needs observational data plus interventions on both confounded variables (or interventions on both).
- **Closest work.**
  - Active hypothesis testing by sequential design (Chernoff, 1959).
  - Anytime-valid e-processes (Ramdas et al., 2023). Running-MLE / split likelihood-ratio tests from universal inference (Wasserman, Ramdas & Balakrishnan).
  - Learning model discrepancy through Bayesian experimental design (Yang et al., 2025).
  - A limit result: distribution-free falsification of a model class is impossible (Müller, Luo & Barber, 2025). E3 avoids that result only because it assumes a finite discrete class and interventions. This must not be generalized.
- **Unresolved distinction.** Measuring, under one shared budget, the trade-off between identification loss and detection time. A single policy may have to serve both goals. Label this evaluation, not method.
- **Strongest counterargument.** This is Chernoff-style testing plus a textbook interventional test for confounding. It is also not clear that a tiny discrete case teaches anything about larger worlds.
- **Detection statistic** (validity must be unit-tested under adaptive action choice):
  - Numerator: predictive probability under a saturated per-regime Dirichlet model.
  - Denominator: the maximum likelihood over the in-class models on all data so far. Each DAG has closed-form counts.
- **Baselines** (all get equal N):
  - passive observation;
  - random intervention;
  - round-robin;
  - E1's information-gain policy;
  - uniform sampling over observation, do(X1) and do(X2), which assumes knowledge of which variables are confounded and is labeled privileged.
- **Thresholds, set before measuring:**
  - Correctness: false alarms on in-class worlds ≤ α = 0.05.
  - Detectability: power ≥ 0.8 for the best non-privileged policy by N = 400.
  - Active-design question: the targeted policy's median detection time ≤ 0.75× random intervention's.
- **Falsifier.** If power is < 0.8 for every non-privileged policy, or the targeted policy is > 0.75× random, report a negative result.
- **Pre-check, exact calculation with no learner or policy.**
  - For each confounded world, compute D*(w): the minimum over in-class DAGs of Σ_a w_a·KL(P_a ‖ P_a^m) for a fixed action mix w. This is closed form, because each node's CPT is fit to the regimes in which it is not intervened.
  - Require N·D* ≥ log(1/α) + R_N, where R_N is the Dirichlet/KT regret of the numerator: about Σ_regimes (7/2)·log n_r, which is tens of nats. Otherwise no policy can detect within the budget, so strengthen confounding or reject.
  - Check D*(passive) = 0, which confirms actions are necessary.
  - If the best action mix gives D* less than 1.33× the uniform-over-7 D*, active design has no headroom. Keep only the detection diagnostic.
- **Verdict: TEST, but only the pre-check first.**

## 3. Overall choice

**E3, gated by its pre-check, with E1 as its required replication control. E2 is deferred.**

**No-go:** if E3's pre-check fails its budget condition, or shows under 1.33× headroom for active design, and E1's pre-checks show under 0.02 nats of intervention headroom, stop. The harness can then be kept as a teaching and evaluation tool.

None of the three is claimed as a methods innovation. Running the pre-checks needs a small exact-calculation script, and that requires separate user approval.

## 4. Sources and reading limits

| Source | Depth read |
| --- | --- |
| Tong & Koller, IJCAI 2001 — https://ai.stanford.edu/~koller/Papers/Tong+Koller:IJCAI01.pdf | PDF not readable here; used index and abstract summaries only. |
| Toth et al., *Active Bayesian Causal Inference*, NeurIPS 2022 — https://arxiv.org/abs/2206.02063 | HTML methods, baselines and limitations read. It excludes unobserved confounding. |
| Annadani et al., CAASL, NeurIPS 2024 — https://arxiv.org/abs/2405.16718 | Abstract. |
| Cooper & Velasquez, *ACE*, arXiv 2602.02451 (Feb/Jun 2026) — https://arxiv.org/abs/2602.02451 | HTML experiments read. Trains and tests on the same system; known structure. Its "70–71%" figure not verified. |
| Hedman et al., *Step-DAD*, ICML 2025 — https://proceedings.mlr.press/v267/hedman25a.html | Abstract. |
| Wilson, Fern & Tadepalli, 2012 — https://proceedings.mlr.press/v27/wilson12a.html | Abstract. |
| Chernoff, 1959 — https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-30/issue-3/Sequential-Design-of-Experiments/10.1214/aoms/1177706205.full | Bibliographic record and secondary summary only. |
| Ramdas, Grünwald, Vovk & Shafer, *Statistical Science* 2023 — https://arxiv.org/abs/2210.01948 | Abstract. |
| Wasserman, Ramdas & Balakrishnan, *Universal Inference* — https://arxiv.org/abs/1912.11436 | Abstract. The summarizer gave PNAS 2022; I recall 2020. Unresolved. |
| Yang, Chen & Wu, 2025 — https://arxiv.org/abs/2502.05372 | Abstract. |
| Müller, Luo & Barber, 2025 — https://arxiv.org/abs/2502.06765 | Abstract. |

Cooper–Yoo interventional scoring and the claims about Markov-equivalence classes are from memory and were not re-verified. Existing repository notes on controlled sensing, EPIG and robust design were checked, and E1–E3 were chosen not to repeat them. Coverage is bounded: it omits active inference, program synthesis and most 2026 causal-design work.

## Appendix: recovered scripts, verbatim from the session transcript

**a1.py**
```python
import json, math, statistics as st, sys
sys.path.insert(0,'.')
from artificial_scientist import adaptive_state_v2 as v2
from artificial_scientist.sequence_worlds import probability_one
from collections import deque
import random
cfg=json.load(open('experiments/adaptive_state_v2.json'))
rows,summary,events,timings,decisions=v2.simulate(cfg)
tracked=json.load(open('results/adaptive_state_v2_dev/summary.json'))
key=lambda r:(r['seed'],r['condition'],r['baseline'],r['phase'])
T={key(r):r for r in tracked}
mx=max(abs(T[key(r)]['log_loss']-r['log_loss']) for r in summary)
print('reproduction max abs diff vs tracked summary', mx, len(summary), len(tracked))
# oracle loss: evaluator true probability (labelled privileged reference)
def oracle(seed,cond,steps=1200,change=600):
    stream,lag=v2.generate(seed,cond,steps,change)
    h=deque(random.Random(seed+3000001).choices((0,1),k=5),maxlen=5)
    L=[]
    for t,y in enumerate(stream):
        c='structural' if cond.startswith('structural') else cond
        p=probability_one(h,c,t>=change,lag)
        L.append(-math.log(p if y else 1-p)); h.append(y)
    return st.mean(L[change:])
by={(r['seed'],r['condition'],r['baseline']):r['log_loss'] for r in summary if r['phase']=='after'}
seeds=cfg['seeds']
for cond in v2.CONDITIONS:
    orc=[oracle(s,cond) for s in seeds]
    line=f"{cond:12s} oracle {st.mean(orc):.4f} |"
    for n in v2.NAMES:
        line+=f" {n} {st.mean(by[s,cond,n]-o for s,o in zip(seeds,orc)):.4f}"
    print(line)
def paired(a,b,conds):
    d=[by[s,c,a]-by[s,c,b] for s in seeds for c in conds]
    # seed-cluster: average within seed first
    ds=[st.mean(by[s,c,a]-by[s,c,b] for c in conds) for s in seeds]
    return st.mean(d), min(ds), max(ds), sum(x>0 for x in ds)
S=[c for c in v2.CONDITIONS if c.startswith('structural')]
for a,b in [('v2','matched_mixture'),('v1','matched_mixture'),('v2','v1'),('v1','sparse_mixture'),('matched_mixture','sparse_mixture')]:
    print(a,'-',b,'structural: mean, seed-min, seed-max, #seeds a worse', paired(a,b,S))
for c in ['stable','parameter','noise']:
    print(c,'v2-matched',paired('v2','matched_mixture',[c]),'v2-slow',paired('v2','slow',[c]))
for c in S:
    print(c,'v2-matched per seed',[round(by[s,c,'v2']-by[s,c,'matched_mixture'],4) for s in seeds])
```

**a2.py**
```python
import json, math, statistics as st, sys, time
sys.path.insert(0,'.')
from artificial_scientist import adaptive_state_v2 as v2
from artificial_scientist.adaptive_state import AdaptiveContext, SparsePredictor
from artificial_scientist.metrics import scores
cfg=json.load(open('experiments/adaptive_state_v2.json'))
def post_loss(learner, stream, change=600):
    L=[]
    for t,y in enumerate(stream):
        p=learner.predict()
        if t>=change: L.append(scores(p,y)['log_loss'])
        learner.update(y)
    return st.mean(L)
def mk(name,every=64):
    d,f,s=.99,.90,.01; th=math.log(400)
    return {'v1':lambda:AdaptiveContext(d,128,every,th),
            'v2':lambda:v2.ReversibleContext(d,f,128,every,th),
            'mix':lambda:v2.MatchedMixture(d,f,s)}[name]()
def run(seeds, label):
    S=[c for c in v2.CONDITIONS if c.startswith('structural')]
    res={}
    for c in v2.CONDITIONS:
        for s in seeds:
            stream,lag=v2.generate(s,c,1200,600)
            r={}
            for n in ('v1','v2','mix'): r[n]=post_loss(mk(n),stream)
            r['v2_every1']=post_loss(mk('v2',1),stream)
            r['v1_every1']=post_loss(mk('v1',1),stream)
            if c.startswith('structural'):
                r['true_sparse_only(priv)']=post_loss(SparsePredictor((1,lag),.99),stream)
            res[s,c]=r
    print('==',label)
    for grp,conds in [('stable',['stable']),('parameter',['parameter']),('noise',['noise']),('structural',S)]:
        names=res[seeds[0],conds[0]].keys()
        print(f"{grp:10s}",' '.join(f"{n}={st.mean(res[s,c][n] for s in seeds for c in conds):.4f}" for n in names))
    for a in ('v1','v2','v2_every1','v1_every1'):
        d=[st.mean(res[s,c][a]-res[s,c]['mix'] for c in S) for s in seeds]
        cases=[res[s,c][a]-res[s,c]['mix'] for s in seeds for c in S]
        m=st.mean(d); se=st.stdev(d)/len(d)**.5
        print(f"  structural {a}-mix: mean {m:.4f} seed-SE {se:.4f} cases worse {sum(x>0 for x in cases)}/{len(cases)}")
    for c in ('parameter','stable','noise'):
        d=[res[s,c]['v2']-res[s,c]['mix'] for s in seeds]
        print(f"  {c} v2-mix mean {st.mean(d):.4f} SE {st.stdev(d)/len(d)**.5:.4f} worse {sum(x>0 for x in d)}/{len(d)}")
t=time.time()
run(cfg['seeds'],'dev seeds 0..4 (already inspected)')
run(list(range(100,120)),'non-reserved sensitivity seeds 100..119 (exploratory)')
print('elapsed',time.time()-t)
```

**a3.py**
```python
import math, statistics as st, sys, random
sys.path.insert(0,'.')
from collections import deque
from artificial_scientist import adaptive_state_v2 as v2
from artificial_scientist.adaptive_state import AdaptiveContext
from artificial_scientist.sequence_worlds import ContextPredictor, probability_one
from artificial_scientist.metrics import scores
def gen(seed,lag,steps=1800,a=600,b=1200):
    h=deque(random.Random(seed+3000001).choices((0,1),k=5),maxlen=5); nz=random.Random(seed+2000003); out=[]
    for t in range(steps):
        p=probability_one(h,'structural',a<=t<b,lag); y=int(nz.random()<p); out.append(y); h.append(y)
    return out
th=math.log(400)
res={n:[] for n in ('slow','v1','v2','mix','v2_every1')}; contracted=[]; delay=[]
for s in range(100,120):
    for lag in (2,3,4,5):
        y=gen(s,lag)
        L={'slow':ContextPredictor(1,.99),'v1':AdaptiveContext(.99,128,64,th),'v2':v2.ReversibleContext(.99,.9,128,64,th),
           'mix':v2.MatchedMixture(),'v2_every1':v2.ReversibleContext(.99,.9,128,1,th)}
        loss={n:[] for n in L}; first=None
        for t,o in enumerate(y):
            for n,m in L.items():
                p=m.predict()
                if t>=1200: loss[n].append(scores(p,o)['log_loss'])
                m.update(o)
            if t>=1200 and first is None and L['v2'].active<2: first=t+1
        for n in L: res[n].append(st.mean(loss[n]))
        contracted.append(first is not None); delay.append(first-1200 if first else None)
print('phase 3 (return to simple, ticks 1200-1799) mean log loss:')
for n,v in res.items(): print(f'  {n}: {st.mean(v):.4f}')
d=[a-b for a,b in zip(res['v2'],res['mix'])]; print('v2-mix', round(st.mean(d),4),'worse',sum(x>0 for x in d),'/',len(d))
d=[a-b for a,b in zip(res['v2'],res['slow'])]; print('v2-slow', round(st.mean(d),4))
print('v2 contracted', sum(contracted),'/',len(contracted),'delays',sorted(x for x in delay if x is not None)[:3],'..',max(x for x in delay if x is not None))
```
