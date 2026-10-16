# Gate 2 Storyline Segmentation Generalization — Working V0.1

Status: WORKING DESIGN / NOT FROZEN / NOT IMPLEMENTED / NOT PRODUCTION

Date: 2026-09-02

Baseline commit: `6d71788e0cb1c28d8d7cf83d84b01c2a80772505`

Product and evaluation authority: `CANONICAL_CHECKPOINT_V1_29_REAL_MEDIA_QUALITY_RECOVERY.md`

Latest real-run evidence: `INTEGRATION_CHECKPOINT_V1_30_X02_V03_GATE1_EVIDENCE_AND_FIELD_RELIABILITY.md`

Inherited frozen architecture: V1.15 bounded defer/lookahead, V1.17 Chapter/Aha Candidate generation, V1.19 Editorial Set Selection, and all earlier checkpoints not explicitly superseded.

This document is a design and paper-simulation artifact. It does not change Algorithm code, Web code, Firmware/SDK, App Sync, shared state, source media, or any accepted checkpoint.

## 1. Why Gate 2 must be generalized before implementation

The Person 1 failure is an example of a general structural problem, not an ancient-town-only defect.

Current X02 behavior is effectively:

```text
same broad Episode Code
→ allow one Chapter candidate
→ prefer the candidate set covering the most assets
```

In the current implementation:

- `_build_chapter_candidates` accepts a Chapter when all members share one `episode_code`;
- `_deterministic_episode_groups` groups nearby KEEP Observations by that broad code;
- `_select_chapter_set` compares `covered_asset_count` before every editorial-quality consideration;
- `_select_chapter_set` silently limits consideration to the first 16 candidates, so proposal order can become an undocumented recall/ranking decision;
- the structure prompt contains ancient-town-specific merge guidance but no universal Storyline identity contract;
- Writer receives the already selected membership and cannot repair an impure Chapter.

This produces two symmetric errors:

1. **under-splitting** — different experiences in one broad outing are mixed because place/Episode is shared;
2. **over-splitting or loss** — complementary content is split or dropped because it does not share the same narrow object/label.

Therefore Gate 2 is not “split the historic-town Chapter into two or three.” It is:

> Add an explicit, general Chapter Storyline layer below Day Episode and above final Chapter publication.

## 2. Semantic hierarchy

### 2.1 Day Episode

A broad day context or occasion envelope.

Examples:

- an ancient-town visit;
- a birthday gathering;
- a concert night;
- a workday;
- a family park outing.

Day Episode answers: **What broad occasion was this part of the day?**

It does not prove that everything inside belongs to one Chapter.

### 2.2 Chapter Storyline

An evidence-grounded, bounded, independently tellable memory thread inside a Day Episode.

Storyline answers:

> What single experience, discovery thread, event progression, or interaction is this Chapter actually remembering?

A Storyline must have one dominant memory thesis and enough complementary Content Beats to make that thesis complete. It may be temporally contiguous or may resume after a bounded interruption.

### 2.3 Content Beat

A concrete, non-redundant contribution to the Storyline.

Examples:

- entering the old lane;
- walking beside the canal;
- noticing prayer plaques;
- seeing vendors arrange vegetables;
- the cake arriving;
- the group beginning to sing;
- a gift being revealed.

A visually different asset is not automatically a new Beat. A visually similar asset may still be a new Beat when it records a different place, phase, subject, result, or meaningful perspective.

### 2.4 Final Chapter

A published product object selected from one qualified Storyline, normally represented by three to five final media items.

Not every Storyline hypothesis becomes a Chapter. A thin or ungrounded thread may remain audit-only, contribute Context, be considered by the Aha path, or be dropped.

### 2.5 Aha

A local, independently memorable peak or discovery. It can occur inside a Chapter's time range only when it performs a different story duty.

Gate 2 preserves that separation. It does not solve Gate 3 ranking, but its Storyline identity becomes the reference used to test Chapter/Aha independence.

## 3. The common inductive rule

The common rule is not visual clustering, topic clustering, time slicing, or a fixed Chapter count.

```text
SAME STORYLINE
= one dominant memory thesis
+ bounded experiential continuity
+ complementary Beat contribution
+ no unresolved competing story duty

SPLIT STORYLINES
= materially different memory theses
+ reliable boundary evidence
+ independent viability of the resulting thread(s)
```

In plain language:

1. **Do these items answer the same memory question?**
2. **Does each item add a useful phase, facet, discovery, or result to that answer?**
3. **Can the group be expressed naturally as one memory rather than an “and also” inventory?**
4. **If it is split, does each resulting thread actually deserve and support an independent Memory?**

This last question prevents over-splitting. A change of room, object, camera angle, or short activity does not create a Chapter by itself.

## 4. Storyline basis — general, not scene-specific

A Storyline proposal should state one primary basis. These are working structural categories, not user-visible labels and not hard-coded scene names.

| Working basis | Meaning | Typical pattern |
|---|---|---|
| `EVENT_PROGRESSION` | phases of one bounded event | preparation → action → result |
| `ACTIVITY_ROUTE` | one sustained or resumed activity/route | enter → walk → reach waterside |
| `DISCOVERY_SERIES` | repeated attention to one coherent subject/theme within a bounded outing | prayer plaques → courtyard → temple marker |
| `SOCIAL_INTERACTION` | one interaction thread among the same anonymous participants | meet → exchange → reaction |

