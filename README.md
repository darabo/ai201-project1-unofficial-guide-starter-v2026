# The Unofficial Guide

Author: Dara Bonakdar

Corpus: campus_life

---

# Unit 1

## What This Does

This is a retrieval-augmented question-answering system built on the `campus_life` corpus — 88 short, single-topic posts about things like course workload, dining halls, housing, registration deadlines, and campus admin trivia that don't show up on any official university page. It answers specific questions a student would actually ask, like "How does the housing lottery work?" or "How can I save money on textbooks?", by retrieving the most relevant post, checking whether the match is close enough to be trustworthy, and generating a short answer that names its source. Questions the corpus doesn't cover — general trivia unrelated to campus life — are refused rather than answered from the model's own training data.

## Chunking Strategy

**Chunk size:** paragraph-grouped, capped at 800 characters
**Overlap:** none — splits only happen between paragraphs, never mid-text

Every document in `campus_life` is short: 183–554 characters, well under the 800-character cap. So instead of the fallback's fixed-size character windows, `split_documents` groups a document's paragraphs together and only cuts between paragraphs, never inside one — and for this corpus, since nothing reaches the cap, that means every document stays a single chunk (88 documents, 88 chunks, same count as the fallback). The 800-character number isn't tuned against anything I actually saw here; it's a safety net for a longer document that isn't in this corpus yet, not a real constraint on today's chunks. Overlap doesn't apply to this strategy at all, since a shared character window only matters when a split happens through the middle of continuous text, and this chunker never does that — it only ever splits at a paragraph boundary.

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_biol_160.txt#0` — produced by: `chunker.py::split_documents`

```
BIOL 160 Cell Biology

I lived here my sophomore year. Format is lecture three times a week with a weekly lab. Assessment: four unit tests and a cumulative final. Not curved.

Expect 9 to 11 hours a week, the heaviest first-year course by reputation.

The one piece of advice: the unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.
```

**Chunk 3** — source: `course_hist_118_workload.txt#0` — produced by: `chunker.py::split_documents`

```
Workload for HIST 118 Modern World History

People keep asking so: a lot of reading, about 120 pages a week, but no problem sets. That's real time, not optimistic time.

It's front-loaded — the first month is heavier than the rest, partly because you're learning the format.
```

**Chunk 4** — source: `dining_pellew_dining_hall_followup.txt#0` — produced by: `chunker.py::split_documents`

```
Re: Pellew Dining Hall

Adding to what people have said about Pellew Dining Hall. The wait figure of 12 to 18 minutes at peak matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.

Also worth saying: the furthest hall from anywhere, next to the athletics centre. Nobody tells you this at orientation.
```

**Chunk 5** — source: `housing_innisfree_hall.txt#0` — produced by: `chunker.py::split_documents`

```
Innisfree Hall — what it's actually like

Transferred in last year, so take this with a grain of salt. Built 1991, renovated 2022. Rooms are doubles arranged as pairs sharing one bathroom between two rooms.

The good: the shared-bathroom-between-two-rooms arrangement is the best compromise on campus.

The bad: no air conditioning, which matters for the first three weeks of September.

Laundry costs $1.75 wash, $1.75 dry, app-based. On noise: moderate; the building is L-shaped and the short wing is much quieter.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:** What are the most common student reactions?

**Answer:**

```
I don't have enough information to answer what the most common student reactions are.

