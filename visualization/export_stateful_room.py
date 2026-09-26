"""Export an offline stateful-room replay solely from a verified recorded run."""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICIES = ['random', 'cycle', 'greedy', 'lookahead2']

def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024*1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

def build(run, output):
    run, output = Path(run).resolve(), Path(output).resolve()
    if ROOT not in run.parents or ROOT not in output.parents:
        raise ValueError('Run and output must remain inside this repository')
    metadata = json.loads((run/'metadata.json').read_text())
    if (metadata.get('status') != 'completed' or metadata.get('sources_unchanged') is not True
            or metadata.get('mode') != 'full' or metadata.get('completed_episodes') != 640
            or metadata.get('expected_episodes') != 640):
        raise ValueError('Completed, source-stable full study required')
    hashes = metadata.get('artifact_sha256', {})
    for name in ['config.json','worlds.json','trajectories.jsonl','summary.json','decision.json']:
        path = (run/name).resolve()
        if ROOT not in path.parents or hashes.get(name) != sha(path):
            raise ValueError('Out-of-scope or mismatched artifact: '+name)
    config = json.loads((run/'config.json').read_text())
    worlds = json.loads((run/'worlds.json').read_text())
    seeds = config['seeds']
    prior = config['dirichlet_prior']
    if len(worlds) != 5 or len(seeds) != 32 or len(set(seeds)) != 32 or prior != 0.5:
        raise ValueError('Expected reviewed five-world, 32-seed, symmetric-prior protocol')
    selected, episodes, seen = seeds[:2], [], set()
    cells = {(w['id'],p): [] for w in worlds for p in POLICIES}
    digest = hashlib.sha256()
    with (run/'trajectories.jsonl').open('rb') as handle:
        for line in handle:
            digest.update(line)
            e = json.loads(line)
            key = (e['world'],e['seed'],e['policy'])
            if key in seen or e['seed'] not in seeds or (e['world'],e['policy']) not in cells:
                raise ValueError('Duplicate or undeclared episode')
            seen.add(key)
            records = e['records']
            if e['schema_version'] != 1 or e['steps'] != 96 or len(records) != 97:
                raise ValueError('Unsupported or incomplete trajectory')
            for i,r in enumerate(records):
                if r['step'] != i or len(r['counts']) != 12 or any(len(row)!=5 for row in r['counts']):
                    raise ValueError('Malformed counts or step order')
                if any(type(n) is not int or n < 0 for row in r['counts'] for n in row):
                    raise ValueError('Noninteger transition counts')
                if sum(sum(row) for row in r['counts']) != i:
                    raise ValueError('Counts do not match completed observations')
                if (r['two_step_metrics'] is not None) != (i in [0,24,48,96]):
                    raise ValueError('Unexpected two-step checkpoint')
            losses = [r['query_metrics']['excess_log_loss'] for r in records[1:]]
            final2 = records[-1]['two_step_metrics']['excess_log_loss']
            if not all(math.isfinite(v) for v in losses+[final2]):
                raise ValueError('Nonfinite query score')
            cells[e['world'],e['policy']].append((sum(losses)/96,final2))
            if e['seed'] in selected:
                episodes.append(e)
    if digest.hexdigest() != hashes['trajectories.jsonl']:
        raise ValueError('Trajectories changed during export')
    if len(seen)!=640 or len(episodes)!=40 or any(len(v)!=32 for v in cells.values()):
        raise ValueError('Incomplete full-study or replay coverage')
    overview = [dict(world=w,policy=p,n=len(v),auc_excess_log_loss=sum(a for a,_ in v)/len(v),
                     final_two_step_excess=sum(b for _,b in v)/len(v)) for (w,p),v in cells.items()]
    data = dict(worlds=worlds,episodes=episodes,overview=overview,seeds=selected,
                all_seed_count=32,prior=prior,run=run.name,sha256=digest.hexdigest())
    template = (ROOT/'visualization/stateful_room_template.html').read_text()
    if template.count('__ROOM_DATA__') != 1:
        raise ValueError('Expected exactly one payload placeholder')
    payload = json.dumps(data,separators=(',',':'),allow_nan=False).replace('<','\\u003c')
    html = template.replace('__ROOM_DATA__',payload)
    if len(html.encode()) > 5_000_000:
        raise ValueError('Replay exceeds 5 MB budget')
    output.write_text(html)
    print(f'Built {output}: {len(html.encode()):,} bytes, 40 recorded episodes; overview 640 episodes')

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=ROOT/'visualization/stateful_room.html')
    args=parser.parse_args()
    build(args.run,args.output)
