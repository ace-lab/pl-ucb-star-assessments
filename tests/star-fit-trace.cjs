const { test } = require('node:test')
const assert = require('node:assert/strict')
const { fit, sampleCurve, simplifyTrace, placeCurves } = require('../elements/pl-sketch-extension/star-fit.js')

test('shape simplification removes straight-line sampling without removing corners', () => {
  const dense = [[0, 0], [1, 1], [2, 2], [3, 1], [4, 0], [5, 0], [6, 0]]
  assert.deepEqual(simplifyTrace(dense, 0.1), [[0, 0], [2, 2], [4, 0], [6, 0]])
  assert.deepEqual(dense[1], [1, 1])
})

test('transcription retains vertices and endpoints regardless of sample count', () => {
  const points = [[-3, 0], [-1, 4], [0, 1], [2, 1]]
  const model = fit(points, { family: 'trace' })
  assert.deepEqual(sampleCurve(model, 16), points)
  assert.equal(model.f(-2), 2)
  assert.equal(model.f(1), 1)
  assert.ok(Number.isNaN(model.f(-4)))
  assert.ok(Number.isNaN(model.f(3)))
  sampleCurve(model)[0][1] = 99
  assert.equal(model.f(-3), 0)
})

test('invalid function branches fail instead of inventing a shape', () => {
  for (const points of [[], [[1, 2]], [[0, 0], [0, 1]], [[1, 0], [0, 1]], [[0, 0], [1, NaN]]]) {
    assert.throws(() => fit(points, { family: 'trace' }), /distinct x/)
  }
})

test('native corner supports stay on adjacent segments and leave other branches unchanged', () => {
  let stored
  const si = { getState: () => JSON.stringify({ data: { other: [7] } }), setState: s => { stored = JSON.parse(s) } }
  const config = { width: 600, height: 400, xrange: [0, 6], yrange: [0, 4], plugins: [{ id: 'sp', name: 'spline' }] }
  placeCurves(si, config, 'sp', [[[0, 0], [3, 3], [6, 0]], [[0, 1], [6, 1]]], { preserveCorners: [true, false] })
  assert.equal(stored.data.sp[0].length, 5)
  assert.equal(stored.data.sp[1].length, 2)
  assert.deepEqual(stored.data.other, [7])
  const [start, before, corner, after, end] = stored.data.sp[0]
  assert.deepEqual(start, { x: 0, y: 400 })
  assert.deepEqual(corner, { x: 300, y: 100 })
  assert.deepEqual(end, { x: 600, y: 400 })
  for (const p of [before, after]) assert.ok(Math.abs(Math.hypot(p.x - corner.x, p.y - corner.y) - 12) < 1e-10)
  assert.ok(Math.abs(before.x + before.y - corner.x - corner.y) < 1e-10)
  assert.ok(Math.abs(after.x - after.y - corner.x + corner.y) < 1e-10)
})

test('freeform receives cubic controls with straight segments for rendering and grading', () => {
  let stored
  const si = { getState: () => '{"data":{}}', setState: s => { stored = JSON.parse(s) } }
  const config = { width: 600, height: 400, xrange: [0, 6], yrange: [0, 4], plugins: [{ id: 'ff', name: 'freeform' }] }
  placeCurves(si, config, 'ff', [[[0, 0], [3, 3], [6, 0]]], { preserveCorners: [true] })
  assert.deepEqual(stored.data.ff[0], [
    { x: 0, y: 400 }, { x: 100, y: 300 }, { x: 200, y: 200 }, { x: 300, y: 100 },
    { x: 400, y: 200 }, { x: 500, y: 300 }, { x: 600, y: 400 }
  ])
})
