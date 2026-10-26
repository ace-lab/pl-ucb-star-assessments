#!/usr/bin/env node
// Exercise the real photo UI and native SVG renderer, without benchmark images.
const { spawnSync } = require('node:child_process')
const { mkdirSync, writeFileSync } = require('node:fs')
const { resolve } = require('node:path')

async function checkBranches (page, options) {
  const checks = []
  const errors = []
  const check = (condition, name) => {
    if (!condition) throw new Error(name)
    checks.push(name)
  }
  page.on('pageerror', error => errors.push(String(error)))
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()) })
  const fixtures = [
    { id: 'single-line', branches: [[-1.5, 1.5, x => 0.45 * x + 0.3]] },
    { id: 'two-lines', branches: [[-1.6, -0.3, x => 0.3 * x + 0.9], [0.3, 1.6, x => -0.4 * x - 0.6]] },
    { id: 'reciprocal', branches: [[-1.65, -0.38, x => 0.55 / x], [0.38, 1.65, x => 0.55 / x]] },
    { id: 'overlapping-x', branches: [[-1.4, 1.4, x => 0.2 * x + 1], [-1.4, 1.4, x => 0.2 * x - 1]] },
    { id: 'three-branches', branches: [[-1.8, -0.5, x => 0.3 / (1 - (x / 0.45) ** 2)], [-0.4, 0.4, x => 0.3 / (1 - (x / 0.45) ** 2)], [0.5, 1.8, x => 0.3 / (1 - (x / 0.45) ** 2)]] },
    { id: 'mobile-two-lines', mobile: true, branches: [[-1.6, -0.3, x => 0.3 * x + 0.9], [0.3, 1.6, x => -0.4 * x - 0.6]] },
    { id: 'sharp-v', vertices: [[-1.5, 1.4], [0, -1.3], [1.5, 1.4]] },
    { id: 'sharp-peak', vertices: [[-1.5, -1], [-0.25, 1.5], [0.6, -0.7], [1.5, 0.2]] },
    { id: 'plateau', vertices: [[-1.5, -1], [-0.6, 1.3], [0.6, 1.3], [1.5, -1]] },
    { id: 'mobile-peak', mobile: true, vertices: [[-1.5, -1], [-0.25, 1.5], [0.6, -0.7], [1.5, 0.2]] }
  ]
  const outcomes = []
  for (const fixture of fixtures) {
    if (options.cases && !options.cases.includes(fixture.id)) continue
    await page.setViewportSize(fixture.mobile ? { width: 390, height: 844 } : { width: 1600, height: 1500 })
    await page.goto(options.url, { waitUntil: 'networkidle' })
    check((await page.title()).includes('star-photo-test'), fixture.id + ': correct page')
    check(await page.getByRole('heading', { name: 'STAR: hand-drawn switch test', exact: true }).isVisible(), fixture.id + ': meaningful page')
    await page.locator('#hand-drawn-on-star-photo-btn').click()
    const panel = page.locator('#hand-drawn-on-star-panel')
    const canvas = panel.locator('.star-canvas')
    const confirm = panel.locator('.star-confirm')
    const guides = fixture.vertices
      ? [fixture.vertices.slice(1).flatMap((b, j) => {
          const a = fixture.vertices[j]
          return Array.from({ length: 17 }, (_, k) => [300 + 150 * (a[0] + (b[0] - a[0]) * k / 16), 220 - 100 * (a[1] + (b[1] - a[1]) * k / 16)])
        })]
      : fixture.branches.map(([lo, hi, f]) => Array.from({ length: 45 }, (_, i) => {
        const x = lo + (hi - lo) * i / 44
        return [300 + 150 * x, 220 - 100 * f(x)]
      }))
    const data = await page.evaluate(guides => {
      const c = document.createElement('canvas')
      c.width = 600; c.height = 400
      const ctx = c.getContext('2d')
      ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, 600, 400)
      ctx.strokeStyle = '#222'; ctx.lineWidth = 3
      for (const points of guides) {
        ctx.beginPath()
        points.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))
        ctx.stroke()
      }
      return c.toDataURL('image/png').split(',')[1]
    }, guides)
    await panel.locator('input[type=file]').setInputFiles({ name: fixture.id + '.png', mimeType: 'image/png', buffer: Buffer.from(data, 'base64') })
    await panel.locator('.star-status').filter({ hasText: 'Place the axes, then trace your curve.' }).waitFor()
    await page.evaluate(() => {
      window.__branchFits = []
      window.__branchTransfers = 0
      const fit = window.StarFit.fit
      window.StarFit.fit = function (points, spec) {
        const model = fit(points, spec)
        window.__branchFits.push({
          points,
          spec: model && model.spec,
          expression: model && model.expr,
          degree: model && model.degree,
          family: model && model.family,
          complete: model && points.every(([x]) => Number.isFinite(model.f(x))) &&
            (model.family === 'trace' ? window.StarFit.sampleCurve(model, 16).length >= 2 : window.StarFit.sampleCurve(model, 16).length === 17)
        })
        return model
      }
      const place = window.StarFit.placeCurves
      window.StarFit.placeCurves = function (...args) {
        window.__branchTransfers++
        return place(...args)
      }
    })
    await panel.locator('.star-mode-curve').click()
    for (const guide of guides) {
      await canvas.scrollIntoViewIfNeeded()
      const b = await canvas.boundingBox()
      if (fixture.mobile) check(b.y >= 0 && b.y + b.height <= 844, 'Mobile photo is visible for tracing without layout changes')
      for (const [i, p] of guide.entries()) {
        await page.mouse.move(b.x + p[0] * b.width / 600, b.y + p[1] * b.height / 400)
        if (!i) await page.mouse.down()
      }
      await page.mouse.up()
    }
    await panel.locator('.star-use').click()
    const fits = await page.evaluate(() => window.__branchFits)
    check(fits.length === guides.length, fixture.id + ': every traced branch reaches the fitter')
    check(fits.every(f => f.complete), fixture.id + ': models cover every traced point and the complete sampled domain')
    check(fits.every(f => f.family === 'trace'), fixture.id + ': default keeps the traced shape without choosing an equation')
    check(await confirm.isEnabled(), fixture.id + ': complete proposal is confirmable')
    check(await panel.locator('.star-fit-eq > div').count() === guides.length, fixture.id + ': preview lists every branch')
    check(await panel.locator('.star-branch-wrap').isHidden() === (guides.length === 1), fixture.id + ': branch selector matches proposal')

    if (fixture.id === 'two-lines') {
      await panel.locator('.star-branch').selectOption('1')
      check(await page.evaluate(() => window.__branchFits.length) === 2, 'Selecting a branch preserves the proposal without refitting')
      await panel.locator('.star-fit-options > summary').click()
      await panel.locator('.star-family').selectOption('polynomial')
      await panel.locator('.star-degree').fill('2')
      check(await confirm.isDisabled(), 'Changing branch degree invalidates the complete proposal')
      check(await panel.locator('.star-fit-eq').textContent() === '', 'Invalidated multi-branch equations disappear')
      await confirm.dispatchEvent('click')
      check(await page.evaluate(() => window.__branchTransfers) === 0, 'Invalidated multi-branch proposal cannot transfer')
      await panel.locator('.star-refit').click()
      const edited = await page.evaluate(() => window.__branchFits.slice(-2))
      check(edited[0].expression === fits[0].expression, 'Editing branch 2 preserves branch 1 model')
      check(edited[1].degree === 2, 'Degree override applies to the selected branch')
      await page.evaluate(() => {
        window.__branchOriginalFit = window.StarFit.fit
        let calls = 0
        window.StarFit.fit = (...args) => ++calls === 2 ? null : window.__branchOriginalFit(...args)
      })
      await panel.locator('.star-refit').click()
      check(await confirm.isDisabled(), 'Failure of a later branch blocks the whole proposal')
      check((await panel.locator('.star-status').textContent()).includes('Branch 2:'), 'Failure identifies the affected branch')
      await confirm.dispatchEvent('click')
      check(await page.evaluate(() => window.__branchTransfers) === 0, 'A partially fitted proposal cannot transfer')
      await page.evaluate(() => { window.StarFit.fit = window.__branchOriginalFit })
      await panel.locator('.star-mode-curve').click()
      await panel.locator('.star-use').click()
    }

    await panel.screenshot({ path: options.output + '/' + fixture.id + '--preview.png' })
    await confirm.click()
    await page.waitForFunction(n => [...document.querySelectorAll('#hand-drawn-on-si-container path.plugin-id-sp')].filter(p => p.getAttribute('d')).length === n, guides.length)
    const rendering = await page.evaluate(() => {
      const si = window.SketchExtensionInput.instances['hand-drawn-on']
      const state = JSON.parse(si.getState())
      return { state, gradeable: JSON.parse(si.getGradeable()) }
    })
    const branches = rendering.state.data.sp.filter(b => b.length > 1)
    check(branches.length === guides.length, fixture.id + ': native state retains every branch')
    check(rendering.gradeable.data.sp.length === guides.length, fixture.id + ': submission data retains every branch')
    check(await panel.isHidden(), fixture.id + ': successful confirmation closes panel')
    if (fixture.vertices) {
      const geometry = await page.evaluate(() => {
        const si = window.SketchExtensionInput.instances['hand-drawn-on']
        const config = JSON.parse(si.getState()).meta.config
        const vertices = window.StarFit.graphToPixels(config, window.__branchFits[0].points)
        const path = document.querySelector('#hand-drawn-on-si-container path.plugin-id-sp')
        const controls = JSON.parse(si.getGradeable()).data.sp[0].spline
        const grade = document.createElementNS('http://www.w3.org/2000/svg', 'path')
        grade.setAttribute('d', 'M' + controls[0].join(',') + 'C' + controls.slice(1).map(p => p.join(',')).join(' '))
        const distance = (p, a, b) => {
          const dx = b.x - a.x; const dy = b.y - a.y
          const t = Math.max(0, Math.min(1, ((p.x - a.x) * dx + (p.y - a.y) * dy) / (dx * dx + dy * dy)))
          return Math.hypot(p.x - a.x - t * dx, p.y - a.y - t * dy)
        }
        let previewError = 0; let gradingError = 0
        const samples = []
        for (let i = 0; i <= 1000; i++) {
          const p = path.getPointAtLength(path.getTotalLength() * i / 1000)
          const g = grade.getPointAtLength(grade.getTotalLength() * i / 1000)
          samples.push({ x: p.x, y: p.y })
          previewError = Math.max(previewError, Math.min(...vertices.slice(1).map((b, j) => distance(p, vertices[j], b))))
          gradingError = Math.max(gradingError, Math.hypot(p.x - g.x, p.y - g.y))
        }
        const vertexError = Math.max(...vertices.map(v => Math.min(...samples.map(p => Math.hypot(p.x - v.x, p.y - v.y)))))
        return { previewError, gradingError, vertexError, vertices: vertices.length }
      })
      check(geometry.previewError < 3 && geometry.vertexError < 3, fixture.id + ': native spline preserves preview and corner locations within 3 SVG pixels')
      check(geometry.gradingError < 0.05, fixture.id + ': actual rendered and submitted cubic geometry agree')
      rendering.geometry = geometry
    }
    if (fixture.id === 'reciprocal') {
      const config = await page.evaluate(() => JSON.parse(atob(document.getElementById('hand-drawn-on-sketchresponse-data').textContent)))
      const originPx = -config.xrange[0] * config.width / (config.xrange[1] - config.xrange[0])
      check(branches[0].every(p => p.x < originPx) && branches[1].every(p => p.x > originPx), 'Reciprocal branches remain disconnected across the asymptote')
    }
    await page.locator('#hand-drawn-on-si-container').screenshot({ path: options.output + '/' + fixture.id + '--canvas.png' })
    outcomes.push({ id: fixture.id, expected: guides.length, output: branches.length, rendering })
    if (fixture.id === 'sharp-peak') {
      await page.locator('#hand-drawn-on-si-container').scrollIntoViewIfNeeded()
      const peak = await page.evaluate(() => {
        const si = window.SketchExtensionInput.instances['hand-drawn-on']
        const points = JSON.parse(si.getState()).data.sp[0]
        const highest = points.reduce((a, b) => a.y < b.y ? a : b)
        const path = document.querySelector('#hand-drawn-on-si-container path.plugin-id-sp')
        const p = path.ownerSVGElement.createSVGPoint()
        p.x = highest.x; p.y = highest.y
        const screen = p.matrixTransform(path.getScreenCTM())
        return { x: screen.x, y: screen.y, before: highest }
      })
      check(peak.x > 0 && peak.y > 0 && peak.y < 1500, 'Native corner is on screen before editing')
      await page.getByRole('button', { name: 'Select Select', exact: true }).first().click()
      await page.mouse.move(peak.x, peak.y)
      await page.mouse.down()
      await page.mouse.move(peak.x, peak.y - 30, { steps: 6 })
      await page.mouse.up()
      const edited = await page.evaluate(() => JSON.parse(window.SketchExtensionInput.instances['hand-drawn-on'].getState()).data.sp)
      await page.locator('#hand-drawn-on-si-container').screenshot({ path: options.output + '/sharp-peak--edited.png' })
      check(edited[0].some(p => p.y < peak.before.y - 5), 'Confirmed corner remains editable through native mouse controls')
      // Fill the independent switch-off control so its missing answer cannot
      // hide a validation error in the imported shape.
      await page.evaluate(() => {
        const config = JSON.parse(atob(document.getElementById('hand-drawn-off-sketchresponse-data').textContent))
        window.StarFit.placeCurve(window.SketchExtensionInput.instances['hand-drawn-off'], config, 'sp2',
          window.StarFit.sampleCurve({ lo: -2.2, hi: 2.2, f: x => x * x }, 16))
      })
      await Promise.all([
        page.waitForNavigation({ waitUntil: 'networkidle' }),
        page.getByRole('button', { name: 'Save & Grade', exact: true }).click()
      ])
      const restored = await page.evaluate(() => {
        const si = window.SketchExtensionInput.instances['hand-drawn-on']
        return { state: JSON.parse(si.getState()).data.sp, gradeable: JSON.parse(si.getGradeable()).data.sp }
      })
      check(JSON.stringify(restored.state.filter(b => b.length)) === JSON.stringify(edited.filter(b => b.length)), 'Edited corner survives an actual Save & Grade and page restoration')
      check(restored.gradeable.length === 1 && restored.gradeable[0].spline.every(p => p.every(Number.isFinite)), 'Restored shape has complete finite gradeable geometry')
      check(!(await page.locator('body').innerText()).includes('invalid, not gradable'), 'Existing function grader accepts the edited shape as a valid answer')
      await page.locator('#hand-drawn-on-si-container').screenshot({ path: options.output + '/sharp-peak--restored.png' })
      rendering.restored = restored
    }
    if (fixture.id === 'two-lines') {
      await page.locator('#hand-drawn-on-star-photo-btn').click()
      await panel.locator('.star-mode-curve').click()
      await panel.locator('.star-undo').click()
      check(await confirm.isDisabled(), 'Undoing a branch invalidates the complete proposal')
      await panel.locator('.star-use').click()
      check(await panel.locator('.star-branch-wrap').isHidden(), 'Undoing the second branch restores single-branch controls')
      await confirm.click()
      await page.waitForFunction(() => [...document.querySelectorAll('#hand-drawn-on-si-container path.plugin-id-sp')].filter(p => p.getAttribute('d')).length === 1)
      const remaining = await page.evaluate(() => JSON.parse(window.SketchExtensionInput.instances['hand-drawn-on'].getState()).data.sp.filter(b => b.length > 1).length)
      check(remaining === 1, 'Fresh single-branch confirmation removes the previous second branch')
      await page.locator('#hand-drawn-on-star-photo-btn').click()
      await panel.locator('.star-mode-curve').click()
      const bounds = await canvas.boundingBox()
      for (const [i, fraction] of [0.15, 0.25, 0.35].entries()) {
        await page.mouse.move(bounds.x + bounds.width * 0.15, bounds.y + bounds.height * fraction)
        if (!i) await page.mouse.down()
      }
      await page.mouse.up()
      await panel.locator('.star-use').click()
      check(await confirm.isDisabled(), 'An unusable extra stroke blocks confirmation instead of disappearing')
      check((await panel.locator('.star-status').textContent()).includes('Branch 2:'), 'Unusable stroke identifies the branch to retrace or undo')
      const before = await page.evaluate(() => window.__branchTransfers)
      await confirm.dispatchEvent('click')
      check(await page.evaluate(() => window.__branchTransfers) === before, 'Unusable later stroke cannot replace the native drawing')
      await panel.locator('.star-undo').click()
      await panel.locator('.star-use').click()
      check(await confirm.isEnabled(), 'Undoing an unusable stroke restores a complete proposal')
    }
  }
  check(errors.length === 0, 'No application console errors')
  return { passed: checks.length, checks, outcomes, consoleErrors: errors }
}

