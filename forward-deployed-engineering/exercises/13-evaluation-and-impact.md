# Exercises: Chapter 13, [Evaluation and Measuring Business Impact](../chapters/13-evaluation-and-impact.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation** and **hands-on**. All companies are fictional and all figures illustrative.

## Questions

1. **Concept.** Explain the difference between evaluation and impact measurement. Give one example of a system that scores well on evaluation but has no impact, and one with modest accuracy but large impact.

2. **Scenario.** Design a first evaluation set of about 200 cases for Contoso Insurance's coverage assistant (home and motor policies, English and some Welsh documents). Say where the cases come from, how you would stratify them, which "should refuse" cases you would include, how you would label them with SMEs, and what you would hold back.

3. **Calculation.** The coverage assistant's evaluation set has 200 cases, tagged by slice. The baseline run and a run after a prompt change give:

   | Slice | Cases | Baseline passes | After-change passes |
   |---|---|---|---|
   | Home | 150 | 141 | 144 |
   | Motor | 30 | 21 | 18 |
   | Should refuse | 20 | 18 | 17 |

   (a) Compute each slice's pass rate and the overall pass rate for both runs. (b) The release gate is "overall pass rate ≥ 88% and no slice drops by more than 5 percentage points". Does the change ship? (c) What would you do next?

4. **Calculation.** You validate an LLM judge for "is every statement supported by the cited passages?" against two SMEs' agreed labels on 100 cases. Humans marked 70 as pass and 30 as fail. The judge passed 68 of the human-pass cases and 10 of the human-fail cases. (a) What is the judge's overall agreement with the humans? (b) Of the cases the judge passes, what share are actually failures? (c) What share of true failures does the judge miss? (d) Should this judge gate releases?

5. **Calculation.** Wide World Importers piloted a picking-assistant in its Rotterdam depot. Order-error rate in Rotterdam fell from 4.8% to 3.1% over the pilot; in the comparison depot (Antwerp), it fell from 5.0% to 4.6% over the same period. (a) What is the difference-in-differences estimate of the effect? (b) Rotterdam handles 400,000 orders a year, and each error costs €35 to fix. What is the annual value attributable to the system, and what would a naive before-and-after comparison have claimed? (c) What assumption does difference-in-differences rely on, and how could you check it?

6. **Calculation.** In week 8 of a rollout at Woodgrove Bank: 40 underwriters are in the target group; 34 have used the assistant at least once; of 2,500 eligible applications, the assistant was used on 1,600; of the 34 users, 28 used it in week 8; and in 30% of uses, the underwriter re-did the analysis manually. Compute reach, depth and retention, and comment on reliance.

7. **Hands-on and calculation.** A deployment at Fabrikam has these finance-validated figures: annual value £250,000 (low), £320,000 (base), £400,000 (high); annual running costs £114,000 (platform £90,000 plus model usage £24,000); one-off costs £76,000 (FDE time £60,000 plus customer staff time £16,000). (a) For each scenario compute first-year net benefit, first-year ROI (net benefit ÷ total first-year cost) and payback period in months on the one-off costs. (b) Reproduce the figures with [`../examples/impact-calculator/`](../examples/impact-calculator/) using its `roi()` and `payback_months()` functions. (c) Write the one-sentence headline for the impact report.

8. **Hands-on.** In [`../examples/llm-eval-harness/`](../examples/llm-eval-harness/): (a) run the evaluation set and read the pass rate by tag; (b) add three cases of your own, including one "should refuse" case and one with a citation check; (c) create a deliberately worse version of the system under test (for example, one that drops citations), compare the two runs, and confirm the harness reports the regression by slice.

## Solutions

1. **Evaluation** asks "does the system work?": on the customer's real cases, how often is it right and how does it fail? **Impact measurement** asks "did it make a difference?": did the business outcome improve, by how much, because of the system?

   - High evaluation, no impact: an invoice extractor that is 98% accurate but that clerks don't use because it lives in a separate application; or one that automates a step that took two minutes a day.
   - Modest accuracy, large impact: a triage model that is right on only 60% of claims overall, but confidently and correctly handles the easy 60% while routing the rest to experts, freeing a large share of the team's time.

2. A good design:
   - **Sources:** historical coverage questions with known answers (from the email trail to underwriting); SME-written tricky cases (exclusions, endorsements, conflicting clauses); known failure cases from the pilot; a few adversarial cases (injected instructions in a document); a small number of synthetic variants, validated by an SME.
   - **Stratify** by line (home and motor, roughly in proportion to volume but with enough motor cases to measure, at least 30), by document language (include Welsh cases if in scope), by question type (coverage yes/no, limits, exclusions, endorsements) and by difficulty.
   - **Should-refuse cases** (about 10%): questions about policies the user shouldn't access; questions outside policy wording ("will this claim be paid?" when that is the adjuster's decision); questions where the answer isn't in the documents (the system should say "not found").
   - **Labelling:** a one-page rubric (correct, partially correct, wrong, with examples); two SMEs label a sample independently and you measure agreement; use a spreadsheet, not JSON.
   - **Hold back** about 20% of cases that are not used during prompt iteration, to detect overfitting.
   - **Version** the set in source control; never edit a case to make a failing run pass.

