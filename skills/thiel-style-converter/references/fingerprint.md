# Measured Thiel Fingerprint (Zero to One corpus, ~43,500 words)

Read this before book-mode conversions. Numbers below were measured directly from the epub text; quoted fragments are micro-evidence of each device, kept short and used for analysis only. Do not reproduce them in output.

## Sentence distribution

| metric | measured | rewrite target |
|---|---|---|
| mean sentence length | 19.8 words | 18–21 |
| median | 17 | 16–18 |
| spread (sd) | high (mix of very short and very long) | keep real variance: doctrine lines under 8 words next to 30+ word evidence sentences |
| ≤8-word sentences | 12.7% | 11–15% |
| ≥35-word sentences | 7.3% | 5–9% |

The rhythm is not uniform mid-length prose. It is long evidence sentences discharged into short doctrine lines: "Monopoly is the condition of every successful business."

## Punctuation operators (per 1,000 words)

| mark | rate | function |
|---|---|---|
| colon | 8.7 | abstract → concrete instantiation; the signature operator |
| em dash | 4.55 | sharpening correction of the preceding clause ("doing new things — going from 0 to 1") |
| semicolon | 2.8 | symmetry or inversion between equal clauses |
| question mark | 3.4 | Socratic pivot, answered in the very next sentence |
| exclamation | ~0 (19 total, almost all inside quoted speech) | never in doctrine |

## Evidence density

- Numeric tokens: ~21.6 per 1,000 words. A number roughly every 46 words.
- Year mentions: ~4.4 per 1,000 words. A date roughly every 230 words.
- Pattern for quantitative claims: year + absolute figure + ratio. "In 2012, when the average airfare each way was $178, the airlines made only 37 cents per passenger trip. Compare them to Google... $50 billion in 2012."
- Named corpses next to named winners: Kaczynski as the extreme of "no secrets left"; dead cleantech companies against the seven questions; the 1999 crash against its four false lessons.

## Negative space (grep-verified absences)

Measured across the whole book: "I think" 0, "arguably" 0, "Let's" 2, "sort of" 2, "important to note" 0, "perhaps" 16 (mostly in reported views, not authorial hedging), "maybe" 10. Practical rule for rewrites: zero hedges, zero "Let's", zero exclamation, zero closing recap.

Cognitive imperatives (Consider / Suppose / Imagine / Compare / Ask yourself) appear ~24 times: used to run thought experiments, never to motivate.

## Signature structural moves

1. **The interview question opening.** "Whenever I interview someone for a job, I like to ask this question: 'What important truth do very few people agree with you on?'" Question posed, difficulty acknowledged, answered.
2. **The inverted famous line.** "Tolstoy opens Anna Karenina by observing: 'All happy families are alike...' Business is the opposite. All happy companies are different: each one earns a monopoly by solving a unique problem. All failed companies are the same: they failed to escape competition."
3. **The 2x2 typology.** Definite/indefinite × optimist/pessimist, each cell given a country and an era.
4. **Enumerated doctrine.** The seven questions every business must answer, each named (Engineering, Timing, Monopoly, People, Distribution, Durability, Secret) and each used to autopsy cleantech.
5. **Steelman then reversal.** Competition gets its full ideological due (Marx, Shakespeare, war metaphors) before the verdict that it destroys value.
6. **Epigram as payoff.** "Brilliant thinking is rare, but courage is in even shorter supply than genius." Lands at the end of a developed passage, 3–5 per 3,000 words, never stacked.

## Em dash modes

- **Default: zero em dashes.** Replace with colon or full stop; the colon at 8.7/1k is the signature operator and absorbs most of the dash's work.
- **Voice-faithful mode (opt-in only):** when the user explicitly asks for voice-faithful punctuation, use ~4.5/1k, correction-sharpening function only, never as a breath mark.