module.exports = checkBranches
if (require.main === module) {
  const options = {
    url: process.env.PL_PHOTO_TEST_URL,
    output: resolve(process.env.PL_PHOTO_TEST_OUTPUT || '/tmp/pl-sketch-photo-branches'),
    cases: process.env.PL_PHOTO_TEST_CASES ? process.env.PL_PHOTO_TEST_CASES.split(',') : null
  }
  if (!options.url) throw new Error('Set PL_PHOTO_TEST_URL to the preview URL for Sketch2Graph/star-photo-test.')
  mkdirSync(options.output, { recursive: true })
  const cli = process.env.PL_PHOTO_TEST_CLI || 'playwright-cli'
  const run = args => {
    const result = spawnSync(cli, ['-s=photo-branches', ...args], { encoding: 'utf8', timeout: 180000, maxBuffer: 8 * 1024 * 1024 })
    const output = (result.stdout || '') + (result.stderr || '')
    if (args[0] !== 'snapshot') process.stdout.write(output.split('### Ran Playwright code')[0])
    if (result.error || result.status !== 0 || output.includes('### Error')) throw result.error || new Error('Browser check failed (exit ' + result.status + ')')
    if (args[0] === 'run-code') {
      const json = output.split('### Result\n')[1]?.split('\n###')[0]
      if (json) writeFileSync(options.output + '/results.json', JSON.stringify(JSON.parse(json), null, 2) + '\n')
    }
  }
  try {
    run(['open', options.url, '--browser', 'chrome'])
    run(['snapshot'])
    run(['run-code', 'async (page) => (' + checkBranches.toString() + ')(page, ' + JSON.stringify(options) + ')'])
  } catch (error) {
    console.error(error.message)
    process.exitCode = 1
  } finally {
    run(['close'])
  }
}
