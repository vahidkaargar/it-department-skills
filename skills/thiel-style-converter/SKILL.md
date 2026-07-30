---
name: thiel-style-converter
description: Convert any supplied context into book-grade Thiel-style strategic argument, with the measured Zero to One voice fingerprint enforced. Use whenever the user asks to rewrite, sharpen, translate, reframe, or convert notes, essays, arguments, startup analysis, positioning work, market commentary, founder ideas, or book sections into a Thiel-like strategic mode, and also when they say "make it Thiel", "Zero to One style", "contrarian rewrite", or ask for a strategic reframing of a draft.
---

# Thiel Style Converter

Convert supplied context into a Thiel-style strategic argument. Two jobs, both mandatory:

1. **Convert the frame.** Find the consensus hiding in the context, invert it into a secret, split the world in two, name what becomes scarce, end with a consequence that makes misunderstanding costly.
2. **Hit the measured voice.** Zero to One argues through history, named cases, and numbers, in sentences with a specific measured shape. Frame without texture reads as a generic strategy essay. Texture without frame reads as parody. You need both.

Do not impersonate Peter Thiel as a living author or reproduce his sentences. Apply the rhetorical mode: contrarian framing, first-principles distinctions, monopoly and category logic, secrets, definite optimism, cold compression. Never write in his first person or sign anything as him.

Before any book-mode conversion, read `references/fingerprint.md` for the full measured fingerprint with examples from the source corpus.

## Fidelity Law

This converter changes how an idea argues. It must not change what is true.

- Never invent statistics, survey results, quotes, or events about the user's subject. If the argument needs a figure the context does not supply, leave a labeled slot: `[FIGURE NEEDED: e.g. churn % before/after]`. A visible slot is correct; a confident fabrication is a defect.
- Real public history you are certain of (the 1999 crash, Google vs the airlines, known founding dates) is allowed and encouraged. That is how this voice argues. If you are not certain, use a slot.
- If the context supplies a claim the user flags as unverified ("don't quote me on the number"), either drop it or carry it visibly hedged as reported, never as fact.
- Inversion sharpens claims. When your inversion changes the truth-value of the user's claim rather than its frame, append one line after the output: `Note: the original claimed X; this version claims Y.` The user decides which they believe.

## Conversion Workflow

Before writing:

1. Extract the user's actual claim.
2. State the consensus version of that claim **fairly, at its strongest**. Two or more sentences. The reversal lands only if the consensus looked reasonable first. Zero to One treats Marx and Shakespeare seriously before ruling against competition; it does not dunk on strawmen. A consensus made to look lazy produces a cheap contrarian, not a secret.
3. Ask what the consensus misses. Invert into a secret: important, non-obvious, under-believed, consequential, tied to a concrete mechanism.
4. Define the two worlds (old/new, monopoly/competition, definite/indefinite, execution/judgment, capability/credibility).
5. Name what was scarce in the old world and what becomes scarce in the new one.
6. Choose evidence: which named cases, dates, and figures from the context or from public history will carry each claim (see Evidence Requirements).
7. Consider a typology if the material supports one: a 2x2 (the definite/indefinite optimism move) or an enumerated doctrine (the seven questions move). These are as characteristic as binaries.
8. If the context involves markets or companies, ask the monopoly questions: what comparison must be destroyed, what category can be owned, what sentence should the market repeat unprompted.
9. End with a hard consequence stated as doctrine.

## No House Thesis

Every conversion derives its own secret from the supplied material. Never carry a favorite thesis, a previous conversion's conclusion, or a canned frame into new material: a converter that routes every input to one conclusion has stopped converting.

## Evidence Requirements

Zero to One runs a number roughly every 46 words and a year every 230. Doctrine floats; evidence anchors. Enforce:

- At least one named real-world case per 300 to 500 words, with a date or a figure attached, or a labeled slot where the user must supply one.
- Quantitative claims get year + figure + ratio ("Google took in $50 billion in 2012; the airlines made 37 cents per passenger" is the pattern: absolute number, then the comparison that makes it mean something).
- Named failures argue alongside named successes. One corpse per argument. Kaczynski sits next to Google; cleantech's dead companies prove the seven questions.
- Examples are proof inside the argument, never decoration after it.
- Personal witness beats citation when the context supplies it ("we rebuilt X in 4 days" is better evidence than any industry report). Use what the user gave you before reaching outward.

## Opening Moves

Vary the opening by type. Never open two consecutive conversions the same way, and never use the literal template "Most people think X. The opposite is true."

- **The contrarian question.** Pose the question whose honest answer is unpopular. Answer it in the next sentence.
- **The historical scene.** A specific moment with a date, then the lesson everyone drew from it, then the lesson they should have drawn.
- **The inverted famous line.** Take a known quotation or proverb and reverse it ("All happy companies are different"). Only when a genuinely famous line fits.
- **The definitional cleave.** "X is not Y. X is Z." Then spend the piece earning the second sentence.
- **The steelman.** Open with the consensus at its most persuasive, sustained long enough that the reader nods, then break it.

## Sentence Mechanics

Measured targets from the source corpus (per 1,000 words unless noted):

| metric | target |
|---|---|
| mean sentence length | 18–21 words |
| median | ~17 |
| short sentences (≤8 words) | ~13% |
| long sentences (≥35 words) | ~7% |
| colons | ~8.7 |
| semicolons | ~2.8 |
| questions | ~3.4, each answered in the next sentence |
| numbers/dates | ~20 |
| hedges, exclamations, "Let's", recaps | zero |

Punctuation is functional, not decorative:

- **Colon** = abstract claim, then its concrete instantiation. This is the workhorse operator.
- **Semicolon** = symmetry or inversion between two clauses of equal weight.
- **Em dash** = a sharpening correction of what was just said, nothing else. **Default: zero em dashes.** Substitute the colon (his heavier operator anyway) or a full stop. Only when the user explicitly asks for voice-faithful punctuation, use em dashes at roughly 4 to 5 per 1,000 words, correction function only.
- Questions are Socratic pivots, never rhetorical dangles. Every question gets its answer immediately. Never end a piece on a question.
- Imperatives are cognitive (Consider, Suppose, Imagine, Compare), never motivational (no "Start today").
- Epigrams: 3 to 5 per 3,000 words, placed at section boundaries as the paragraph's payoff line. One aphorism earns its place at the end of a developed argument. Stacked aphorisms are the failure mode of imitation; aphorism-free prose is the failure mode of caution.
- **Measure before returning.** Estimate your draft's mean sentence length. Staccato inputs pull imitations choppy; that drift is the classic voice-transfer failure, and preserved quote lines make it worse. If the body mean sits under ~15 words, fuse adjacent short sentences into mid-length load-bearing ones and keep standalone doctrine lines only where a developed argument earned them.

## Format Modes

- **Book mode** (chapters, essays, manuscript): developed paragraphs, integrated examples, built transitions, hard consequence ending. Read the fingerprint reference first.
- **Diagnostic mode** (user asks what is weak): return the weak thesis, the sharper secret, the missing world-split, the missing scarcity shift, the missing evidence anchors, and a rewrite direction. Do not rewrite unless asked.
- **Direct rewrite mode** (user just says rewrite): return the converted text, plus the truth-value note only if triggered, plus any `[FIGURE NEEDED]` slots listed once at the end.

Short-form requests keep the full strategic structure, compressed; length compresses, the frame does not.

## Quality Checklist

Before returning:

- Frame converted, not just prose restyled? A secret, two worlds, a scarcity shift, a costly consequence?
- Consensus stated fairly for 2+ sentences before the reversal?
- A named case with a date or figure (or a labeled slot) in every 300 to 500 words? A named failure somewhere?
- Zero invented figures about the subject? Unverified supplied claims dropped or visibly hedged?
- Opening differs from the last conversion's opening, and is not the banned template?
- Every question answered immediately? No hedges, no exclamations, no recap ending?
- Em dash mode correct for the request? Epigram count in range, placed at boundaries?
- Matches the requested mode and length?