Sources retrieved: course_cs_210.txt, course_cs_210_exams.txt, course_econ_101.txt, course_stat_150.txt, money_textbooks.txt
```

This is a near-miss: the gate passed it (best distance 0.663, under the 0.7 cutoff), so it reached the model — but none of the retrieved chunks actually answer "student reactions" in general, they just share vocabulary with the question. There's no source line here because the model correctly declined to cite anything, rather than naming a source that doesn't actually support the claim. This is the second grounding layer catching what the distance-based gate let through.

**My relevance cutoff:**

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

My cutoff is **0.6**.

| Question                                                     | In corpus? | Best distance |
| ------------------------------------------------------------ | ---------- | ------------- |
| How does the housing lottery work?                           | yes        | 0.315         |
| What do students say about the food options?                 | yes        | 0.593         |
| How do students feel about the workload?                     | yes        | 0.455         |
| What happens if I drop a course after the add/drop deadline? | yes        | 0.253         |
| How can I save money on textbooks?                           | yes        | 0.362         |
| What is the capital of Mongolia?                             | no         | 0.825         |
| How do I change the oil in a diesel engine?                  | no         | 0.934         |
| Who won the 1994 World Cup?                                  | no         | 0.886         |
| What is the recommended dosage of ibuprofen for a headache?  | no         | 0.844         |
| How do I write a for loop in Rust?                           | no         | 0.896         |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

I asked Claude Code to replace the starter's fixed-size chunking function for Milestone 3. Instead of just picking a number, it read the actual files in `corpora/campus_life/documents/` first and reported that every document was under 554 characters, well under the 800-character chunk size, so a character-count splitter would never even fire on this corpus. It proposed grouping by paragraph breaks instead, keeping 800 characters only as a safety cap for a longer document that doesn't exist in this corpus yet. I kept that as-is, printing the 5 sample chunks afterward confirmed every one read as a complete thought, with no sentence cut in half.

After running retrieval on all five of my test questions, three of them had noticeably worse best-distances (0.64–0.68) than the other two. I asked Claude to check why. It grepped the corpus for the keywords in each question's `expects` field and found that three of my questions — "student population," "academic support," "extracurricular activities" — had expected answers that didn't match anything actually in the corpus; they read like leftover placeholder text rather than something written for `campus_life`. I had it rewrite those three questions using real document content instead (the housing lottery, the add/drop deadline, and textbook costs), each with an `expects` value pulled from the actual source text, which dropped their best-distances to 0.25–0.36.

For Unit 2, I built `scorer.py`'s `judge()` as an exact substring check, and every question came back failing. I asked Claude Code why, and it traced it to two separate problems: the check required my full `expects` sentences to appear verbatim in the model's paraphrased answers, and separately, my `expects` values didn't match the corpus's own wording (12-hour clock notation, "student shuttle" vs. "campus shuttle"). I rewrote `expects` into short phrases myself, then iterated twice more when two of the five still failed — once on spacing ("7 am" vs. "7am") and once on an inserted word ("120 hours" vs. "120 credit hours") — asking each time what specifically didn't match rather than asking it to patch the code.

Later, after all five criteria came back MET with nothing to diagnose, I asked Claude to check whether that was a real result or a target set too low. It ran `python chunker.py` and found the corpus's longest document was 549 characters against my chunker's 650-character single-chunk cutoff — meaning `split_documents` had never actually split anything. The two "easy" criteria (chunk contains the answer, chunk reads as complete) had never been tested against a real chunk boundary. That diagnosis is what the Milestone 4 chunking rewrite was built to test.

For the Unit 2 stretch, I gave Claude Code the grading rubric and my first
Unit 2 grade (13 of 15) and asked why. It matched each rubric line against
the README and the results files and traced the gap to one rule: the two
points for "every miss names a pipeline stage" aren't available when nothing
was missed, and all five of my criteria were MET — so 13 was the ceiling for
that submission. It re-ran the chunker and retrieval read-only to check that
the all-MET result was real rather than a scoring mistake (it was). It also
flagged that my `expects` edits in `questions.py` amounted to changing
criterion 5's yardstick without a recorded revision in `criteria.md`. For
the second improvement it recommended lowering `top_k` over hybrid search,
because my own What's Still Broken said criterion 1 passed only because the
window was exactly 5 wide, and a one-line change would test that directly.
I went with that. It then made the change, ran `run_eval.py`, and drafted
the Run Log — After 2 from the results file; the criterion 5 call — MET
against the criterion as written, even though the scorer fails the same
question — is the part of that draft I read most carefully, because it's
where the criterion and the scorer disagree.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion                                    | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer       | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 2. Every answer names a source               | 5 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 3. Gate stops out-of-corpus questions        | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 4. Sampled chunks read as complete thoughts  | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 5. Named source contains the expected phrase | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |

Full per-question, per-run data: `results/run_2026-09-23_2116_before.md`.

**Criterion 1** — `store.py::search`, chunks from `chunker.py::split_documents`. Every question's top-1 result is the correct document, e.g. for "When do parking permits go on sale?":

```
#   distance   source                           preview
1   0.3423     admin_parking_permits.txt        On the parking permits  Student permits for the west...
```

That document is a single chunk (`admin_parking_permits.txt#0`), and its full text contains the answer:

