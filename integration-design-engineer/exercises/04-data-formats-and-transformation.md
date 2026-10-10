# Exercises: Chapter 4, Data Formats and Transformation

## Questions

1. A partner sends `{"id": 9007199254740993}`. What does a JavaScript consumer see, and how should the API be designed instead?
2. An order is placed at `2026-03-08T01:30:00-08:00` in Los Angeles. What is the UTC instant? What is the local business date? Which date should an ERP's "transaction date" use?
3. Convert 1234.5 JPY, 1234.5 USD and 1234.5 KWD into integer minor units. What goes wrong if you always multiply by 100?
4. Give the four states a field can be in when sent in a PATCH, and what each typically means.
5. A CSV from a partner shows customer IDs `1234` where your system has `001234`. Give two likely causes and a fix.
6. Write a mapping-spec row for the target field `ShipToCountry` (ISO 3166-1 alpha-2, required) from a source with free-text country names such as "United Kingdom", "UK", "Great Britain".
7. Run the tests in `examples/data-mapping`, then add a golden-file case for a KWD order with a price of `"1.2345"`. What should the rate be?
8. Which changes are backward-compatible for consumers who are tolerant readers? (a) add optional field, (b) rename field, (c) add enum value, (d) change `amount` from cents to dollars, (e) make an optional field required.

## Solutions

1. `9007199254740992` (precision lost above 2^53). Send IDs as strings (`"id": "9007199254740993"`).
2. UTC: `2026-03-08T09:30:00Z`. Local business date: 2026-03-08. Use the local business date in the company's (or store's) time zone, as defined in the mapping spec.
3. JPY has 0 decimals: 1235 (after half-up rounding) or reject the fractional yen; USD: 123450; KWD (3 decimals): 1234500. Multiplying by 100 makes yen amounts 100× too large and loses KWD precision.
4. Absent (leave unchanged), null (clear the value; in JSON Merge Patch, delete), empty string (set to empty; some systems treat it as null), a value (set).
5. Someone opened and saved the file in a spreadsheet (leading zeros stripped), or the partner's system stores IDs as numbers. Fix: quote the field or agree a fixed-width, zero-padded format in the interface agreement; normalise by left-padding on ingestion if the rule is well defined; never let humans round-trip integration files in spreadsheets.
6. Example: target `ShipToCountry`; source `shipping.country`; rule "trim, case-fold, look up in value map COUNTRY_NAMES (United Kingdom/UK/Great Britain/England → GB …); if no match reject with MAP-CTRY-001 to the business queue"; required yes; default none; example "UK" → "GB"; owner: e-commerce ops maintains the value map.
7. KWD has 3 minor units, so `"1.2345"` rounds half-up to `"1.235"`. Expected line `rate` "1.235". (Remember `subtotal_price` must match the quantity × rate.)
8. Compatible: (a); (c) only if consumers tolerate unknown enum values. Breaking: (b), (d) (semantic change), (e).
