# Field feedback tracker (Chapter 16)

## The problem

FDEs find product gaps first. At Contoso the FDE builds a SAML proxy because the product lacks single sign-on; at Woodgrove Bank another FDE writes a nightly script to archive AI answers for compliance. Each workaround solves one customer's problem, and each is invisible to the product team unless someone writes it down.

The feedback loop from field to product is what separates an FDE-led software company from a consultancy (Chapter 3): what FDEs build for one customer should become product for the next. This tracker turns scattered field reports into a ranked list the product team can act on.

## Terms

- **Field report:** a short structured record of a gap found in the field: customer, problem, the **workaround** built, severity, ARR affected and tags.
- **ARR (annual recurring revenue):** the yearly value of a customer's subscription. "ARR affected" is the revenue at risk or blocked by the gap.
- **Productise:** turn a field-built solution into a supported product feature, so the next customer gets it without FDE effort.
- **Rule of three:** when the same need appears at three or more *distinct* customers, it is a pattern rather than a one-off, and a candidate for the product. (Two is a coincidence worth watching; one is a field solution.)
- **Jaccard similarity:** the overlap of two sets, |A ∩ B| ÷ |A ∪ B|, from 0 (nothing in common) to 1 (identical).

## How `tracker.py` works

1. **Load** reports from JSON (`field_reports.json`) and CSV (`more_reports.csv`, tags separated by `;`).
2. **Normalise** each report into a set of **concepts**: its tags, plus words from the problem statement mapped through a synonym table (`SAML`, `Okta`, `Entra`, `log in` and `single sign-on` all become `sso`; `Excel`, `CSV`, `spreadsheet` and `download` become `export`). The synonym table is the shared vocabulary between the field and product teams.
3. **Cluster** reports whose concept sets have Jaccard similarity ≥ 0.5, directly or through a chain of similar reports (single-link clustering with union-find). A report with no tags still clusters through its keywords.
4. **De-duplicate by customer.** Two reports from Woodgrove Bank are one customer for the rule of three, and their ARR is counted once.
5. **Recommend:** ≥ 3 customers → `PRODUCTISE`; 2 → `WATCH`; 1 → `FIELD SOLUTION`.
6. **Rank** by recommendation, then ARR affected, then number of customers, then worst severity.

## The sample result

14 reports from 8 fictional customers become 5 needs:

| Rank | Need | Customers | ARR affected | Recommendation |
|---|---|---|---|---|
| 1 | Audit log of AI answers (compliance) | 4 | £2,580,000 | PRODUCTISE |
| 2 | Single sign-on | 4 | £2,430,000 | PRODUCTISE |
| 3 | Export results | 3 | £590,000 | PRODUCTISE |
| 4 | SharePoint permissions | 2 | £550,000 | WATCH |
| 5 | Welsh-language answers | 1 | £600,000 | FIELD SOLUTION |

Note that the Welsh-language request affects more ARR than SharePoint permissions but ranks lower: one large customer's need is a field solution until a second customer asks.

## Run it

```bash
python3 tracker.py
python3 tracker.py field_reports.json more_reports.csv
python3 -m unittest -v
```

## Extending it

- **Feed it from where FDEs already work.** A form, a Slack shortcut or a ticket template that produces the same fields.
- **Track productisation.** Link each cluster to a roadmap item, and measure the **productisation rate** (share of field-built components that became product) from Chapter 3.
- **Weight by strategy.** Multiply ARR by segment priority, or add pipeline (deals blocked) alongside current ARR.
- **Better grouping.** Use text embeddings to suggest clusters, and have a product manager confirm them; keep the synonym table as the confirmed vocabulary.
- **Close the loop.** Tell the FDE and the customer when the need ships, and retire the workaround.

## Limitations

- Keyword and synonym matching misses needs described in unfamiliar words. Review unclustered reports by hand.
- ARR affected is self-reported by FDEs and tends to be the whole account's ARR. Agree a definition (blocked expansion, renewal at risk) and apply it consistently.
- Single-link clustering can chain loosely related reports together. Inspect large clusters before acting on them.
- The rule of three is a heuristic, not a law: a single critical need from a strategic customer may still justify product work.
