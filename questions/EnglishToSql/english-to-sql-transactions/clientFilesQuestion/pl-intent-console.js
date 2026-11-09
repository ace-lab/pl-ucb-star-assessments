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