```
On the parking permits

Student permits for the west lots go on sale in August and sell out in about three days. The east lot never sells out because it's a 12-minute walk. There is no waitlist — people who miss the window park on Verrill Street and walk in, which is legal but unmarked and confuses everyone.
```

**Criterion 2** — `generate.py::answer_from_chunks`. Every answer names a source, e.g.:

```
Student permits for the west lots go on sale in August.

Source: admin_parking_permits.txt
```

**Criterion 3** — `gate.py::check` via `run_eval.py::check_out_of_scope`:

```
| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.825 | refused |
| How do I change the oil in a diesel engine? | 0.934 | refused |
| Who won the 1994 World Cup? | 0.886 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.844 | refused |
| How do I write a for loop in Rust? | 0.896 | refused |
```

**Criterion 4** — `chunker.py::split_documents` via `app.py::cmd_chunks` (spread sample of 5 across the corpus). Two of the five:

```
Chunk  |  source: admin_add_drop_deadline.txt#0  |  produced by: chunker.py::split_documents

On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

```
Chunk  |  source: housing_innisfree_hall.txt#0  |  produced by: chunker.py::split_documents

Innisfree Hall — what it's actually like

Transferred in last year, so take this with a grain of salt. Built 1991, renovated 2022. Rooms are doubles arranged as pairs sharing one bathroom between two rooms.

The good: the shared-bathroom-between-two-rooms arrangement is the best compromise on campus.

The bad: no air conditioning, which matters for the first three weeks of September.

Laundry costs $1.75 wash, $1.75 dry, app-based. On noise: moderate; the building is L-shaped and the short wing is much quieter.
```

**Criterion 5** — named source document checked against `expects` in `questions.py`:

```
Q: What are the graduation requirements?
Answer cites: admin_graduation_requirements.txt
expects: "120"
admin_graduation_requirements.txt: "120 credit hours, a completed major, and the general education requirements..."
```

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| #   | Criterion                                 | Verdict | How I decided                                                                                                                                                                                                                                                                                                                                                                  |
| --- | ----------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Retrieved chunk contains the answer       | MET     | `python app.py retrieve` on all 5 questions: the top-1 result is always the correct document, and every one of those documents turns out to be a single chunk, so the answer is never split away from what got retrieved. 5/5, not 4/5.                                                                                                                                        |
| 2   | Every answer names a source               | MET     | Read all 15 answers (5 questions × 3 runs) in the run log; every one names at least one source file, either as an explicit "Source:" line or an inline citation. 15/15.                                                                                                                                                                                                        |
| 3   | Gate stops out-of-corpus questions        | MET     | Directly from `run_eval.py::check_out_of_scope`: all 5 out-of-scope questions were refused, with distances (0.82–0.93) well clear of the 0.6 cutoff.                                                                                                                                                                                                                           |
| 4   | Sampled chunks read as complete thoughts  | MET     | `python app.py chunks` on a 5-chunk spread sample: each one is a full, self-contained post with no sentence cut at either edge. This follows from the same fact as criterion 1 — the corpus has 88 documents and produces exactly 88 chunks, so no document is ever split, and "does the chunk read as complete" reduces to "is the source post itself coherent," which it is. |
| 5   | Named source contains the expected phrase | MET     | For each question, checked the document the answer cited against the `expects` value in `questions.py`: `admin_parking_permits.txt` contains "August", `transit_shuttle.txt` contains "7am to 11pm" and "free", `admin_graduation_requirements.txt` contains "120", `admin_add_drop_deadline.txt` contains "end of week six". 5/5.                                             |

Every criterion cleared its target, several at 5/5 against a 4/5 bar. That's not evidence the system is unusually strong, it's evidence that criteria 1 and 4 in particular were close to unmissable by construction: nothing in this corpus is long enough for `chunker.py` to ever split a document, so "the chunk has the answer" and "the chunk is a complete thought" were never really at risk once retrieval found the right document. Worth tightening in a future unit, see What I'd Do Differently.

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

Nothing was missed — all five criteria came out MET (see Verdicts above). So
there's no failure to trace to a pipeline stage. What there is instead is a
reason two of those targets couldn't really have failed, and it traces to one
stage: chunking.

**Stage: chunking (`chunker.py::split_documents`).** The function only splits
a document into multiple chunks once it's longer than 650 characters — below
that, the whole document becomes chunk `#0` and the paragraph/sentence-boundary
logic never runs. Running `python chunker.py` on the corpus shows why that
threshold never engages: `campus_life` produces 88 chunks from 88 documents,
average 317 characters, longest only 549. No document in this corpus reaches
650 characters, so `split_documents` has never executed its actual splitting
branch — every chunk it has ever produced here is one whole document.

