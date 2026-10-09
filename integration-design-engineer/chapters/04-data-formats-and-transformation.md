# Chapter 4. Data Formats, Schemas and Transformation

> "There are only two hard things in integration: dates, money, character encodings, and off-by-one errors."

## What you will learn

- The data formats you will exchange (JSON, XML, CSV, fixed-width, Avro, Protobuf, Parquet) and their pitfalls.
- How to describe data with schemas (JSON Schema, XSD, Avro and Protobuf schemas) and how schemas evolve without breaking consumers.
- The traps that cause most data bugs: character encoding, dates and time zones, numbers and money, nulls, identifiers.
- How to design and document a **data mapping**, the integration engineer's most important artefact.
- Canonical data models: when they help and when they hurt.
- Transformation tools: code, JSONata, XSLT, DataWeave, jq and iPaaS mappers.

---

## 4.1 Why transformation is the heart of integration

Two systems almost never agree on how to represent the same thing. Consider a customer address:

**Shopify (JSON):**
```json
{"address1": "12 High St", "address2": "Flat 3", "city": "Leeds",
 "province_code": null, "country_code": "GB", "zip": "LS1 4AB"}
```

**NetSuite (SuiteTalk REST, simplified):**
```json
{"addr1": "12 High St", "addr2": "Flat 3", "city": "Leeds",
 "state": "", "country": {"id": "GB"}, "zip": "LS1 4AB"}
```

**The 3PL (fixed-width file, positions 1–40, 41–80, …):**
```
12 HIGH ST FLAT 3                       LEEDS                   GB LS1 4AB
```

Even this tiny example raises decisions. Should the 3PL get upper case? How do two address lines merge into one 40-character field, and what happens to text beyond 40 characters? Is a `null` province the same as an empty string? Is `GB` correct, or does the 3PL expect `UK`? Multiply that by hundreds of fields and dozens of entities, and you see why **mapping** is where integration projects spend much of their effort, and where most production defects originate.

---

## 4.2 Formats

### JSON

**JavaScript Object Notation** (RFC 8259) is the default for modern APIs.

