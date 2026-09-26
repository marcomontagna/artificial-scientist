"""Residual-guided local proposals, not causal inference or human cognition."""
import itertools
import math
import time
from .lab_models import Model, complexity, expression, fit, grammar, program_id, value

PRIMITIVES = ('v', 'u', 'lag_u', 'p', 'one')


def _remove_span(values, basis, audit):
    projected = list(values)
    audit['projection_calls'] += 1
    for vector in basis:
        coefficient = sum(a*b for a,b in zip(projected,vector))
        projected = [a-coefficient*b for a,b in zip(projected,vector)]
    return projected


def _base_span(records, base_terms, centered, audit):
    """Small orthonormal design span; no fitted world model or hidden inputs."""
    basis = []
    for term in base_terms:
        column = [value(term,r['inputs']) for r in records]
        audit['projection_feature_evaluations'] += len(column)
        if centered and column:
            mean = sum(column)/len(column)
            column = [x-mean for x in column]
        # Two passes reduce loss of orthogonality for nearly dependent terms.
        for _ in range(2):
            column = _remove_span(column,basis,audit)
        norm = math.sqrt(sum(x*x for x in column))
        if norm > 1e-10:
            basis.append([x/norm for x in column])
    return basis


def _score(xs, residuals, constant=False):
    n = len(xs)
    if n < 3:
        return 0.0
    mr = sum(residuals)/n
    if constant:
        rms = math.sqrt(sum(r*r for r in residuals)/n)
        return mr/rms if rms > 1e-10 else 0.0
    mx = sum(xs)/n
    xx = sum((x-mx)**2 for x in xs)
    rr = sum((r-mr)**2 for r in residuals)
    denominator = math.sqrt(xx*rr)
    return sum((x-mx)*(r-mr) for x,r in zip(xs,residuals))/denominator if denominator>1e-10 else 0.0


def _association(term, evidence, audit, deadline, base_terms=(), partial=False, cache=None):
    """Coordinate-wise Pearson association; constant uses mean/RMS residual."""
    results = []
    for axis in ('x', 'y'):
        if time.process_time() >= deadline:
            raise TimeoutError('guided feature screening CPU cap')
        records = [r for r in evidence if r['axis'] == axis]
        xs = []
        for record in records:
            xs.append(value(term, record['inputs']))
            audit['feature_evaluations'] += 1
        residuals = [r['residual'] for r in records]
        n = len(records)
        raw_score = _score(xs,residuals,term=='one')
        score = raw_score
        if partial and base_terms and n >= 3:
            centered = term != 'one'
            key = (axis,centered)
            if key not in cache:
                cache[key] = _base_span(records,base_terms,centered,audit)
            basis = cache[key]
            if term == 'one':
                score = 0.0 if 'one' in base_terms else _score(xs,_remove_span(residuals,basis,audit),True)
            else:
                mx,mr = sum(xs)/n,sum(residuals)/n
                xp = _remove_span([x-mx for x in xs],basis,audit)
                rp = _remove_span([r-mr for r in residuals],basis,audit)
                score = _score(xp,rp)
        results.append(dict(feature=expression(term), axis=axis, count=n, raw_score=max(-1.0,min(1.0,raw_score)),
                            conditioning_terms=[expression(t) for t in base_terms] if partial else [],
                            score=max(-1.0, min(1.0, score)),
                            shares_sensor_inputs=('p' in expression(term) or 'v' in expression(term))))
    audit['diagnosis']['associations'].extend(results)
    return max(abs(r['score']) for r in results)


