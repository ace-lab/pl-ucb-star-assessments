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
        submitter.form.__plIntentConsoleSubmitter = submitter
      }
    },
    true
  )

  document.addEventListener(
    'submit',
    function (event) {
      const form = event.target
      if (!form || !form.querySelectorAll) return

      const label = submitLabel(event.submitter || form.__plIntentConsoleSubmitter)
      const isGrade = label.indexOf('grade') !== -1
      form.querySelectorAll('[data-pl-intent-console-two-pass-generate]').forEach(function (input) {
        input.value = isGrade ? '0' : '1'
      })
    },
    true
  )
})()
