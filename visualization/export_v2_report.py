"""Create a small offline comparison from recorded v2 results, without training."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONDITIONS = ['stable', 'parameter', 'noise', 'structural2', 'structural3', 'structural4', 'structural5']
NAMES = ['slow', 'fast', 'v1', 'sparse_mixture', 'matched_mixture', 'v2']

def build(run, output):
    run, output = Path(run).resolve(), Path(output).resolve()
    if ROOT not in output.parents:
        raise ValueError('Output must remain in the repository')
    config = json.loads((run / 'config.json').read_text())
    if config['steps'] != 1200 or config['change_at'] != 600 or config['seeds'] != list(range(5)):
        raise ValueError('Expected the reviewed 35-world development protocol')
    worlds = {c+':'+str(s): {'timeline': {'v1': [], 'v2': []}} for c in CONDITIONS for s in config['seeds']}
    counts = {(k,n): 0 for k in worlds for n in NAMES}
    with (run / 'predictions.csv').open(newline='') as f:
        for r in csv.DictReader(f):
            key, name, tick = r['condition']+':'+r['seed'], r['baseline'], int(r['tick'])
            if counts[key,name] != tick:
                raise ValueError('Duplicate or noncontiguous prediction sequence')
            counts[key,name] += 1
            if name not in ('v1', 'v2'):
                continue
            segments = worlds[key]['timeline'][name]
            state = [int(r['active_expert']), int(r['active_lag']), int(r['active_width'])]
            if segments and segments[-1][2:] == state:
                segments[-1][1] = tick+1
            else:
                segments.append([tick,tick+1]+state)
    if any(n != 1200 for n in counts.values()):
        raise ValueError('Incomplete recording')
    for field in ['summary', 'events', 'decisions']:
        rows = json.loads((run / (field+'.json')).read_text())
        for key, world in worlds.items():
            c,s = key.split(':')
            world[field] = [r for r in rows if r['condition'] == c and r['seed'] == int(s)]
    for world in worlds.values():
        if len(world['summary']) != 12 or len(world['decisions']) != 2:
            raise ValueError('Missing summary/decision records')
    data = dict(worlds=worlds, config=config, run=run.name,
                sha256=hashlib.sha256((run/'predictions.csv').read_bytes()).hexdigest(),
                diagnostic=json.loads((run/'diagnostic.json').read_text()))
    payload = json.dumps(data,separators=(',',':'),allow_nan=False).replace('<','\\u003c')
    output.write_text(TEMPLATE.replace('__DATA__',payload))
    print(f'Built {output}: {output.stat().st_size:,} bytes; 35 recorded worlds')

TEMPLATE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Artificial Scientist · v2 comparison</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f3f6f5;color:#203b40;font:16px system-ui,sans-serif}main{max-width:1160px;margin:auto;padding:32px 20px}h1{font-size:clamp(28px,5vw,42px);letter-spacing:-1.4px;margin:10px 0}h2{font-size:20px;margin:0 0 12px}p{line-height:1.55}.small{font-size:13px;color:#5a6f70}.tag{letter-spacing:2px;font-size:12px;font-weight:700;color:#527b70}.panel{background:white;border:1px solid #dce6e0;border-radius:15px;padding:22px;margin:20px 0}.scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:9px;border-bottom:1px solid #e5ece8;white-space:nowrap}th{color:#506963}td:last-child{font-weight:650;background:#f7faf8}.controls{display:flex;gap:20px;align-items:center;flex-wrap:wrap}label{font-size:14px;display:grid;gap:6px}select{font:inherit;padding:8px;border:1px solid #9cbbb1;border-radius:7px;background:white}input{accent-color:#197767;flex:1;min-width:180px}select:focus-visible,input:focus-visible{outline:3px solid #578eb1;outline-offset:3px}.timeline{width:100%;height:150px}.legend{display:flex;gap:12px;flex-wrap:wrap;font-size:12px}.chip{display:inline-block;width:11px;height:11px;margin-right:5px;border-radius:3px}.note{border-left:3px solid #c3945b;padding-left:12px}.footer{overflow-wrap:anywhere;font-size:12px;color:#607775}@media(max-width:650px){main{padding:24px 12px}.panel{padding:16px}.timeline{height:135px}}
</style></head><body><main>
<div class="tag">ARTIFICIAL SCIENTIST / RECORDED DEVELOPMENT EXPERIMENT</div><h1>Adapt speed, or add history?</h1>
<p>Version 2 can choose faster adaptation, add a lag, or return to simple memory. Compare its recorded choices with the irreversible v1 selector and fixed probabilistic baselines.</p>
<p class="small note">No live training, neural network or invented concept is shown. These methods learn probabilities inside a fixed, human-supplied expert library. All shadow experts and monitoring buffers remain allocated; selecting fewer features does not save that memory.</p>
<p id="coverage" class="small note"></p>
<section class="panel"><h2>Prediction after the hidden change</h2><p class="small">Mean log loss over ticks 600–1199, averaged equally over five development seeds per world. Lower is better. The matched mixture uses the same six experts as v2. These are descriptive, correlated-seed results—not independent confirmatory trials.</p><div class="scroll"><table><thead id="overviewHead"></thead><tbody id="overview"></tbody></table></div></section>
<section class="panel"><h2>Inspect one recorded world</h2><div class="controls"><label>World<select id="world"></select></label><label>Seed<select id="seed"></select></label><label for="tick">Tick</label><input id="tick" type="range" min="0" max="1199" value="599"><output id="tickLabel"></output></div><p id="law" class="small"></p>
<div id="legend" class="legend"></div><svg id="timeline" class="timeline" viewBox="0 0 1000 150" role="img" aria-label="Full recorded v1 and v2 active expert timelines"></svg><p id="selected"></p><p class="small">Full-run timeline includes future relative to the cursor. Grey dashed boundary: evaluator-only tick 600. Solid cursor: selected prediction tick. Choices shown are those active before that observation; a decision after a tick first affects the next tick.</p>
<div class="scroll"><table><thead><tr><th>Selector</th><th>Ever added lag</th><th>Before change</th><th>Switches</th><th>Mean dwell</th><th>Correct lag after</th></tr></thead><tbody id="decisions"></tbody></table></div></section>
<section class="panel"><h2>Full-run comparisons and events</h2><p class="small">All rows below summarize the complete run, including future relative to the cursor. Storage is mean logical slots after tick 600, not bytes. It includes shadow experts and monitoring buffers.</p><div class="scroll"><table><thead><tr><th>Model</th><th>Before loss</th><th>After loss</th><th>Logical slots</th></tr></thead><tbody id="models"></tbody></table></div><p id="rule" class="small"></p><div class="scroll"><table><thead><tr><th>Model</th><th>Observed → effective tick</th><th>Change</th><th>Selected expert</th><th>Window gain</th></tr></thead><tbody id="events"></tbody></table></div></section>
<p class="small note">Parameter changes and noise do not require additional history: any added-lag choice in those controls is not evidence of structural discovery. Final correct lag alone can conceal repeated switching. All 35 worlds use five previously inspected seeds and supplied rule families; no held-out evaluation, causal diagnosis, calibration guarantee, novelty or resource advantage follows.</p><p id="provenance" class="footer"></p></main>
<script id="data" type="application/json">__DATA__</script><script>
'use strict';const D=JSON.parse(document.getElementById('data').textContent),$=id=>document.getElementById(id);
const names={slow:'Slow simple',fast:'Fast simple',v1:'v1 selector',sparse_mixture:'Sparse mixture',matched_mixture:'Matched mixture',v2:'v2 selector'};
const worlds={stable:'Stable',parameter:'Parameter change',noise:'Noise',structural2:'Added lag 2',structural3:'Added lag 3',structural4:'Added lag 4',structural5:'Added lag 5'};
const labels=['Slow simple','Fast simple','Lag 1 + 2','Lag 1 + 3','Lag 1 + 4','Lag 1 + 5'],colors=['#8daba2','#deab58','#3980a6','#8870ad','#ba6789','#358c78'];
const kinds={expand:0,contract:0,speed:0,reselect:0};for(const w of Object.values(D.worlds))for(const e of w.events)if(e.baseline==='v2')kinds[e.kind]++;$('coverage').textContent=`Recorded v2 transitions: ${kinds.expand} expansions, ${kinds.speed} speed changes, ${kinds.contract} contractions, ${kinds.reselect} lag reselections. ${kinds.contract===0&&kinds.reselect===0?'These worlds did not exercise contraction or lag reselection; support for those operations is not empirical validation of them.':''}`;
const mean=a=>a.reduce((x,y)=>x+y,0)/a.length, stateLabel=(n,s)=>labels[n==='v1'?(s[2]===0?0:s[2]+1):s[2]], stateColor=(n,s)=>colors[n==='v1'?(s[2]===0?0:s[2]+1):s[2]];
$('world').innerHTML=Object.entries(worlds).map(([k,v])=>`<option value="${k}">${v}</option>`).join('');$('seed').innerHTML=D.config.seeds.map(s=>`<option>${s}</option>`).join('');
$('overviewHead').innerHTML='<tr><th>World</th>'+Object.values(names).map(n=>`<th>${n}</th>`).join('')+'</tr>';
$('overview').innerHTML=Object.entries(worlds).map(([c,title])=>'<tr><td>'+title+'</td>'+Object.keys(names).map(n=>'<td>'+mean(D.config.seeds.map(s=>D.worlds[c+':'+s].summary.find(r=>r.baseline===n&&r.phase==='after').log_loss)).toFixed(4)+'</td>').join('')+'</tr>').join('');
$('legend').innerHTML=labels.map((v,i)=>`<span><i class="chip" style="background:${colors[i]}"></i>${v}</span>`).join('');
$('rule').textContent=`Every ${D.config.check_every} observations after ${D.config.gain_window}, v2 compares trailing pre-update losses. A sparse expert must beat the better simple expert by more than ${D.config.gain_threshold.toFixed(3)} nats; otherwise choose that simple expert. Choices are reversible. The threshold is not a calibrated statistical test. V1 event gains instead compare against its slow base.`;
$('provenance').textContent='Source: results/runs/'+D.run+' · CSV SHA-256 '+D.sha256+' · Timelines compressed losslessly from recorded active-expert rows. No network requests or new experiments.';
function render(){const c=$('world').value,w=D.worlds[c+':'+$('seed').value],t=+$('tick').value;$('tickLabel').textContent=t+' / 1199';$('law').textContent=c.startsWith('structural')?'Human evaluator information: after tick 599 the target is latest bit XOR lag '+c.slice(-1)+', matched with probability 0.8. The learner does not receive this law or change time.':c==='stable'?'Stable control: repeat the latest bit with probability 0.8 throughout.':c==='parameter'?'From tick 600, repeat probability changes from 0.8 to 0.2. No additional history is required.':'From tick 600, outcomes are fair independent bits. No additional history can predict that noise.';
const x=v=>95+v/1200*890;let svg='';let selected=[];['v1','v2'].forEach((n,i)=>{const y=22+i*46;svg+=`<text x="0" y="${y+20}" fill="#35524b" font-size="15">${n}</text>`;for(const s of w.timeline[n]){svg+=`<rect x="${x(s[0])}" y="${y}" width="${x(s[1])-x(s[0])}" height="30" fill="${stateColor(n,s)}"><title>${n}: ${stateLabel(n,s)}, ticks ${s[0]}–${s[1]-1}</title></rect>`;if(s[0]<=t&&t<s[1])selected.push(n+': '+stateLabel(n,s))}});svg+=`<line x1="${x(600)}" x2="${x(600)}" y1="10" y2="106" stroke="#344f45" stroke-dasharray="5 3"/><line x1="${x(t)}" x2="${x(t)}" y1="10" y2="106" stroke="#192e35" stroke-width="2"/>`;for(const z of [0,600,1199])svg+=`<text x="${x(z)-10}" y="132" font-size="13" fill="#4e6860">${z}</text>`;$('timeline').innerHTML=svg;$('selected').textContent='Active before selected observation — '+selected.join(' · ');
$('decisions').innerHTML=w.decisions.map(r=>`<tr><td>${r.baseline}</td><td>${r.ever_expanded?'Yes':'No'}</td><td>${r.premature?'Yes':'No'}</td><td>${r.switches}</td><td>${r.mean_dwell.toFixed(1)} ticks</td><td>${r.correct_fraction_after===null?'Not applicable':(100*r.correct_fraction_after).toFixed(1)+'%'}</td></tr>`).join('');
$('models').innerHTML=Object.keys(names).map(n=>{const before=w.summary.find(r=>r.baseline===n&&r.phase==='before'),after=w.summary.find(r=>r.baseline===n&&r.phase==='after');return `<tr><td>${names[n]}</td><td>${before.log_loss.toFixed(4)}</td><td>${after.log_loss.toFixed(4)}</td><td>${after.logical_slots.toFixed(1)}</td></tr>`}).join('');
$('events').innerHTML=w.events.length?w.events.map(e=>`<tr><td>${e.baseline}</td><td>${e.observed_tick} → ${e.effective_tick}</td><td>${e.kind||'expand'}</td><td>${e.baseline==='v1'?'Lag 1 + '+e.selected_lag:labels[e.selected_expert]}</td><td>${e.window_gain.toFixed(3)} nats</td></tr>`).join(''):'<tr><td colspan="5">No switches recorded.</td></tr>';}
$('world').onchange=render;$('seed').onchange=render;$('tick').oninput=render;render();
</script></body></html>'''

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,default=ROOT/'results/runs/adaptive_state_v2_dev_20260925')
    parser.add_argument('--output',type=Path,default=ROOT/'visualization/v2_report.html')
    args=parser.parse_args()
    build(args.run,args.output)