Rules:

- a candidate may have secondary evidence from another basis, but only one dominant basis;
- `same place`, `same Episode Code`, `same visual style`, and `same object class` are never valid primary bases by themselves;
- a broad `OUTING` envelope may constrain candidates but cannot by itself pass the One Story Gate;
- these basis names remain working terms until cross-pack evidence is reviewed.

`DISCOVERY_SERIES` needs extra protection because it could otherwise become a new name for an arbitrary thematic montage. It may be nominated only when:

- all members belong to one bounded occasion envelope;
- at least three non-redundant content units contribute distinct discoveries;
- focal-thread evidence is supported by at least one independent family such as route/locality, repeated grounded observing activity, or anonymous entity continuity;
- every extension passes both local compatibility and group-wide thesis stability;
- interruptions and unsupported gaps remain inside inherited V1.17 bounds;
- the thread is not assembled from remote parts of the day merely because the same object class appears again.

### 4.1 Storyline basis and Chapter form are orthogonal

Gate 2 does not replace the frozen V1.17 forms:

```text
SINGLE
ADJACENT_GROUP
RESUMED_EPISODE
LOCAL_EPISODE_GROUP
```

The form describes **how members relate on the timeline**. Storyline basis describes **why they constitute one memory**.

Examples:

- a birthday `EVENT_PROGRESSION` may use `SINGLE` or `ADJACENT_GROUP`;
- an ancient-town `ACTIVITY_ROUTE` may use `RESUMED_EPISODE`;
- a bounded culture `DISCOVERY_SERIES` may use `LOCAL_EPISODE_GROUP` with explicit interruption refs;
- two candidates with the same form can still represent different Storylines.

## 5. Storyline evidence model

Gate 2 inherits the frozen principle of saving evidence in both directions. It adds Storyline-level continuity and boundary evidence; it does not overwrite S05 seam decisions.

### 5.1 Continuity evidence families

| Evidence family | What it supports | Strength boundary |
|---|---|---|
| event/occasion continuity | same bounded event or visit | broad envelope only; insufficient alone |
| activity/progression continuity | same activity or causal phase progression | strong when grounded |
| focal-thread continuity | attention remains on one coherent subject/theme | strong for `DISCOVERY_SERIES` when repeated and bounded |
| result/payoff continuity | earlier content prepares or explains the same outcome | strong |
| route/subzone continuity | movement through connected local spaces | medium; not enough alone |
| anonymous entity/social continuity | same person/group/animal continues the interaction | medium to strong with activity evidence |
| interruption/resume evidence | the prior concrete activity reappears after a bounded interruption | strong only with at least one additional independent family |
| motif/visual/embedding similarity | possible semantic relation | nomination only; never decides membership alone |
| temporal proximity | possible continuity | weak alone |

### 5.2 Boundary evidence families

| Evidence family | What it indicates |
|---|---|
| dominant activity changes | walking becomes eating, meeting, performing, commuting, etc. |
| focal thread changes | architecture discovery becomes vendor life or a different social event |
| independent payoff appears | a subthread has its own result, surprise, or resolved experience |
| setting change plus activity change | indoor cafe stop during an outdoor walking route |
| causal chain ends and another begins | event closure followed by a separate activity |
| unsupported time/context gap | continuity cannot be safely claimed |
| internal story contradiction | one title/kernel cannot safely cover all members |
| removable independent block | removing a block leaves the other story intact and the removed block remains meaningful |

### 5.3 Evidence that cannot decide by itself

The following may nominate a comparison but cannot independently return JOIN or SPLIT:

- same or different `episode_code`;
- same or different scene label;
- image embedding similarity;
- the presence of stone, water, buildings, food, pets, or people;
- capture/import adjacency;
- Manual/Auto source;
- image quality;
- asset count;
- a Chapter count target.

## 6. One Story Gate

Every Chapter Storyline candidate must pass a new `ONE_STORY_GATE` before entering S09.

### 6.1 Required structured record

```text
StorylineIdentity
  storyline_basis
  occasion_envelope_refs[]
  thesis_signature
    primary_activity_or_event
    primary_focal_thread
    progression_or_discovery_basis
  dominant_memory_thesis_explanation
  focal_thread
  grounded_activity_or_progression
  temporal_segments[]
  interruption_refs[]
  content_unit_refs[]
  beat_map[]
  continuity_evidence[]
  boundary_evidence[]
  contradiction_refs[]
  split_alternative_refs[]
  one_story_gate
```

`thesis_signature` is the executable structured identity. `dominant_memory_thesis_explanation` is an internal, grounded explanation for humans, not final copy and not an independent hard fact. It cannot add facts, emotions, place names, intentions, or relationships absent from Evidence.

The `THESIS_SPECIFICITY_GATE` fails when the signature merely repeats a broad Day Episode or place, such as `HISTORIC_TOWN_WALK`, `WORKDAY`, `BIRTHDAY_GATHERING`, “travel,” or “the park.” It must state the activity/event progression or focal discovery thread that makes this Storyline distinct inside that envelope.

