const { test } = require('node:test')
const assert = require('node:assert/strict')
const { readFileSync } = require('node:fs')
const { join } = require('node:path')
const { runInNewContext } = require('node:vm')

test('extension canvases coexist with stock pl-sketch in either script loading order', () => {
  const stock = () => 'stock canvas'
  const canvases = []
  const submissions = []
  const window = {
    SketchInput: stock,
    sketchresponse: {
      default: class {
        constructor (container, id, config) {
          this.id = id
          this.config = config
          this.messageBus = { on () {} }
          canvases.push(this)
        }

        getGradeable () { return '{"data":{"sp":[]}}' }
        getState () { return '{"data":{"sp":[]}}' }
      }
    }
  }
  const config = { width: 600, height: 400, xrange: [-5, 5], yrange: [-5, 5], plugins: [] }
  const fields = new Map()
  const context = {
    window,
    document: { getElementById: () => ({ closest: () => ({ addEventListener: (event, handler) => submissions.push(handler) }) }) },
    $: selector => ({
      text: () => btoa(JSON.stringify(config)),
      val: value => fields.set(selector, value)
    }),
    atob, btoa, escape, unescape
  }
  runInNewContext(readFileSync(join(__dirname, '../elements/pl-sketch-extension/pl-sketch.js'), 'utf8'), context)
  assert.equal(window.SketchInput, stock, 'loading the extension preserves the stock initializer')
  window.SketchExtensionInput('first')

  window.SketchInput = () => 'stock loaded later'
  window.SketchExtensionInput('second')
  assert.equal(window.SketchInput(), 'stock loaded later')
  assert.deepEqual(canvases.map(canvas => canvas.id), ['first', 'second'])
  for (const canvas of canvases) assert.equal(window.SketchExtensionInput.instances[canvas.id], canvas)
  for (const submit of submissions) submit()
  for (const id of ['first', 'second']) {
    const saved = JSON.parse(atob(fields.get('#' + id + '-sketchresponse-submission')))
    assert.deepEqual(saved, { data: { sp: [] }, gradeable: { sp: [] } })
  }
})
