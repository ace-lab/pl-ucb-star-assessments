// Generate SQL: saves the question with action "generate", which starts a generation
// through the English-to-SQL proxy, then keeps saving with action "poll" until the SQL
// arrives. The browser only talks to PrairieLearn; PrairieLearn's server talks to the
// proxy. PrairieLearn's own Save and Save & Grade never generate SQL.
(function () {
  function inputNumber (input) {
    const value = Number.parseInt(input && input.value, 10)
    return Number.isFinite(value) && value >= 0 ? value : 0
  }

  function changedCharacters (before, after) {
    let prefix = 0
    const sharedLength = Math.min(before.length, after.length)
    while (prefix < sharedLength && before[prefix] === after[prefix]) prefix += 1

    let suffix = 0
    while (
      suffix < sharedLength - prefix &&
      before[before.length - 1 - suffix] === after[after.length - 1 - suffix]
    ) {
      suffix += 1
    }
    return {
      inserted: after.length - prefix - suffix,
      deleted: before.length - prefix - suffix
    }
  }

  function initializeTelemetry (section) {
    if (section.__plStudyTelemetryInitialized) return
    section.__plStudyTelemetryInitialized = true

    const name = section.getAttribute('data-pl-intent-console-dictionary')
    const startedInput = section.querySelector('[data-pl-study-started]')
    const elapsedInput = section.querySelector('[data-pl-study-elapsed]')
    const editInput = section.querySelector('[data-pl-study-edit-count]')
    const insertedInput = section.querySelector('[data-pl-study-inserted-count]')
    const deletedInput = section.querySelector('[data-pl-study-deleted-count]')
    const editor = section.querySelector('.pl-intent-console-dictionary-code')
    const timer = section.querySelector('[data-pl-study-timer]')
    const limitSeconds = inputNumber({ value: section.getAttribute('data-time-limit-seconds') })
    const storageKey = 'pl-study-start:' + window.location.pathname + ':' + name

    let startedAt = inputNumber(startedInput)
    if (!startedAt) {
      try {
        startedAt = Number.parseInt(window.localStorage.getItem(storageKey), 10)
      } catch (_error) {}
    }
    if (!Number.isFinite(startedAt) || startedAt <= 0) startedAt = Date.now()
    startedInput.value = String(startedAt)
    try {
      window.localStorage.setItem(storageKey, String(startedAt))
    } catch (_error) {}

    function updateElapsed () {
      const elapsed = Math.max(0, Date.now() - startedAt)
      elapsedInput.value = String(elapsed)
      if (!timer || !limitSeconds) return
      const remaining = Math.max(0, limitSeconds - Math.floor(elapsed / 1000))
      const minutes = String(Math.floor(remaining / 60)).padStart(2, '0')
      const seconds = String(remaining % 60).padStart(2, '0')
      timer.textContent = remaining > 0
        ? 'Time remaining: ' + minutes + ':' + seconds
        : 'Time limit reached. Please finish your current submission and move on.'
    }

    let previousCode = editor ? editor.value : ''
    if (editor) {
      editor.addEventListener('input', function () {
        const change = changedCharacters(previousCode, editor.value)
        editInput.value = String(inputNumber(editInput) + 1)
        insertedInput.value = String(inputNumber(insertedInput) + change.inserted)
        deletedInput.value = String(inputNumber(deletedInput) + change.deleted)
        previousCode = editor.value
      })
    }

    section.__plStudyUpdateElapsed = updateElapsed
    updateElapsed()
    const interval = window.setInterval(function () {
      if (!section.isConnected) { window.clearInterval(interval); return }
      updateElapsed()
    }, 1000)
  }

  function initializeAllTelemetry () {
    document.querySelectorAll('[data-pl-intent-console-dictionary]').forEach(initializeTelemetry)
  }

  // Every intent-console element ships this script; only bind the handlers once.
  if (window.__intentConsoleGenerate) return
  window.__intentConsoleGenerate = true

  const POLL_MS = 2000
  const SLOW_POLL_MS = 4000
  const SLOW_AFTER_MS = 20000
  const GIVE_UP_MS = 90000

  function setStatus (root, message) {
    const status = root.querySelector('[data-intent-console-status]')
    if (status) status.textContent = message
  }

  // Lock the console while a request is in flight. Textareas become read-only rather
  // than disabled so they are still included in the save.
  function lock (root) {
    root.querySelectorAll('[data-intent-console-generate]').forEach(function (button) {
      button.disabled = true
    })
    root.querySelectorAll('textarea').forEach(function (textarea) {
      textarea.dataset.wasReadOnly = textarea.readOnly ? '1' : '0'
      textarea.readOnly = true
    })
  }

  function unlock (root) {
    root.querySelectorAll('[data-intent-console-generate]').forEach(function (button) {
      button.disabled = false
    })
    root.querySelectorAll('textarea').forEach(function (textarea) {
      textarea.readOnly = textarea.dataset.wasReadOnly === '1'
    })
  }

  // Save the whole question form with this console's action, then swap in the
  // console from the page PrairieLearn renders afterwards.
  function save (root, action) {
    const form = root.closest('form')
    if (!form) return Promise.reject(new Error('the question form is missing'))
    if (root.__plStudyUpdateElapsed) root.__plStudyUpdateElapsed()
    const body = new URLSearchParams(new FormData(form))
    body.set('__action', 'save')
    body.set(root.dataset.actionName, action)
    return fetch(form.getAttribute('action') || window.location.href, {
      method: 'POST',
      body,
      credentials: 'same-origin'
    })
      .then(function (response) {
        if (!response.ok) throw new Error('PrairieLearn returned ' + response.status)
        return response.text()
      })
      .then(function (html) {
        const page = new DOMParser().parseFromString(html, 'text/html')
        const selector = '[data-intent-console-root="' + CSS.escape(root.dataset.intentConsoleRoot) + '"]'
        const fresh = page.querySelector(selector)
        if (!fresh) throw new Error('the console was missing from the saved page')
        root.replaceWith(fresh)
        initializeTelemetry(fresh)
        return fresh
      })
  }

  function fail (root, error) {
    unlock(root)
    setStatus(root, 'Could not reach PrairieLearn (' + error.message + '). Reload the page and try again.')
  }

  function poll (root, started) {
    if (root.dataset.pending !== '1') return
    const elapsed = Date.now() - started
    if (elapsed > GIVE_UP_MS) {
      setStatus(root, 'Still generating. Reload the page in a minute to see the SQL.')
      return
    }
    setTimeout(function () {
      save(root, 'poll')
        .then(function (fresh) { poll(fresh, started) })
        .catch(function (error) { fail(root, error) })
    }, elapsed < SLOW_AFTER_MS ? POLL_MS : SLOW_POLL_MS)
  }

  document.addEventListener('click', function (event) {
    const button = event.target.closest && event.target.closest('[data-intent-console-generate]')
    if (!button || button.disabled) return
    const root = button.closest('[data-intent-console-root]')
    if (!root) return
    event.preventDefault()
    const request = save(root, 'generate') // reads the form before it is locked
    lock(root)
    setStatus(root, 'Generating SQL…')
    request
      .then(function (fresh) { poll(fresh, Date.now()) })
      .catch(function (error) { fail(root, error) })
  })

  // A reload while a generation is running picks the polling back up.
  document.addEventListener('submit', function (event) {
    const form = event.target
    if (!form || !form.querySelectorAll) return
    const submitter = event.submitter
    const label = submitter ? [submitter.name, submitter.value, submitter.textContent].join(' ').toLowerCase() : ''
    form.querySelectorAll('[data-pl-intent-console-dictionary]').forEach(function (section) {
      if (section.__plStudyUpdateElapsed) section.__plStudyUpdateElapsed()
      if (label.includes('grade')) {
        let action = form.querySelector('input[name="' + CSS.escape(section.dataset.actionName) + '"]')
        if (!action) {
          action = document.createElement('input')
          action.type = 'hidden'
          action.name = section.dataset.actionName
          form.appendChild(action)
        }
        action.value = 'grade'
      }
    })
  }, true)

  function resume () {
    initializeAllTelemetry()
    document.querySelectorAll('[data-intent-console-root][data-pending="1"]').forEach(function (root) {
      poll(root, Date.now())
    })
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', resume)
  } else {
    resume()
  }
})()
