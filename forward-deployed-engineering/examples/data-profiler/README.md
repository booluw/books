# Data profiler (Chapter 10)

## The problem

On day three of an engagement the customer sends "the claims extract". Before you design a pipeline, promise an accuracy figure or train anyone on a dashboard, you need to know what is actually in it. **Data profiling** means computing summary facts about every column of a dataset (how complete it is, what type it really holds, what its values look like) so that you find the problems before your users do.

Customers rarely know the quality of their own data. Profiling turns "the data is fine" into evidence you can show them: "8% of claims have no usable date, and one claim appears twice."

## What `profiler.py` reports

For every column:

| Measure | Meaning | Why it matters |
|---|---|---|
| **Null rate** | Share of rows that are empty or only whitespace | Completeness |
| **Missing incl. placeholders** | Nulls plus placeholder values | The real completeness figure |
| **Distinct count** | Number of different real values | A "unique" ID with fewer distinct values than rows has duplicates |
| **Inferred type** | The dominant type (integer, decimal, date, boolean, text) if at least 90% of real values agree; otherwise `mixed` | Tells you what parsing will break |
| **Min / max** | Compared numerically for numbers and chronologically for dates | Finds negative amounts, outliers and impossible dates |
| **Top values** | The five most common values | Shows inconsistent spellings such as `Open` / `open` / `CLOSED` |
| **Shapes** | Each value reduced to a pattern: upper-case letter → `A`, lower-case → `a`, digit → `9` (`CLM-1001` → `AAA-9999`) | A second shape in an ID column is usually an error (`POL-48291` is one digit short) |
| **Suspicious values** | Placeholders, leading/trailing whitespace, values that don't fit the column type, sentinel numbers such as `99999999` | The values that quietly corrupt joins and totals |

A **placeholder** is a value someone typed because they had no real value: `N/A`, `unknown`, `TBC`, `0000-00-00`. A **sentinel number** is a number used as a code for "not set", such as `99999999`. Both are non-empty, so a naive null check counts them as data.

For the table, it also reports **duplicate keys** (the key column defaults to the first column; keys are compared after trimming and upper-casing) and **ragged rows**: rows with the wrong number of fields, usually caused by an unquoted comma inside a value.

## The sample

`sample.csv` is a fictional claims extract from Contoso Insurance with deliberate problems: a duplicated claim, a lower-case ID, a short policy number, `N/A` / `unknown` / `TBC` placeholders, a `0000-00-00` date, a UK-format date among ISO dates, the date `yesterday`, an amount of `99999999`, a negative amount, inconsistent status capitalisation, a trailing space in a customer name, and an unquoted `£1,200.00` that shifts a row's columns.

## Run it

```bash
python3 profiler.py sample.csv
python3 profiler.py sample.csv --key policy_number
python3 -m unittest -v
```

## Extending it

- **Rules from the customer.** Add per-column expectations ("claim_date must be after policy start", "status in {Open, Closed, Pending}") and report violations. This is the start of a data contract (Chapter 10).
- **Outliers.** Flag numbers more than, say, three interquartile ranges from the median.
- **Cross-column checks.** Same postcode with different customers; closed claims with no adjuster.
- **Trend.** Save each profile as JSON and diff tomorrow's extract against today's, so a schema change or a jump in nulls raises an alert.
- **Bigger files.** Stream rows and keep counters instead of loading everything; sample for top values.

## Limitations

- Type inference understands ISO (`2026-03-02`) and UK (`02/03/2026`) dates only. Ambiguous dates such as `03/04/2026` are read as day/month; check with the customer.
- The placeholder list is generic. Every organisation has its own (`ZZZ`, `DO NOT USE`); add them.
- Everything is held in memory. For files of millions of rows, use a database or a dataframe library and the same ideas.
- Profiling finds symptoms. Deciding which values are wrong, and fixing them at source, needs the people who own the data.
