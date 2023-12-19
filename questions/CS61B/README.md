Add your project's questions here, one question per subdirectory.
At a minimum, a question **must** have an `info.json` file (whose
presence is what lets PL recognize it as a question) and
`question.html`.

All contributions for your project should go into your project's
`courseInstances` subdirectory or here, with the following exceptions:

* Static assets or other files shared across multiple questions can go
in `serverFilesCourse` and `clientFilesCourse` as needed (see
[PrairieLearn docs](https://prairielearn.readthedocs.io).

* If you developed an element, its files should be as self-contained
as possible in `elements/` at the top level of the repo.  Document in
the element's `README` any files it relies on that live elsewhere (eg
`serverFilesCourse`) and give those files a name that begins with the
same name as the subdirectory for your project.

Before doing a pull request to master, **rebase** against master
(which should not be a problem if we all follow the isolation rules
above) and make sure the rebased course successfully loads into PL
with no errors when you use Load From Disk.