That's the mechanism behind criteria 1 and 4 both landing at 5/5 against a 4/5
target: criterion 1 ("retrieved chunk contains the answer") can't fail unless
retrieval picks the wrong document, because there's no such thing as a chunk
that's _part of_ a document here. Criterion 4 ("chunks read as complete
thoughts") can't fail either, for the same reason — every "chunk" I sampled is
just a full post someone wrote to already read as one complete thought.
Neither criterion has ever tested what happens when a document actually gets
cut in two.

**Pattern:** these aren't two independent easy passes, they're the same root
cause twice — a chunk-size threshold that this corpus never crosses.

**What I'd tighten:** criterion 1's target, from "4 of 5 questions have the
answer in a retrieved chunk" to something that's actually at risk of failing,
e.g. lowering `CHUNK_SIZE`/the 650-character threshold enough that at least
some of my 5 answer documents get split, then requiring the answer survive
being retrieved from a partial chunk. As written, the target was safe by
construction, not because retrieval is strong.

## The Improvement

**What I changed:** Rewrote `chunker.py::split_documents`. The old version
only ever cut between paragraphs and used a 650/500-character size cutoff;
since every document in `campus_life` is under 550 characters and almost all
of them are a single body paragraph after the heading, that logic never
actually split a document — 88 in, 88 out. The new version lowers the
single-chunk cutoff to 160 characters and splits on **sentence** boundaries,
not just paragraph boundaries, so a one-paragraph post can be divided too. It
still attaches the heading to every resulting chunk and merges a trailing
fragment under 60 characters onto the previous chunk rather than leaving it
to stand alone. Re-indexing now produces 220 chunks from the same 88
documents (avg 143 characters, down from 317).

**Why I picked it:** This is exactly what the Milestone 3 diagnosis named —
criteria 1 and 4 were MET only because the chunker never actually split
anything, so neither one had ever been tested against a real chunk boundary.
This change makes that boundary real and re-runs the same five criteria
against it.

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion                                    | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer       | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 2. Every answer names a source               | 5 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 3. Gate stops out-of-corpus questions        | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 4. Sampled chunks read as complete thoughts  | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 5. Named source contains the expected phrase | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |

Full per-question, per-run data: `results/run_2026-09-23_2149_after.md`.

`python app.py retrieve` on the same 5 questions, post-rebuild:

```
When do parking permits go on sale?         → #1 admin_parking_permits.txt#0          distance 0.308
What are the hours of the campus shuttle?   → #1 transit_shuttle.txt#0                distance 0.281
What are the graduation requirements?       → #1 admin_graduation_requirements.txt#0  distance 0.274
How much is the student shuttle?            → #1 transit_shuttle.txt#1                distance 0.523
What is the deadline to drop a class        → #5 admin_add_drop_deadline.txt#1        distance 0.502
```

Four of the five answer-bearing chunks still rank #1. The fifth —
`admin_add_drop_deadline.txt#1`, the chunk holding "through the end of week
six" — now ranks **5th out of 5**, distance 0.502, because splitting the
document created two other `admin_add_drop_deadline.txt` chunks (the add
deadline, and the "nothing on the registrar's site" aside) that now compete
with it for the same slots. It still clears the 0.6 gate and still lands
inside `top_k=5`, so criterion 1 still counts it a pass — but only just.

