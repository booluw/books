# Record linkage (Chapter 10)

## The problem

The customer wants one view of each of their customers, but the CRM says `Fabrikam, Inc.` with phone `+44 20 7946 0002` and the billing system says `Fabrikam Inc` with `02079460002`. There is no shared ID. **Record linkage** (also called entity resolution) finds records in two systems that refer to the same real-world thing.

FDEs meet this in almost every deployment: joining a CRM to billing, claims to policies, patients across hospital systems. Getting it wrong is costly in both directions. A false link merges two customers (and may show one customer's data to another); a missed link double-counts revenue or hides a customer's history.

## How `linkage.py` works

1. **Normalise.** Make equal things look equal: lower-case, strip accents and punctuation, drop legal suffixes (`Ltd`, `Limited`, `Inc`, `plc`, `GmbH`…), remove spaces from postcodes, reduce phone numbers to digits with `+44` turned into `0`.
2. **Block.** Comparing every record with every other is n × m comparisons: fine for 10, impossible for 10 million. **Blocking** only compares records that share a cheap key: here the postcode district (`SW1A`) or the first four letters of the normalised name. In the sample, 90 possible pairs become 14.
3. **Score.** Compare each field. Names use **Jaro-Winkler similarity**, a measure between 0 (nothing in common) and 1 (identical) that tolerates typos and rewards a shared prefix; it is implemented from scratch in `jaro()` and `jaro_winkler()`. Postcode, email and phone are compared exactly after normalisation. The pair's score is the **weighted average** of the fields both records have (name 0.45, postcode 0.2, email 0.2, phone 0.15). A missing field is left out rather than counted as a disagreement.
4. **Classify** with two thresholds: score ≥ 0.88 is a **match** (link automatically), 0.70–0.88 goes to **review** by a person, below 0.70 is a **non-match**. By default each record is used in at most one link (one-to-one, best score first).
5. **Evaluate** against `labels.csv`, pairs a person has confirmed. **Precision** is the share of links you made that are correct; **recall** is the share of true pairs you found. Raising thresholds usually buys precision with recall, and the review band is where people recover the difference.

## The sample

`crm.csv` (9 records) and `billing.csv` (10 records) are fictional. They include suffix and case differences, a typo (`Litware` / `Litwear`), an abbreviation (`Contoso Pharmaceuticals` / `Contoso Pharma`), a firm sharing a postcode with another (`Fourth Coffee` and `Contoso`), and a different branch that should *not* be linked (`Woodgrove Bank (Scotland)`).

Result: 7 automatic matches, all correct, plus 1 review pair (`Tailspin Toys` / `Tailspin Toy Co`, which has a different email). Automatic precision 1.00 and recall 0.88; with the review pair accepted, both are 1.00.

## Run it

```bash
python3 linkage.py
python3 -m unittest -v
```

## Extending it

- **Learn the weights.** The Fellegi-Sunter model, the statistical basis of record linkage, derives field weights from how often fields agree among true matches versus non-matches. Libraries such as Splink implement it at scale.
- **Better name comparison.** Token-based similarity (so `Works Adventure` matches `Adventure Works`), nickname and abbreviation tables, and term-frequency adjustment (agreement on a rare name means more than on `Smith`).
- **Clusters, not pairs.** Within one system, link records transitively into clusters and pick a "golden record".
- **Review workflow.** Send review pairs to a queue, record decisions, and add them to the labelled set so evaluation improves over time.

## Limitations

- Thresholds and weights here are tuned to a tiny sample. On real data, label a few hundred pairs (stratified across score bands) and choose thresholds from the precision and recall you need.
- Blocking can hide true pairs: a record with a typo in the first letters of its name *and* a different postcode is never compared. Use several blocking keys and measure recall on labelled data.
- Exact comparison of email and phone treats `accounts@` and `finance@` at the same company as a disagreement.
- Linking personal data is processing under data protection law; record why you are doing it and keep the review decisions auditable.
