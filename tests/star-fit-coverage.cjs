const { test } = require('node:test')
const assert = require('node:assert/strict')
const { fit, fitModel, sampleCurve } = require('../elements/pl-sketch-extension/star-fit.js')

const points = (lo, hi, f) => Array.from({ length: 81 }, (_, i) => {
  const x = lo + (hi - lo) * i / 80
  return [x, f(x)]
})

for (const [name, lo, hi] of [['left', -5, -1.08], ['right', 1.08, 5]]) {
  test('the ' + name + ' steep branch cannot be replaced by a flat partial fit', () => {
    const trace = points(lo, hi, x => 0.8 / (1 - x * x))
    const model = fit(trace)
    assert.ok(model)
    assert.equal(model.lo, trace[0][0])
    assert.equal(model.hi, trace.at(-1)[0])
    assert.ok(trace.every(([x]) => Number.isFinite(model.f(x))))
    assert.equal(sampleCurve(model, 16).length, 17)
    const rmse = Math.sqrt(trace.reduce((sum, [x, y]) => sum + (model.f(x) - y) ** 2, 0) / trace.length)
    assert.ok(rmse < 0.08, 'Full-branch error remains small, including the steep end')
  })
}

test('a forced rational pole between trace points cannot bridge one continuous stroke', () => {
  const trace = [-2, -1, -0.5, 0.5, 1, 2].map(x => [x, 1 / x])
  assert.equal(fitModel({ family: 'rational', shift: 0 }, trace), null)
})

test('a forced tangent cannot ignore trace points around its poles', () => {
  const trace = points(-4, 4, x => 0.2 * x + 1)
  const model = fitModel({ family: 'tan', period: 1 }, trace)
  // The existing polynomial fallback is safe only if it covers the whole trace.
  assert.ok(!model || trace.every(([x]) => Number.isFinite(model.f(x))))
  assert.ok(!model || !model.poles.some(p => p > model.lo && p < model.hi))
})

for (const [name, lo, hi, f] of [
  ['line', -2, 2, x => 0.4 * x + 0.3],
  ['parabola', -2, 2, x => x * x],
  ['square root', 0, 4, x => Math.sqrt(x)],
  ['logarithm', 0.2, 4, x => Math.log(x)],
  ['sine', -2, 2, x => Math.sin(x)],
  ['continuous tangent', -0.6, 0.6, x => Math.tan(x)]
]) {
  test(name + ' still admits a complete model', () => {
    const trace = points(lo, hi, f)
    const model = fit(trace)
    assert.ok(model)
    assert.ok(trace.every(([x]) => Number.isFinite(model.f(x))))
    assert.equal(sampleCurve(model, 16).length, 17)
  })
}
