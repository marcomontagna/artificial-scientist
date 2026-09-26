"""Export a recorded switch-lab replay; no training and no external dependencies."""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICIES = ['hybrid_epig', 'hybrid_random', 'hybrid_roundrobin', 'structured_epig']

def build(run, output):
    run, output = Path(run).resolve(), Path(output).resolve()
    if ROOT not in output.parents or ROOT not in run.parents:
        raise ValueError('Input run and output must remain inside the repository')
    metadata = json.loads((run/'metadata.json').read_text())
    if (metadata.get('status') != 'completed' or metadata.get('sources_unchanged') is not True
            or metadata.get('mode') != 'full' or metadata.get('completed_episodes') != 960
            or metadata.get('expected_episodes') != 960):
        raise ValueError('A completed, source-stable full study is required')
    hashes = metadata.get('artifact_sha256', {})
    for filename in ['trajectories.jsonl', 'config.json', 'worlds.json', 'library.json', 'summary.json', 'decision.json']:
        artifact = (run/filename).resolve()
        if ROOT not in artifact.parents:
            raise ValueError('Input artifact resolves outside the repository')
        digest = hashlib.sha256()
        with artifact.open('rb') as handle:
            for chunk in iter(lambda: handle.read(1024*1024), b''):
                digest.update(chunk)
        if hashes.get(filename) != digest.hexdigest():
            raise ValueError('Artifact hash mismatch: '+filename)
    config = json.loads((run/'config.json').read_text())
    seeds = config['seeds']
    selected = seeds[:3]
    worlds = json.loads((run/'worlds.json').read_text())
    library = json.loads((run/'library.json').read_text())
    if len(worlds) != 6 or len(seeds) != 40 or len(set(seeds)) != 40:
        raise ValueError('Expected all six worlds and forty declared seeds')
    cells = {(w['id'],p): [] for w in worlds for p in POLICIES}
    episodes, seen, digest = [], set(), hashlib.sha256()
    with (run/'trajectories.jsonl').open('rb') as stream:
        for line in stream:
            digest.update(line)
            e = json.loads(line)
            key = (e['world'],e['seed'],e['policy'])
            if key in seen or e['seed'] not in seeds or (e['world'],e['policy']) not in cells:
                raise ValueError('Duplicate or undeclared episode')
            seen.add(key)
            records = e['records']
            if e['schema_version'] != 1 or e['steps'] != 48 or len(records) != 49:
                raise ValueError('Unsupported or incomplete trajectory')
            for i,r in enumerate(records):
                if r['step'] != i or len(r['query_probabilities']) != 8:
                    raise ValueError('Malformed recorded state')
                if not all(math.isfinite(x) and 0 <= x <= 1 for x in r['query_probabilities']):
                    raise ValueError('Invalid probabilities')
            losses = [r['query_metrics']['excess_log_loss'] for r in records[1:]]
            if not all(math.isfinite(x) for x in losses):
                raise ValueError('Invalid evaluator scores')
            cells[e['world'],e['policy']].append((sum(losses)/48,losses[-1]))
            if e['seed'] in selected:
                episodes.append(e)
    if digest.hexdigest() != hashes['trajectories.jsonl']:
        raise ValueError('Trajectory changed during export')
    if len(seen) != 6*40*4 or len(episodes) != 72 or any(len(v)!=40 for v in cells.values()):
        raise ValueError('Full study or replay coverage is incomplete')
    overview = [dict(world=w,policy=p,n=len(v),auc_excess_log_loss=sum(a for a,_ in v)/len(v),
                     final_excess_log_loss=sum(b for _,b in v)/len(v)) for (w,p),v in cells.items()]
    data = dict(schema_version=1,worlds=worlds,library=library,episodes=episodes,overview=overview,
                seeds=selected,all_seed_count=len(seeds),run=run.name,sha256=digest.hexdigest())
    payload = json.dumps(data,separators=(',',':'),allow_nan=False).replace('<','\\u003c')
    template = (ROOT/'visualization/interactive_lab_template.html').read_text()
    if template.count('__LAB_DATA__') != 1:
        raise ValueError('Expected one data placeholder')
    html = template.replace('__LAB_DATA__',payload)
    if len(html.encode()) > 5_000_000:
        raise ValueError('Replay exceeds 5 MB budget')
    output.write_text(html)
    print(f'Built {output}: {len(html.encode()):,} bytes, 72 replay episodes; overview 960 episodes')

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=ROOT/'visualization/interactive_lab.html')
    args=parser.parse_args()
    build(args.run,args.output)