3. (a)

   | Slice | Baseline | After change | Change |
   |---|---|---|---|
   | Home | 141/150 = 94.0% | 144/150 = 96.0% | +2.0 points |
   | Motor | 21/30 = 70.0% | 18/30 = 60.0% | **−10.0 points** |
   | Should refuse | 18/20 = 90.0% | 17/20 = 85.0% | −5.0 points |
   | Overall | 180/200 = 90.0% | 179/200 = 89.5% | −0.5 points |

   (b) Overall 89.5% ≥ 88%, which passes; but motor drops 10 points, more than the 5-point limit, so **the change does not ship**. (Should-refuse drops exactly 5 points, which is at the limit, not over it; watch it.) The overall score barely moved, which is exactly how aggregate scores hide slice regressions.

   (c) **Read the failures**: look at the three motor cases that newly fail and the refusal case that newly fails, and find what the prompt change did (perhaps a home-insurance example in the prompt now biases motor answers). Fix, re-run the full suite, and compare again. Note that 30 motor cases is a small slice (one case is 3.3 points), so add more motor cases to make the gate more reliable.

4. (a) Agreement: the judge agrees on 68 human-pass cases and on 30 − 10 = 20 human-fail cases. (68 + 20) ÷ 100 = **88%**.

   (b) The judge passes 68 + 10 = 78 cases, of which 10 are failures: 10 ÷ 78 ≈ **12.8%** of its passes are wrong.

   (c) It misses 10 of 30 true failures: **33.3%**.

   (d) **Not as a sole release gate.** 88% agreement sounds good, but the errors fall where they hurt: one in three unsupported answers is passed. Improve the judge (a clearer rubric, one property at a time, binary judgement, examples of unsupported claims), re-validate, and until then use it to prioritise cases for human review rather than to gate releases.

5. (a) DiD = (3.1 − 4.8) − (4.6 − 5.0) = −1.7 − (−0.4) = **−1.3 percentage points**.

   (b) Attributable: 400,000 × 1.3% = 5,200 errors avoided × €35 = **€182,000 a year**. Naive before-and-after: 400,000 × 1.7% = 6,800 × €35 = **€238,000**, overstating the value by €56,000 (about 31%), because some of the improvement happened in both depots for other reasons.

   (c) The **parallel trends assumption**: without the system, Rotterdam's error rate would have changed by the same amount as Antwerp's. Check it by plotting both depots' error rates for several months before the pilot: if they moved in parallel, the assumption is more plausible. Also check for anything that changed at only one depot during the pilot (new staff, a new product range, a warehouse layout change).

6. - **Reach:** 34 ÷ 40 = **85%** of target users have used it.
   - **Depth:** 1,600 ÷ 2,500 = **64%** of eligible applications.
   - **Retention:** 28 ÷ 34 ≈ **82%** of users who tried it used it in week 8.
   - **Reliance:** in 30% of uses the analysis was re-done, so effective reliance is 70% of uses, roughly 1,600 × 0.7 = 1,120 applications where it actually saved work (about 45% of eligible applications).

   Comment: reach is strong; depth and especially reliance are the constraints on impact. Investigate why underwriters re-do the work (trust, specific failure types, or policy requirements) by sampling those cases; the human override rate is your best production quality signal.

7. (a) First-year total cost = £114,000 + £76,000 = **£190,000**.

   | Scenario | First-year net benefit | First-year ROI | Monthly net running benefit | Payback on one-off costs |
   |---|---|---|---|---|
   | Low | £250k − £190k = **£60,000** | 60 ÷ 190 = **31.6%** | (250 − 114) ÷ 12 = £11,333 | 76 ÷ 11.333 ≈ **6.7 months** |
   | Base | £320k − £190k = **£130,000** | 130 ÷ 190 = **68.4%** | (320 − 114) ÷ 12 = £17,167 | 76 ÷ 17.167 ≈ **4.4 months** |
   | High | £400k − £190k = **£210,000** | 210 ÷ 190 = **110.5%** | (400 − 114) ÷ 12 = £23,833 | 76 ÷ 23.833 ≈ **3.2 months** |

   (b) The calculator uses the same definitions: `roi(320_000, 190_000)` returns 0.684, and `payback_months(76_000, 320_000, 114_000)` returns about 4.4. Whatever tool you use, state the definitions in the report so readers can compare figures.

   (c) For example: "The Fabrikam deployment is expected to deliver £250k–£400k a year (base case £320k, validated by Fabrikam finance), paying back its one-off cost in about four months."

8. (a) The harness reports pass rates per tag; note the weakest slice.

   (b) A "should refuse" case might ask for information outside scope or restricted to another role, with checks that the answer contains a refusal phrase and no restricted terms. A citation case should require at least one citation from an allowed list of document IDs.

   (c) With a system that drops citations, every case with a citation check should newly fail. The comparison should list those cases as regressions and show the drop in the affected slices, even if other slices are unchanged. This is the workflow of §13.5: run on every change, compare with the baseline by slice, read the failures, and gate the release.
