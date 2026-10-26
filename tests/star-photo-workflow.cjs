#!/usr/bin/env node
// Check the student workflow in the actual, unmodified desktop/mobile layout.
const { spawnSync } = require('node:child_process')
const { mkdirSync, writeFileSync } = require('node:fs')
const { resolve } = require('node:path')

async function checkWorkflow (page, options) {
  const checks = []
  const errors = []
  const outcomes = []
  const check = (condition, name) => {
    if (!condition) throw new Error(name)
    checks.push(name)
  }
  page.on('pageerror', e => errors.push(String(e)))
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()) })
  const branches = [[-1.7, -0.55], [-0.45, 0.45], [0.55, 1.7]].map(([lo, hi]) =>
    Array.from({ length: 45 }, (_, i) => {
      const x = lo + (hi - lo) * i / 44
      const y = 0.3 / (1 - (x / 0.5) ** 2)
      return [450 + 225 * x, 660 - 300 * y]
    }))
  for (const [name, width, height] of [['desktop', 1440, 1000], ['mobile', 390, 844]]) {
    await page.setViewportSize({ width, height })
    await page.goto(options.url, { waitUntil: 'networkidle' })
    check((await page.title()).includes('star-photo-test'), name + ': correct question')
    check(await page.getByRole('heading', { name: 'STAR: hand-drawn switch test', exact: true }).isVisible(), name + ': meaningful page')
    check(await page.locator('#hand-drawn-off-star-photo-btn').count() === 0, name + ': instructor switch-off control stays unchanged')
    const camera = page.locator('#hand-drawn-on-star-photo-btn')
    await camera.click()
    const panel = page.getByRole('dialog', { name: 'Use your paper graph', exact: true })
    const canvas = panel.locator('.star-canvas')
    const confirm = panel.locator('.star-confirm')
    check(await panel.isVisible() && await panel.evaluate(el => el.open), name + ': native modal opens')
    check(await panel.locator('.star-next').isDisabled() && await panel.locator('.star-mode-curve').isDisabled(), name + ': later steps wait for a photo')
    await page.keyboard.press('Shift+Tab')
    await page.keyboard.press('Tab')
    // Native dialog tab order may include browser chrome; Tab must return to
    // the dialog, rather than a control on the inert background page.
    if (!await page.evaluate(() => document.hasFocus())) await page.keyboard.press('Tab')
    check(await panel.evaluate(el => el.contains(document.activeElement)), name + ': keyboard focus stays in the dialog')
    const data = await page.evaluate(branches => {
      const c = document.createElement('canvas')
      c.width = 900; c.height = 1200
      const x = c.getContext('2d')
      x.fillStyle = '#fffdf5'; x.fillRect(0, 0, 900, 1200)
      x.strokeStyle = '#d2deeb'; x.lineWidth = 1
      for (let y = 30; y < 1200; y += 30) {
        x.beginPath(); x.moveTo(0, y); x.lineTo(900, y); x.stroke()
      }
      x.strokeStyle = '#222'; x.lineWidth = 4
      for (const points of branches) {
        x.beginPath()
        points.forEach(([px, py], i) => i ? x.lineTo(px, py) : x.moveTo(px, py))
        x.stroke()
      }
      return c.toDataURL().split(',')[1]
    }, branches)
    await panel.locator('input[type=file]').setInputFiles({ name: 'portrait-three-branches.png', mimeType: 'image/png', buffer: Buffer.from(data, 'base64') })
    await panel.locator('.star-status').filter({ hasText: 'Place the axes, then trace your curve.' }).waitFor()
    check(await panel.locator('.star-mode-axes').getAttribute('aria-current') === 'step', name + ': upload advances to calibration')
    const within = (b, r) => b.x >= r.x - 1 && b.y >= r.y - 1 && b.x + b.width <= r.x + r.width + 1 && b.y + b.height <= r.y + r.height + 1
    const viewport = { x: 0, y: 0, width, height }
    const photo = await canvas.boundingBox()
    check(within(photo, await panel.locator('.star-canvas-wrap').boundingBox()), name + ': entire portrait photo fits without scrolling')
    check(within(await panel.locator('.star-next').boundingBox(), viewport), name + ': calibration action stays on screen')
    check(await panel.evaluate(el => el.scrollWidth <= el.clientWidth + 1), name + ': dialog has no horizontal overflow')
    await panel.screenshot({ path: options.output + '/' + name + '--axes.png' })
    await panel.locator('.star-xval').fill('0')
    check(await panel.locator('.star-next').isDisabled() && await panel.locator('.star-mode-curve').isDisabled(), name + ': zero reference cannot proceed silently as one')
    check(await panel.locator('.star-axis-error').isVisible(), name + ': invalid calibration has a visible explanation')
    await panel.locator('.star-xval').fill('1')
    await page.evaluate(() => {
      window.__workflowSubmits = 0
      const form = document.getElementById('hand-drawn-on-star-panel').closest('form')
      if (form) form.addEventListener('submit', event => { window.__workflowSubmits++; event.preventDefault() })
    })
    await panel.locator('.star-xval').press('Enter')
    check(await page.evaluate(() => window.__workflowSubmits) === 0 && await panel.isVisible(), name + ': Enter in a coordinate field does not submit the question')
    const pixels = await canvas.evaluate(el => el.toDataURL())
    await canvas.focus()
    await page.keyboard.press('ArrowRight')
    check(await canvas.evaluate(el => el.toDataURL()) !== pixels, name + ': keyboard moves an axis marker')
    await page.keyboard.press('ArrowLeft')
    check(await canvas.evaluate(el => el.toDataURL()) === pixels, name + ': keyboard can restore the original calibration')
    await panel.locator('.star-next').click()
    check(await panel.locator('.star-use').isVisible(), name + ': tracing step exposes its primary action')
    await page.evaluate(() => {
      window.__workflowFits = []
      const fit = window.StarFit.fit
      window.StarFit.fit = (...args) => {
        window.__workflowFits.push(JSON.parse(JSON.stringify(args[0])))
        return fit(...args)
      }
    })
    const touch = name === 'mobile' ? await page.context().newCDPSession(page) : null
    if (touch) await touch.send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 1 })
    const drag = async points => {
      if (touch) {
        for (const [i, [x, y]] of points.entries()) await touch.send('Input.dispatchTouchEvent', { type: i ? 'touchMove' : 'touchStart', touchPoints: [{ x, y }] })
        await touch.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] })
      } else {
        for (const [i, [x, y]] of points.entries()) {
          await page.mouse.move(x, y)
          if (!i) await page.mouse.down()
        }
        await page.mouse.up()
      }
    }
    await panel.locator('.star-zoom-in').click()
    await panel.locator('.star-zoom-in').click()
    check(await panel.locator('.star-zoom-level').textContent() === '156%', name + ': zoom controls magnify the photo')
    await panel.locator('.star-pan').click()
    const area = await panel.locator('.star-canvas-wrap').boundingBox()
    const start = [area.x + area.width / 2, area.y + area.height / 2]
    const transform = await canvas.evaluate(el => el.style.transform)
    await drag([start, [start[0], start[1] - 15], [start[0], start[1] - 30]])
    check(await canvas.evaluate(el => el.style.transform) !== transform, name + ': move-photo gesture pans the magnified image')
    check(await panel.locator('.star-branch-count').textContent() === 'No branches traced', name + ': panning creates no accidental stroke')
    await panel.locator('.star-fit-view').click()
    await panel.locator('.star-pan').click()
    for (const [i, branch] of branches.entries()) {
      if (i === 1) await panel.locator('.star-zoom-in').click()
      const b = await canvas.boundingBox()
      await drag(branch.map(([x, y]) => [b.x + x * b.width / 900, b.y + y * b.height / 1200]))
      if (i === 1) await panel.locator('.star-fit-view').click()
    }
    check(await panel.locator('.star-branch-count').textContent() === '3 branches traced', name + ': three separate gestures give three branches')
    await panel.locator('.star-use').click()
    check(await panel.locator('.star-mode-review').getAttribute('aria-current') === 'step', name + ': reading advances to review')
    check(await confirm.isEnabled() && within(await confirm.boundingBox(), viewport), name + ': confirmation is enabled and on screen')
    check(await panel.locator('.star-fit-eq > div').count() === 3 && await panel.locator('.star-branch option').count() === 3, name + ': review represents every branch')
    const fits = await page.evaluate(() => window.__workflowFits)
    check(fits.length === 3, name + ': view gestures did not add fitting inputs')
    const middle = fits[1]
    check(middle[0][0] < -0.4 && middle.at(-1)[0] > 0.4 &&
      middle.every(([x, y]) => Math.abs(y - 0.3 / (1 - (x / 0.5) ** 2)) < 0.2), name + ': tracing while zoomed preserves graph coordinates')
    await panel.locator('.star-branch').selectOption('1')
    await panel.locator('.star-zoom-in').click()
    const validEquation = await panel.locator('.star-fit-eq').textContent()
    const reviewArea = await panel.locator('.star-canvas-wrap').boundingBox()
    const reviewStart = [reviewArea.x + reviewArea.width / 2, reviewArea.y + reviewArea.height / 2]
    await drag([reviewStart, [reviewStart[0], reviewStart[1] - 20]])
    await panel.locator('.star-fit-view').click()
    await panel.locator('.star-show-trace').check()
    await panel.locator('.star-show-trace').uncheck()
    check(await confirm.isEnabled() && await panel.locator('.star-fit-eq').textContent() === validEquation, name + ': zoom, pan and trace visibility preserve the current proposal')
    check(await page.evaluate(() => window.__workflowFits.length) === 3, name + ': view changes do not refit')
    await panel.locator('.star-mode-axes').click()
    await canvas.focus()
    await page.keyboard.press('ArrowRight')
    check(await confirm.isDisabled() && await panel.locator('.star-fit-eq').textContent() === '', name + ': keyboard calibration invalidates the proposal')
    await page.keyboard.press('ArrowLeft')
    await panel.locator('.star-next').click()
    await panel.locator('.star-use').click()
    await panel.screenshot({ path: options.output + '/' + name + '--review.png' })
    await page.keyboard.press('Escape')
    check(await panel.isHidden() && await camera.evaluate(el => document.activeElement === el), name + ': Escape closes and restores focus')
    await camera.click()
    check(await confirm.isEnabled(), name + ': reopening preserves the reviewed proposal')
    await confirm.click()
    const state = await page.evaluate(() => {
      const si = window.SketchExtensionInput.instances['hand-drawn-on']
      return { state: JSON.parse(si.getState()), gradeable: JSON.parse(si.getGradeable()) }
    })
    check(state.state.data.sp.filter(b => b.length > 1).length === 3, name + ': all three branches reach the native canvas')
    check(state.gradeable.data.sp.length === 3, name + ': all three branches reach submission data')
    check(await panel.isHidden() && await camera.evaluate(el => document.activeElement === el), name + ': confirmation closes dialog and restores focus')
    await page.locator('#hand-drawn-on-si-container').screenshot({ path: options.output + '/' + name + '--canvas.png' })
    outcomes.push({ name, viewport: [width, height], photo, native_branches: 3, pointer_input: touch ? 'Chromium touch events' : 'mouse' })
    if (touch) await touch.detach()
  }
  check(errors.length === 0, 'No application console errors')
  return { passed: checks.length, checks, outcomes, consoleErrors: errors }
}

