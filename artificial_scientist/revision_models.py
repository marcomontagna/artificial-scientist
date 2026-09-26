"""Safe vector programs and three bounded, supplied structure-edit families."""
import math
import time
from . import lab_models as old

VARIABLES=('p','v','u','lag_u','one','other_p','other_v','other_u','other_lag_u')
LIMIT=1000.


def restore(term):
    return tuple(restore(x) for x in term) if isinstance(term,(list,tuple)) else term


def nodes(term,depth=0):
    if depth>12:
        raise ValueError('expression nesting exceeds12')
    if isinstance(term,str):
        if term not in VARIABLES:
            raise ValueError('unknown variable')
        return 1
    if not isinstance(term,tuple) or not term or term[0] not in ('abs','positive','mul') or len(term)!=(3 if term[0]=='mul' else 2):
        raise ValueError('invalid expression')
    return 1+sum(nodes(x,depth+1) for x in term[1:])


def value(term,inputs):
    nodes(term)
    def run(t):
        if isinstance(t,str):
            result=inputs[t]
        elif t[0]=='abs':
            result=abs(run(t[1]))
        elif t[0]=='positive':
            result=max(0.,run(t[1]))
        else:
            result=run(t[1])*run(t[2])
        if not math.isfinite(result):
            raise ValueError('nonfinite feature')
        return max(-LIMIT,min(LIMIT,result))
    return run(term)


def inputs_for(pos,vel,push,lag,axis):
    other=1-axis
    return dict(p=pos[axis],v=vel[axis],u=push[axis],lag_u=lag[axis],one=1.,
                other_p=pos[other],other_v=vel[other],other_u=push[other],other_lag_u=lag[other])


class VectorModel:
    max_terms=4

    def __init__(self,terms,shared,coefficients):
        self.terms=tuple(restore(t) for t in terms)
        self.shared=shared
        if type(shared) is not bool or len(self.terms)>self.max_terms or sum(nodes(t) for t in self.terms)>40:
            raise ValueError('vector program exceeds declared budget')
        if len(set(self.terms))!=len(self.terms):
            raise ValueError('duplicate term')
        self.coefficients=tuple(coefficients) if shared else tuple(tuple(row) for row in coefficients)
        rows=(self.coefficients,) if shared else self.coefficients
        if len(rows)!=(1 if shared else 2) or any(len(row)!=len(self.terms) for row in rows):
            raise ValueError('coefficient dimensions differ')
        if not all(type(c) in (int,float) and math.isfinite(c) and abs(c)<=10 for row in rows for c in row):
            raise ValueError('invalid coefficient')

    @property
    def id(self):
        return ('shared:' if self.shared else 'untied:')+('+'.join(old.expression(t) for t in self.terms) or 'zero')

    @property
    def parameter_count(self):
        return len(self.terms)*(1 if self.shared else 2)

    @property
    def formula(self):
        rows=(self.coefficients,self.coefficients) if self.shared else self.coefficients
        return '; '.join('delta_'+axis+' = '+(' + '.join('%.6g*%s'%(c,old.expression(t)) for c,t in zip(row,self.terms)) or '0') for axis,row in zip(('x','y'),rows))

    def snapshot(self):
        return dict(id=self.id,terms=self.terms,shared=self.shared,coefficients=self.coefficients,
                    formula=self.formula,parameter_count=self.parameter_count)

    @classmethod
    def from_snapshot(cls,snapshot):
        return cls(snapshot['terms'],snapshot['shared'],snapshot['coefficients'])

    def predict_tape(self,observation,history,actions):
        previous=history[-1] if history else None
        pos=(observation.x,observation.y)
        vel=old.velocity(previous)
        lag=old.impulse(previous.action) if previous else (0.,0.)
        tape=[]
        rows=(self.coefficients,self.coefficients) if self.shared else self.coefficients
        for action in actions:
            action.validate()
            if action.kind=='reset':
                pos=vel=lag=(0.,0.)
            else:
                push=old.impulse(action)
                for tick in range(action.ticks if action.kind=='wait' else 1):
                    current=push if tick==0 else (0.,0.)
                    # Both axes read the same old vector state before either updates.
                    delta=tuple(max(-LIMIT,min(LIMIT,math.fsum(c*value(t,inputs_for(pos,vel,current,lag,axis)) for c,t in zip(rows[axis],self.terms)))) for axis in range(2))
                    pos=tuple(max(-LIMIT,min(LIMIT,p+d)) for p,d in zip(pos,delta))
                    vel=delta
                    lag=current
            tape.append(tuple(pos))
        return tape


class LinearReference(VectorModel):
    """Evaluator-only nine-variable reference; runtime model cap remains four."""
    max_terms=9


def training_rows(history):
    pairs=[]
    previous=None
    for transition in history:
        reliable=previous is None or previous.action.kind=='reset' or previous.after.tick-previous.before.tick==1
        if transition.action.kind!='reset' and transition.after.tick-transition.before.tick==1 and reliable:
            pos=(transition.before.x,transition.before.y)
            vel=old.velocity(previous)
            push=old.impulse(transition.action)
            lag=old.impulse(previous.action) if previous else (0.,0.)
            pairs.append(tuple((inputs_for(pos,vel,push,lag,axis),target-pos[axis]) for axis,target in enumerate((transition.after.x,transition.after.y))))
        previous=transition
    return pairs


