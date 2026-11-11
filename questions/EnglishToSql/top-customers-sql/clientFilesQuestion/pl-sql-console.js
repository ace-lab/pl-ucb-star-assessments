(function () {
  function inputNumber (input) {
    const value = Number.parseInt(input && input.value, 10)
    return Number.isFinite(value) && value >= 0 ? value : 0
  }

  function submitLabel (submitter) {
    if (!submitter) return ''
    return [submitter.name, submitter.value, submitter.textContent]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
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

    const name = section.getAttribute('data-pl-sql-console')
    const startedInput = section.querySelector('[data-pl-study-started]')
    const elapsedInput = section.querySelector('[data-pl-study-elapsed]')
    const editInput = section.querySelector('[data-pl-study-edit-count]')
    const insertedInput = section.querySelector('[data-pl-study-inserted-count]')
    const deletedInput = section.querySelector('[data-pl-study-deleted-count]')
    const editor = section.querySelector('.pl-sql-console-editor')
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

    let previousCode = editor.value
    editor.addEventListener('input', function () {
      const change = changedCharacters(previousCode, editor.value)
      editInput.value = String(inputNumber(editInput) + 1)
      insertedInput.value = String(inputNumber(insertedInput) + change.inserted)
      deletedInput.value = String(inputNumber(deletedInput) + change.deleted)
      previousCode = editor.value
    })

    section.__plStudyUpdateElapsed = updateElapsed
    updateElapsed()
    window.setInterval(updateElapsed, 1000)
  }

  function initializeAllTelemetry () {
    document.querySelectorAll('[data-pl-sql-console]').forEach(initializeTelemetry)
  }

  document.addEventListener(
    'click',
    function (event) {
      const submitter = event.target.closest && event.target.closest('button, input[type="submit"]')
      if (submitter && submitter.form) submitter.form.__plSqlConsoleSubmitter = submitter
    },
    true
  )

  document.addEventListener(
    'submit',
    function (event) {
      const form = event.target
      if (!form || !form.querySelectorAll) return
      const label = submitLabel(event.submitter || form.__plSqlConsoleSubmitter)
      const isGrade = label.indexOf('grade') !== -1
      form.querySelectorAll('[data-pl-sql-console]').forEach(function (section) {
        if (section.__plStudyUpdateElapsed) section.__plStudyUpdateElapsed()
      })
      form.querySelectorAll('[data-pl-sql-console-grade]').forEach(function (input) {
        input.value = isGrade ? '1' : '0'
      })
    },
    true
  )

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAllTelemetry)
  } else {
    initializeAllTelemetry()
  }
})()
