"""Export an offline viewer from an existing adaptive-state run; never trains."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINES = ['order1', 'order5', 'order_mixture', 'sparse_mixture', 'monitor_only', 'adaptive']

def build(run, output):
    run, output = Path(run).resolve(), Path(output).resolve()
    if ROOT not in output.parents:
        raise ValueError('Output must remain inside this repository')
    config = json.loads((run / 'config.json').read_text())
    if config['steps'] != 1200 or config['change_at'] != 600:
        raise ValueError('This viewer supports the reviewed 1200-tick / 600-boundary protocol')
    source, worlds, count = run / 'predictions.csv', {}, 0
    with source.open(newline='') as handle:
        for row in csv.DictReader(handle):
            key = row['condition'] + ':' + row['seed']
            world = worlds.setdefault(key, {'y': [], 'models': {b: {'p': [], 'l': [], 's': [], 'a': [], 'w': [], 'c': []} for b in BASELINES}})
            tick, outcome = int(row['tick']), int(row['outcome'])
            if tick == len(world['y']):
                world['y'].append(outcome)
            if tick >= len(world['y']) or world['y'][tick] != outcome:
                raise ValueError('Baselines must share a contiguous outcome stream')
            model = world['models'][row['baseline']]
            if tick != len(model['p']):
                raise ValueError('Duplicate or unsorted baseline row')
            for short, field in [('p', 'probability'), ('l', 'log_loss')]:
                model[short].append(round(float(row[field]), 6))
            model['s'].append(int(row['logical_slots']))
            if row['active_lag']:
                for short, field in [('a', 'active_lag'), ('w', 'active_width'), ('c', 'checks')]:
                    model[short].append(int(row[field]))
            count += 1
    summary = json.loads((run / 'summary.json').read_text())
    events = json.loads((run / 'events.json').read_text())
    for key, world in worlds.items():
        condition, seed = key.split(':')
        world['summary'] = [r for r in summary if r['condition'] == condition and r['seed'] == int(seed)]
        world['events'] = [e for e in events if e['condition'] == condition and e['seed'] == int(seed)]
        world['lag'] = world['summary'][0]['evaluator_lag']
        if len(world['y']) != config['steps'] or any(len(m['p']) != config['steps'] for m in world['models'].values()):
            raise ValueError('Incomplete recorded world')
    if len(worlds) != 4 * len(config['seeds']):
        raise ValueError('Incomplete condition/seed coverage')
    data = {'worlds': worlds, 'config': config, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'run': run.name}
    payload = json.dumps(data, separators=(',', ':'), allow_nan=False).replace('<', '\\u003c')
    template = (ROOT / 'visualization/adaptive_template.html').read_text()
    if template.count('__REPLAY_DATA__') != 1:
        raise ValueError('Expected one data placeholder')
    output.write_text(template.replace('__REPLAY_DATA__', payload))
    print(f'Built {output}: {output.stat().st_size:,} bytes, {len(worlds)} worlds, {count:,} predictions')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, default=ROOT / 'results/runs/adaptive_state_v1_dev_20260925')
    parser.add_argument('--output', type=Path, default=ROOT / 'visualization/adaptive_replay.html')
    args = parser.parse_args()
    build(args.run, args.output)
