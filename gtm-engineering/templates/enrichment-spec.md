# Enrichment Specification: <Table / job name>

*Owner: · Schedule: · Budget per run: · Last updated:*

## Input
- Entity: account / contact · Source: · Key: domain / email · Expected rows:

## Pre-filters (run before paid steps)
| Filter | Rule | Rationale |
|---|---|---|

## Steps

| # | Field | Method (provider / AI / formula) | Run condition | Acceptance criteria | Cost per row | Cache window |
|---|---|---|---|---|---|---|
| 1 | Company firmographics | | | | | |
| 2 | Persona match | | | | | |
| 3 | Email (waterfall: A → B → C) | | only if persona match | verification = valid | | 90 days |
| 4 | AI custom attribute | | | YES/NO/UNKNOWN + evidence URL | | |

## Provenance fields written
`<field>_source`, `<field>_updated_at`, `<field>_confidence`

## Outputs and destinations
| Field | Destination system | Field name | Write mode (upsert key) | Overwrite policy |
|---|---|---|---|---|

## Quality checks
- Sample review size: · Accuracy target: · Bounce target:

## Failure handling
- Provider errors: retry later; do not mark not-found
- Budget exceeded: stop and alert

## Change log