### 6.2 Beat contribution test

Every included CandidateContentUnit must have exactly one auditable primary contribution:

```text
ENTRY
PROGRESSION
DISCOVERY
INTERACTION
CONTRAST
PEAK
RESULT
EXIT
ATMOSPHERE_SUPPORT
```

Working rules:

- `ATMOSPHERE_SUPPORT` cannot be the only contribution from most members;
- repeated items with no material gain are suppressed inside the candidate;
- an item with a strong but unrelated contribution is excluded or assigned to an alternative Storyline; it is not retained to increase coverage;
- no raw asset is duplicated across two selected Chapters, even if it can support two competing candidates.

### 6.3 Natural-compression test

Before Writer, the structure must be representable as:

```text
one dominant experience
+ a small number of complementary phases/facets
+ optional grounded atmosphere
```

It fails when the only honest representation is:

```text
X happened, and also Y, and also Z, and also an unrelated W.
```

This is a structural test. Writer phrasing is not used to rescue or reject membership.

### 6.4 Internal partition challenge

Every heterogeneous candidate must be challenged with at least one plausible partition before it passes:

```text
parent candidate
→ detect strong internal boundary or competing focal threads
→ construct bounded child alternatives
→ compare shared-thesis evidence and independent viability
```

Decision pattern:

| Evidence | Result |
|---|---|
| same thesis + complementary phases | keep parent |
| strong internal boundary + both children independently viable | prefer split alternatives |
| strong outlier but outlier not independently viable | exclude outlier; do not pad parent |
| child is the causal climax/result of the parent | keep as one Storyline; do not split mechanically |
| unresolved material conflict | `NEEDS_VALIDATION` when S08 can ask one bounded factual question; otherwise reject current candidate |

Insufficient support for a child never becomes permission to contaminate the parent.

## 7. Moment and Storyline are different axes

S05 Moment answers: **Which adjacent evidence belongs to one locally coherent time block?**

Gate 2 Storyline answers: **Which local blocks or content contributions serve the same independently tellable memory thread?**

Consequences:

1. `SPLIT/SPLIT` at S05 does not imply three Chapters;
2. one S05 Moment may contain more than one potential content contribution;
3. Storyline candidate membership is defined by `CandidateContentUnit` refs; each unit retains its immutable owner Moment ref;
4. one Moment may nominate multiple alternative Storylines, and different RawAssets inside one Moment may contribute to different selected Storylines when each passes independently;
5. the same CandidateContentUnit or underlying RawAsset can never appear in two selected Chapters;
6. a Storyline may contain multiple non-contiguous `temporal_segments` when resume evidence is sufficient;
7. Storyline grouping never rewrites Moment membership or hides interruption refs;
8. repeated impurity inside Moments must be reported as an S05 evaluation finding, not silently misrepresented as a successful Gate 2 fix.

This distinction is necessary for Person 1, where one current Moment contains prayer plaques, a stone lane, and dog/courtyard material. Gate 2 must compare content-unit contributions without pretending the Moment was editorially indivisible.

This is an additive Gate 2 clarification to the V1.17 Moment-seed architecture. If an implementation schema currently treats the entire owner Moment as indivisible candidate content, the Gate 2 checkpoint must explicitly supersede only that membership granularity while preserving Moment identity, seams, roles, provenance, and all RawAsset conflicts.

## 8. Candidate-generation workflow

### 8.1 Inputs

Only current-Revision grounded information:

- S04 Observation facts, motifs, subjects, setting/activity/Episode fields, limitations, support and quality;
- S05 Moment membership and seam ledgers;
- S06 role and CandidateContentUnit eligibility;
- source/time/provenance;
- existing interruption/resume and alternative refs.

### 8.2 Proposed flow

```text
S06 content-active Moment packets
→ build MomentStorySignature
→ deterministic bounded local/resume nominations
→ one structured model proposal over IDs and grounded facts
→ normalize StorylineIdentity + Beat map
→ One Story Gate
→ internal partition challenge
→ duplicate/alternative audit
→ S07 candidate dispositions
→ S09 relation graph and set selection
```

### 8.3 Model boundary

The model may propose:

- Storyline basis;
- member Observation/ContentUnit refs;
- dominant focal thread;
- Beat roles;
- interruption/resume hypothesis;
- competing split alternatives;
- references to supplied grounded facts.

The model may not:

- create facts or user intent;
- decide final Chapter count;
- use free-text confidence as a gate;
- select a candidate merely because it covers more assets;
- rewrite S05/S06;
- generate final title/story/media;
- make an unbounded pairwise search.

### 8.4 Deterministic validator boundary

The validator must verify:

- every referenced member and fact exists;
- every member is content-active and grounded;
- each member has a Beat contribution;
- no strong contradiction is omitted;
- Storyline is bounded to one occasion envelope;
- resume/interruption limits and refs are valid;
- child alternatives are recorded when the partition trigger fires;
- duplicate assets do not inflate support;
- candidates with an unrelated outlier fail or exclude it;
- same input and versions reproduce the same normalized candidate set.