module.exports = checkWorkflow
if (require.main === module) {
  const options = {
    url: process.env.PL_PHOTO_TEST_URL,
    output: resolve(process.env.PL_PHOTO_TEST_OUTPUT || '/tmp/pl-sketch-photo-workflow')
  }
  if (!options.url) throw new Error('Set PL_PHOTO_TEST_URL to the preview URL for Sketch2Graph/star-photo-test.')
  mkdirSync(options.output, { recursive: true })
  const cli = process.env.PL_PHOTO_TEST_CLI || 'playwright-cli'
  const run = args => {
    const p = spawnSync(cli, ['-s=photo-workflow', ...args], { encoding: 'utf8', timeout: 180000, maxBuffer: 8 * 1024 * 1024 })
    const text = (p.stdout || '') + (p.stderr || '')
    if (args[0] !== 'snapshot') process.stdout.write(text.split('### Ran Playwright code')[0])
    if (p.error || p.status !== 0 || text.includes('### Error')) throw p.error || new Error('Browser workflow check failed')
    const result = text.split('### Result\n')[1]?.split('\n###')[0]
    if (result) writeFileSync(options.output + '/results.json', JSON.stringify(JSON.parse(result), null, 2) + '\n')
  }
  try {
    run(['open', options.url, '--browser', 'chrome'])
    run(['snapshot'])
    run(['run-code', 'async (page) => (' + checkWorkflow.toString() + ')(page,' + JSON.stringify(options) + ')'])
  } catch (e) {
    console.error(e.message)
    process.exitCode = 1
  } finally {
    run(['close'])
  }
}
