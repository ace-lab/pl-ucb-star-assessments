/* ---------------------------------------------------------------------------
 * STAR: hand-drawn graph capture for pl-sketch.
 *
 * Ported from the Sketch to Graph prototype. This file covers the guided
 * markup path only: upload a photo, place the axes by dragging three handles,
 * trace roughly along the curve, and snap that trace onto the actual ink.
 * The result is a list of points in GRAPH coordinates.
 *
 * Everything here runs in the browser with no network and no model calls,
 * which is what lets it work inside a locked-down exam.
 *
 * Each canvas on a page gets its own instance, so nothing is shared in module
 * scope — the upstream prototype used page-wide globals and would collide if
 * a question had two sketch canvases.
 * ------------------------------------------------------------------------- */

window.StarPhoto = (function () {
  'use strict'

  function create (options) {
    const root = options.root // container element for the UI
    const onConfirm = options.onConfirm || function () { return { ok: false, message: '' } }

    // ---- per-instance state (was module-global in the prototype) ----
    let photoBmp = null
    let MW = 0
    let MH = 0
    let maskCache = null
    let markup = null
    let mode = 'axes'
    let drag = null
    let refined = null
    let lastHandle = 'X'
    let tracedCurves = null
    let tracedShapes = null
    let currentModels = null
    let branchSpecs = []
    let activeBranch = 0
    let photoLoading = false
    let photoReady = false
    let photoRequest = 0
    let step = 'photo'
    let zoom = 1
    let pan = [0, 0]
    let movingPhoto = false
    let fittedSize = [0, 0]

    root.innerHTML = `
      <div class="star-photo-ui" data-step="photo">
        <nav class="star-steps" aria-label="Photo graph steps">
          <button type="button" class="star-step star-mode-photo"><span>1</span> Photo</button>
          <button type="button" class="star-step star-mode-axes" disabled><span>2</span> Axes</button>
          <button type="button" class="star-step star-mode-curve" disabled><span>3</span> Trace</button>
          <button type="button" class="star-step star-mode-review" disabled><span>4</span> Review</button>
        </nav>
        <div class="star-workspace">
          <div class="star-photo-stage">
            <div class="star-view-toolbar">
              <div class="star-view-controls" role="group" aria-label="Photo view">
                <button type="button" class="star-zoom-out" aria-label="Zoom out" disabled>&minus;</button>
                <output class="star-zoom-level" aria-label="Photo zoom">100%</output>
                <button type="button" class="star-zoom-in" aria-label="Zoom in" disabled>+</button>
                <button type="button" class="star-fit-view" disabled>Fit</button>
                <button type="button" class="star-pan" aria-pressed="false" disabled>Move photo</button>
              </div>
              <div class="star-view-controls">
                <label class="star-grid-toggle"><input type="checkbox" class="star-units" checked> Unit grid</label>
                <label class="star-trace-toggle" hidden><input type="checkbox" class="star-show-trace"> Show trace</label>
              </div>
            </div>
            <p class="star-hint" id="${root.id}-hint"></p>
            <div class="star-canvas-wrap">
              <div class="star-empty"><strong>Your photo goes here</strong><span>Include the full graph and its axis labels.</span></div>
              <canvas class="star-canvas" tabindex="0" aria-label="Graph photo" aria-describedby="${root.id}-hint" hidden></canvas>
            </div>
            <div class="star-photo-legend">
              <span class="star-branch-count" role="status">No branches traced</span>
              <span class="star-legend-trace">Your trace</span>
              <span class="star-legend-ink" hidden>Detected line</span>
              <span class="star-legend-preview">Preview</span>
            </div>
          </div>
          <div class="star-controls">
            <section class="star-step-panel" data-panel="photo">
              <h6>Start with your paper graph</h6>
              <p>Take a photo or choose one from your device. Keep the axes and numbers readable.</p>
              <button type="button" class="btn btn-primary star-file-btn">
                Take or choose photo
                <input type="file" accept="image/jpeg,image/png,image/webp" capture="environment" hidden>
              </button>
              <p class="star-photo-name"></p>
            </section>
            <section class="star-step-panel star-scale" data-panel="axes" hidden>
              <h6>Match the paper coordinates</h6>
              <p>Place <strong>O</strong> at the origin. Put each colored marker on a known point along its axis.</p>
              <div class="star-axis-values">
                <label>Value at x marker <input type="number" step="any" value="1" class="star-xval"></label>
                <label>Value at y marker <input type="number" step="any" value="1" class="star-yval"></label>
              </div>
              <p class="star-axis-error" role="alert" hidden></p>
              <label class="star-checkbox"><input type="checkbox" class="star-equal"> Same scale on both axes</label>
              <details class="star-axis-options"><summary>Keyboard controls</summary>
                <label>Keyboard marker
                  <select class="star-marker"><option value="O">O &middot; origin</option><option value="X">x &middot; reference point</option><option value="Y">y &middot; reference point</option></select>
                </label>
                <p class="star-small">Focus the photo and use arrow keys to move this marker. Hold Shift for larger steps.</p>
              </details>
              <p class="star-scale-read"></p>
            </section>
            <section class="star-step-panel" data-panel="curve" hidden>
              <h6>One stroke for each branch</h6>
              <p>Trace only the curve. Lift your finger or mouse at each gap or asymptote, then start the next branch.</p>
              <div class="star-row">
                <button type="button" class="btn btn-light border star-undo">Undo stroke</button>
                <button type="button" class="btn btn-light border star-clear">Clear trace</button>
              </div>
              <details class="star-trace-options"><summary>Trace options</summary>
                <label>Search width <input type="range" min="6" max="48" value="16" class="star-brush"></label>
                <p class="star-small">Increase this if the detected line misses the ink near your trace.</p>
              </details>
            </section>
            <section class="star-step-panel" data-panel="review" hidden>
              <h6 class="star-review-title">Check your preview</h6>
              <p>The <strong>orange line</strong> is the graph that will go on the canvas. Check its branches, endpoints, and important coordinates against your paper.</p>
              <button type="button" class="btn btn-light border star-edit-trace">Edit my trace</button>
              <div class="star-fit-box" hidden>
                <label class="star-branch-wrap" hidden>Edit branch <select class="star-branch"></select></label>
                <p class="star-fit-meta"></p>
                <details class="star-fit-options"><summary>Adjust curve type</summary>
                  <label>Curve type
                    <select class="star-family">
                      <option value="trace">Keep my traced shape</option>
                      <option value="">Fit a mathematical curve automatically</option>
                      <option value="polynomial">Polynomial</option>
                      <option value="sine">Sine wave</option>
                      <option value="exponential">Exponential</option>
                      <option value="sqrt">Square root</option>
                      <option value="logarithmic">Logarithm</option>
                      <option value="abs">Absolute value</option>
                      <option value="rational">Rational (1/x type)</option>
                      <option value="tan">Tangent</option>
                    </select>
                  </label>
                  <label class="star-degree-wrap" hidden>Degree <input type="number" class="star-degree" min="1" max="6" step="1" value="3"></label>
                  <button type="button" class="btn btn-light border star-refit">Refit</button>
                </details>
                <details class="star-equations"><summary>View curve details</summary><div class="star-fit-eq"></div></details>
              </div>
            </section>
          </div>
        </div>
        <div class="star-workflow-footer">
          <span class="star-status" role="status" aria-live="polite"></span>
          <div class="star-footer-actions">
            <button type="button" class="btn btn-light border star-back" hidden>Back</button>
            <button type="button" class="btn btn-primary star-next" disabled>Continue to axes</button>
            <button type="button" class="btn btn-primary star-use" disabled hidden>Read my trace</button>
            <button type="button" class="btn btn-success star-confirm" disabled hidden>This matches my sketch</button>
          </div>
        </div>
      </div>
    `

    const q = (sel) => root.querySelector(sel)
    const canvas = q('.star-canvas')
    const statusEl = q('.star-status')

    const setStatus = (text) => {
      if (statusEl.textContent !== (text || '')) statusEl.textContent = text || ''
    }

    function clearFit () {
      currentModels = null
      q('.star-confirm').disabled = true
      q('.star-fit-eq').textContent = ''
      q('.star-fit-meta').textContent = ''
      updateWorkflow()
      drawPhoto()
    }

    // A fit belongs to the photo, calibration and trace it was calculated from.
    // Keep extracted points only when changing fit settings, not those inputs.
    function invalidateTrace () {
      tracedCurves = null
      tracedShapes = null
      branchSpecs = []
      activeBranch = 0
      refined = null
      clearFit()
      q('.star-fit-box').hidden = true
      setStatus('Read your trace again to update the preview.')
    }

    // ---- photo loading -----------------------------------------------------
    async function showPhoto (blob, request) {
      let bitmap
      try {
        bitmap = await window.createImageBitmap(blob, { imageOrientation: 'from-image' })
      } catch (e) {
        bitmap = await window.createImageBitmap(blob)
      }
      // A slower, superseded upload must not replace the latest chosen photo.
      if (request !== photoRequest) {
        bitmap.close()
        return
      }
      if (photoBmp) photoBmp.close()
      photoBmp = bitmap
      const sc = Math.min(1, 900 / Math.max(photoBmp.width, photoBmp.height))
      MW = Math.round(photoBmp.width * sc)
      MH = Math.round(photoBmp.height * sc)
      maskCache = null
      refined = null
      markup = {
        O: [MW * 0.5, MH * 0.55],
        X: [MW * 0.75, MH * 0.55],
        Y: [MW * 0.5, MH * 0.3],
        strokes: []
      }
      zoom = 1
      pan = [0, 0]
      canvas.hidden = false
      setMode('axes')
      resizeView()
      drawPhoto()
    }

    function calibrationError () {
      if (!markup) return ''
      const xv = Number(q('.star-xval').value)
      const yv = Number(q('.star-yval').value)
      if (!Number.isFinite(xv) || !Number.isFinite(yv) || !xv || !yv) {
        return 'Enter a nonzero number for each axis marker.'
      }
      const ax = [markup.X[0] - markup.O[0], markup.X[1] - markup.O[1]]
      const ay = [markup.Y[0] - markup.O[0], markup.Y[1] - markup.O[1]]
      if (Math.abs(ax[0] * ay[1] - ax[1] * ay[0]) < 1) {
        return 'Move the three markers apart so they are not on one straight line.'
      }
      return ''
    }

    function updateWorkflow () {
      const ready = photoReady && !photoLoading
      const count = markup ? markup.strokes.filter(st => st.length >= 3).length : 0
      const error = calibrationError()
      q('.star-photo-ui').dataset.step = step
      for (const name of ['photo', 'axes', 'curve', 'review']) {
        const button = q('.star-mode-' + name)
        button.classList.toggle('star-on', step === name)
        if (step === name) button.setAttribute('aria-current', 'step')
        else button.removeAttribute('aria-current')
        q(`[data-panel="${name}"]`).hidden = step !== name
      }
      q('.star-mode-axes').disabled = !ready
      q('.star-mode-curve').disabled = !ready || !!error
      q('.star-mode-review').disabled = !ready || !tracedCurves
      q('.star-back').hidden = step === 'photo'
      q('.star-next').hidden = step !== 'photo' && step !== 'axes'
      q('.star-next').textContent = step === 'photo' ? 'Continue to axes' : 'Continue to tracing'
      q('.star-next').disabled = !ready || (step === 'axes' && !!error)
      q('.star-use').hidden = step !== 'curve'
      q('.star-use').disabled = !ready
      q('.star-confirm').hidden = step !== 'review'
      q('.star-confirm').disabled = !ready || !currentModels || !!error
      q('.star-undo').disabled = !count
      q('.star-clear').disabled = !count
      q('.star-axis-error').hidden = !error
      q('.star-axis-error').textContent = error
      const branchLabel = count ? `${count} branch${count === 1 ? '' : 'es'} traced` : 'No branches traced'
      if (q('.star-branch-count').textContent !== branchLabel) q('.star-branch-count').textContent = branchLabel
      q('.star-review-title').textContent = currentModels
        ? `Review ${currentModels.length} branch${currentModels.length === 1 ? '' : 'es'}`
        : 'Update your preview'
      q('.star-empty').hidden = !!photoBmp
      q('.star-trace-toggle').hidden = step !== 'review'
      const showTrace = step !== 'review' || q('.star-show-trace').checked
      q('.star-legend-trace').hidden = !showTrace
      q('.star-legend-ink').hidden = !refined || !showTrace
      q('.star-legend-preview').hidden = !currentModels
      q('.star-zoom-in').disabled = !ready || zoom >= 4
      q('.star-zoom-out').disabled = !ready || zoom <= 1
      q('.star-fit-view').disabled = !ready
      q('.star-pan').disabled = !ready
      q('.star-pan').hidden = step === 'photo' || step === 'review'
      q('.star-pan').setAttribute('aria-pressed', String(movingPhoto))
      canvas.style.cursor = movingPhoto || step === 'review' ? 'grab' : 'crosshair'
      const hints = {
        photo: 'Choose a clear photo that includes your graph and its axes.',
        axes: 'Drag O to the origin. Place x and y on known points along their axes, then enter those values.',
        curve: 'Trace each continuous branch separately. Lift your finger or mouse between branches.',
        review: 'Compare the orange preview with your paper. You can zoom and drag the photo to inspect it.'
      }
      q('.star-hint').textContent = movingPhoto
        ? 'Drag to move around the photo. Turn Move photo off to place markers or trace.'
        : hints[step]
      canvas.setAttribute('aria-label', step === 'axes' ? 'Graph photo: move axis markers with the arrow keys' : 'Graph photo: ' + hints[step])
    }

    function setMode (m) {
      step = m
      mode = m
      movingPhoto = false
      drag = null
      updateWorkflow()
      q('.star-controls').scrollTop = 0
    }

    // View changes use CSS only. The bitmap, calibration and trace stay in the
    // same photo coordinates, including while the photo is zoomed or panned.
    function transformView () {
      const wrap = q('.star-canvas-wrap')
      const limit = [Math.max(0, (fittedSize[0] * zoom - wrap.clientWidth) / 2),
        Math.max(0, (fittedSize[1] * zoom - wrap.clientHeight) / 2)]
      pan = pan.map((value, i) => Math.max(-limit[i], Math.min(limit[i], value)))
      canvas.style.transform = `translate(${pan[0]}px, ${pan[1]}px) scale(${zoom})`
      const zoomLabel = Math.round(zoom * 100) + '%'
      if (q('.star-zoom-level').textContent !== zoomLabel) q('.star-zoom-level').textContent = zoomLabel
      updateWorkflow()
      drawPhoto()
    }

    function resizeView () {
      if (!photoBmp) return
      const wrap = q('.star-canvas-wrap')
      const scale = Math.min((wrap.clientWidth - 2) / MW, (wrap.clientHeight - 2) / MH)
      if (scale <= 0) return
      fittedSize = [MW * scale, MH * scale]
      canvas.style.width = fittedSize[0] + 'px'
      canvas.style.height = fittedSize[1] + 'px'
      transformView()
    }

    // ---- drawing the photo, handles and unit grid --------------------------
    function drawPhoto () {
      if (!photoBmp) return
      if (canvas.width !== MW) {
        canvas.width = MW
        canvas.height = MH
      }
      const x = canvas.getContext('2d')
      x.clearRect(0, 0, MW, MH)
      x.drawImage(photoBmp, 0, 0, MW, MH)
      if (!markup) return

      const O = markup.O
      const X = markup.X
      const Y = markup.Y

      const ray = (A, B) => {
        const dx = B[0] - A[0]
        const dy = B[1] - A[1]
        const L = Math.hypot(dx, dy) || 1
        const k = (4 * Math.max(MW, MH)) / L
        x.beginPath()
        x.moveTo(A[0] - dx * k, A[1] - dy * k)
        x.lineTo(A[0] + dx * k, A[1] + dy * k)
        x.stroke()
      }

      const xv = +q('.star-xval').value || 1
      const yv = +q('.star-yval').value || 1
      const uxv = [(X[0] - O[0]) / xv, (X[1] - O[1]) / xv]
      const uyv = [(Y[0] - O[0]) / yv, (Y[1] - O[1]) / yv]
      const lux = Math.hypot(uxv[0], uxv[1])
      const luy = Math.hypot(uyv[0], uyv[1])

      if (q('.star-units').checked && lux > 3 && luy > 3) {
        const diag = Math.hypot(MW, MH)
        const nx = Math.min(60, Math.ceil(diag / lux))
        const ny = Math.min(60, Math.ceil(diag / luy))
        x.lineWidth = 1
        for (let k = -nx; k <= nx; k++) {
          if (!k) continue
          const b0 = [O[0] + uxv[0] * k, O[1] + uxv[1] * k]
          x.strokeStyle = k % 5 ? 'rgba(30,100,215,.18)' : 'rgba(30,100,215,.38)'
          x.beginPath()
          x.moveTo(b0[0] - (uyv[0] / luy) * diag, b0[1] - (uyv[1] / luy) * diag)
          x.lineTo(b0[0] + (uyv[0] / luy) * diag, b0[1] + (uyv[1] / luy) * diag)
          x.stroke()
        }
        for (let k = -ny; k <= ny; k++) {
          if (!k) continue
          const b0 = [O[0] + uyv[0] * k, O[1] + uyv[1] * k]
          x.strokeStyle = k % 5 ? 'rgba(30,100,215,.18)' : 'rgba(30,100,215,.38)'
          x.beginPath()
          x.moveTo(b0[0] - (uxv[0] / lux) * diag, b0[1] - (uxv[1] / lux) * diag)
          x.lineTo(b0[0] + (uxv[0] / lux) * diag, b0[1] + (uxv[1] / lux) * diag)
          x.stroke()
        }
      }

      x.lineWidth = 2.5
      x.strokeStyle = 'rgba(214,48,32,.9)'
      ray(O, X)
      ray(O, Y)

      // rough strokes, then the ink the tracer locked onto
      x.strokeStyle = 'rgba(175,60,190,.32)'
      x.lineWidth = Math.max(6, +q('.star-brush').value)
      x.lineCap = 'round'
      x.lineJoin = 'round'
      const showTrace = step !== 'review' || q('.star-show-trace').checked
      if (showTrace) {
        markup.strokes.forEach((st) => {
          x.beginPath()
          st.forEach((p, i) => (i ? x.lineTo(p[0], p[1]) : x.moveTo(p[0], p[1])))
          if (st.length === 1) x.lineTo(st[0][0] + 0.1, st[0][1])
          x.stroke()
        })
      }
      if (refined && showTrace) {
        x.strokeStyle = 'rgba(30,100,215,.95)'
        x.lineWidth = 4
        refined.forEach((st) => {
          x.beginPath()
          st.forEach((p, i) => (i ? x.lineTo(p[0], p[1]) : x.moveTo(p[0], p[1])))
          x.stroke()
        })
      }
      // Preview each fitted branch separately, in the same calibrated frame.
      // Starting a new path for every branch keeps gaps disconnected.
      if (currentModels) {
        x.strokeStyle = '#d87900'
        x.lineWidth = 2.5
        currentModels.forEach((model) => {
          x.beginPath()
          window.StarFit.sampleCurve(model).forEach(([gx, gy], i) => {
            const px = O[0] + uxv[0] * gx + uyv[0] * gy
            const py = O[1] + uxv[1] * gx + uyv[1] * gy
            if (i) x.lineTo(px, py)
            else x.moveTo(px, py)
          })
          x.stroke()
        })
      }

      const dot = (p, r, fill, txt) => {
        const displayScale = canvas.getBoundingClientRect().width / MW || 1
        r = Math.max(r, 12 / displayScale)
        x.beginPath()
        x.arc(p[0], p[1], r, 0, 7)
        x.fillStyle = fill
        x.fill()
        x.lineWidth = 2.5
        x.strokeStyle = '#fff'
        x.stroke()
        x.fillStyle = '#fff'
        x.font = `600 ${Math.max(13, 12 / displayScale)}px ui-sans-serif,system-ui`
        x.textAlign = 'center'
        x.textBaseline = 'middle'
        x.fillText(txt, p[0], p[1])
      }
      if (step !== 'review') {
        dot(X, 11, '#b0431f', 'x')
        dot(Y, 11, '#1f6bb0', 'y')
        dot(O, 13, '#c2452d', 'O')
      }

      q('.star-scale-read').textContent =
        `Reference points: x = ${xv}, y = ${yv}.`
    }

    function applyEqual (from) {
      if (!q('.star-equal').checked || !markup) return
      const xv = +q('.star-xval').value || 1
      const yv = +q('.star-yval').value || 1
      const O = markup.O
      const dx = [markup.X[0] - O[0], markup.X[1] - O[1]]
      const dy = [markup.Y[0] - O[0], markup.Y[1] - O[1]]
      const lx = Math.hypot(dx[0], dx[1]) / Math.abs(xv)
      const ly = Math.hypot(dy[0], dy[1]) / Math.abs(yv)
      if (!lx || !ly) return
      if (from === 'X') {
        const k = (lx * Math.abs(yv)) / Math.hypot(dy[0], dy[1])
        markup.Y = [O[0] + dy[0] * k, O[1] + dy[1] * k]
      } else {
        const k = (ly * Math.abs(xv)) / Math.hypot(dx[0], dx[1])
        markup.X = [O[0] + dx[0] * k, O[1] + dx[1] * k]
      }
    }

    // ---- pointer handling --------------------------------------------------
    function canvasPt (ev) {
      const r = canvas.getBoundingClientRect()
      return [((ev.clientX - r.left) * MW) / r.width, ((ev.clientY - r.top) * MH) / r.height]
    }

    canvas.addEventListener('pointerdown', (e) => {
      if (!markup || !photoReady || photoLoading || e.button !== 0) return
      const p = canvasPt(e)
      canvas.setPointerCapture(e.pointerId)
      canvas.focus({ preventScroll: true })
      e.preventDefault()
      if (movingPhoto || mode === 'review' || mode === 'photo') {
        drag = { kind: 'pan', start: [e.clientX, e.clientY], pan: [...pan] }
      } else if (mode === 'axes') {
        const near = [
          ['O', markup.O],
          ['X', markup.X],
          ['Y', markup.Y]
        ]
          .map(([k, v]) => [k, Math.hypot(v[0] - p[0], v[1] - p[1])])
          .sort((a, b) => a[1] - b[1])[0]
        const displayScale = canvas.getBoundingClientRect().width / MW
        drag = near[1] < Math.max(26, 22 / displayScale) ? { kind: 'handle', key: near[0] } : null
        if (drag) {
          invalidateTrace()
          markup[drag.key] = p
          if (drag.key !== 'O') applyEqual(drag.key)
          lastHandle = drag.key
          q('.star-marker').value = drag.key
          drawPhoto()
        }
      } else {
        invalidateTrace()
        drag = { kind: 'stroke' }
        markup.strokes.push([p])
        drawPhoto()
      }
    })

    canvas.addEventListener('pointermove', (e) => {
      if (!drag || photoLoading) return
      e.preventDefault()
      if (drag.kind === 'pan') {
        pan = [drag.pan[0] + e.clientX - drag.start[0], drag.pan[1] + e.clientY - drag.start[1]]
        transformView()
        return
      }
      const p = canvasPt(e)
      invalidateTrace()
      if (drag.kind === 'handle') {
        markup[drag.key] = p
        if (drag.key !== 'O') applyEqual(drag.key)
      } else {
        const st = markup.strokes[markup.strokes.length - 1]
        const last = st[st.length - 1]
        if (Math.hypot(p[0] - last[0], p[1] - last[1]) > 2) st.push(p)
      }
      drawPhoto()
    })

    const endDrag = () => {
      if (drag && drag.kind === 'stroke') {
        const st = markup.strokes[markup.strokes.length - 1]
        if (st.length < 3) markup.strokes.pop()
      }
      drag = null
      updateWorkflow()
      drawPhoto()
    }
    canvas.addEventListener('pointerup', endDrag)
    canvas.addEventListener('pointercancel', endDrag)
    canvas.addEventListener('keydown', (e) => {
      const offsets = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }
      if (!photoReady || photoLoading || mode !== 'axes' || movingPhoto || !offsets[e.key]) return
      e.preventDefault()
      const key = q('.star-marker').value
      const delta = e.shiftKey ? 10 : 1
      invalidateTrace()
      markup[key] = markup[key].map((value, i) => Math.max(0, Math.min(i ? MH : MW, value + offsets[e.key][i] * delta)))
      if (key !== 'O') applyEqual(key)
      lastHandle = key
      updateWorkflow()
      drawPhoto()
    })

    // ---- ink detection -----------------------------------------------------
    // Adaptive threshold: a pixel counts as ink when it is meaningfully darker
    // than the average of its neighbourhood. That handles uneven lighting and
    // shadows across a photographed page, which a fixed threshold does not.
    function buildMask () {
      if (maskCache) return maskCache
      const c = document.createElement('canvas')
      c.width = MW
      c.height = MH
      const cx = c.getContext('2d', { willReadFrequently: true })
      cx.fillStyle = '#fff'
      cx.fillRect(0, 0, MW, MH)
      cx.drawImage(photoBmp, 0, 0, MW, MH)
      const d = cx.getImageData(0, 0, MW, MH).data
      const v = new Float32Array(MW * MH)
      for (let i = 0; i < MW * MH; i++) {
        const r = d[i * 4]
        const g = d[i * 4 + 1]
        const b = d[i * 4 + 2]
        const mx = Math.max(r, g, b)
        const mn = Math.min(r, g, b)
        v[i] = 0.299 * r + 0.587 * g + 0.114 * b + 0.6 * (mx - mn)
      }
      const I = new Float64Array((MW + 1) * (MH + 1))
      for (let y = 0; y < MH; y++) {
        let rs = 0
        for (let x = 0; x < MW; x++) {
          rs += v[y * MW + x]
          I[(y + 1) * (MW + 1) + x + 1] = I[y * (MW + 1) + x + 1] + rs
        }
      }
      const R = Math.max(8, Math.round(Math.max(MW, MH) / 40))
      const dk = new Uint8Array(MW * MH)
      for (let y = 0; y < MH; y++) {
        const y0 = Math.max(0, y - R)
        const y1 = Math.min(MH, y + R + 1)
        for (let x = 0; x < MW; x++) {
          const x0 = Math.max(0, x - R)
          const x1 = Math.min(MW, x + R + 1)
          const m =
            (I[y1 * (MW + 1) + x1] - I[y0 * (MW + 1) + x1] - I[y1 * (MW + 1) + x0] + I[y0 * (MW + 1) + x0]) /
            ((y1 - y0) * (x1 - x0))
          if (v[y * MW + x] < m - 20) dk[y * MW + x] = 1
        }
      }
      maskCache = { dark: dk }
      return maskCache
    }

    // Walk along the rough stroke; at each step look sideways (perpendicular to
    // the direction of travel) for ink, and move the point onto it. Runs that
    // sit on the axis lines are ignored so the trace does not get captured by
    // them where the curve crosses.
    function snapStroke (st, R) {
      const dark = buildMask().dark
      const D = (x, y) => {
        x = Math.round(x)
        y = Math.round(y)
        return x >= 0 && y >= 0 && x < MW && y < MH && dark[y * MW + x]
      }
      const O = markup.O
      const X = markup.X
      const Y = markup.Y
      const distLine = (p, A, B) => {
        const dx = B[0] - A[0]
        const dy = B[1] - A[1]
        const L = Math.hypot(dx, dy) || 1
        return Math.abs((p[0] - A[0]) * dy - (p[1] - A[1]) * dx) / L
      }
      const onAxis = (p) => distLine(p, O, X) < 4 || distLine(p, O, Y) < 4

      const path = []
      for (let i = 1; i < st.length; i++) {
        const a = st[i - 1]
        const b = st[i]
        const L = Math.hypot(b[0] - a[0], b[1] - a[1])
        const n = Math.max(1, Math.round(L / 2))
        for (let k = 0; k < n; k++) {
          path.push([a[0] + ((b[0] - a[0]) * k) / n, a[1] + ((b[1] - a[1]) * k) / n])
        }
      }
      path.push(st[st.length - 1])

      const out = []
      let prevOff = 0
      let hits = 0
      path.forEach((p, i) => {
        const a = path[Math.max(0, i - 3)]
        const b = path[Math.min(path.length - 1, i + 3)]
        let tx = b[0] - a[0]
        let ty = b[1] - a[1]
        const L = Math.hypot(tx, ty) || 1
        tx /= L
        ty /= L
        const nx = -ty
        const ny = tx
        const runs = []
        let s0 = null
        for (let k = -R; k <= R; k++) {
          const pt = [p[0] + nx * k, p[1] + ny * k]
          const on = D(pt[0], pt[1]) && !onAxis(pt)
          if (on && s0 === null) s0 = k
          if ((!on || k === R) && s0 !== null) {
            runs.push([(s0 + (on ? k : k - 1)) / 2, (on ? k : k - 1) - s0 + 1])
            s0 = null
          }
        }
        const good = runs.filter((r) => r[1] <= Math.max(6, R * 0.8))
        const pick = (good.length ? good : runs).sort(
          (A, B) =>
            Math.abs(A[0]) + Math.abs(A[0] - prevOff) * 0.8 - (Math.abs(B[0]) + Math.abs(B[0] - prevOff) * 0.8)
        )[0]
        if (pick) {
          prevOff = 0.5 * prevOff + 0.5 * pick[0]
          hits++
          out.push([p[0] + nx * pick[0], p[1] + ny * pick[0]])
        } else {
          out.push([p[0], p[1]])
        }
      })

      const sm = out.map((p, i) => {
        let sx = 0
        let sy = 0
        let n = 0
        for (let k = Math.max(0, i - 2); k <= Math.min(out.length - 1, i + 2); k++) {
          sx += out[k][0]
          sy += out[k][1]
          n++
        }
        return [sx / n, sy / n]
      })
      return { pts: sm, raw: out, snapped: hits / Math.max(1, path.length) }
    }

    // ---- pixels to graph coordinates ---------------------------------------
    // The three handles define an affine frame. Inverting it maps any pixel to
    // graph coordinates, which also means a photo taken at a slight angle still
    // reads correctly: the axes need not be perpendicular on the page.
    function markupToGraph () {
      const error = calibrationError()
      if (error) throw new Error(error)
      const O = markup.O
      const X = markup.X
      const Y = markup.Y
      const ux = +q('.star-xval').value || 1
      const uy = +q('.star-yval').value || 1
      const R = Math.round(+q('.star-brush').value)
      const ax = [X[0] - O[0], X[1] - O[1]]
      const ay = [Y[0] - O[0], Y[1] - O[1]]
      const det = ax[0] * ay[1] - ax[1] * ay[0]
      if (!det) throw new Error('The three axis dots are in a straight line — move them apart.')

      const toData = (p) => {
        const dx = p[0] - O[0]
        const dy = p[1] - O[1]
        return [((dx * ay[1] - dy * ay[0]) / det) * ux, ((ax[0] * dy - ax[1] * dx) / det) * uy]
      }

      refined = []
      const curves = []
      let snap = 0
      let n = 0
      markup.strokes.forEach((st, branchIndex) => {
        if (st.length < 3) throw new Error(`Branch ${branchIndex + 1}: trace a longer curve before reading.`)
        const r = snapStroke(st, R)
        refined.push(r.pts)
        snap += r.snapped
        n++
        // Collapse to one y per x, since pl-sketch treats a curve as a function.
        const seen = new Map()
        r.pts.map(toData).forEach(([x, y]) => {
          const k = Math.round(x * 200) / 200
          const e = seen.get(k)
          if (e) {
            e[0] += y
            e[1]++
          } else {
            seen.set(k, [y, 1])
          }
        })
        const pts = [...seen.entries()]
          .sort((a, b) => a[0] - b[0])
          .map(([x, [sy, c]]) => [Math.round(x * 100) / 100, Math.round((sy / c) * 100) / 100])
        const step = Math.max(1, Math.floor(pts.length / 60))
        const out = []
        for (let i = 0; i < pts.length; i += step) out.push(pts[i])
        if (pts.length) out.push(pts[pts.length - 1])
        if (out.length < 3) throw new Error(`Branch ${branchIndex + 1}: trace a curve with more distinct x positions.`)
        // Keep the unsmoothed ink for shape transcription. Sort in calibrated
        // x, as with the mathematical path, but retain photo-pixel precision and
        // simplify by a small geometric tolerance instead of dropping samples.
        const ordered = r.raw.slice().sort((a, b) => toData(a)[0] - toData(b)[0])
        const shape = window.StarFit.simplifyTrace(ordered, 1.25).map(toData)
          .filter((p, i, all) => !i || p[0] - all[i - 1][0] > 1e-8)
        curves.push({ points: out, tracePoints: shape })
      })

      if (!curves.length) throw new Error('No usable trace. Switch to "Trace the curve" and drag along your line.')

      const frac = snap / Math.max(1, n)
      drawPhoto()
      return { curves, snapFraction: frac, xUnit: ux, yUnit: uy }
    }

    // ---- wiring ------------------------------------------------------------
    q('.star-file-btn input').addEventListener('change', async (e) => {
      const f = e.target.files && e.target.files[0]
      if (!f) return
      const request = ++photoRequest
      photoLoading = true
      photoReady = false
      drag = null
      invalidateTrace()
      q('.star-use').disabled = true
      setStatus('Loading photo…')
      try {
        await showPhoto(f, request)
        if (request !== photoRequest) return
        photoLoading = false
        photoReady = true
        q('.star-photo-name').textContent = f.name
        updateWorkflow()
        resizeView()
        setStatus('Place the axes, then trace your curve.')
      } catch (err) {
        if (request !== photoRequest) return
        photoLoading = false
        if (photoBmp) photoBmp.close()
        photoBmp = null
        markup = null
        canvas.hidden = true
        q('.star-photo-name').textContent = ''
        setMode('photo')
        setStatus('Could not read that image.')
      }
    })

    q('.star-file-btn').addEventListener('click', (e) => {
      const input = q('.star-file-btn input')
      if (e.target !== input) input.click()
    })
    q('.star-mode-photo').addEventListener('click', () => setMode('photo'))
    q('.star-mode-axes').addEventListener('click', () => setMode('axes'))
    q('.star-mode-curve').addEventListener('click', () => setMode('curve'))
    q('.star-mode-review').addEventListener('click', () => setMode('review'))
    q('.star-edit-trace').addEventListener('click', () => setMode('curve'))
    q('.star-back').addEventListener('click', () => {
      setMode(step === 'review' ? 'curve' : step === 'curve' ? 'axes' : 'photo')
    })
    q('.star-next').addEventListener('click', () => {
      if (!q('.star-next').disabled) setMode(step === 'photo' ? 'axes' : 'curve')
    })
    q('.star-zoom-in').addEventListener('click', () => {
      zoom = Math.min(4, zoom * 1.25)
      transformView()
    })
    q('.star-zoom-out').addEventListener('click', () => {
      zoom = Math.max(1, zoom / 1.25)
      transformView()
    })
    q('.star-fit-view').addEventListener('click', () => {
      zoom = 1
      pan = [0, 0]
      transformView()
    })
    q('.star-pan').addEventListener('click', () => {
      movingPhoto = !movingPhoto
      updateWorkflow()
    })
    q('.star-undo').addEventListener('click', () => {
      if (markup && markup.strokes.length) {
        markup.strokes.pop()
        invalidateTrace()
        drawPhoto()
      }
    })
    q('.star-clear').addEventListener('click', () => {
      if (markup) {
        markup.strokes = []
        invalidateTrace()
        drawPhoto()
      }
    })
    q('.star-brush').addEventListener('input', () => {
      invalidateTrace()
      drawPhoto()
    })
    q('.star-units').addEventListener('change', drawPhoto)
    q('.star-show-trace').addEventListener('change', () => {
      updateWorkflow()
      drawPhoto()
    })
    q('.star-xval').addEventListener('input', () => {
      invalidateTrace()
      applyEqual('X')
      updateWorkflow()
      drawPhoto()
    })
    q('.star-yval').addEventListener('input', () => {
      invalidateTrace()
      applyEqual('Y')
      updateWorkflow()
      drawPhoto()
    })
    q('.star-equal').addEventListener('change', () => {
      invalidateTrace()
      applyEqual(lastHandle === 'Y' ? 'Y' : 'X')
      updateWorkflow()
      drawPhoto()
    })

    // ---- fitting ------------------------------------------------------------
    function updateFitControls () {
      const model = currentModels && currentModels[activeBranch]
      const spec = branchSpecs[activeBranch]
      const family = (spec && spec.family) || (model && model.family) || ''
      q('.star-family').value = family
      q('.star-degree-wrap').hidden = family !== 'polynomial'
      q('.star-degree').value = (spec && spec.degree) || (model && model.degree) || 3
      q('.star-fit-meta').textContent = model
        ? (currentModels.length > 1 ? `Branch ${activeBranch + 1} · ` : '') +
          `${model.label} · x from ${model.lo.toFixed(2)} to ${model.hi.toFixed(2)}`
        : ''
    }

    function selectedSpec () {
      const family = q('.star-family').value
      return family ? { family, degree: +q('.star-degree').value || 3, constraints: [], traceWeight: 1 } : null
    }

    function runFit (spec) {
      if (spec !== undefined) branchSpecs[activeBranch] = spec
      clearFit()
      if (!tracedCurves || photoLoading) return
      q('.star-fit-box').hidden = false
      setMode('review')
      try {
        const models = tracedCurves.map((fittingPoints, i) => {
          try {
            const points = branchSpecs[i] && branchSpecs[i].family === 'trace' ? tracedShapes[i] : fittingPoints
            const model = window.StarFit.fit(points, branchSpecs[i])
            const sampled = model && window.StarFit.sampleCurve(model, 16)
            if (!model || (model.family === 'trace' ? sampled.length < 2 : sampled.length !== 17) ||
                sampled.some(p => !p.every(Number.isFinite)) ||
                points.some(([x]) => !Number.isFinite(model.f(x)))) {
              throw new Error('Could not fit the whole branch. Choose another curve type or retrace it.')
            }
            return model
          } catch (err) {
            throw new Error(`Branch ${i + 1}: ${err.message || 'Could not fit that trace.'}`)
          }
        })

        q('.star-fit-box').hidden = false
        q('.star-fit-eq').replaceChildren(...models.map((model, i) => {
          const line = document.createElement('div')
          line.textContent = (models.length > 1 ? `Branch ${i + 1}: ` : '') + model.expr
          return line
        }))

        currentModels = models
        updateFitControls()
        updateWorkflow()
        drawPhoto()
        q('.star-confirm').disabled = false
      } catch (err) {
        clearFit()
        setStatus(err.message || 'Could not fit a curve to that trace.')
      }
    }

    // The student confirms the curve is a fair transcription of what they drew.
    // Only at that point does anything reach the canvas.
    q('.star-confirm').addEventListener('click', () => {
      if (!currentModels || photoLoading || q('.star-confirm').disabled) return
      const res = onConfirm(currentModels)
      setStatus(res && res.message ? res.message : '')
    })

    q('.star-use').addEventListener('click', () => {
      if (!markup || photoLoading || q('.star-use').disabled) return
      invalidateTrace()
      try {
        const result = markupToGraph()
        tracedCurves = result.curves.map((curve) => curve.points)
        tracedShapes = result.curves.map((curve) => curve.tracePoints)
        branchSpecs = tracedCurves.map(() => ({ family: 'trace' }))
        q('.star-branch-wrap').hidden = tracedCurves.length === 1
        q('.star-branch').replaceChildren(...tracedCurves.map((_, i) => {
          const option = document.createElement('option')
          option.value = i
          option.textContent = `Branch ${i + 1}`
          return option
        }))
        const pct = Math.round(result.snapFraction * 100)
        setStatus(
          pct > 80
            ? 'Preview ready. Compare the orange graph with your paper before confirming.'
            : 'Some ink was missed. Check the preview, widen the search width, or trace closer to the curve.'
        )
        runFit()
      } catch (err) {
        setStatus(err.message || 'Could not read the markup.')
      }
    })

    // Structured correction: the student overrides the family rather than
    // describing the problem in words. Same constraint objects the prototype
    // produced, without needing anything to interpret English.
    q('.star-family').addEventListener('change', () => {
      runFit(selectedSpec())
    })
    q('.star-refit').addEventListener('click', () => {
      runFit(selectedSpec())
    })
    q('.star-branch').addEventListener('change', () => {
      activeBranch = +q('.star-branch').value
      updateFitControls()
    })
    q('.star-degree').addEventListener('input', () => {
      branchSpecs[activeBranch] = selectedSpec()
      clearFit()
      setStatus('Fit settings changed. Refit to update the preview.')
    })

    if (window.ResizeObserver) new window.ResizeObserver(resizeView).observe(q('.star-canvas-wrap'))
    setMode('photo')
    return { drawPhoto, resizeView }
  }

  return { create }
})()