Exact `episode_code` equality is removed as a Chapter-membership hard gate. A cross-code candidate such as historic lane plus wooded path may pass only when one bounded occasion/activity thread and additional evidence support it. The mismatch must remain visible in the ledger; a model assertion alone cannot erase it.

## 9. S09 objective correction

Gate 2 must implement the frozen V1.19 ordered objective rather than invent a new overall score.

For the Gate 2 implementation slice, the relevant order is:

1. legal, grounded, One Story Gate-passing sets only;
2. every selected Chapter has material independent Memory contribution;
3. cover more meaningful independent Storylines, not more assets;
4. prefer stronger completeness, trust, and lower inference risk;
5. control Chapter–Chapter and Chapter–Aha redundancy;
6. only then apply quality-qualified count preference;
7. stability and deterministic parsimony last.

`covered_asset_count` may be reported as telemetry. It must not be the first editorial objective and must never compensate for impurity.

The current `first 16 candidates` slice must also be removed as an editorial shortcut. Gate 2 must either evaluate the complete policy-bounded eligible pool or return an explicit deterministic search-limit status with excluded-candidate audit. Input order cannot silently decide Storyline recall.

## 10. Fine-grained paper simulation C01 — Person 1 real ancient-town pack

The source order is treated as synthetic chronology. Times below are explanatory two-minute positions, not original capture timestamps.

| Time | Item | Grounded content summary | Candidate contribution | Boundary/ambiguity note |
|---|---:|---|---|---|
| 09:00 | 1 | traditional gate, street stalls, people, wet ground | market/outing entry | gate can also look architectural; entrance alone does not decide |
| 09:02 | 2 | rainy road, cars, umbrellas, distant gate | transition/context | transit should not pad a Chapter |
| 09:04 | 3 | prayer plaques, stone bridge, lantern tree | culture discovery; possible scenic facet | one RawAsset carries multiple facets; final primary duty needed |
| 09:06 | 4 | stone lane, white walls, lanterns, potted pine | strolling progression | architecture style is context, not automatic culture membership |
| 09:08 | 5 | dog walking toward courtyard | strolling/context | no grounded independent playful peak |
| 09:10 | 6 | vegetable stall and vendor activity | local market discovery | clear market contribution |
| 09:12 | 7 | vendors arranging vegetables | market interaction/progression | complements item 6 rather than duplicating it |
| 09:14 | 8 | stone lane ending at traditional gate | route entry/progression; culture alternative | requires primary-duty comparison |
| 09:16 | 9 | forest stone path with dog | route/subzone progression | different scene can remain in same walking thread |
| 09:18 | 10 | courtyard and traditional building details | culture discovery | multiple angles within one asset count as one content unit |
| 09:20 | 11 | canal, traditional houses, willow, boat | scenic walking discovery | distinct waterside Beat |
| 09:22 | 12 | local food stall and customer | market/food discovery | no grounded tasting result; independent food Aha is not assumed |
| 09:24 | 13 | `古越龍山` stone marker | culture marker discovery | specific and complementary |
| 09:26 | 14 | canal-side stone road and bridge | scenic route progression | complements item 11; duplication still checked |
| 09:28 | 15 | forest stone steps and fallen leaves | route/subzone progression | may bridge item 9 without visual identity |
| 09:30 | 16 | temple sign and stone marker | culture discovery/progression | strong culture thread contribution |
| 09:32 | 17 | dog walking, sightseeing car, tea-shop front | mixed context/outlier | current `PLAYFUL_ANIMAL/HIGH` label is not supported by an action peak |
| 09:34 | 18 | fruit/produce display and vendor | market discovery/progression | later resumption of local market thread |
| 09:36 | 19 | waterside path, bridge, building entrance | scenic route; culture alternative | primary duty and marginal gain required |
| 09:38 | 20 | inside moving car | transition/exit | closes outing; not Chapter content |

### C01 expected Storyline hypotheses

#### P1-SL-A — local vendors and street life

Likely contributions: 1 as optional entry/context, 6, 7, 12, 18.

Dominant thesis: a bounded series of local stalls, vendors, and street-life discoveries during the outing.

Why it can pass:

- repeated grounded focal thread;
- different market Beats rather than the same stall angle;
- item 7 adds vendor action, item 12 adds local food stall, item 18 adds fruit display;
- it can be remembered independently from architecture and route scenery.

Risks:

- item 1 may be only an outing threshold, not a final media item;
- item 12 must not be called “tasting” without evidence;
- interleaving requires bounded `DISCOVERY_SERIES` evidence rather than pretending continuous market browsing.

#### P1-SL-B — old-town cultural and architectural discoveries

Likely contributions: 3 or its culture facet, 10, 13, 16; items 8/19 are alternatives, not automatic additions.

Dominant thesis: repeated discoveries of ritual, courtyard, marker, and temple details within one visit.

Why it can pass:

- a coherent focal thread across distinct cultural objects;
- at least three non-redundant discoveries;
- not merely “all buildings look old.”

Risks:

- item 3 also contains bridge/scenic facts and needs a primary Beat duty;
- similar architecture angles must be deduplicated when they add no new facet;
- the Chapter must not absorb lanes/canal merely to increase coverage.

