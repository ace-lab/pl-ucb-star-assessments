# Photo graph input

Enable `allow-hand-drawn` on a `pl-sketch-extension` element with an editable curve tool.
Students upload a photo, calibrate the origin and two axis references, trace
each continuous branch separately, then review and confirm the orange preview.
Nothing reaches the native canvas until confirmation. Changing the photo,
calibration, trace or fit settings invalidates the previous proposal.

The default **Keep my traced shape** follows the detected ink. It simplifies
the unsmoothed points with a 1.25-pixel geometric tolerance in the resized photo
(longest side at most 900 pixels). It retains corner vertices and endpoints,
then connects them with straight segments. It does not infer an equation.
The student should check important coordinates and branches before confirming.

**Adjust curve type** offers optional mathematical fits, including automatic
family selection, polynomials and rational curves. These use the existing
smoothed extraction and least-squares fitter. They can change a shape, so the
preview must be checked again. Each branch has its own choice.

Native spline tools smooth tangents even when given a corner vertex. Shape
transfer adds support anchors along adjacent segments, at most 12 SVG pixels
away and at most one quarter of either segment. This limits rounding while
keeping long-edge handles separately selectable. The native renderer and
grader use the same anchors. Freeform tools instead receive cubic controls
for exact straight segments. The question's configured tool, coordinate ranges,
solution and grading rules stay in place. Students can edit the native anchors
after confirmation or reopen the photo dialog to revise their trace.

This is guided ink extraction, not LLM recognition. Axis placement and tracing
still affect accuracy; preserving a detected shape also preserves extraction
mistakes and some hand wobble. Branches are treated as functions of x: loops,
vertical curves and meaningful backtracking are unsupported, and overlapping
branch domains may be rejected by the existing function grader. There is no
perspective correction, automatic critical-number recognition or confidence
score. A traced model's zero interpolation residual describes agreement with
its retained vertices; it is not a measure of accuracy against the photo.

Run the checks described in [tests/README.md](../../tests/README.md). Benchmark
datasets and experiment archives belong on research branches, outside the
production course branch.