def deadline_check(deadline):
    if time.process_time()>=deadline:
        raise TimeoutError('vector fitting CPU cap')


def solve(terms,rows,deadline,audit):
    n=len(terms)
    matrix=[[0.]*(n+1) for _ in range(n)]
    for inputs,target in rows:
        deadline_check(deadline)
        features=[value(t,inputs) for t in terms]
        audit['feature_evaluations']+=n
        for i in range(n):
            for j in range(n):
                matrix[i][j]+=features[i]*features[j]
            matrix[i][n]+=features[i]*target
    for i in range(n):
        matrix[i][i]+=1e-4
    for i in range(n):
        deadline_check(deadline)
        pivot=max(range(i,n),key=lambda j:abs(matrix[j][i]))
        matrix[i],matrix[pivot]=matrix[pivot],matrix[i]
        divisor=matrix[i][i]
        if abs(divisor)<1e-12 or not math.isfinite(divisor):
            raise ArithmeticError('invalid ridge pivot')
        matrix[i]=[v/divisor for v in matrix[i]]
        for j in range(n):
            if i!=j:
                factor=matrix[j][i]
                matrix[j]=[a-factor*b for a,b in zip(matrix[j],matrix[i])]
    coefficients=tuple(max(-10.,min(10.,matrix[i][n])) for i in range(n))
    if not all(math.isfinite(c) for c in coefficients):
        raise ArithmeticError('nonfinite ridge fit')
    return coefficients


def _fit(terms,shared,pairs,deadline,audit,cls=VectorModel):
    deadline_check(deadline)
    # Validate the structure before allocating fit work.
    cls(terms,shared,(0.,)*len(terms) if shared else ((0.,)*len(terms),)*2)
    audit['candidate_fits']+=1
    if shared:
        coefficients=solve(terms,[row for pair in pairs for row in pair],deadline,audit)
    else:
        coefficients=tuple(solve(terms,[pair[axis] for pair in pairs],deadline,audit) for axis in range(2))
    return cls(terms,shared,coefficients)


def fit_model(structure,history,deadline=float('inf'),audit=None):
    """Structure is a VectorModel or dict containing terms and shared."""
    audit={} if audit is None else audit
    audit.setdefault('candidate_fits',0)
    audit.setdefault('feature_evaluations',0)
    terms=structure.terms if isinstance(structure,VectorModel) else tuple(restore(t) for t in structure['terms'])
    shared=structure.shared if isinstance(structure,VectorModel) else structure['shared']
    return _fit(terms,shared,training_rows(history),deadline,audit)


def nonlinear_menu():
    return tuple(t for t in old.grammar() if not isinstance(t,str))+tuple(('mul',name,'other_'+name) for name in ('p','v','u'))


def propose(incumbent,history,deadline=float('inf'),audit=None):
    audit={} if audit is None else audit
    audit.update(candidate_fits=0,feature_evaluations=0,families=[],training_pairs=0)
    pairs=training_rows(history)
    audit['training_pairs']=len(pairs)
    families=[('unshare',[(incumbent.terms,False)] if incumbent.shared else [])]
    for family,menu in [('primitive',VARIABLES),('nonlinear',nonlinear_menu())]:
        edits=[(incumbent.terms+(term,),False) for term in menu if term not in incumbent.terms] if len(incumbent.terms)<4 else []
        families.append((family,edits))
    selected=[]
    for family,edits in families:
        scored=[]
        for terms,shared in edits:
            deadline_check(deadline)
            if sum(nodes(t) for t in terms)>40:
                continue
            model=_fit(terms,shared,pairs,deadline,audit)
            if model.id==incumbent.id:
                continue
            errors=[]
            coefficients=(model.coefficients,model.coefficients) if model.shared else model.coefficients
            for pair in pairs:
                deadline_check(deadline)
                errors.append(sum((math.fsum(c*value(t,inputs) for c,t in zip(coefficients[axis],terms))-target)**2 for axis,(inputs,target) in enumerate(pair)))
                audit['feature_evaluations']+=2*len(terms)
            mse=math.fsum(errors)/max(1,len(errors))
            scored.append((mse+1e-4*model.parameter_count,model.id,model,mse))
        scored.sort(key=lambda item:(item[0],item[1]))
        best=scored[0] if scored else None
        audit['families'].append(dict(family=family,candidates=len(scored),selected_model_id=best[1] if best else None,
                                      training_score=best[0] if best else None,training_mse=best[3] if best else None))
        if best and best[1] not in {m.id for m in selected}:
            selected.append(best[2])
    return selected,audit


def linear_reference(history,deadline=float('inf')):
    audit=dict(candidate_fits=0,feature_evaluations=0)
    return _fit(VARIABLES,False,training_rows(history),deadline,audit,LinearReference)
