# M1a completed-enclosure audit — 2026-09-08

**Six numerical enclosures qualify under the frozen M1a geometry protocol.**
This read-only audit checked all 8,625 completed point receipts, their referenced
SHA-256 hashes, accepted five-point cell stencils, connectivity, exclusion-mask
dilation, and recorded bounds. No field values were reevaluated and no tests,
labels, source files, or experiment receipts were changed during the audit.

The encompassing label job subsequently reached its `600s` cap and exited
**124**. The eight-run input/label freeze remains incomplete. Completed geometry
does not establish completed labels, a passing calibration, or a qualified
detector. Preserve this attempt and its completed receipts; the root-owned
timeout/recovery record governs any separately bounded recovery.

Receipts are under
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_labels_v1/`, at
`geometry_{1,2,3}_sources/source_{1,2}/geometry.json`. Source 1 is local and
source 2 is global in each group. Each sibling `started.json` records its
source geometry, bounds, full contract and input/owner provenance.

| Group / source | Completed locations | Max dual uncertainty | Sampled barrier Δ | Positive cells | Positive hole cells | Exclusion hole cells | Region radius (m) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 / local | 1,382 | 4.57738e-7 | 0.0210160 | 165 | 88 | 24 | 0.460824 |
| 1 / global | 1,483 | 9.81182e-7 | 0.0474669 | 266 | 112 | 32 | 0.543026 |
| 2 / local | 1,382 | 4.60467e-7 | 0.0207621 | 164 | 88 | 24 | 0.458351 |
| 2 / global | 1,483 | 9.91392e-7 | 0.0473768 | 266 | 112 | 32 | 0.543026 |
| 3 / local | 1,412 | 4.31039e-7 | 0.0258556 | 195 | 88 | 24 | 0.478895 |
| 3 / global | 1,483 | 9.91683e-7 | 0.0474436 | 266 | 112 | 32 | 0.543026 |

Cost quantities retain the existing raw-cost units. Every point has two
qualified integrations, no warning and no exception. Global uncertainties
are close to the `1e-6` ceiling, particularly group 3; they pass without any
tolerance change. Sampled barriers exceed maximum numerical uncertainty by
approximately 45,089–59,984 times, versus the required strict ratio above 10.
The final sublevel-to-outer-boundary margins are `0.010381–0.012928` locally
and approximately `0.0237` globally. Both mean disagreement and QUADPACK error
estimates were inspected; these are numerical checks, not rigorous error bounds.

All grids lie completely inside the recorded `[-1,5] × [-1,5] m` domain:

| Grid | x extent (m) | y extent (m) | Derived area centroid (m) |
| --- | --- | --- | --- |
| 1 / local | [0.310660, 1.810660] | [0.310660, 1.810660] | (1.091484, 1.091484) |
| 2 / local | [-0.175975, 1.324025] | [0.635819, 2.135819] | (0.602036, 1.405827) |
| 3 / local | [0.133883, 1.633883] | [0.133883, 1.633883] | (0.910446, 0.910446) |
| All global grids | [2.750000, 4.250000] | [2.750000, 4.250000] | (3.497357, 3.497357) |

Each positive mask has one component connected through shared edges and one
bounded hole. Each low-vertex mask has one eight-neighbor component. Every
positive cell is contained in the exact incident-low-cell plus one-cell
Chebyshev exclusion mask. Dilation reduces the remaining holes rather than
filling them, as specified by the frozen negative-exclusion rule.

All six reported area centroids lie **inside their annular holes**, outside
the positive cell unions. They describe region geometry; they are neither
low-cost-point assertions nor target minima. Local centroids are displaced
`0.0344–0.0436 m` from their exploration seeds. The global masks share the same
finite-grid shape despite different underlying cost values. This is plausible
at the declared resolution, not evidence that the continuous fields coincide.

Grid spacing is `0.046875 m`, with a cell diagonal of approximately `0.0663 m`.
The checked cell centers/corners and outer witnesses do not certify every
unsampled spatial location. These remain **finite sampled operational
enclosures**, not continuous-domain barriers or formal attraction basins.

## Hash interpretation

- `provenance.contract_sha256` is the SHA-256 of the frozen JSON **file bytes**:
  `ae4a7fb242c20fb5f1ee410eb1bb261a12c49e9ee059d1567ff7d5ef733fb40f`.
- `canonical_contract_sha256` hashes compact, sorted-key JSON **content**:
  `702b127705e811e2d594229557b05ce207397e05b1066909fd948204b3ccb9e0`.

The distinct names and values are intentional. Every inspected enclosure
references the same frozen content. Its recorded numerical helper owner hash
is `d02cceb71cccca462b4eb350f7a8cb24bb605574888990ced2c923de5ef1e070`.
Each point is bound to its enclosure identity, and the final source receipt
lists each complete point file and its SHA-256. This audit verified those point
file hashes; it did not regenerate owner code or model/configuration files.

## Read-only reproduction

The audit used bounded Python reads of completed JSON receipts with NumPy and
`scipy.ndimage`; no evaluator or detector import is needed. The following
consolidates the performed hash, stencil, topology, bounds and numerical checks:

```bash
timeout 30s python3 - <<'PY'
import hashlib, json
from pathlib import Path
import numpy as np
from scipy.ndimage import binary_dilation, binary_fill_holes, label
root = Path('/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_labels_v1')
paths = sorted(root.glob('geometry_*_sources/source_*/geometry.json'))
assert len(paths) == 6
for path in paths:
    d = json.loads(path.read_text())
    started = json.loads((path.parent / 'started.json').read_text())
    assert d['qualified']
    points = {}
    for entry in d['point_receipts']:
        raw = Path(entry['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == entry['sha256']
        p = json.loads(raw)
        assert p['qualified']
        assert all(not q['warnings'] and q['exception'] is None for q in p['passes'])
        points[tuple(p['half_grid_index_xy'])] = p
    low = np.asarray(d['low_vertices'], bool)
    pos = np.asarray(d['positive_cells'], bool)
    neg = np.asarray(d['exclusion_cells'], bool)
    assert label(low, structure=np.ones((3, 3)))[1] == 1
    assert label(pos)[1] == 1
    T = d['final_level']['threshold']
    for y, x in np.argwhere(pos):
        keys = ((2*x,2*y), (2*x+2,2*y), (2*x,2*y+2),
                (2*x+2,2*y+2), (2*x+1,2*y+1))
        assert all(points[k]['mean'] + points[k]['uncertainty'] < T for k in keys)
    incident = low[:-1,:-1] | low[1:,:-1] | low[:-1,1:] | low[1:,1:]
    assert np.array_equal(neg, binary_dilation(incident, structure=np.ones((3,3))))
    assert np.all(neg[pos])
    origin = np.asarray(d['grid_origin_xy'])
    extent = origin + 32*d['grid_spacing_m']
    b = started['bounds_m']
    assert b[0] <= origin[0] and extent[0] <= b[1]
    assert b[2] <= origin[1] and extent[1] <= b[3]
    x, y = np.floor((np.asarray(d['center_xy'])-origin)/d['grid_spacing_m']).astype(int)
    assert not pos[y,x] and binary_fill_holes(pos)[y,x]
    print(path.parent, len(points), max(p['uncertainty'] for p in points.values()),
          d['final_level'], 'holes:', int((binary_fill_holes(pos) & ~pos).sum()))
PY
```

The performed read batches completed with exit 0. This document records
completed geometry evidence only; the timed-out label attempt remains incomplete.
