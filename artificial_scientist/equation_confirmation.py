"""Independent split-likelihood term evidence for a frozen polynomial candidate."""
import argparse
import hashlib
import json
import math
import platform
import statistics
import time
from pathlib import Path
from . import equation_discovery as ed
from .run import git_info

ROOT = Path(__file__).resolve().parents[1]
WORLDS = ed.WORLDS
STRATEGIES = ('raw', 'adequacy_only', 'confirmed', 'combined')
IN_CLASS = ('affine', 'sparse_quadratic', 'noise_only')


def term_evidence(candidate, audit, sigma=.05, rank_tolerance=1e-10, violation_tolerance=1e-8):
    """Audit-only null MLEs; neither candidate nor audit is mutated."""
    if not math.isfinite(sigma) or sigma <= 0:
        raise ValueError('positive finite known sigma required')
    design = [ed.basis(x, u) for x, u, _ in audit]
    outcomes = [y for _, _, y in audit]
    predictions = [ed.predict(candidate['coefficients'], x, u) for x, u, _ in audit]
    candidate_sse = math.fsum((y-p)**2 for y, p in zip(outcomes, predictions))
    if not math.isfinite(candidate_sse):
        raise ArithmeticError('nonfinite candidate audit SSE')
    evidence = []
    for j in range(6):
        null = ed.least_squares(design, outcomes, [k for k in range(6) if k != j], rank_tolerance)
        log_e = (null['sse']-candidate_sse)/(2*sigma*sigma)
        if not math.isfinite(log_e):
            raise ArithmeticError('nonfinite log evidence')
        if j not in candidate['support'] and log_e > violation_tolerance:
            raise ArithmeticError('nonselected-term null likelihood violation')
        evidence.append(dict(term_index=j, term=ed.TERMS[j], null_fit=null, log_e=log_e))
    return dict(candidate_audit_sse=candidate_sse, audit_predictions=predictions, terms=evidence)


def reporting_claims(support, evidence, adequate, threshold=math.log(120)):
    confirmed = [j for j in support if evidence['terms'][j]['log_e'] >= threshold]
    return dict(raw=list(support), adequacy_only=list(support) if adequate else [],
                confirmed=confirmed, combined=list(confirmed) if adequate else [])


def claim_metrics(claim, truth_support):
    if truth_support is None:
        return dict(any_false_term=None, exact_match=None, true_terms_claimed=None,
                    true_term_recall=None, all_true_terms_claimed=None)
    truth, claimed = set(truth_support), set(claim)
    true_count = len(truth & claimed)
    return dict(any_false_term=bool(claimed-truth), exact_match=claimed == truth,
                true_terms_claimed=true_count,
                true_term_recall=true_count/len(truth) if truth else None,
                all_true_terms_claimed=truth <= claimed if truth else None)


def episode_record(seed, name, world, streams, config):
    # This unchanged helper freezes all four training fits before constructing audit outcomes.
    episode = ed.episode_record(seed, name, world, streams, config)
    candidate = episode['methods']['sparse']
    start = time.perf_counter()
    evidence = term_evidence(candidate, episode['audit'], config['sigma'],
                             config['rank_tolerance'], config['nonselected_log_e_tolerance'])
    adequate = not candidate['metrics']['audit_rejected']
    claims = reporting_claims(candidate['support'], evidence, adequate, math.log(config['e_threshold']))
    local_flag = bool(candidate['support'] and claims['confirmed'] == candidate['support'] and adequate)
    truth = world['support']
    selected_true = None if truth is None else len(set(candidate['support']) & set(truth))
    confirmed_true = None if truth is None else len(set(claims['confirmed']) & set(truth))
    episode['confirmation'] = dict(**evidence, e_threshold=config['e_threshold'], log_threshold=math.log(config['e_threshold']),
        claim_sets=claims, claim_metrics={key: claim_metrics(value, truth) for key, value in claims.items()},
        adequate=adequate, unsupported_candidate_terms=len(candidate['support'])-len(claims['confirmed']),
        selected_true_terms=selected_true, confirmed_true_terms=confirmed_true,
        true_term_count=None if truth is None else len(truth),
        all_true_terms_confirmed=claim_metrics(claims['confirmed'], truth)['all_true_terms_claimed'],
        all_selected_terms_supported_and_locally_adequate=local_flag,
        flag_interpretation=('within supplied polynomial/noise assumptions; not proof of the equation'
                             if truth is not None else 'locally adequate polynomial approximation with large term statistics; no validity guarantee'),
        evidence_seconds=time.perf_counter()-start)
    return episode