- Types: object, array, string, number, boolean, `null`.
- **Numbers have no defined precision.** Many parsers (JavaScript's, and any that use IEEE-754 doubles) lose precision beyond 2^53 (about 9 × 10^15). A 64-bit ID such as `1234567890123456789` silently becomes `1234567890123456800`. **Send large integers and identifiers as strings.** Twitter's API famously added `id_str` for this reason.
- **Decimals:** `0.1 + 0.2 != 0.3` in binary floating point. Never put money in a float (§4.5).
- No date type; dates are strings by convention (§4.4).
- Duplicate keys are technically allowed but behave unpredictably. Avoid them.
- Variants: **JSON Lines / NDJSON** (one object per line, ideal for bulk streams), **JSON:API** (a convention for REST payloads), **HAL** (hypermedia links), **JSON-LD** (linked data).

### XML

**Extensible Markup Language** dominates SOAP, EDI-adjacent B2B formats, finance (ISO 20022), healthcare (CDA), government and publishing.

- Elements, attributes, text and **namespaces** (`xmlns`). Namespaces cause most XML parsing bugs: `<ord:Order xmlns:ord="urn:acme:orders">` and `<Order xmlns="urn:acme:orders">` are the *same* element. XPath queries must be namespace-aware.
- **Mixed content** and whitespace handling are subtle.
- Schema language: **XSD** (§4.3).
- Querying and transformation: **XPath**, **XQuery**, **XSLT**.
- Security: disable external entity resolution to prevent **XXE** (XML External Entity) attacks, and guard against "billion laughs" entity expansion (Chapter 10).

### CSV and delimited files

Comma-separated values look trivial and are not. RFC 4180 describes a common form, but real-world files vary:

- Delimiter: comma, semicolon (common in locales that use a decimal comma), tab or pipe.
- Quoting: fields containing the delimiter, quotes or newlines must be quoted, and embedded quotes doubled (`"He said ""hi"""`). Many producers get this wrong.
- **Line endings:** `\r\n` versus `\n`.
- **Header row:** present or not, and column order stable or not.
- **Encoding:** UTF-8, UTF-8 with a BOM, Windows-1252 or Latin-1 (§4.4).
- **Spreadsheet corruption:** when a human opens and saves a CSV in Excel, leading zeros vanish (`00123` → `123`), long numbers become scientific notation (`1.23457E+15`), dates are reinterpreted, and gene names turn into dates. Never let humans round-trip integration files through a spreadsheet.
- **CSV injection:** cells beginning with `=`, `+`, `-` or `@` can execute as formulas when opened. Sanitise CSVs destined for humans.

Always use a real CSV library, never `line.split(",")`.

### Fixed-width (positional) files

Each field occupies fixed character positions, defined in a layout document or a COBOL copybook:

```
Pos  Len  Field          Format
1    10   CUSTOMER_ID    left-aligned, space-padded
11   8    ORDER_DATE     YYYYMMDD
19   11   AMOUNT         9(9)V99, zero-padded, implied decimal
30   3    CURRENCY       ISO 4217
```

`00000012345` with an implied decimal (`V99`) means 123.45. Mainframe files may also use **EBCDIC** encoding and **packed decimal (COMP-3)** fields, which store two digits per byte. Use a library that understands copybooks.

### Binary and schema-driven formats

| Format | Where | Notes |
|---|---|---|
| **Apache Avro** | Kafka, data pipelines | Compact binary; the schema travels separately (via a **schema registry**); designed for schema evolution. |
| **Protocol Buffers (Protobuf)** | gRPC, Kafka, Google APIs | Compact; fields identified by *numbers*, which makes evolution rules explicit. |
| **Apache Parquet** | Data lakes and warehouses | Columnar; ideal for analytics and bulk exports. |
| **Apache Arrow** | In-memory analytics interchange | Zero-copy columnar memory format. |
| **MessagePack / CBOR** | Compact JSON-like binary | CBOR (RFC 8949) appears in IoT and WebAuthn. |

### Industry formats

EDI (X12, EDIFACT), HL7 v2 (pipe-delimited), FHIR (JSON/XML), ISO 20022 (XML), SWIFT MT (tagged text), FIX (tag=value) and others are covered in Chapter 13.

---

## 4.3 Schemas: contracts for data

A **schema** describes what valid data looks like. Schemas give you validation, documentation, code generation and the basis for compatibility rules.

### JSON Schema

The current version is **Draft 2020-12**. OpenAPI 3.1 and 3.2 use JSON Schema 2020-12 directly; OpenAPI 3.0 used a modified subset.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.acme.com/order/v1",
  "type": "object",
  "required": ["order_id", "currency", "lines"],
  "properties": {
    "order_id": {"type": "string", "pattern": "^ORD-[0-9]{5,}$"},
    "currency": {"type": "string", "enum": ["USD", "EUR", "GBP"]},
    "total": {"type": "string", "pattern": "^-?[0-9]+(\\.[0-9]{1,4})?$",
              "description": "Decimal amount as a string to avoid float rounding"},
    "placed_at": {"type": "string", "format": "date-time"},
    "lines": {
      "type": "array", "minItems": 1,
      "items": {
        "type": "object",
        "required": ["sku", "qty"],
        "properties": {
          "sku": {"type": "string"},
          "qty": {"type": "integer", "minimum": 1}
        }
      }
    }
  },
  "additionalProperties": true
}
```

Note that `format` (such as `date-time`) is an *annotation* by default in 2020-12. Many validators do not enforce it unless configured to.

### XSD (XML Schema Definition)

XSD is more expressive than JSON Schema for some things (strict types, sequences, inheritance) and more verbose. SOAP WSDLs embed XSDs, and ISO 20022 messages are defined by XSDs.

### Avro and Protobuf schemas

```protobuf
syntax = "proto3";
message OrderPlaced {
  string order_id = 1;
  string currency = 2;
  string total = 3;          // decimal as string
  repeated Line lines = 4;
  google.protobuf.Timestamp placed_at = 5;
  // field 6 was "coupon", removed. Never reuse the number:
  reserved 6;
  reserved "coupon";
}
```

### Schema evolution and compatibility

Systems change. The question is whether a schema change breaks existing producers or consumers. Confluent Schema Registry's vocabulary has become standard:

| Mode | Guarantee | Allowed changes (typical) |
|---|---|---|
| **Backward** | New consumers can read data written with the old schema. | Delete fields; add *optional* fields (with defaults). |
| **Forward** | Old consumers can read data written with the new schema. | Add fields; delete *optional* fields. |
| **Full** | Both directions. | Add or delete optional fields only. |
| **None** | No checks. | Anything (dangerous). |
| `*_TRANSITIVE` | Checked against *all* previous versions, not just the last one. | |

Breaking changes in any format:

- removing or renaming a required field;
- changing a field's type (`string` → `integer`), or its meaning, even if the type stays the same (`amount` switching from cents to dollars);
- narrowing allowed values (removing an enum member that consumers send);
- **widening enums that consumers do not expect.** Adding `"status": "on_hold"` breaks a consumer with a `switch` that has no default branch. Design consumers to tolerate unknown enum values, and document that producers may add them.

**The tolerant reader principle** (Postel's law applied to integration): consumers should ignore fields they do not understand and should not fail on additional properties. Producers should be conservative in what they send. Tolerant readers let producers evolve without coordinated releases.

---

## 4.4 The classic traps

### Character encoding

Text is bytes plus an encoding. **UTF-8** is the default for the modern web, but you will meet:

- **Windows-1252 / ISO-8859-1 (Latin-1)** in older Windows and European systems;
- **Shift_JIS, GB2312 / GBK** in East Asian systems;
- **EBCDIC** (code pages such as 037 or 500) on IBM mainframes and IBM i;
- **UTF-16** in some Microsoft exports;
- a **byte-order mark (BOM)** at the start of UTF-8 files from some Windows tools, which breaks naive parsers (the first header becomes `﻿customer_id`).

Symptoms of an encoding mismatch ("mojibake"): `JosÃ©` instead of `José`, `â€™` instead of `'`, or `?` and `�` replacement characters. The fix is to *know* the encoding of every input (put it in the interface spec) and decode explicitly.