Real output, the two questions where the split mattered most:

```
How much is the student shuttle? — run 1
The campus shuttle is free with a student ID.
Source: transit_shuttle.txt
```

```
What is the deadline to drop a class — run 1
The deadline to drop a class is the end of week six, though dropping after
week two will show as a "W" on your transcript (admin_add_drop_deadline.txt).
```

**Did it help?** It didn't flip any verdict — all five criteria were MET
before and stayed MET after. But "didn't change the verdict" isn't the same
as "didn't matter": before this change, criteria 1 and 4 passed because
nothing was ever really tested (every chunk was a whole document). Now they
pass because the answer actually survived being split away from the rest of
its document, which is what those criteria were supposed to measure in the
first place. The one place this got interesting is question 5: its
answer-bearing chunk dropped from comfortably retrieved to the very last slot
in `top_k=5`. That's a real, if narrow, margin — a slightly smaller `top_k`,
or a slightly different sentence split, and this specific question would flip
to a miss. The improvement made the test honest; it also showed the honest
version has less margin than the old numbers implied.

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## Stretch — A Second Measured Improvement

<!-- Stretch item from the unit 2 list: a second change from the Milestone 4
     menu, run and logged the same way as the first. Declared here BEFORE
     building it — the commit that adds this section changes nothing else. -->

**Declared before building.** I'm making a second change from the Milestone 4
menu: lowering `TOP_K` in `config.py` from 5 to 3. Nothing else changes; the
sentence-boundary chunker from The Improvement stays in place, so this is
measured on top of it, not instead of it.

**Which weakness it targets:** the first item in What's Still Broken. After
the chunking change, the answer-bearing chunk for "What is the deadline to
drop a class" (`admin_add_drop_deadline.txt#1`, "through the end of week six")
ranks 5th of 5 at distance 0.502 — criterion 1 passes for that question only
because the retrieval window is exactly 5 wide. A narrower window does two
things at once: it tests whether that pass was real or an accident of `top_k`,
and it hands the model less off-topic material (for that question, two of the
five retrieved chunks come from `admin_grade_appeals.txt` and
`admin_pass_fail_option.txt`, which have nothing to do with dropping a class).

**How I'll measure it:** `python run_eval.py --label after2`, then the same
five-criterion table as the two logs above, real output pasted underneath,
and a plain statement of whether it helped — including if it made things
worse. My expectation going in: criterion 1 drops to 4/5 (still MET at a
4-of-5 target) because the week-six chunk falls outside the top 3, and the
drop-deadline answer itself probably gets worse, since the model will only
see the add-deadline half of that document.

### Run Log — After 2

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after2`, with TOP_K = 3. -->

| Criterion                                    | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer       | 4 of 5 | 4/5   | 4/5   | 4/5   | MET     |
| 2. Every answer names a source               | 5 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 3. Gate stops out-of-corpus questions        | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 4. Sampled chunks read as complete thoughts  | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 5. Named source contains the expected phrase | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |

Full per-question, per-run data: `results/run_2026-09-27_2131_after2.md`.
The same file's `scorer.py::judge` column — does the *answer text* contain
`expects` — reads 4/5 in every run, because the drop-deadline question
fails all three times:

```
| Question | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| When do parking permits go on sale? | pass | pass | pass |
| What are the hours of the campus shuttle? | pass | pass | pass |
| What are the graduation requirements? | pass | pass | pass |
| How much is the student shuttle? | pass | pass | pass |
| What is the deadline to drop a class | fail | fail | fail |
```

**Criterion 1** — `store.py::search` via `app.py::cmd_retrieve`, now
`top_k=3`. The other four questions still put the answer chunk at rank 1
(distances 0.308, 0.281, 0.274, 0.523, unchanged from the after log). The
drop-deadline question no longer retrieves the chunk that holds the answer:

```
Question: What is the deadline to drop a class

#   distance   source                           preview
1   0.3954     admin_add_drop_deadline.txt      On the add/drop deadline  You can add a course throu...
2   0.4187     admin_add_drop_deadline.txt      On the add/drop deadline  Nothing anywhere on the re...
3   0.4868     admin_grade_appeals.txt          On the grade appeals  Skipping the instructor step g...