def guided_propose(rows, excluded, base, residual_records, escape_cursor=0,
                   count=2, deadline=float('inf'), audit=None, partial=False):
    """At most seven guided fits and one escape fit; diagnostic budget 20 term features.

    Evidence consists only of past outcomes minus predictions frozen before
    those outcomes, for the selected incumbent structure. Coefficient versions
    remain explicit because structure scores describe an updating procedure.
    """
    if audit is None:
        audit = {}
    evidence = [dict(r) for r in residual_records if r['model_id'] == base.id][-24:]
    audit.update(mode='guided-partial' if partial else 'guided', candidate_fits=0, feature_evaluations=0, projection_feature_evaluations=0, projection_calls=0,
                 diagnosis=dict(base_model_id=base.id, evidence=evidence, associations=[],
                                selected_features=[], reason='Association suggests candidates; it does not establish a mechanism.'),
                 candidates=[], rejected_by_size=0, excluded_edits=0, escape_cursor_before=escape_cursor)
    atoms = grammar()
    order = {expression(t): i for i, t in enumerate(atoms)}
    canonical = lambda terms: tuple(sorted(terms, key=lambda t: order[expression(t)]))
    # Cheap correlations screen individual features, not complete fitted
    # formulas. Screening all 20 features avoids a main-effect-only blind spot.
    projection_cache = {}
    scored = [(term, _association(term, evidence, audit, deadline, base.terms, partial, projection_cache)) for term in atoms]
    scored = [(term, score) for term, score in scored if score >= 0.25]
    scored.sort(key=lambda item: (-item[1], order[expression(item[0])]))
    audit['diagnosis']['selected_features'] = [expression(t) for t, _ in scored]
    shortlist, ids = [], set()
    for term, score in scored:
        edits = []
        if term not in base.terms:
            if len(base.terms) < 2:
                edits.append(base.terms + (term,))
            edits += [base.terms[:i] + (term,) + base.terms[i+1:] for i in range(len(base.terms))]
        for edited in edits:
            chosen = canonical(edited)
            ident = program_id(chosen)
            if complexity(chosen) > 12:
                audit['rejected_by_size'] += 1
            elif ident in excluded or ident in ids:
                audit['excluded_edits'] += 1
            else:
                shortlist.append((chosen, 'residual_association', expression(term), score))
                ids.add(ident)
                if len(shortlist) == 7:
                    break
        if len(shortlist) == 7:
            break
    # One rotating, explicitly unguided structural escape. Listing structures
    # performs no coefficient fits or in-sample scoring of excluded candidates.
    catalogue = [c for size in (1, 2) for c in itertools.combinations(atoms, size) if complexity(c) <= 12]
    scanned = 0
    while scanned < len(catalogue):
        chosen = catalogue[escape_cursor % len(catalogue)]
        escape_cursor += 1
        scanned += 1
        if program_id(chosen) not in excluded and program_id(chosen) not in ids:
            shortlist.append((chosen, 'scheduled_escape', None, None)); break
    audit['escape_structures_checked'] = scanned
    audit['escape_cursor_after'] = escape_cursor
    # The complete shortlist is fixed BEFORE any coefficient fitting.
    audit['diagnosis']['reason'] = ('Associations suggest local edits, not mechanisms; noise and adaptive sampling can create them.' if scored else 'No association above threshold or insufficient same-incumbent evidence; only scheduled escape is eligible.')
    audit['no_candidates'] = not shortlist
    audit['shortlist'] = [program_id(item[0]) for item in shortlist]
    candidates = []
    for chosen, origin, feature, score in shortlist:
        if time.process_time() >= deadline:
            raise TimeoutError('guided fitting CPU cap')
        audit['candidate_fits'] += 1
        coefficients = fit(chosen, rows)
        error = sum((sum(c*value(t, inputs) for c, t in zip(coefficients, chosen))-target)**2 for inputs, target in rows) / max(1, len(rows))
        model = Model(chosen, coefficients)
        candidate = dict(model_id=model.id, origin=origin, feature=feature,
                         association_score=score, training_score=error+0.0001*complexity(chosen), selected=False)
        audit['candidates'].append(candidate)
        candidates.append((candidate['training_score'], model.id, model, candidate))
    candidates.sort(key=lambda item: (item[0], item[1]))
    for _, _, _, record in candidates[:count]:
        record['selected'] = True
    return [item[2] for item in candidates[:count]], escape_cursor
