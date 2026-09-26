# Equation discovery stage 1 — September 26, 2026

Completed100worlddatasets/400methodfits,4,000observations (24fit+16audit perworld). Clean sourcec0aa246; all74tests passed. Internal0.313633seconds, external0.344874seconds,1,870,359bytes. No settings changedafterresults. Independent audit reproduced all4,500model fits and allmetrics; maximum discrepancy1.46e-11.

**Recovery screen failed:** sparsefitter selected correctterms in20/20affine and15/20sparsequadraticworlds, but selected nonzeroformulas in9/20pure-noise worlds (45%, Wilson95interval25.8–65.8%), exceeding the8/20limit. Sparsequadraticfalseinclusion5/20passesitslimit. Noise-only maximum-weight heuristic is not calibrated confidence.

**Large-mismatch adequacy screen passed:** sparse equations rejected all20sine and20exponentialworlds, with0/20rejects ineachaffine/quadratic/noise family. This doesnotprove discovery: densequadraticfits rejectedonly1/20exponentialworlds despite mean extrapolationMSE0.99146; their interpolation latent-mean MSEwas0.00366 (auditMSE0.00659). Thus local adequacy doesnotestablisha globally correctlaw. Sparsefits' exponentialfailurealso reflects their3termcap.

Sparse mean interpolation/extrapolationMSE: affine0.000447/0.001922; sparsequadratic0.000515/0.015156; noise0.000352/0.010651. DensequadraticMSE0.001879/0.057885inbothin-classfamilies, becausepairednoise/design yieldsidenticalcoefficienterrors. Fullmetrics, perseedpairedcomparisons andWilsonintervals remainraw.

The fitter searches42combinations ofsixsuppliedmonomials and fitscoefficients. It constructs explicitformulas but doesnotinventoperators, variables ornewphysicalconcepts. SmallknownGaussian-noise systems anddesignedfamilies limitclaims. No scientificnovelty.

**Decision:** honor the predeclared stoprule; do not implementactiveacquisition orgrammarrevision now. Proposednextstudies: independent evidence fornonzeroterms (withoutchangingthisfitter), then a domainchallenge foracceptedpolynomialapproximations. Claude mustrevieweachplan andoutcome. Keepcurrentfailure, nottuneBICuntilitpasses.

Claude agrees that the preset failure stands. A rough independent-null heuristic predicted about37%nonzero selection, so9/20is unsurprising andnot evidenceofasoftwarebug; the40%screenwasapracticaltolerance,notacalibrationguarantee. Highsignal andsharedfamily noise/design limitrecovery claims.
