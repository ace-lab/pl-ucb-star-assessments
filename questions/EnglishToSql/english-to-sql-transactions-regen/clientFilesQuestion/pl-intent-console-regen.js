(function () {
  function submitLabel(submitter) {
    if (!submitter) return '';
    return [submitter.name, submitter.value, submitter.textContent]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
  }

  document.addEventListener(
    'click',
    function (event) {
      var submitter = event.target.closest && event.target.closest('button, input[type="submit"]');
      if (submitter && submitter.form) {
        submitter.form.__plIntentConsoleRegenSubmitter = submitter;
      }
    },
    true
  );

  // Tell the server which button was clicked. The server decides whether to
  // regenerate from whether the English changed; the button only decides
  // whether a changed plan is regenerated (Save) or blocked from grading
  // (Save & Grade).
  document.addEventListener(
    'submit',
    function (event) {
      var form = event.target;
      if (!form || !form.querySelectorAll) return;

      var label = submitLabel(event.submitter || form.__plIntentConsoleRegenSubmitter);
      var action = label.indexOf('grade') !== -1 ? 'grade' : 'save';
      form.querySelectorAll('[data-pl-intent-console-regen-action]').forEach(function (input) {
        input.value = action;
      });
    },
    true
  );

  // "Reset to generated SQL" restores the last generated query without a new
  // generation. It is disabled while the editor already matches it.
  function setUpReset(section) {
    var button = section.querySelector('[data-pl-intent-console-regen-reset]');
    var editor = section.querySelector('.pl-intent-console-regen__code');
    var generated = section.querySelector('[data-pl-intent-console-regen-generated-sql]');
    if (!button || !editor || !generated) return;

    function refresh() {
      button.disabled = editor.value.trim() === generated.value.trim();
    }

    button.addEventListener('click', function () {
      editor.value = generated.value;
      refresh();
      editor.focus();
    });
    editor.addEventListener('input', refresh);
    refresh();
  }

  function setUpAll() {
    document.querySelectorAll('[data-pl-intent-console-regen]').forEach(setUpReset);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setUpAll);
  } else {
    setUpAll();
  }
})();
