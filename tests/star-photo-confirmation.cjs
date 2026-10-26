#!/usr/bin/env node
// Live UI regression test. Requires a running PrairieLearn and Playwright CLI.
const { spawnSync } = require('node:child_process')
const { mkdirSync } = require('node:fs')
const { resolve } = require('node:path')

async function checkConfirmation (page, options) {
  const passed = []
  const errors = []
  page.on('pageerror', error => errors.push(String(error)))
  page.on('console', message => {
    if (message.type() === 'error') errors.push(message.text())
  })
  const check = (condition, name) => {
    if (!condition) throw new Error(name)
    passed.push(name)
  }
  await page.setViewportSize({ width: 1600, height: 1400 })
  await page.goto(options.url, { waitUntil: 'networkidle' })
  check((await page.title()).includes('star-photo-test'), 'Correct question loaded')
  check(await page.getByRole('heading', { name: 'STAR: hand-drawn switch test', exact: true }).isVisible(), 'Meaningful question content')
  await page.locator('#hand-drawn-on-star-photo-btn').click()
  const panel = page.locator('#hand-drawn-on-star-panel')
  const confirm = panel.locator('.star-confirm')
  const read = panel.locator('.star-use')
  const canvas = panel.locator('.star-canvas')
  const fitOptions = async () => {
    if (!await panel.locator('.star-fit-options').evaluate(el => el.open)) await panel.locator('.star-fit-options > summary').click()
  }
  const fresh = async () => {
    await panel.locator('.star-mode-curve').click()
    await read.click()
    check(await confirm.isEnabled() && await confirm.isVisible(), 'Fresh reading enables confirmation')
  }
  const unavailable = async name => {
    check(await confirm.isDisabled(), name + ': confirmation disabled')
    check((await panel.locator('.star-fit-eq').textContent()) === '', name + ': old equation cleared')
    const before = await page.evaluate(() => window.__photoConfirmCalls)
    // Exercise the handler as well as the native disabled-button behavior.
    await confirm.dispatchEvent('click')
    check(await page.evaluate(() => window.__photoConfirmCalls) === before, name + ': old model cannot reach canvas')
  }
  await page.evaluate(() => {
    window.__photoConfirmCalls = 0
    const original = window.StarFit.placeCurves
    window.StarFit.placeCurves = function (...args) {
      window.__photoConfirmCalls++
      return original(...args)
    }
  })
  const image = async (name, offset = 0) => {
    const data = await page.evaluate(offset => {
      const c = document.createElement('canvas')
      c.width = 600; c.height = 300
      const ctx = c.getContext('2d')
      ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, 600, 300)
      ctx.strokeStyle = '#222'; ctx.lineWidth = 3
      ctx.beginPath(); ctx.moveTo(80, 240 + offset); ctx.lineTo(520, 65 + offset); ctx.stroke()
      return c.toDataURL('image/png').split(',')[1]
    }, offset)
    return { name, mimeType: 'image/png', buffer: Buffer.from(data, 'base64') }
  }
  const first = await image('first.png')
  const second = await image('second.png', 8)
  const upload = async file => {
    await panel.locator('input[type=file]').setInputFiles(file)
    await panel.locator('.star-status').filter({ hasText: 'Place the axes, then trace your curve.' }).waitFor()
  }
  const stroke = async () => {
    await panel.locator('.star-mode-curve').click()
    const b = await canvas.boundingBox()
    for (let i = 0; i <= 35; i++) {
      await page.mouse.move(b.x + (80 + 440 * i / 35) * b.width / 600,
        b.y + (240 - 175 * i / 35) * b.height / 300)
      if (i === 0) await page.mouse.down()
    }
    await page.mouse.up()
  }
  await upload(first)
  await stroke()
  await fresh()
  await panel.locator('.star-mode-curve').click()
  await panel.locator('.star-clear').click()
  await unavailable('Clear trace')
  await panel.locator('.star-mode-curve').click()
  await read.click()
  check((await panel.locator('.star-status').textContent()).includes('No usable trace'), 'Empty trace shows an actionable error')
  await unavailable('Failed empty-trace reading')
  await stroke(); await fresh()
  await upload(second)
  await unavailable('Replace photo')
  await stroke(); await fresh()
  await panel.screenshot({ path: options.output + '/fresh-preview.png' })

  const changes = [
    ['Change x units', async () => { await panel.locator('.star-mode-axes').click(); await panel.locator('.star-xval').fill('2') }],
    ['Change y units', async () => { await panel.locator('.star-mode-axes').click(); await panel.locator('.star-yval').fill('2') }],
    ['Change equal-axis scale', async () => { await panel.locator('.star-mode-axes').click(); await panel.locator('.star-equal').check() }],
    ['Change search width', async () => {
      await panel.locator('.star-mode-curve').click()
      await panel.locator('.star-trace-options > summary').click()
      await panel.locator('.star-brush').focus()
      await page.keyboard.press('ArrowRight')
    }],
    ['Move origin', async () => {
      await panel.locator('.star-mode-axes').click()
      const b = await canvas.boundingBox()
      await page.mouse.move(b.x + b.width * 0.5, b.y + b.height * 0.55)
      await page.mouse.down()
      await page.mouse.move(b.x + b.width * 0.51, b.y + b.height * 0.56, { steps: 3 })
      await page.mouse.up()
    }],
    ['Add stroke', stroke],
    ['Undo stroke', async () => { await panel.locator('.star-mode-curve').click(); await panel.locator('.star-undo').click() }]
  ]
  for (const [name, change] of changes) {
    await change()
    await unavailable(name)
    if (name === 'Change x units') await panel.screenshot({ path: options.output + '/invalidated-preview.png' })
    await fresh()
  }
  await panel.screenshot({ path: options.output + '/updated-preview.png' })
  await fitOptions()
  await panel.locator('.star-family').selectOption('polynomial')
  await panel.locator('.star-degree').fill('2')
  await unavailable('Change polynomial degree')
  await panel.locator('.star-refit').click()
  check(await confirm.isEnabled(), 'Refit re-enables confirmation')
  await panel.locator('.star-family').selectOption('abs')
  check(await confirm.isEnabled(), 'Changing curve family generates a fresh fit')
  await panel.locator('.star-units').uncheck()
  await panel.locator('.star-mode-axes').click()
  check(await confirm.isEnabled(), 'Display-only controls preserve a valid fit')
  await panel.locator('.star-mode-review').click()

  for (const kind of ['null', 'throw']) {
    await page.evaluate(kind => {
      window.__originalPhotoFit = window.StarFit.fit
      window.StarFit.fit = () => {
        if (kind === 'throw') throw new Error('Simulated fit failure')
        return null
      }
    }, kind)
    await panel.locator('.star-refit').click()
    await unavailable('Failed refit (' + kind + ')')
    await page.evaluate(() => { window.StarFit.fit = window.__originalPhotoFit })
    await panel.locator('.star-refit').click()
    check(await confirm.isEnabled(), 'Successful refit recovers from ' + kind)
  }

  // Simulate slow image decoding without changing the production image loader.
  await page.evaluate(() => {
    window.__originalPhotoDecode = window.createImageBitmap
    window.__photoDecodes = []
    window.createImageBitmap = (...args) => new Promise((resolve, reject) => {
      window.__photoDecodes.push(() => window.__originalPhotoDecode(...args).then(resolve, reject))
    })
  })
  await panel.locator('input[type=file]').setInputFiles(first)
  await unavailable('Photo loading')
  check(await read.isDisabled(), 'Reading is disabled while a photo loads')
  await panel.locator('input[type=file]').setInputFiles(second)
  await page.waitForFunction(() => window.__photoDecodes.length === 2)
  await page.evaluate(() => window.__photoDecodes[1]())
  await panel.locator('.star-status').filter({ hasText: 'Place the axes, then trace your curve.' }).waitFor()
  await stroke(); await fresh()
  const latestPreview = await canvas.evaluate(el => el.toDataURL())
  await page.evaluate(() => window.__photoDecodes[0]())
  check(await canvas.evaluate(el => el.toDataURL()) === latestPreview && await confirm.isEnabled(), 'Late older upload cannot replace the newest photo or preview')
  await page.evaluate(() => { window.createImageBitmap = window.__originalPhotoDecode })

  await panel.locator('input[type=file]').setInputFiles({ name: 'invalid.png', mimeType: 'image/png', buffer: Buffer.from('invalid image') })
  await panel.locator('.star-status').filter({ hasText: 'Could not read that image.' }).waitFor()
  await unavailable('Failed photo load')
  check(await read.isDisabled(), 'Failed photo load cannot reread the previous photo')
  await upload(second); await stroke(); await fresh()

  await confirm.click()
  await page.waitForFunction(() => [...document.querySelectorAll('#hand-drawn-on-si-container path.plugin-id-sp')].some(p => p.getAttribute('d')))
  check(await panel.isHidden(), 'Fresh confirmation closes photo panel')
  check(await page.evaluate(() => window.__photoConfirmCalls) === 1, 'Exactly one fresh model reached native canvas')
  await page.locator('#hand-drawn-on-si-container').screenshot({ path: options.output + '/confirmed-canvas.png' })
  check(errors.length === 0, 'No application console errors')
  return { passed: passed.length, checks: passed, screenshots: options.output, consoleErrors: errors }
}

