// Generate SQL: saves the question with action "generate", which starts a generation
// through the English-to-SQL proxy, then keeps saving with action "poll" until the SQL
// arrives. The browser only talks to PrairieLearn; PrairieLearn's server talks to the
// proxy. PrairieLearn's own Save and Save & Grade never generate SQL.
(function () {
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
  function resume () {
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

// Regen only: tell the server which PrairieLearn button was clicked, so Save & Grade can
// refuse SQL that no longer matches the English plan, and make "Reset to generated SQL"
// restore the last generated query without a new generation.
(function () {
  function submitLabel (submitter) {
    if (!submitter) return ''
    return [submitter.name, submitter.value, submitter.textContent]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
  }

  document.addEventListener(
    'click',
    function (event) {
      const submitter = event.target.closest && event.target.closest('button, input[type="submit"]')
      if (submitter && submitter.form) {
        submitter.form.__plIntentConsoleRegenSubmitter = submitter
      }
    },
    true
  )

  document.addEventListener(
    'submit',
    function (event) {
      const form = event.target
      if (!form || !form.querySelectorAll) return
      const label = submitLabel(event.submitter || form.__plIntentConsoleRegenSubmitter)
      const button = label.indexOf('grade') !== -1 ? 'grade' : 'save'
      form.querySelectorAll('[data-pl-intent-console-regen-button]').forEach(function (input) {
        input.value = button
      })
    },
    true
  )

  function resetParts (section) {
    return {
      button: section.querySelector('[data-pl-intent-console-regen-reset]'),
      editor: section.querySelector('.pl-intent-console-regen__code'),
      generated: section.querySelector('[data-pl-intent-console-regen-generated-sql]')
    }
  }

  // The reset button is disabled while the editor already matches the generated SQL.
  function refresh (section) {
    const parts = resetParts(section)
    if (!parts.button || !parts.editor || !parts.generated) return
    parts.button.disabled = parts.editor.value.trim() === parts.generated.value.trim()
  }

  document.addEventListener('click', function (event) {
    const button = event.target.closest && event.target.closest('[data-pl-intent-console-regen-reset]')
    if (!button) return
    const section = button.closest('[data-pl-intent-console-regen]')
    const parts = resetParts(section)
    if (!parts.editor || !parts.generated) return
    parts.editor.value = parts.generated.value
    refresh(section)
    parts.editor.focus()
  })

  document.addEventListener('input', function (event) {
    const section = event.target.closest && event.target.closest('[data-pl-intent-console-regen]')
    if (section) refresh(section)
  })

  // Consoles swapped in after Generate SQL are refreshed as they appear.
  function refreshAll () {
    document.querySelectorAll('[data-pl-intent-console-regen]').forEach(refresh)
  }
  new MutationObserver(refreshAll).observe(document.documentElement, { childList: true, subtree: true })

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', refreshAll)
  } else {
    refreshAll()
  }
})()