#### P1-SL-C — stone lanes, wooded paths, and waterside walking

Likely contributions: 4, 8, 9, 11, 14, 15, 19, with only three to five selected later.

Dominant thesis: an activity/route Storyline moving through lanes, wooded paths, and waterside sections of the same outing.

Why different objects can join:

- the dominant activity is walking/exploring;
- the changing subzones form route progression;
- lanes, forest paths, canal, and bridge are complementary route Beats;
- the story is not “all contain stone.”

Risks:

- if route continuity is unsupported, forest and waterside must become alternatives rather than being forced together;
- repeated lane/bridge views require marginal-gain checks;
- dog walking is context unless an independent event is grounded.

### C01 set expectation

The rich Person 1 day plausibly supports two or three Chapters. Three is justified only if all three hypotheses pass independently. The engine must not hard-code three and must not merge a weak child into another Chapter to reach three content units.

Ambiguous assets 3, 8, and 19 may support competing candidates during proposal. The final set cannot reuse the same RawAsset across Chapters.

## 11. Fine-grained simulation C02 — birthday gathering

| Time | Content | Likely role |
|---|---|---|
| 18:00 | entering the decorated room | event entry |
| 18:02 | friends gathering around the table | social setup |
| 18:04 | gifts placed beside the cake | setup |
| 18:06 | cake is brought in | progression |
| 18:08 | candles are lit | progression |
| 18:10 | group starts singing | ceremony progression |
| 18:12 | birthday person reacts | event peak/support |
| 18:14 | candles are blown out | Chapter climax/result |
| 18:16 | applause and laughter | result |
| 18:18 | cake is cut | continuation |
| 18:20 | food is shared | gathering continuation |
| 18:22 | a wrapped gift is opened | possible independent reveal peak |
| 18:24 | surprised reaction to the gift | possible Aha result |
| 18:26 | casual conversation | atmosphere/context |
| 18:28 | guests leave | exit |

Expected common logic:

- decorations, cake arrival, singing, candle blowing, and applause are phases of one `EVENT_PROGRESSION`, not separate Chapters;
- blowing candles is normally owned by the birthday Storyline climax and should not be duplicated as Aha;
- gift reveal may become an embedded distinct Aha only when it has its own grounded setup/result and different story duty;
- food sharing becomes a second Chapter only when it has enough independent progression and value, not because “food” differs from “cake.”

Over-split trap: splitting each visual phase into a Chapter.

Under-split trap: absorbing a later independent party game or separate outing merely because the same people are present.

## 12. Fine-grained simulation C03 — concert night

| Time | Content | Likely role |
|---|---|---|
| 19:00 | queue outside venue | entry/setup |
| 19:02 | ticket and entrance gate | entry |
| 19:04 | finding the seat | setup |
| 19:06 | stage lights turn on | progression |
| 19:08 | first song begins | event progression |
| 19:10 | performer close view | performance Beat |
| 19:12 | audience waves lights | social atmosphere |
| 19:14 | confetti falls | climax |
| 19:16 | encore begins | continuation/result |
| 19:18 | final bow | result/exit |
| 19:20 | leaving the venue | exit |
| 19:22 | separate street musician outside | new event hypothesis |
| 19:24 | brief interaction with musician | possible local peak |

Expected common logic:

- entry, performance, confetti, encore, and bow normally form one concert Storyline;
- scene and lighting changes do not split the event lifecycle;
- confetti is not automatically an Aha if it is simply the Chapter climax;
- the street musician is a separate event hypothesis because the concert has closed and a new interaction begins;
- the street-musician hypothesis becomes Chapter/Aha only if independently supported, never because a second output slot is desired.

## 13. Fine-grained simulation C04 — ordinary workday

| Time | Content | Likely route |
|---|---|---|
| 08:20 | subway platform | commute/context |
| 08:22 | train interior | commute/context |
| 08:24 | office entrance | transition |
| 09:00 | laptop and desk | ordinary context |
| 09:02 | colleagues gather at whiteboard | workshop setup |
| 09:04 | diagram is drawn | workshop progression |
| 09:06 | prototype is demonstrated | workshop result |
| 09:08 | colleagues react | workshop result/support |
| 12:00 | restaurant exterior | lunch entry |
| 12:02 | dishes arrive | lunch progression |
| 12:04 | shared toast or clear interaction | possible lunch peak |
| 12:06 | empty plates and leaving | lunch result/exit |
| 18:10 | riverside running path | after-work activity |
| 18:12 | reaching a viewpoint | possible activity result |

Expected common logic:

- `WORKDAY` is only a Day Episode envelope;
- the workshop can be one Storyline when setup/progression/result are grounded;
- commute and a static desk do not pad the workshop;
- lunch and after-work run are separate experiences, but each still needs independent Chapter value/support;
- if only ordinary desk/commute images exist, an empty Chapter result remains legal.

## 14. Fine-grained simulation C05 — parent and child in a park