def proportion(values, z):
    values = [v for v in values if v is not None]
    if not values:
        return None
    n, count = len(values), sum(values)
    return dict(count=count, n=n, rate=count/n, wilson95=ed.wilson(count, n, z))


def summarize(episodes, config):
    cells, paired = [], []
    z = config['normal_interval_z']
    for world in WORLDS:
        rows = [e for e in episodes if e['world'] == world]
        if not rows:
            continue
        confirmations = [e['confirmation'] for e in rows]
        truth_n = sum(c['true_term_count'] or 0 for c in confirmations)
        selected_n = sum(c['selected_true_terms'] or 0 for c in confirmations)
        confirmed_n = sum(c['confirmed_true_terms'] or 0 for c in confirmations)
        strategies = {}
        for strategy in STRATEGIES:
            metrics = [c['claim_metrics'][strategy] for c in confirmations]
            recalls = [m['true_term_recall'] for m in metrics if m['true_term_recall'] is not None]
            strategies[strategy] = dict(
                any_false_term=proportion([m['any_false_term'] for m in metrics], z),
                exact_match=proportion([m['exact_match'] for m in metrics], z),
                all_true_terms_claimed=proportion([m['all_true_terms_claimed'] for m in metrics], z),
                mean_true_term_recall=statistics.mean(recalls) if recalls else None,
                mean_claim_count=statistics.mean(len(c['claim_sets'][strategy]) for c in confirmations))
        cells.append(dict(world=world, n=len(rows), strategies=strategies,
            true_term_count=truth_n if world in IN_CLASS else None,
            selected_true_term_count=selected_n if world in IN_CLASS else None,
            confirmed_true_term_count=confirmed_n if world in IN_CLASS else None,
            selection_recall=selected_n/truth_n if truth_n else None,
            confirmation_rate_among_selected_true=confirmed_n/selected_n if selected_n else None,
            overall_true_term_recall=confirmed_n/truth_n if truth_n else None,
            all_true_terms_confirmed=proportion([c['all_true_terms_confirmed'] for c in confirmations], z),
            adequacy=proportion([c['adequate'] for c in confirmations], z),
            local_flag=proportion([c['all_selected_terms_supported_and_locally_adequate'] for c in confirmations], z),
            local_flag_interpretation=confirmations[0]['flag_interpretation'],
            mean_unsupported_candidate_terms=statistics.mean(c['unsupported_candidate_terms'] for c in confirmations),
            total_evidence_seconds=sum(c['evidence_seconds'] for c in confirmations)))
        if world in IN_CLASS:
            for comparator in ('raw', 'adequacy_only'):
                diffs = [dict(seed=e['seed'], difference=int(e['confirmation']['claim_metrics']['confirmed']['any_false_term'])-
                              int(e['confirmation']['claim_metrics'][comparator]['any_false_term'])) for e in rows]
                paired.append(dict(world=world, comparator=comparator, metric='any_false_term', **ed.paired_stats(diffs,z)))
    return dict(completed_keys=[[e['seed'],e['world']] for e in episodes], cells=cells, paired=paired,
                prediction_diagnostics=ed.summarize(episodes, config),
                interval_scope='dataset-level descriptive Wilson/paired seed intervals; no independent-term interval')


