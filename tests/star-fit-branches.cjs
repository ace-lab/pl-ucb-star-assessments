const { test } = require('node:test')
const assert = require('node:assert/strict')
const { placeCurve, placeCurves } = require('../elements/pl-sketch-extension/star-fit.js')

const config = { xrange: [-5, 5], yrange: [-5, 5], width: 600, height: 400 }
const initial = { data: { graph: [[{ x: 1, y: 2 }, { x: 3, y: 4 }]], other: [{ value: 7 }] }, selected: 'other' }
const canvas = () => {
  let state = structuredClone(initial)
  let writes = 0
  return { getState: () => JSON.stringify(state), setState: value => { writes++; state = JSON.parse(value) }, state: () => state, writes: () => writes }
}

test('transfer keeps disconnected branches separate and preserves other tools', () => {
  const si = canvas()
  placeCurves(si, config, 'graph', [[[-2, -1], [-1, -2]], [[1, 2], [2, 1]]])
  assert.deepEqual(si.state(), {
    ...initial,
    data: { ...initial.data, graph: [[{ x: 180, y: 240 }, { x: 240, y: 280 }], [{ x: 360, y: 120 }, { x: 420, y: 160 }]] }
  })
  assert.equal(si.writes(), 1)
})

test('an invalid later branch cannot partially overwrite the existing drawing', () => {
  for (const invalid of [[], [[1, 2]], [[1, 2], [3, NaN]], [[1, 2], [3, Infinity]]]) {
    const si = canvas()
    assert.throws(() => placeCurves(si, config, 'graph', [[[0, 0], [1, 1]], invalid]), /Every branch/)
    assert.deepEqual(si.state(), initial)
    assert.equal(si.writes(), 0)
  }
})

test('single-curve callers retain their existing coordinate mapping', () => {
  const si = canvas()
  placeCurve(si, config, 'graph', [[-5, 5], [5, -5]])
  assert.deepEqual(si.state().data.graph, [[{ x: 0, y: 0 }, { x: 600, y: 400 }]])
})