| Time | Content | Likely thread |
|---|---|---|
| 10:00 | entering the park | outing entry |
| 10:02 | walking beside the lake | outing route |
| 10:04 | child notices ducks | duck interaction setup |
| 10:06 | feeding ducks | interaction progression |
| 10:08 | ducks gather and child reacts | interaction result |
| 10:10 | walking to playground | transition |
| 10:12 | child approaches climbing frame | playground setup |
| 10:14 | attempts to climb | progression |
| 10:16 | reaches the top | result/peak |
| 10:18 | snack on a bench | interruption/context |
| 10:20 | family resumes lakeside walk | resumed route |
| 10:22 | leaving the park | outing exit |

Expected common logic:

- on a sparse day, the whole park visit may be one coherent outing Storyline if the smaller threads cannot stand independently;
- on a rich day, duck interaction and playground challenge can become two Storylines because each has setup, action, result, and independent value;
- the choice is determined by independent viability and One Story Gate, not by a fixed granularity setting;
- snack does not become a Chapter merely because the setting changes;
- the lakeside route can resume after the snack when resume evidence is present.

## 15. Fine-grained simulation C06 — restaurant meal

| Time | Content | Likely role |
|---|---|---|
| 12:00 | restaurant exterior | entry |
| 12:02 | menu and ordering | setup |
| 12:04 | visible cooking/preparation | progression/discovery |
| 12:06 | main dish arrives | result/progression |
| 12:08 | first bite | interaction |
| 12:10 | clear reaction | possible peak/result |
| 12:12 | shared dishes | continuation |
| 12:14 | distinctive dessert arrives | possible subthread |
| 12:16 | dessert interaction/reaction | possible local peak |
| 12:18 | leaving | exit |

Expected common logic:

- ordering, preparation, dish arrival, eating, and leaving usually form one meal Storyline;
- dessert is not automatically separate because it is a different food;
- dessert becomes an independent Aha only with a grounded distinctive event/discovery and a different story duty;
- a separate dessert Chapter requires enough independent progression and content, not one attractive image.

## 16. Fine-grained simulation C07 — A–B–A interruption and resume

| Time | Content | Structural reading |
|---|---|---|
| 09:00 | walking through old lane | A begins |
| 09:02 | passing traditional houses | A progression |
| 09:04 | crossing a small bridge | A progression |
| 09:06 | entering a modern milk-tea shop | boundary into B |
| 09:08 | ordering a drink | B progression |
| 09:10 | ordinary seated drinking | B ordinary result/context |
| 09:12 | leaving the shop | B exit |
| 09:14 | returning to the same lane route | C resumes A |
| 09:16 | continuing beside canal | C progression |
| 09:18 | reaching another old gate | C result/discovery |

Expected common logic:

- S05 can correctly preserve `A | B | C`;
- A and C may form one `ACTIVITY_ROUTE` Storyline when concrete resume evidence exists;
- B remains an interruption ref and is not hidden;
- ordinary milk tea does not automatically become Chapter or Aha;
- if B contains a grounded spill, surprise encounter, or distinctive reaction, that local peak can enter the Aha path without forcing A/C apart;
- a broader A+B+C outing alternative may be proposed, but it must fail if B has no Beat contribution to one common thesis.

## 17. Fine-grained simulation C08 — sparse ordinary day

| Time | Content | Structural reading |
|---|---|---|
| 08:00 | one coffee photo | possible discovery, insufficient Chapter |
| 13:00 | ordinary desk video | context/drop |
| 18:10 | one sunset photo | possible visual discovery, insufficient Chapter |
| 22:00 | cat jumps onto table and knocks over a cup | grounded event peak |

Expected common logic:

- no Chapter is forced;
- the cat event should be actively evaluated as an Aha;
- the sunset may be a Discovery Aha only if sufficiently specific and independently memorable;
- failed Chapter coverage cannot be converted into a low-quality Chapter or automatic Aha;
- zero Chapter with one grounded Aha is a valid `HIGHLIGHT_DAY` shape.

## 18. Counterexample C09 — visually similar but different Storylines

| Time | Content | Structural reading |
|---|---|---|
| 07:30 | walking the same dog in a neighborhood park | morning activity |
| 07:32 | dog follows a tree-lined path | morning progression |
| 07:34 | returning home | morning result |
| 20:10 | walking the same dog beside a river | evening activity |
| 20:12 | dog meets another dog | evening interaction |
| 20:14 | leaving riverside | evening result |

Expected common logic:

- same dog, activity, greenery, and high embedding similarity do not merge two independently bounded outings;
- clear time/Episode boundary and independent progression support two hypotheses;
- S09 may still select only one if the day-level editorial contribution is redundant, but S07 must not erase their distinct identity.

## 19. Counterexample C10 — similar architecture can still add value

| Time | Content | Possible contribution |
|---|---|---|
| 09:00 | first temple exterior | entry/first architectural discovery |
| 09:20 | different gate tower | distinct exterior form |
| 09:50 | courtyard with carved wood detail | interior/craft facet |
| 10:30 | different riverside guild hall | distinct place/facade facet |
| 10:50 | near-duplicate second angle of the same guild hall | probable duplicate |

Expected common logic:

- “all ancient architecture” does not mean automatic duplication;
- distinct buildings, distant points on the route, or different architectural facets can contribute separate Beats;
- near-identical angles of the same building with no new information are suppressed;
- a long, architecture-rich Storyline may legitimately select two or three exterior views when each has distinct identity and temporal/route separation;
- visual similarity is compared together with object identity, location/route, time, facet, and marginal contribution.

## 20. Cross-scenario invariant matrix

| ID | Invariant | Ancient town | Birthday | Concert | Workday | Parent-child | Sparse |
|---|---|---:|---:|---:|---:|---:|---:|
| G2-I01 | same Day Episode does not force one Storyline | yes | yes | yes | yes | yes | n/a |
| G2-I02 | different objects may join through one activity/progression | yes | yes | yes | yes | yes | n/a |
| G2-I03 | visual similarity cannot prove same Storyline | yes | n/a | yes | yes | yes | n/a |
| G2-I04 | event phases stay together when causally owned by one event | n/a | yes | yes | yes | yes | n/a |
| G2-I05 | clear interruption does not automatically split resumed A/C | yes | possible | possible | possible | yes | n/a |
| G2-I06 | strong outlier is excluded, not used as padding | yes | yes | yes | yes | yes | yes |
| G2-I07 | split requires boundary plus independent viability | yes | yes | yes | yes | yes | yes |
| G2-I08 | each included unit has a material Beat contribution | yes | yes | yes | yes | yes | yes |
| G2-I09 | one natural memory thesis can cover the candidate | yes | yes | yes | yes | yes | yes |
| G2-I10 | no fixed count may override purity or grounding | yes | yes | yes | yes | yes | yes |
| G2-I11 | model proposals remain auditable and deterministically validated | yes | yes | yes | yes | yes | yes |
| G2-I12 | Writer cannot modify membership | yes | yes | yes | yes | yes | yes |

## 21. Cost and latency boundary

Gate 2 should improve structure without multiplying visual-model cost.

Working cost contract:

1. reuse S04 Observations and Evidence; no new raw media upload;
2. no per-asset or per-candidate VLM call;
3. keep one bounded structured proposal call over Observation/Moment packets where possible;
4. run pair ledger, partition checks, eligibility, and set search deterministically;
5. only `NEEDS_VALIDATION` questions allowed by frozen S08 may spend extra bounded evidence/model budget;
6. record Gate 2 model calls, input/output Tokens, latency, and cost separately;
7. do not claim cost safety from one 20-video pack.

The expected primary new cost is deterministic CPU/audit size, not media inference. Any design requiring unbounded pairwise LLM comparison is rejected.

## 22. Audit and Web evaluation requirements

Every Chapter candidate shown to evaluators should expose:

- Storyline ID and working basis;
- dominant internal memory thesis;
- member Moment/Observation/asset IDs;
- each member's Beat role and inclusion reason;
- continuity evidence;
- boundary/contradiction evidence;
- interruption/resume segments;
- split alternatives considered;
- One Story Gate result;
- rejection/exclusion reasons;
- S09 selection reason and relation conflicts;
- per-stage time, Tokens, model calls, and configured cost.

Human feedback must be attachable to:

- entire Storyline;
- exact member asset;
- exact Beat assignment;
- a missing or wrong boundary;
- a wrong inclusion/exclusion;
- final Chapter wording separately from structure.

This prevents a generic “bad result” score from hiding whether the owner is S04, S05, Gate 2, S09, S10, or Writer.

## 23. Full-run acceptance plan

After this design is reviewed and implemented, every formal quality run remains a fresh full run:

```text
raw test pack
→ fresh browser Evidence
→ fresh S00-S04
→ fresh S05-S07 including Gate 2 Storyline
→ fresh S08-S12
→ explicit S13 NOT_EXECUTED
```

No cross-run semantic cache may be used for a formal acceptance claim.

### 23.1 Person 1 Gate 2 acceptance

Required:

- no selected Chapter mixes market, culture, and scenic walking merely because all are ancient-town content;
- plausible Storyline alternatives are visible and auditable;
- every selected member has a Beat contribution;
- two or three Chapters may emerge, but count alone is not acceptance;
- ambiguous assets have a primary story duty and are not duplicated across Chapters;
- all 20 Observations retain an auditable terminal route.

### 23.2 Cross-pack acceptance

Authorized folders 1, 2, and 3 are separate read-only test days. After Person 1 structural acceptance:

- run all three independently through the full chain;
- do not learn a universal threshold from Person 1 alone;
- compare purity, missing-thread recall, over-split rate, Beat contribution, grounding, latency, Tokens, and cost;
- collect structured feedback before changing thresholds or weights;
- implementation pass, real-model quality pass, and Production readiness remain separate claims.

## 24. Failure taxonomy for Gate 2 evaluation