Gate: best distance 0.395 is under the 0.6 cutoff
```

Ranks 1 and 2 are `admin_add_drop_deadline.txt#0` (the add deadline) and
`#2` (the "nothing on the registrar's site" aside). `#1` — "Dropping is a
longer window — through the end of week six" — was rank 5 at 0.502 in the
after log and is now outside the window. Retrieval is deterministic, so this
is one number in all three columns: 4/5.

**Criterion 2** — `generate.py::answer_from_chunks`. All 15 answers name a
source, including the three where the model declines. Drop-deadline, run 1
(runs 2 and 3 differ only by "state" vs. "mention"):

```
Based on the provided documents, you can add a course through the end of the second week, but the documents do not state the deadline to drop a class. 

Source: admin_add_drop_deadline.txt
```

**Criterion 3** — `gate.py::check` via `run_eval.py::check_out_of_scope`.
`top_k` doesn't change the best distance, so this is identical to the after
log:

```
| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.825 | refused |
| How do I change the oil in a diesel engine? | 0.871 | refused |
| Who won the 1994 World Cup? | 0.858 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.833 | refused |
| How do I write a for loop in Rust? | 0.864 | refused |
```

**Criterion 4** — `chunker.py::split_documents` via `app.py::cmd_chunks`.
`top_k` doesn't touch chunking, so the index is the same 220 chunks as the
after log. The 5-chunk spread sample from the current index, first two:

```
Chunk 1  |  source: admin_add_drop_deadline.txt#0  |  produced by: chunker.py::split_documents

On the add/drop deadline

You can add a course through the end of the second week.
```

```
Chunk 2  |  source: course_cs_210.txt#2  |  produced by: chunker.py::split_documents

CS 210 Data Structures

Expect 8 to 10 hours a week outside class. The one piece of advice: do the labs even though they're only 10% — the exams reuse the lab problems.
```

Each is a complete sentence with nothing cut at either edge, so 5/5 against
the criterion as written. Chunk 1 is also exactly what the model was handed
for the drop question: a complete thought about the *add* deadline.