Related issues:

- **Field lengths:** a target field "VARCHAR(40)" may count bytes, not characters. `"Zoë"` is 3 characters but 4 bytes in UTF-8. Truncating in the middle of a multi-byte sequence corrupts the text.
- **Unicode normalisation:** `é` can be one code point (U+00E9) or two (`e` + U+0301). They look identical but compare differently. Normalise (NFC) before comparing or de-duplicating.
- **Target systems that cannot store the characters,** such as emoji in a legacy system limited to MySQL's 3-byte `utf8`, or an ASCII-only bank file. Define a transliteration rule (`Zoë` → `Zoe`).

### Dates, times and time zones

The rules:

1. **Exchange instants in UTC in ISO 8601 / RFC 3339 format** with an explicit offset: `2026-10-09T14:03:11Z` or `2026-10-09T15:03:11+01:00`.
2. **Distinguish an instant from a local date and a local date-time.** A *birth date* (`1990-05-17`) is not an instant; converting it to UTC midnight and back in a negative-offset zone produces `1990-05-16`, a classic bug. A *store opening time* ("09:00 local") is not an instant either.
3. **When the business meaning depends on a place, send the IANA zone name** (`Europe/London`), not just an offset. Offsets change with daylight-saving time, and governments change zone rules with little notice. Keep the tz database updated.
4. **Beware of ambiguous and non-existent local times** around daylight-saving changes (01:30 occurs twice in autumn; 02:30 does not exist in spring in many zones).
5. **Know each system's convention.** Some APIs return local server time without an offset (a design defect). Some store dates as epoch seconds and some as epoch milliseconds: `1760018591` versus `1760018591000`. Microsoft's legacy JSON dates look like `/Date(1760018591000)/`, Excel stores serial day numbers, and .NET ticks count 100-nanosecond intervals from year 1.
6. **Business dates** such as "invoice date", "posting date" and "value date" in banking are dates in a specific calendar and zone, often with **cut-off times** ("payments after 17:00 CET settle next business day"). Capture the rule in the mapping spec.

### Numbers and money

