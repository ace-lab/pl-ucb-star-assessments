/* ---------------------------------------------------------------------------
 * STAR: fitting a transformed parent function to traced points.
 *
 * Ported from the Sketch to Graph prototype. Pure math, no network, no model.
 *
 * Two ideas carry the whole thing:
 *
 *  1. Each family is linear in its coefficients once its one non-linear
 *     parameter is fixed (the period of a sine, the pole of a rational, the
 *     shift of a log). So we grid-search that parameter and solve least
 *     squares for the rest at each step. Cheap, and no optimiser needed.
 *
 *  2. Choosing between families is not "lowest error wins". A degree-10
 *     polynomial can thread any hand-drawn wobble, and that is exactly the
 *     failure we do not want. Each family carries a cost in how unlikely a
 *     student is to have drawn it, and among fits that are close enough, the
 *     cheapest one wins.
 * ------------------------------------------------------------------------- */

(function (root) {
  'use strict'

  // Weighted least squares by Gauss-Jordan on the normal equations, with a
  // small ridge term so a near-singular basis does not blow up.
  function solveLS (rows, rhs, w) {
    const n = rows[0].length
    const A = Array.from({ length: n }, () => new Float64Array(n + 1))
    rows.forEach((r, i) => {
      const ww = w[i] * w[i]
      for (let a = 0; a < n; a++) {
        if (!r[a]) continue
        for (let b = 0; b < n; b++) A[a][b] += ww * r[a] * r[b]
        A[a][n] += ww * r[a] * rhs[i]
      }
    })
    let tr = 0
    for (let a = 0; a < n; a++) tr += A[a][a]
    for (let a = 0; a < n; a++) A[a][a] += 1e-11 * tr + 1e-14
    for (let c = 0; c < n; c++) {
      let pv = c
      for (let r = c + 1; r < n; r++) if (Math.abs(A[r][c]) > Math.abs(A[pv][c])) pv = r
      const tmp = A[c]
      A[c] = A[pv]
      A[pv] = tmp
      const d = A[c][c] || 1e-14
      for (let r = 0; r < n; r++) {
        if (r === c) continue
        const f = A[r][c] / d
        if (f) for (let k = c; k <= n; k++) A[r][k] -= f * A[c][k]
      }
    }
    return A.map((r, i) => r[n] / (r[i] || 1e-14))
  }

  const g3 = (v) => {
    if (!isFinite(v)) return '0'
    const a = Math.abs(v)
    return a >= 1000 || (a < 0.001 && a > 0) ? v.toPrecision(3) : String(+v.toPrecision(4))
  }

  // Cost = how unlikely a student is to have drawn it, in parameter-equivalents.
  const FAMS = {
    polynomial: { cost: (d) => (d <= 3 ? d : d === 4 ? 5 : d === 5 ? 6.5 : 8.5) },
    sine: { cost: () => 3.5 },
    exponential: { cost: () => 4 },
    sqrt: { cost: () => 4.5 },
    logarithmic: { cost: () => 4.5 },
    abs: { cost: () => 4.5 },
    rational: { cost: () => 5.5 },
    tan: { cost: () => 6.5 }
  }
  const FAM_LABEL = {
    trace: 'traced shape',
    polynomial: 'polynomial',
    sine: 'sine wave',
    exponential: 'exponential',
    sqrt: 'square root',
    logarithmic: 'logarithm',
    abs: 'absolute value',
    rational: 'rational (1/x type)',
    tan: 'tangent'
  }

  function fitModel (spec, pts) {
    const xs = pts.map((p) => p[0])
    let lo = Math.min.apply(null, xs)
    let hi = Math.max.apply(null, xs)
    if (
      Array.isArray(spec.domain) &&
      spec.domain.length === 2 &&
      spec.domain.every(Number.isFinite) &&
      spec.domain[1] > spec.domain[0]
    ) {
      lo = spec.domain[0]
      hi = spec.domain[1]
    }
    const span = hi - lo || 1
    const ys = pts.map((p) => p[1])
    const yspan = Math.max.apply(null, ys) - Math.min.apply(null, ys) || 1
    const tw = Math.max(0.02, Math.min(1, spec.traceWeight == null ? 1 : spec.traceWeight))
    const cons = (spec.constraints || []).filter((c) => Number.isFinite(c.x))
    const wc = 60 * Math.sqrt(pts.length) // constraints outweigh the trace
    const BIG = 1e6

    // B: basis functions, D1/D2: their derivatives (so a slope or inflection
    // constraint is just another linear row), valid: domain guard.
    const lsq = (B, D1, D2, valid) => {
      const rows = []
      const rhs = []
      const w = []
      const ok = (x) => (!valid || valid(x)) && B(x).every(Number.isFinite)
      pts.forEach((p) => {
        if (!ok(p[0])) return
        rows.push(B(p[0]))
        rhs.push(p[1])
        w.push(tw)
      })
      if (rows.length < 2) return null
      cons.forEach((c) => {
        if (!ok(c.x)) return
        if (c.type === 'point' && Number.isFinite(c.y)) {
          rows.push(B(c.x))
          rhs.push(c.y)
          w.push(wc)
        } else if (c.type === 'slope' && Number.isFinite(c.slope)) {
          rows.push(D1(c.x))
          rhs.push(c.slope)
          w.push(wc)
        } else if (c.type === 'inflection') {
          rows.push(D2(c.x))
          rhs.push(0)
          w.push(wc)
        }
      })
      const coef = solveLS(rows, rhs, w)
      if (coef.some((q) => !Number.isFinite(q))) return null
      const f = (x) => {
        if (valid && !valid(x)) return NaN
        const v = B(x).reduce((a, b, k) => a + b * coef[k], 0)
        return Math.abs(v) > BIG ? NaN : v
      }
      let se = 0
      let n = 0
      pts.forEach((p) => {
        const v = f(p[0])
        if (Number.isFinite(v)) {
          se += (v - p[1]) * (v - p[1])
          n++
        }
      })
      // A stroke represents one complete branch. Scoring only the points a
      // model accepts lets a short, flat fragment beat a faithful full fit.
      if (n < 4 || n !== pts.length) return null
      const rmse = Math.sqrt(se / n)
      const cerr = cons.reduce(
        (a, c) => a + (c.type === 'point' && Number.isFinite(f(c.x)) ? Math.abs(f(c.x) - c.y) : 0),
        0
      )
      return { coef, f, rmse, cerr, valid: valid || (() => true) }
    }

    const score = (m) => m.rmse + m.cerr
    const search = (grid, mk) => {
      let best = null
      grid.forEach((nl) => {
        const m = mk(nl)
        if (m && (!best || score(m) < score(best))) best = Object.assign({}, m, { nl })
      })
      return best
    }
    // Coarse grid, then zoom: an asymptote at 1.5 should not be reported as 1.56.
    const search1 = (vals, mk, fixed) => {
      fixed = fixed || []
      let best = null
      let bi = 0
      vals.forEach((v, i) => {
        const m = mk([v].concat(fixed))
        if (m && (!best || score(m) < score(best))) {
          best = Object.assign({}, m, { nl: [v].concat(fixed) })
          bi = i
        }
      })
      if (!best) return null
      let a = vals[Math.max(0, bi - 1)]
      let b = vals[Math.min(vals.length - 1, bi + 1)]
      for (let pass = 0; pass < 3; pass++) {
        let bv = best.nl[0]
        for (let k = 0; k <= 12; k++) {
          const v = a + ((b - a) * k) / 12
          const m = mk([v].concat(fixed))
          if (m && score(m) < score(best)) {
            best = Object.assign({}, m, { nl: [v].concat(fixed) })
            bv = v
          }
        }
        const step = (b - a) / 12
        a = bv - step
        b = bv + step
      }
      return best
    }
    const lin = (a, b) => Array.from({ length: 41 }, (_, k) => a + ((b - a) * k) / 40)

    let r = null
    let fam = spec.family || 'polynomial'
    let extra = {}

    if (fam === 'sine' || fam === 'tan') {
      const periods =
        Number.isFinite(spec.period) && spec.period > 0
          ? [spec.period]
          : Array.from({ length: 60 }, (_, k) => (span / 8) * Math.pow(24, k / 59))
      const grid = []
      periods.forEach((P) => {
        if (fam === 'sine') grid.push([P, 0])
        else for (let k = 0; k < 16; k++) grid.push([P, lo + (P * k) / 16])
      })
      const mkTrig = (nl) => {
        const P = nl[0]
        const sh = nl[1]
        const b = (Math.PI * (fam === 'sine' ? 2 : 1)) / P
        if (fam === 'sine') {
          return lsq(
            (x) => [Math.sin(b * x), Math.cos(b * x), 1],
            (x) => [b * Math.cos(b * x), -b * Math.sin(b * x), 0],
            (x) => [-b * b * Math.sin(b * x), -b * b * Math.cos(b * x), 0]
          )
        }
        const u = (x) => b * (x - sh)
        const okx = (x) => Math.abs(Math.cos(u(x))) > 0.18
        return lsq(
          (x) => [Math.tan(u(x)), 1],
          (x) => [b / Math.pow(Math.cos(u(x)), 2), 0],
          (x) => [(2 * b * b * Math.tan(u(x))) / Math.pow(Math.cos(u(x)), 2), 0],
          okx
        )
      }
      r = search(grid, mkTrig)
      if (r && periods.length > 1) {
        const around = periods.filter((P) => P > r.nl[0] / 2 && P < r.nl[0] * 2)
        const rr = search1(around.length > 2 ? around : periods, mkTrig, [r.nl[1]])
        if (rr && rr.rmse + rr.cerr < r.rmse + r.cerr) r = rr
      }
      if (r) {
        const P = r.nl[0]
        const sh = r.nl[1]
        const b = (Math.PI * (fam === 'sine' ? 2 : 1)) / P
        if (fam === 'sine') {
          const pp = r.coef[0]
          const qq = r.coef[1]
          const dd = r.coef[2]
          const A = Math.hypot(pp, qq)
          const ph = Math.atan2(qq, pp)
          extra = {
            period: P,
            expr: `y = ${g3(A)}sin(${g3(b)}x ${ph < 0 ? '-' : '+'} ${g3(Math.abs(ph))}) ${dd < 0 ? '-' : '+'} ${g3(Math.abs(dd))}`,
            poles: []
          }
        } else {
          const poles = []
          for (
            let k = Math.floor((b * (lo - sh) - Math.PI / 2) / Math.PI) - 1;
            k <= Math.ceil((b * (hi - sh) + Math.PI / 2) / Math.PI) + 1;
            k++
          ) {
            const xp = sh + (Math.PI / 2 + k * Math.PI) / b
            if (xp > lo && xp < hi) poles.push(xp)
          }
          extra = {
            period: P,
            shift: sh,
            expr: `y = ${g3(r.coef[0])}tan(${g3(b)}(x ${sh < 0 ? '+' : '-'} ${g3(Math.abs(sh))})) ${r.coef[1] < 0 ? '-' : '+'} ${g3(Math.abs(r.coef[1]))}`,
            poles
          }
        }
      }
    } else if (fam === 'exponential') {
      const ks =
        Number.isFinite(spec.rate) && spec.rate !== 0
          ? [spec.rate]
          : lin(-6 / span, 6 / span).filter((k) => Math.abs(k) > 0.15 / span)
      r = search1(ks, (nl) => {
        const k = nl[0]
        return lsq(
          (x) => [Math.exp(k * (x - lo)), 1],
          (x) => [k * Math.exp(k * (x - lo)), 0],
          (x) => [k * k * Math.exp(k * (x - lo)), 0]
        )
      })
      if (r) {
        const k = r.nl[0]
        const A = r.coef[0] * Math.exp(-k * lo)
        extra = {
          rate: k,
          expr: `y = ${g3(A)}e^(${g3(k)}x) ${r.coef[1] < 0 ? '-' : '+'} ${g3(Math.abs(r.coef[1]))}`,
          poles: [],
          asymY: r.coef[1]
        }
      }
    } else if (fam === 'logarithmic' || fam === 'sqrt') {
      const ps = Number.isFinite(spec.shift)
        ? [spec.shift]
        : Array.from({ length: 36 }, (_, k) => lo - span * 0.01 * Math.pow(300, k / 35))
      const sq = fam === 'sqrt'
      r = search1(ps, (nl) => {
        const q = nl[0]
        return lsq(
          (x) => [sq ? Math.sqrt(x - q) : Math.log(x - q), 1],
          (x) => [sq ? 0.5 / Math.sqrt(x - q) : 1 / (x - q), 0],
          (x) => [sq ? -0.25 / Math.pow(x - q, 1.5) : -1 / ((x - q) * (x - q)), 0],
          (x) => x - q > span * 0.002
        )
      })
      if (r) {
        const q = r.nl[0]
        const sgn = q < 0 ? '+' : '-'
        extra = {
          shift: q,
          expr: `y = ${g3(r.coef[0])}${sq ? '√' : 'ln'}(x ${sgn} ${g3(Math.abs(q))}) ${r.coef[1] < 0 ? '-' : '+'} ${g3(Math.abs(r.coef[1]))}`,
          poles: [],
          domainFrom: q
        }
      }
    } else if (fam === 'rational') {
      const ps = Number.isFinite(spec.shift) ? [spec.shift] : lin(lo - span * 0.3, hi + span * 0.3)
      r = search1(ps, (nl) => {
        const q = nl[0]
        return lsq(
          (x) => [1 / (x - q), 1],
          (x) => [-1 / ((x - q) * (x - q)), 0],
          (x) => [2 / Math.pow(x - q, 3), 0],
          (x) => Math.abs(x - q) > span * 0.02
        )
      })
      if (r) {
        const q = r.nl[0]
        const sgn = q < 0 ? '+' : '-'
        extra = {
          shift: q,
          expr: `y = ${g3(r.coef[0])}/(x ${sgn} ${g3(Math.abs(q))}) ${r.coef[1] < 0 ? '-' : '+'} ${g3(Math.abs(r.coef[1]))}`,
          poles: q > lo && q < hi ? [q] : [],
          asymY: r.coef[1]
        }
      }
    } else if (fam === 'abs') {
      const ps = Number.isFinite(spec.shift) ? [spec.shift] : lin(lo, hi)
      r = search1(ps, (nl) => {
        const q = nl[0]
        return lsq(
          (x) => [Math.abs(x - q), 1],
          (x) => [Math.sign(x - q), 0],
          () => [0, 0]
        )
      })
      if (r) {
        const q = r.nl[0]
        const sgn = q < 0 ? '+' : '-'
        extra = {
          shift: q,
          expr: `y = ${g3(r.coef[0])}|x ${sgn} ${g3(Math.abs(q))}| ${r.coef[1] < 0 ? '-' : '+'} ${g3(Math.abs(r.coef[1]))}`,
          poles: []
        }
      }
    }

    if (!r) {
      // Polynomial, and the fallback when a named family could not be fitted.
      fam = 'polynomial'
      const deg = Math.max(1, Math.min(6, Math.round(spec.degree == null ? 3 : spec.degree)))
      // Scale x before taking powers, or x^6 overflows the solver on a wide domain.
      const s = Math.max.apply(null, [1e-9].concat(xs.map(Math.abs), [Math.abs(lo), Math.abs(hi)]))
      r = lsq(
        (x) => Array.from({ length: deg + 1 }, (_, k) => Math.pow(x / s, k)),
        (x) => Array.from({ length: deg + 1 }, (_, k) => (k ? (k * Math.pow(x / s, k - 1)) / s : 0)),
        (x) => Array.from({ length: deg + 1 }, (_, k) => (k > 1 ? (k * (k - 1) * Math.pow(x / s, k - 2)) / (s * s) : 0))
      )
      if (!r) return null
      const a = r.coef.map((c, k) => c / Math.pow(s, k))
      const mx = Math.max.apply(null, a.map(Math.abs)) || 1
      const terms = []
      for (let k = deg; k >= 0; k--) {
        if (Math.abs(a[k]) < mx * 1e-6) continue
        const sg = a[k] < 0 ? '-' : '+'
        const m = g3(Math.abs(a[k]))
        terms.push({ sg, t: (k === 0 ? m : m === '1' ? '' : m) + (k === 0 ? '' : k === 1 ? 'x' : 'x^' + k) })
      }
      extra = {
        degree: deg,
        expr: 'y = ' + (terms.length ? terms.map((t, i) => (i ? ` ${t.sg} ` : t.sg === '-' ? '-' : '') + t.t).join('') : '0'),
        poles: []
      }
    }

    const out = Object.assign({}, r, extra, {
      family: fam,
      lo,
      hi,
      span,
      yspan,
      label: FAM_LABEL[fam],
      cost: FAMS[fam].cost(extra.degree == null ? 3 : extra.degree)
    })
    if (!out.poles) out.poles = []
    // A pole inside a continuous stroke would join disconnected intervals,
    // even when it happens to fall between the supplied trace points.
    if (out.poles.some((p) => p > lo && p < hi)) return null
    return out
  }

  // Pick the simplest believable curve: a near-perfect degree-10 loses to a
  // close-enough cubic.
  function autoSpec (pts) {
    const n = pts.length
    const ys = pts.map((p) => p[1])
    const span = Math.max.apply(null, ys) - Math.min.apply(null, ys) || 1
    const cands = []
    for (let d = 1; d <= Math.min(6, Math.max(1, n - 4)); d++) {
      cands.push({ family: 'polynomial', degree: d, constraints: [], traceWeight: 1 })
    }
    ['sine', 'exponential', 'sqrt', 'logarithmic', 'abs', 'rational', 'tan'].forEach((f) => {
      if (n > 10) cands.push({ family: f, constraints: [], traceWeight: 1 })
    })
    const fits = cands
      .map((sp) => {
        let m = null
        try {
          m = fitModel(sp, pts)
        } catch (e) {
          m = null
        }
        return m ? { sp, rmse: m.rmse, cost: m.cost } : null
      })
      .filter(Boolean)
    if (!fits.length) return { family: 'polynomial', degree: 3, constraints: [], traceWeight: 1 }
    const best = Math.min.apply(null, fits.map((q) => q.rmse))
    // How shaky is the hand-drawn line itself? No model should be asked to beat that.
    const srt = pts.slice().sort((a, b) => a[0] - b[0])
    const dd = []
    for (let i = 1; i < srt.length - 1; i++) {
      const v = Math.abs(srt[i][1] - (srt[i - 1][1] + srt[i + 1][1]) / 2)
      if (Number.isFinite(v)) dd.push(v)
    }
    dd.sort((a, b) => a - b)
    const noise = dd.length ? dd[Math.floor(dd.length / 2)] * 1.2 : 0
    const tol = Math.max(best * 1.3, noise * 1.3, best + span * 0.002)
    const ok = fits.filter((q) => q.rmse <= tol)
    ok.sort((a, b) => a.cost - b.cost || a.rmse - b.rmse)
    return ok[0].sp
  }

  function fit (pts, spec) {
    if (spec && spec.family === 'trace') return traceModel(pts)
    const chosen = spec || autoSpec(pts)
    const model = fitModel(chosen, pts)
    if (!model) return null
    model.spec = chosen
    return model
  }

  // Ramer-Douglas-Peucker in photo pixels: remove small ink/sampling wobble
  // without averaging across a peak or replacing a piecewise shape by a formula.
  function simplifyTrace (points, tolerance) {
    if (points.length < 3) return points.map(p => p.slice())
    const keep = new Set([0, points.length - 1])
    const pending = [[0, points.length - 1]]
    while (pending.length) {
      const [first, last] = pending.pop()
      const a = points[first]
      const b = points[last]
      const dx = b[0] - a[0]
      const dy = b[1] - a[1]
      const length2 = dx * dx + dy * dy
      let maximum = tolerance * tolerance
      let index = -1
      for (let i = first + 1; i < last; i++) {
        const p = points[i]
        const t = length2 ? Math.max(0, Math.min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / length2)) : 0
        const distance2 = (p[0] - a[0] - t * dx) ** 2 + (p[1] - a[1] - t * dy) ** 2
        if (distance2 > maximum) { maximum = distance2; index = i }
      }
      if (index !== -1) {
        keep.add(index)
        pending.push([first, index], [index, last])
      }
    }
    return [...keep].sort((a, b) => a - b).map(i => points[i].slice())
  }

  function traceModel (pts) {
    if (!Array.isArray(pts) || pts.length < 2 || pts.some((p, i) =>
      !Array.isArray(p) || p.length !== 2 || !p.every(Number.isFinite) || (i && p[0] <= pts[i - 1][0]))) {
      throw new Error('A traced branch needs increasing, distinct x positions.')
    }
    const points = pts.map(p => p.slice())
    const lo = points[0][0]
    const hi = points[points.length - 1][0]
    const f = x => {
      if (!Number.isFinite(x) || x < lo || x > hi) return NaN
      let left = 0
      let right = points.length - 1
      while (right - left > 1) {
        const middle = (left + right) >> 1
        if (points[middle][0] <= x) left = middle
        else right = middle
      }
      const a = points[left]
      const b = points[right]
      return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0])
    }
    return { family: 'trace', label: FAM_LABEL.trace, expr: 'Traced shape (no fitted equation)', points, lo, hi, f, rmse: 0, poles: [], spec: { family: 'trace' } }
  }

  /* --- pl-sketch interop ------------------------------------------------- */

  // pl-sketch's `function` attribute wants a Python expression in x, limited to
  // + - * / **, parentheses, e and pi, and a fixed list of calls. Our equation
  // strings are in human notation, so translate.
  function toPlFunction (equation) {
    let s = String(equation).trim()
    s = s.replace(/^\s*y\s*=\s*/, '')
    s = s.replace(/√/g, 'sqrt')
    s = s.replace(/(?<![A-Za-z])ln\s*\(/g, 'log(')
    let guard = 0
    while (s.indexOf('|') !== -1 && guard++ < 20) {
      s = s.replace(/\|([^|]*)\|/, 'abs($1)')
    }
    s = s.replace(/\^/g, '**')
    s = s.replace(/(\d)\s*([A-Za-z(])/g, '$1*$2')
    s = s.replace(/(\))\s*([A-Za-z0-9(])/g, '$1*$2')
    s = s.replace(/\bx\s*\(/g, 'x*(')
    s = s.replace(/\*\*\*/g, '**')
    return s.replace(/\s+/g, ' ').trim()
  }

  // pl-sketch draws a function as one continuous line, so a curve with poles
  // has to be handed over as several intervals.
  function splitDomainAtPoles (lo, hi, poles, gap) {
    gap = gap || 1e-3
    const cuts = (poles || []).filter((p) => p > lo && p < hi).sort((a, b) => a - b)
    const spans = []
    let start = lo
    cuts.forEach((p) => {
      spans.push([start, p - gap])
      start = p + gap
    })
    spans.push([start, hi])
    return spans.filter((s) => s[1] - s[0] > gap * 10)
  }

  // Sample the fitted function into points, which is what a spline on the
  // canvas is made of.
  function sampleCurve (model, n) {
    if (model.family === 'trace') return model.points.map(p => p.slice())
    n = n || 60
    const out = []
    for (let i = 0; i <= n; i++) {
      const x = model.lo + ((model.hi - model.lo) * i) / n
      const y = model.f(x)
      if (Number.isFinite(y)) out.push([Math.round(x * 1000) / 1000, Math.round(y * 1000) / 1000])
    }
    return out
  }

  /* --- putting a curve onto a live canvas -------------------------------- */

  // SketchResponse stores plugin state in SVG PIXEL coordinates, not graph
  // coordinates. This is the same mapping the element's Python uses on the way
  // in (sketchresponse.utils.graph_to_screen):
  //     px = (value - start) * canvas_size / (end - start)
  // with y inverted, because SVG y grows downward. config.xrange/yrange are
  // already the padded ranges the server computed, so no margin maths here.
  function graphToPixels (config, points) {
    const x0 = config.xrange[0]
    const x1 = config.xrange[1]
    const y0 = config.yrange[0]
    const y1 = config.yrange[1]
    return points.map((p) => ({
      x: ((p[0] - x0) * config.width) / (x1 - x0),
      y: ((p[1] - y1) * config.height) / (y0 - y1)
    }))
  }

  // Replace one tool's drawing atomically, preserving each branch as a separate
  // spline. Validate every branch before touching the live canvas.
  function placeCurves (si, config, toolId, curves, options) {
    if (!Array.isArray(curves) || !curves.length || curves.some((points) =>
      !Array.isArray(points) || points.length < 2 || points.some((p) =>
        !Array.isArray(p) || p.length !== 2 || !p.every(Number.isFinite)))) {
      throw new Error('Every branch needs at least two finite points.')
    }
    const state = JSON.parse(si.getState())
    const plugin = (config.plugins || []).find(p => p.id === toolId)
    state.data[toolId] = curves.map((points, i) => {
      let pixels = graphToPixels(config, points)
      if (plugin && plugin.name === 'freeform') {
        // Freeform stores cubic controls, rather than spline interpolation points.
        const controls = [pixels[0]]
        for (let j = 1; j < pixels.length; j++) {
          const a = pixels[j - 1]
          const b = pixels[j]
          for (let k = 1; k <= 3; k++) controls.push({ x: a.x + (b.x - a.x) * k / 3, y: a.y + (b.y - a.y) * k / 3 })
        }
        return controls
      }
      if (options && options.preserveCorners && options.preserveCorners[i]) pixels = cornerAnchors(pixels)
      return pixels
    })
    si.setState(JSON.stringify(state))
  }

  // Native splines interpolate their anchors but smooth the tangent at a corner.
  // Short supports confine that rounding to a few SVG pixels. Twelve pixels
  // also separates handles on long edges (native hit targets have radius 8).
  // The same anchors drive rendering, editing, serialization and grading.
  function cornerAnchors (points) {
    const out = [points[0]]
    for (let i = 1; i < points.length - 1; i++) {
      const a = points[i - 1]
      const p = points[i]
      const b = points[i + 1]
      const before = Math.hypot(a.x - p.x, a.y - p.y)
      const after = Math.hypot(b.x - p.x, b.y - p.y)
      if (!before || !after) continue
      const distance = Math.min(12, before / 4, after / 4)
      out.push({ x: p.x + (a.x - p.x) * distance / before, y: p.y + (a.y - p.y) * distance / before },
        p, { x: p.x + (b.x - p.x) * distance / after, y: p.y + (b.y - p.y) * distance / after })
    }
    out.push(points[points.length - 1])
    return out
  }

  // Retain the single-curve helper for existing callers.
  function placeCurve (si, config, toolId, points) {
    placeCurves(si, config, toolId, [points])
  }

  // Which tool should receive the curve: the first editable curve-drawing tool
  // in the toolbar.
  function curveToolId (config) {
    const plugins = (config && config.plugins) || []
    const curveTypes = ['spline', 'polyline', 'freeform']
    for (let i = 0; i < plugins.length; i++) {
      const p = plugins[i]
      if (curveTypes.indexOf(p.name) !== -1 && !p.readonly) return p.id
    }
    return null
  }

  const api = {
    graphToPixels,
    placeCurve,
    placeCurves,
    curveToolId,
    fit,
    fitModel,
    autoSpec,
    toPlFunction,
    splitDomainAtPoles,
    sampleCurve,
    simplifyTrace,
    FAM_LABEL
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = api
  else root.StarFit = api
})(typeof window !== 'undefined' ? window : this)