const options = {
  url: process.env.PL_PHOTO_TEST_URL,
  output: resolve(process.env.PL_PHOTO_TEST_OUTPUT || '/tmp/pl-sketch-photo-confirmation')
}
if (!options.url) throw new Error('Set PL_PHOTO_TEST_URL to the preview URL for Sketch2Graph/star-photo-test.')
mkdirSync(options.output, { recursive: true })
const cli = process.env.PL_PHOTO_TEST_CLI || 'playwright-cli'
const run = args => {
  const result = spawnSync(cli, ['-s=photo-confirmation-fix', ...args], {
    encoding: 'utf8', timeout: 180000, maxBuffer: 8 * 1024 * 1024
  })
  const output = (result.stdout || '') + (result.stderr || '')
  if (args[0] !== 'snapshot') process.stdout.write(output.split('### Ran Playwright code')[0])
  if (result.error || result.status !== 0 || output.includes('### Error')) {
    throw result.error || new Error('Browser check failed (exit ' + result.status + ')')
  }
}
try {
  run(['open', options.url, '--browser', 'chrome'])
  run(['snapshot'])
  run(['run-code', 'async (page) => (' + checkConfirmation.toString() + ')(page, ' + JSON.stringify(options) + ')'])
} catch (error) {
  console.error(error.message)
  process.exitCode = 1
} finally {
  run(['close'])
}