- **Never use binary floating point for money.** Use a decimal type (`BigDecimal`, Python `Decimal`, SQL `NUMERIC`), or integer **minor units** (cents), as Stripe does (`amount: 1999` means $19.99).
- **Minor units vary by currency:** JPY has 0 decimal places, USD 2, and KWD, BHD and OMR 3 (ISO 4217). Hard-coding "divide by 100" breaks for yen and dinars.
- **Always pair an amount with a currency code.** An amount without a currency is a bug waiting to happen.
- **Rounding:** specify the rule (half-up, half-even/banker's rounding) and *where* rounding happens (per line or on the total). Tax engines and ERPs often disagree by a cent. Design reconciliation tolerances.
- **Locale formatting:** `1.234,56` (Germany) and `1,234.56` (US) are the same number. Exchange machine formats, never display formats.
- **Sign conventions:** credits may be negative numbers, positive numbers with a `CR` flag, or (in EDI and some bank files) a trailing minus or an overpunched last digit.

### Nulls, empties and absence

At least four states are distinct:

| State | JSON | Meaning (typically) |
|---|---|---|
| Absent | key missing | "Not provided / don't change" |
| Null | `"field": null` | "Explicitly no value / clear it" |
| Empty | `"field": ""` | "Empty string", which some systems treat as null |
| Value | `"field": "x"` | |

The difference between *absent* and *null* is critical in **partial updates** (PATCH). JSON Merge Patch (RFC 7396) uses `null` to mean "delete this field". Many target systems (and many iPaaS mappers) collapse these states unexpectedly, which leads to data being wiped. State the rule for every field in the mapping spec.

### Identifiers and keys

- **Every system has its own IDs.** Keep a **cross-reference (xref) table** that maps the identifiers between systems (`shopify_order_id ↔ netsuite_internal_id ↔ 3pl_order_ref`). Many enterprise apps let you store the foreign ID in an **external ID** field (Salesforce External ID fields, NetSuite `externalId`), which enables **upserts** (update if it exists, insert if not).
- **Natural keys** (email, SKU, tax number) are tempting and dangerous: they change, they are reused, and they differ in case and formatting.
- **Leading zeros, case and whitespace:** `"00123"`, `"123"`, `"ABC"`, `"abc "`. Normalise deliberately.
- **Salesforce IDs** come in 15-character case-sensitive and 18-character case-insensitive forms; compare the 18-character form.
- **UUIDs:** UUIDv7 (RFC 9562, 2024) is time-ordered and works well as a database key and event ID.

### Code lists and reference data

Status codes, country codes, units of measure, tax codes, payment terms: each system has its own list. Use international standards where possible:

| Domain | Standard |
|---|---|
| Countries | ISO 3166-1 alpha-2 (`GB`, `US`) |
| Subdivisions | ISO 3166-2 (`US-CA`, `GB-ENG`) |
| Currencies | ISO 4217 (`USD`, `EUR`) |
| Languages / locales | BCP 47 (`en-GB`, `pt-BR`) |
| Units of measure | UN/ECE Recommendation 20 codes (`KGM`, `EA`/`C62`), UCUM in healthcare |
| Time zones | IANA tz database names |
| Phone numbers | E.164 (`+447700900123`) |
| Product identifiers | GS1 GTIN |
| Legal entities | LEI (ISO 17442) |

Maintain **value maps** (lookup tables) as versioned configuration, not code, so business users can update them.

---

## 4.5 Designing a data mapping

A **mapping specification** is the contract between the business and the integration. It is reviewed by business analysts, implemented by engineers, tested by QA and consulted by support during incidents. Write it before coding. A template is in [`templates/data-mapping-spec.md`](../templates/data-mapping-spec.md).

A good mapping spec has, for each target field:

| Column | Example |
|---|---|
| Target field | `NetSuite.SalesOrder.shipAddress.addr1` |
| Source field(s) | `Shopify.order.shipping_address.address1` |
| Transformation rule | Trim whitespace; truncate to 150 characters; if truncated, log a warning |
| Required? | Yes |
| Default if missing | Reject the record (error code `MAP-ADDR-001`) |
| Lookup / value map | n/a |
| Example | `"12 High St"` → `"12 High St"` |
| Notes / open questions | Confirm with finance whether PO boxes are allowed |

And at the document level:

- **Scope:** entities, directions and trigger events.
- **Cardinality:** one order produces one sales order, but each order *line* produces how many item fulfilments?
- **Key strategy:** match on external ID; upsert behaviour.
- **Ownership:** which system is the source of truth for each field? (Field-level ownership is common: CRM owns the phone number, ERP owns the credit limit.)
- **Conflict rules** for bidirectional sync: last-writer-wins, source-of-truth-wins, or manual review (Chapter 9).
- **Error categories** and their handling.
- **Value maps:** status codes, countries, units and tax codes.
- **Sample payloads:** at least one realistic source and target example, ideally several edge cases, checked into the repository as test fixtures.

**Practical advice:** work through real production samples, not documentation examples. Ask for twenty real records, including the weird ones. Documentation describes what the system *should* send; production data shows what it *does* send.

---

## 4.6 Canonical data models

A **canonical data model (CDM)** is a shared, system-neutral representation of business entities. Every system maps to and from the canonical form rather than to each other:

- Without a CDM: *n* systems need up to *n(n−1)* directional mappings.
- With a CDM: each system needs two mappings (to and from canonical), so *2n* in total.

**Benefits:** fewer mappings, a shared vocabulary, easier substitution of one system for another, and a natural fit for event-driven architectures, where an `OrderPlaced` event in canonical form is consumed by many systems.

**Risks:**

- **The "universal model" trap.** Trying to model *everything* about "Customer" for *every* system produces a bloated, contested schema that takes years to agree on.
- **Lowest common denominator.** Fields that exist in only one system get lost.
- **Double transformation** costs latency and gives bugs two places to hide.
- **Organisational bottleneck:** one team must approve every change.

**Pragmatic guidance:**

- Use **bounded canonical models**, scoped to a domain (Orders, Customers, Products) and following domain-driven design's *bounded contexts*.
- Keep them small and versioned, and allow extension fields.
- Prefer **industry standards** as the canonical form where they exist (FHIR in healthcare, ISO 20022 in payments, OAGIS or GS1 in supply chain).
- Treat event schemas as **public contracts**, with the same care as an external API (Chapter 17 covers "data contracts").

---

## 4.7 Transformation techniques and tools

### General-purpose code

Python, Java, C#, TypeScript or Go give full power and are easy to unit-test. This is the best choice when mappings are complex or logic-heavy. The downside is that non-engineers cannot read or maintain them.

### Declarative transformation languages

| Tool | Scope | Notes |
|---|---|---|
| **XSLT** (3.0) | XML → anything | Powerful, standard and verbose. Still common in ESBs and SAP. |
| **XQuery** | Querying and transforming XML | |
| **jq** | JSON on the command line | Excellent for exploration and scripts. |
| **JSONata** | JSON query and transform | Used in Node-RED, AWS Step Functions (JSONata support since late 2024), IBM App Connect and others. |
| **DataWeave** | MuleSoft's transformation language | Handles JSON, XML, CSV and more, with strong typing. |
| **Liquid / Jinja / Handlebars** | Templating text output | Popular in iPaaS and email or document generation. |
| **JOLT** | JSON-to-JSON transformation specs | Used in Apache NiFi. |
| **SQL / dbt** | Tabular transformation in warehouses | Chapter 9. |

A JSONata example converting a Shopify order to a simplified ERP order:

```jsonata
{
  "externalId": "SHOP-" & $string(id),
  "tranDate": $substring(created_at, 0, 10),
  "currency": currency,
  "items": line_items.{
    "sku": sku,
    "quantity": quantity,
    "rate": $string(price)
  },
  "shipTo": {
    "addr1": shipping_address.address1,
    "city": shipping_address.city,
    "country": shipping_address.country_code
  }
}
```

### Visual mappers

iPaaS products provide drag-and-drop mappers with function libraries. They are fast for simple mappings and opaque for complex ones. Two warnings: (1) complex logic in visual mappers is hard to review, diff and test, so push complex rules into scripts or lookup tables; (2) export mappings to version control if the platform allows it.

### Testing transformations

Transformations are pure functions (input in, output out), which makes them the *easiest* part of an integration to test thoroughly:

- Keep sample inputs and expected outputs as **golden files** in the repository.
- Add a test for every production defect, using the offending payload with personal data anonymised.
- Use **property-based testing** for tricky cases such as encoding and rounding.
- Validate outputs against the target schema in the test suite.

See [`examples/data-mapping/`](../examples/data-mapping/) for a runnable mapping with tests.

---

## Summary

- Transformation is where integrations add value and where most defects arise.
- Learn the quirks of JSON (number precision), XML (namespaces), CSV (quoting, spreadsheet damage) and fixed-width/EBCDIC.
- Use schemas as contracts and agree compatibility rules. Make consumers tolerant readers.
- Handle encodings, time zones, money, nulls and identifiers explicitly; these cause the classic bugs.
- Write a field-level mapping specification with real sample data before building.
- Use canonical models in bounded, pragmatic form, and prefer industry standards.

## Exercises

See [`exercises/04-data-formats-and-transformation.md`](../exercises/04-data-formats-and-transformation.md).

## Further reading

- RFC 8259 (JSON), RFC 4180 (CSV), RFC 3339 (timestamps), RFC 9562 (UUIDs).
- JSON Schema 2020-12 specification and *Understanding JSON Schema* (json-schema.org).
- Confluent documentation on Schema Registry compatibility types.
- Joel Spolsky, "The Absolute Minimum Every Software Developer Absolutely, Positively Must Know About Unicode and Character Sets (No Excuses!)" (2003).
- Jon Skeet, "Storing UTC is not a silver bullet" (2019).
