# Photo regression checks

Start local PrairieLearn and load this course. Open the
`Sketch2Graph/star-photo-test` question and copy its preview URL; numeric course
and question IDs depend on your local database. Set that URL before running the
browser checks:

```bash
export PL_PHOTO_TEST_URL='http://localhost:3000/pl/course/1/question/23/preview' # use your preview URL
node tests/star-photo-confirmation.cjs
node tests/star-photo-branches.cjs
node tests/star-photo-workflow.cjs
node --test tests/star-fit-branches.cjs
node --test tests/star-fit-coverage.cjs
node --test tests/star-fit-trace.cjs
node --test tests/star-sketch-extension.cjs
```

Requires Node.js, Playwright CLI (`playwright-cli` on PATH), and Chrome.
No benchmark datasets are needed: the check creates small line images in memory
and exercises the actual `star-photo-test` question through its upload, tracing,
shape review, optional mathematical fitting, and native canvas controls.

Optional environment variables:

- `PL_PHOTO_TEST_CLI`: path to the Playwright CLI executable or a wrapper.
- `PL_PHOTO_TEST_OUTPUT`: directory for screenshots (defaults to `/tmp/pl-sketch-photo-confirmation`).
- `PL_PHOTO_TEST_CASES`: optional comma-separated branch fixture IDs, such as `sharp-peak`.

The check covers photo replacement, clearing/undoing/adding strokes, calibration
changes, search width, polynomial degree, family changes, failed reads/refits,
slow/out-of-order uploads, invalid images, recovery, and successful native canvas
transfer. Display-only controls must preserve a valid proposal. Both browser
regressions use the native photo dialog without CSS expansion or layout overrides.

The branch check covers a single line, two disjoint lines, two reciprocal
branches, a three-branch graph with steep ends, and overlapping x-ranges. It checks every branch in
the preview, native SVG, saved canvas state, and gradeable submission data.
It also exercises branch-specific refitting, a failed later branch, and undo
followed by replacing a two-branch drawing with one branch. Sharp V, peak and
plateau fixtures measure preview-to-native error and rendered-to-gradeable
agreement. A native peak edit is submitted through Save & Grade and checked
after page restoration, with the independent control answer filled. The imported
shape must be valid for the existing function grader; it can still earn a low
score because the question asks for a different mathematical curve. Screenshots and raw
observations default to `/tmp/pl-sketch-photo-branches`.
The mobile case uses the original panel at 390 by 844 pixels and scrolls to the
photo and controls without changing its layout.

Overlapping x-ranges are preserved for review. The existing PrairieLearn
function-input validation may reject them on submission; this change does not
relax that validation or assess the mathematical correctness of the drawing.
The Node unit checks verify coordinate mapping and atomic transfer: a bad later
branch must leave all existing tool drawings intact.

The workflow check uses a portrait three-branch fixture at desktop 1440 by 1000
and mobile 390 by 844. It verifies that the complete photo and primary action
remain on screen, step navigation, axis-value validation, keyboard marker edits,
zoom/pan without accidental tracing or refitting, review, Escape/focus recovery,
and three-branch native state/submission data. Mobile canvas gestures use
Chromium touch events through CDP; these are browser-emulated touches, not a
physical-device camera or student usability study. Screenshots and results
default to `/tmp/pl-sketch-photo-workflow`.

Coverage tests prevent a model from winning by excluding steep sections and
verify that one continuous branch cannot contain an internal fitted pole.
Trace tests check corner-preserving simplification, endpoint retention, domain
limits, native support anchors and freeform cubic-state conversion.
The extension check verifies that its initializer and submission handling coexist
with the stock `pl-sketch` initializer in either script loading order.