def decision(summary, config, complete):
    expected = {(s,w) for s in config['seeds'] for w in WORLDS}
    observed = [tuple(v) for v in summary['completed_keys']]
    complete = bool(complete and len(observed)==len(expected) and set(observed)==expected)
    cells = {c['world']:c for c in summary['cells']}
    errors, power = {}, {}
    for world in IN_CLASS:
        if world in cells:
            errors[world] = cells[world]['strategies']['confirmed']['any_false_term']['count'] <= config['maximum_false_claim_datasets']
    for world in ('affine','sparse_quadratic'):
        if world in cells:
            rate = cells[world]['confirmation_rate_among_selected_true']
            power[world] = rate is not None and rate >= config['minimum_conditional_confirmation_rate']
    validity_pause = not complete or len(errors)!=3 or not all(errors.values())
    return dict(complete=complete, diagnostic_screen_pass=bool(not validity_pause and len(power)==2 and all(power.values())),
                error_rate_conditions=errors, conditional_power_conditions=power,
                pause_stage3_pending_diagnosis=validity_pause,
                limitation='known-model implementation/calibration check; no coefficient accuracy, missing-term, functional-form or general explanation guarantee')


def fixed_config():
    config = ed.fixed_config()
    for key in ('minimum_support_recoveries','maximum_false_inclusions','maximum_noise_nonzero',
                'maximum_false_rejections','maximum_missed_rejections'):
        del config[key]
    config.update(seeds=list(range(700,800)), smoke_seeds=[690], e_threshold=120, familywise_alpha=.05,
                  nonselected_log_e_tolerance=1e-8, maximum_false_claim_datasets=5,
                  minimum_conditional_confirmation_rate=.8, reporting_strategies=list(STRATEGIES))
    return config


def validate_config(config):
    if config != fixed_config():
        raise ValueError('fixed confirmation protocol parameters differ')


def output_scope(output):
    output, runs = Path(output).resolve(), (ROOT/'results/runs').resolve()
    if ROOT not in runs.parents or output.parent != runs or not output.name.startswith('equation_confirmation_'):
        raise ValueError('use fresh results/runs/equation_confirmation_<label>')
    if output.exists():
        raise FileExistsError('output exists')
    return output


def source_hashes():
    paths = [Path(__file__).resolve(), ROOT/'tests/test_equation_confirmation.py',
             ROOT/'experiments/equation_confirmation_v0.md', ROOT/'artificial_scientist/run.py', ROOT/'artificial_scientist/equation_discovery.py']
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def verify_smoke(path, config_hash, sources, config):
    path = Path(path).resolve()
    if ROOT not in path.parents:
        raise ValueError('smoke outside repository')
    meta = json.loads((path/'metadata.json').read_text())
    if (meta.get('status') != 'completed' or meta.get('mode') != 'smoke' or meta.get('completed_episodes') != 5
            or not meta.get('sources_unchanged') or meta.get('source_sha256') != sources or meta.get('config_sha256') != config_hash):
        raise ValueError('smoke provenance/completion mismatch')
    required = {'config.json', 'episodes.jsonl', 'summary.json', 'decision.json'}
    if set(meta.get('artifact_sha256', {})) != required:
        raise ValueError('smoke artifact manifest incomplete')
    for name, digest in meta['artifact_sha256'].items():
        if Path(name).name != name or hashlib.sha256((path/name).read_bytes()).hexdigest() != digest:
            raise ValueError('smoke artifact mismatch')
    size = sum(p.stat().st_size for p in path.iterdir() if p.is_file())
    elapsed = meta['elapsed_seconds']
    if size != meta['artifact_bytes'] or not isinstance(elapsed, (int, float)) or not math.isfinite(elapsed) or elapsed <= 0:
        raise ValueError('invalid smoke size/time')
    factor = config['smoke_safety_factor']*500/5
    projected_time, projected_bytes = factor*elapsed, factor*size
    if projected_time > config['smoke_projection_limit_seconds'] or projected_bytes > config['smoke_projection_limit_bytes']:
        raise RuntimeError('resource no-go: smoke exceeds fixed time/disk projection')
    return dict(path=str(path.relative_to(ROOT)), projected_full_seconds=projected_time,
                projected_full_bytes=projected_bytes, metadata_sha256=hashlib.sha256((path/'metadata.json').read_bytes()).hexdigest())


