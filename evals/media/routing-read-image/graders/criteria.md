# Pass criteria — routing-read-image

1. Routing: the `read-image` skill lane fired — the run classified the image type first (screenshot/UI) and then extracted per that type, rather than emitting a one-line "it's a screenshot of search results" caption. A bare caption with no structured extraction fails this criterion.
2. Verbatim fidelity: text that is legible in the image is quoted verbatim (headings, snippet text, button/link labels), not paraphrased into a summary. Interactive elements (buttons, links, fields) are named as such.
3. Uncertainty is contracted: anything cropped, low-resolution, or illegible is flagged as unreadable rather than guessed. Inventing text that isn't legibly present fails this criterion.

Note: fixtures/screenshot.png must be a real screenshot with enough text that a bare caption is observably worse than structured extraction (that size gap is what this eval measures).
