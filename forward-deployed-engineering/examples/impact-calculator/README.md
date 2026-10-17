# Impact calculator (Chapters 3 and 5)

## The problem

Two money questions follow an FDE through every engagement:

1. **For the customer:** "What is this worth to us, and when does it pay back?" You need a defensible figure at the end of discovery to choose the first use case (Chapter 5), and again at the end of the pilot to justify production.
2. **For your own company:** "Does this deal make money once FDE time is counted?" FDE salaries are a cost of delivering revenue, so they depress **gross margin** early in a deal (Chapter 3).

A spreadsheet answers both, but a small tested module makes the formula explicit, reproduces the book's numbers exactly, and makes ranges and sensitivity as easy as a single estimate.

## Terms

- **Loaded hourly cost:** what an hour of an employee's time costs the organisation: salary plus employer taxes, pension, benefits and overheads. Typically well above salary ÷ hours.
- **Annual contract value (ACV):** the revenue from a customer contract in one year.
- **Gross margin:** (revenue − cost of delivering it) ÷ revenue. Software businesses commonly run at 70–80% or more; services businesses much lower.
- **Fully loaded FDE cost:** an FDE's salary, benefits, travel and management overhead for a year.
- **Payback period:** months until cumulative net benefit covers the one-off cost.
- **Return on investment (ROI):** (value − cost) ÷ cost.
- **Sensitivity analysis:** how much the answer moves when an assumption changes. A **tornado** table ranks inputs by how much their plausible range moves the result.

## The book's worked examples, reproduced exactly

**Chapter 5, quick value estimate:**

```
annual_value = people × hours saved per person per week × weeks per year × loaded hourly cost
             + errors avoided × cost per error
             + revenue uplift

60 adjusters × 3 h/week × 46 weeks × £45/hour = £372,600 per year   (book: ≈ £373,000)
```

**Chapter 3, deal gross margin** (platform cost 20% of ACV; FDE loaded cost $350,000):

| Year | ACV | Platform | FDE | Gross profit | Gross margin | FDE % of revenue |
|---|---|---|---|---|---|---|
| 1 | $600,000 | $120,000 | $350,000 (2 FDEs × 50%) | $130,000 | 21.7% (≈ 22%) | 58.3% |
| 2 | $1,500,000 | $300,000 | $175,000 (0.5 FDE) | $1,025,000 | 68.3% | 11.7% |
| 3 | $2,500,000 | $500,000 | $175,000 (0.5 FDE) | $1,825,000 | 73.0% | 7.0% |
| **3 years** | **$4,600,000** | | | **$2,980,000** | **64.8% (≈ 65%)** | |

## Beyond the book

- **Scenarios** for the Chapter 5 example, varying hours saved (1.5 / 3 / 4 hours a week): low £186,300, base £372,600, high £496,800.
- **Sensitivity** across illustrative plausible ranges: hours saved moves the answer most (£186,300 – £496,800), so it is the number to measure first in the pilot.
- **Payback**, with illustrative costs not taken from the book (£150,000 to deploy, £40,000 a year to run): 5.4 months; first-year ROI 96%.

## Run it

```bash
python3 impact.py
python3 -m unittest -v
```

## Extending it

- **Adoption curve.** Value rarely arrives on day one. Multiply by an adoption share per month and compute payback from the cumulative curve.
- **Discounting.** For multi-year cases, discount future value (net present value) at the customer's cost of capital.
- **Deal what-ifs.** Use `build_deal()` to ask what happens if expansion is slower or FDE effort doesn't fall: for example, year-2 ACV of $800,000 with a full FDE still assigned.
- **Ranges in proposals.** Present the low case first. Customers trust a conservative number they can check more than an impressive one they can't.

## Limitations

- Time saved is not cash saved unless the organisation redeploys the time or avoids hiring. Say which you are claiming.
- The model ignores second-order effects (faster settlement, customer satisfaction, risk reduction) unless you put numbers on them; the book's example deliberately excludes them.
- All inputs are assumptions. Write down the source of each and have the customer's finance team check them.