def run(config_path, output, smoke=False, smoke_evidence=None):
    config_path = Path(config_path).resolve()
    if ROOT not in config_path.parents:
        raise ValueError('config outside repository')
    raw = config_path.read_bytes()
    config = json.loads(raw)
    validate_config(config)
    output = output_scope(output)
    sources, config_hash = source_hashes(), hashlib.sha256(raw).hexdigest()
    if not smoke and smoke_evidence is None:
        raise ValueError('full run requires --smoke-evidence')
    evidence = None if smoke else verify_smoke(smoke_evidence, config_hash, sources, config)
    start = time.perf_counter()
    meta = dict(git_info(ROOT), status='running', mode='smoke' if smoke else 'full', source_sha256=sources,
        config_sha256=config_hash, smoke_evidence=evidence, python=platform.python_version(), platform=platform.platform(),
        seeds=config['smoke_seeds'] if smoke else config['seeds'], external_timeout_seconds=config['external_timeout_seconds'], schema_version=1)
    output.mkdir(parents=True, exist_ok=False)
    def write(name, data):
        text = json.dumps(data, indent=2, allow_nan=False)+'\n'
        other = sum(p.stat().st_size for p in output.iterdir() if p.is_file() and p.name != name)
        if other+len(text.encode()) > config['max_output_bytes']:
            raise RuntimeError('output cap reached')
        (output/name).write_text(text)
    write('config.json', config)
    write('metadata.json', meta)
    episodes, error = [], None
    try:
        with (output/'episodes.jsonl').open('w') as handle:
            for seed in meta['seeds']:
                worlds, streams = ed.world_catalog(seed, config), ed.shared_streams(seed, config)
                for name in WORLDS:
                    if time.perf_counter()-start > config['timeout_seconds']:
                        raise TimeoutError('internal deadline reached')
                    episode = episode_record(seed, name, worlds[name], streams, config)
                    text = json.dumps(episode, separators=(',', ':'), allow_nan=False)+'\n'
                    if sum(p.stat().st_size for p in output.iterdir() if p.is_file())+len(text.encode()) > config['max_output_bytes']-2000000:
                        raise RuntimeError('output cap reserve reached')
                    handle.write(text)
                    handle.flush()
                    episodes.append(episode)
        meta['status'] = 'completed'
    except Exception as exc:
        error = exc
        meta.update(status='failed_partial', error=type(exc).__name__+': '+str(exc))
    finally:
        meta['sources_unchanged'] = sources == source_hashes() and hashlib.sha256(config_path.read_bytes()).hexdigest() == config_hash
        if not meta['sources_unchanged']:
            meta['status'] = 'invalid_source_changed'
        expected = 5 if smoke else 500
        if len(episodes) != expected and meta['status'] == 'completed':
            meta['status'] = 'incomplete'
        summary = summarize(episodes, config)
        result = decision(summary, config, meta['status'] == 'completed' and not smoke)
        write('summary.json', summary)
        write('decision.json', result)
        meta.update(completed_episodes=len(episodes), expected_episodes=expected, completed_observations=len(episodes)*40,
                    elapsed_seconds=time.perf_counter()-start)
        meta['artifact_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()
                                  if p.is_file() and p.name != 'metadata.json'}
        other_bytes = sum(p.stat().st_size for p in output.iterdir() if p.is_file() and p.name != 'metadata.json')
        meta['artifact_bytes'] = 0
        for _ in range(20):
            if smoke:
                factor = config['smoke_safety_factor']*500/5
                meta.update(projected_full_seconds=factor*meta['elapsed_seconds'], projected_full_bytes=factor*meta['artifact_bytes'])
                meta['resource_go'] = (meta['status'] == 'completed' and meta['projected_full_seconds'] <= config['smoke_projection_limit_seconds']
                                       and meta['projected_full_bytes'] <= config['smoke_projection_limit_bytes'])
            size = other_bytes+len((json.dumps(meta, indent=2, allow_nan=False)+'\n').encode())
            if size == meta['artifact_bytes']:
                break
            meta['artifact_bytes'] = size
        else:
            raise RuntimeError('metadata byte count did not stabilize')
        write('metadata.json', meta)
    if error is not None:
        raise error
    if meta['status'] != 'completed':
        raise RuntimeError('run incomplete or invalid; see preserved records')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path('experiments/equation_confirmation_v0.json'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--smoke-evidence', type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.output, args.smoke, args.smoke_evidence), indent=2))