**Criterion 5** — this is where the change exposed something. The
drop-deadline answers all cite `admin_add_drop_deadline.txt`, and that file
does contain "end of week six" — so the criterion as written ("the source
document named in the answer contains the expected phrase") passes, 5/5,
even though the answer itself says the documents don't state the deadline.
The criterion checks the file, not the answer, and can't tell a correct
answer from a non-answer that names the right file. `scorer.py::judge`,
which checks the answer text, fails the same question three times. I've
kept the verdict against the criterion as written, and recorded what it
missed here rather than quietly swapping in the scorer's number.

**Did it help?** No — and this time the numbers move, which the first
improvement's didn't:

| Measure                                  | Before (top_k 5, old chunker) | After (top_k 5, new chunker) | After 2 (top_k 3, new chunker) |
| ---------------------------------------- | ----------------------------- | ---------------------------- | ------------------------------ |
| Criterion 1, all three runs              | 5/5                           | 5/5                          | 4/5                            |
| `scorer.py` passes, out of 15            | 15                            | 15                           | 12                             |
| Drop-deadline answer                     | "end of week six" ×3          | "end of week six" ×3         | "documents do not state" ×3    |
| Rank of the week-six chunk               | 1 (whole document)            | 5                            | not retrieved                  |
| Off-topic chunks handed to the model, Q5 | 3 of 5                        | 2 of 5                       | 1 of 3                         |

No verdict flipped: 4/5 still clears a 4-of-5 target, so the table says MET
across the board. But the system got worse at the one question the change
was aimed at. The narrower window did remove off-topic material (the last
row), and the other four answers are unchanged and still correct — but it
also removed the only chunk that answered the question, and the model did
the right thing with what it was given: it declined instead of guessing. So
the diagnosis in What's Still Broken was right that criterion 1's pass
depended on the window being exactly 5 wide, and wrong about what to do
about it. The problem isn't the window size; it's that the week-six chunk
ranks behind two sibling chunks from its own document. Shrinking `top_k`
can't fix a ranking problem, it can only hide or expose it. I'm leaving
`TOP_K = 3` in `config.py` because the stretch requires the change to be
present in the repository; the after log (top_k 5) remains the better
configuration for this corpus.

## What's Still Broken

Nothing is currently MISSED — all five criteria are MET after the
improvement (see Run Log — After). But two things are closer to failing
than a clean "MET" suggests, and I'm naming them rather than letting the
verdict hide them:

**Criterion 1's margin on question 5.** The "week six" chunk from
`admin_add_drop_deadline.txt` now ranks 5th of 5 in retrieval (distance
0.502) — it still counts as a pass, but only because `top_k` happens to be 5. What I'd do about it: either raise `top_k` for this question's topic
cluster, or tune `SINGLE_CHUNK_LIMIT` so a document doesn't compete against
its own siblings for the same slots. Why I stopped: Milestone 4's rule is
one change per unit, and I already spent it making chunking real in the
first place. Tuning further right now would mean adjusting parameters until
this one question looks safe again — which is exactly the "target passes by
construction" problem Milestone 3 diagnosed, just approached from the other
direction.

> **Update after the stretch:** I did spend a second change on this
> (`TOP_K` 5 → 3, see Stretch above), and it confirmed the margin was real:
> the week-six chunk fell out of the window and the answer went from correct
> in 3 of 3 runs to "the documents do not state the deadline" in 3 of 3.
> That rules out the window as the fix. What's actually wrong is the
> *ranking*: after the sentence split, two other chunks from the same
> document (the add deadline, and the registrar aside) sit closer to the
> query than the one with the answer. The change that would address that is
> hybrid search — BM25 would weight the exact words "drop" and "deadline",
> which the week-six chunk has and the aside doesn't — or merging sibling
> chunks back together at retrieval time. I stopped there because the stretch
> is one change too, and I chose the cheaper one to test the diagnosis first.

**Criterion 3's shrinking gate margin.** Out-of-scope distances moved from
0.844–0.934 (before) to 0.825–0.871 (after) — still comfortably past the 0.6
cutoff, but the smaller, more topic-specific chunks are pulling every
distance down a little, including for questions the corpus doesn't cover.
What I'd do: redo the two-group distance comparison from Milestone 4 of Unit
1 (in-corpus vs. out-of-scope) against the new chunker, instead of assuming
the old 0.6 cutoff still sits in the gap. Why I stopped: that's a second,
separate tuning question — the gate, not the chunker — and this unit's rule
was one change.

**Criterion 4's sample coverage.** The rewritten chunker turned 88 chunks
into 220, but I kept sampling 5 for the completeness check — that's under
half the coverage (as a fraction of the corpus) it used to be. I didn't
expand it because the criterion as written names a flat count of 5, not a
percentage.

## What I'd Do Differently

**Criterion 1** — I'd rewrite the target itself, not just tighten it.
"4 of 5 questions have the answer in a retrieved chunk" treats a chunk
landing at rank 1 the same as rank 5 of `top_k=5` — both just count as a
pass. Milestone 4 showed a question can sit at either extreme depending on
chunk boundaries, and the criterion can't tell the difference. Next time:
"the answer-bearing chunk ranks in the top 3 of retrieval for at least 4 of
5 questions" — something where a result like question 5's would actually
register as a miss instead of hiding inside a wide top-5 window.

**Criterion 5** — I'd write it to match what my scorer actually checks. As
written, it asks whether the _source document named in the answer_ contains
the `expects` phrase; `scorer.py::judge` instead checks whether the
_generated answer text_ contains it — a different check. I never reconciled
the two, so the Verdicts table's evidence for criterion 5 came from a
manual, by-hand check of each source document, separate from the automated
pass/fail column `run_eval.py` produces. Writing the criterion to describe
what the scorer actually measures would remove that manual step on every
future run.

**Criterion 4** — I'd tie the sample size to the corpus instead of a fixed
count, e.g. "at least 5% of chunks, or 5, whichever is greater," so the
criterion's rigor doesn't quietly halve itself the next time the chunking
strategy changes the chunk count.
