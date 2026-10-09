# Data Mapping Specification: <Source entity> → <Target entity>

| | |
|---|---|
| Integration | |
| Direction | Source → Target |
| Trigger | |
| Cardinality | 1 source record → … target records |
| Key strategy | Upsert on `<target external id field>` = `<prefix>` + `<source id>` |
| Business owner (source) | |
| Business owner (target) | |
| Version / date | |

## Field mappings

| # | Target field | Type / length | Req? | Source field(s) | Transformation rule | Default if missing | Value map | Error code if invalid | Example (source → target) | Owner of field | Notes / open questions |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | | | |

### Rules applied to every field unless stated

- Text: trim, NFC-normalise; transliterate if target is ASCII-only: *yes/no*
- Truncation: *reject / truncate with warning*
- Null vs absent: *absent = leave unchanged; null = clear; empty string = …*
- Dates: *instants in UTC RFC 3339; business dates in `<IANA zone>`*
- Money: *decimal strings; currency always present; rounding half-up/half-even at line/total level*

## Value maps

### <Map name> (maintained by: …)

| Source value | Target value | Notes |
|---|---|---|

## Error codes

| Code | Meaning | Handling (business queue / technical DLQ) | Who fixes |
|---|---|---|---|

## Samples

- `samples/<case>.input.json` → `samples/<case>.expected.json` (also used as golden-file tests)

## Sign-off

| Name | Role | Date |
|---|---|---|