| Code | Meaning | Owner |
|---|---|---|
| `G2_BROAD_EPISODE_MERGE` | broad Day Episode replaced Storyline identity | Gate 2 |
| `G2_VISUAL_OBJECT_OVER_SPLIT` | different object/scene caused unjustified split | Gate 2 |
| `G2_SIMILARITY_FALSE_MERGE` | visual similarity merged distinct episodes | Gate 2 |
| `G2_UNRELATED_MEMBER_PADDING` | unrelated member retained for count/coverage | Gate 2 |
| `G2_MISSING_SPLIT_ALTERNATIVE` | heterogeneous parent was never challenged | Gate 2 |
| `G2_FALSE_RESUME` | A/C joined without concrete resumed-thread evidence | Gate 2 |
| `G2_MISSED_RESUME` | bounded A/C continuation was not nominated | Gate 2 |
| `G2_BEAT_NO_CONTRIBUTION` | member has no material story contribution | Gate 2/S10 boundary |
| `G2_UPSTREAM_FACT_DEPENDENCY` | wrong S04 fact/code caused wrong Storyline | S04, not hidden by Gate 2 |
| `G2_UPSTREAM_MOMENT_DEPENDENCY` | S05 block impurity prevented safe grouping | S05, not hidden by Gate 2 |
| `G2_SET_OBJECTIVE_REGRESSION` | S09 asset coverage overrode story quality | S09 implementation |
| `G2_OPERATIONAL_FAILURE` | model/schema/provider failure prevented decision | engineering; not a content judgment |

## 25. Open product and engineering questions

These do not block paper generalization but must be decided before Production:

1. **Non-contiguous time display:** a resumed/thematic Storyline may contain multiple time segments. Showing only first-to-last can falsely imply continuous capture. Internal output must preserve segments; user-visible wording remains a product/UX decision.
2. **Moment partial-contribution serialization:** the product logic is defined in Section 7; the remaining engineering question is the additive schema and validator representation.
3. **Storyline-basis vocabulary:** validate whether four working bases cover all three packs without forcing cases.
4. **Partition trigger:** calibrate when heterogeneity requires a split challenge, without using one uncalibrated scalar score.
5. **Model schema:** decide the smallest structured proposal contract that can express thesis, Beat map, evidence refs, and alternatives without free-text authority.
6. **S08 boundary:** define which Storyline uncertainty is one bounded factual question and which must be conservatively rejected.

## 26. Cross-check against frozen architecture

| Frozen authority | Compatibility result | Gate 2 action |
|---|---|---|
| V1.15 Moment defer/lookahead | compatible | S05 seams remain immutable; A–B–A may be related later without erasing B |
| V1.17 Candidate forms/gates | compatible with one explicit additive clarification | preserve four forms, hard gates, bounds and audit; define content-unit membership below immutable owner Moment |
| V1.19 relation graph/objective | current production-intent contract already contains the right priority | implement Storyline identity and replace coverage-first/first-16 shortcuts with frozen ordered selection behavior |
| V1.29 product/evaluation method | directly implements the frozen Day Episode → Storyline → Content Beat hierarchy | no ancient-town-specific rule or quota |
| V1.30 real evidence | directly addresses confirmed broad-Episode merge and coverage bias | Person 1 becomes the first full-run acceptance case, not the universal training rule |

Cross-scenario challenge findings:

1. **Ancient-town-only subtopic labels are unnecessary.** The same thesis/Beat/independent-viability logic separates workday, concert, birthday, parent-child, and meal content.
2. **A broad new “theme” label would repeat the current Episode mistake.** The Thesis Specificity Gate and bounded Discovery Series conditions are required.
3. **Visual diversity is not Storyline diversity.** Birthday and concert phases demonstrate why different scenes can remain one event.
4. **Visual similarity is not Storyline identity.** Morning/evening dog walks and different architecture examples demonstrate why embedding remains weak nomination evidence.
5. **Granularity must be evidence-adaptive.** A rich park outing may support duck and playground Storylines; a sparse outing may support only one parent Storyline or none.
6. **A strong boundary is not enough to publish both sides.** Independent viability prevents a cafe, dessert, commute, or scene change from becoming an automatic Chapter.
7. **A weak child cannot contaminate a strong parent.** If it is neither complementary nor independently viable, it is excluded rather than used as count padding.
8. **Exact Episode-code equality is too narrow, while shared Episode alone is too broad.** Occasion, activity/progression, focal thread, time, interruption, and contradiction must be evaluated together.
9. **The design does not require additional visual-model fan-out.** One structured proposal call plus deterministic validation remains a viable cost shape.
10. **No contradiction currently requires a product-experience decision before implementation design.** Non-contiguous user-visible time wording remains the first later UX decision; internal segment truth can be implemented now without choosing the display.

Cross-check status: the common logic survives the current ten scenario families at paper-design level. This is not real-model validation and does not freeze thresholds, basis vocabulary, or implementation schema.

## 27. Current design conclusion

The general Storyline rule derived across travel, birthday, concert, workday, parent-child, meal, interruption/resume, sparse day, and visually similar separate outings is:

> A Chapter Storyline is one bounded, grounded memory thesis whose members make complementary, auditable Beat contributions. It may cross a short interruption or include visually different scenes, but it cannot absorb a competing story duty merely for similarity, location, Episode equality, coverage, or count. A split is justified only when reliable boundary evidence and independent thread value both exist.

This conclusion is ready for internal cross-check and Person 1 paper evaluation. It is not yet frozen and does not authorize implementation until contradictions and open design points are reviewed.
