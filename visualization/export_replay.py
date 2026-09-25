"""Build an offline replay from recorded data; does not run an experiment."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'results/runs/state_revision_v0_dev_20260925'
BASELINES = ['order1', 'order5', 'order_mixture']

def build():
    source = RUN / 'predictions.csv'
    worlds = {}
    with source.open(newline='') as handle:
        for row in csv.DictReader(handle):
            key = row['condition'] + ':' + row['seed']
            world = worlds.setdefault(key, {'y': [], 'models': {b: {'p': [], 'l': [], 's': []} for b in BASELINES}})
            tick, outcome = int(row['tick']), int(row['outcome'])
            if tick == len(world['y']):
                world['y'].append(outcome)
            assert world['y'][tick] == outcome, 'Baselines must share outcomes'
            model = world['models'][row['baseline']]
            assert tick == len(model['p']), 'Unexpected duplicate or unsorted row'
            model['p'].append(round(float(row['probability']), 6))
            model['l'].append(round(float(row['log_loss']), 6))
            model['s'].append(int(row['logical_slots']))
    summary = json.loads((RUN / 'summary.json').read_text())
    for key, world in worlds.items():
        condition, seed = key.split(':')
        records = [r for r in summary if r['condition'] == condition and r['seed'] == int(seed)]
        assert records
        world['lag'] = records[0]['evaluator_lag']
        world['summary'] = records
        assert len(world['y']) == 1200
        assert all(len(m['p']) == 1200 for m in world['models'].values())
    assert len(worlds) == 20
    data = {'worlds': worlds, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
    payload = json.dumps(data, separators=(',', ':')).replace('<', '\\u003c')
    template = (ROOT / 'visualization/template.html').read_text()
    assert template.count('__REPLAY_DATA__') == 1
    destination = ROOT / 'visualization/replay.html'
    destination.write_text(template.replace('__REPLAY_DATA__', payload))
    print(f'Built {destination} ({destination.stat().st_size:,} bytes), 20 worlds, 72,000 recorded predictions')

if __name__ == '__main__':
    build()
