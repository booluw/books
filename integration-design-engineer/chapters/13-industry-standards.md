# Chapter 13. Industry Standards: EDI, Healthcare, Finance and More

> "The nice thing about standards is that you have so many to choose from."
> (Andrew S. Tanenbaum)

## What you will learn

- Why industries create their own integration standards, and how to approach a new one.
- **EDI** (ANSI X12, UN/EDIFACT), transports (AS2, VANs, SFTP), acknowledgements and trading-partner onboarding.
- **Healthcare:** HL7 v2, FHIR (R4, R5 and the R6 ballot), SMART on FHIR, CDS Hooks, X12 HIPAA transactions, DICOM, TEFCA and the CMS-0057-F rule.
- **Finance and payments:** ISO 20022 and the SWIFT migration, SWIFT MT, FIX, NACHA, card networks, open banking (PSD2, UK Open Banking, FAPI, FDX and the US Section 1033 rule).
- **E-invoicing:** Peppol, EN 16931, and mandates in Germany, France and the EU (ViDA).
- Other domains: supply chain (GS1), insurance (ACORD), telecom (TM Forum), energy and government.

Domain standards are where integration engineers become hard to replace. A developer who can build REST APIs is common. A developer who understands an X12 856 hierarchy or a FHIR `Bundle` transaction is not.

---

## 13.1 Why industry standards exist

When many organisations exchange the same kinds of documents (orders, invoices, patient records, payments), bilateral custom formats do not scale. Industries form standards bodies to agree on:

- **Document types and their semantics:** what a "purchase order" contains and means.
- **Code lists:** units, qualifiers, reason codes and statuses.
- **Envelopes and acknowledgements:** how to address, batch and confirm receipt.
- **Transport and security profiles.**
- **Implementation guides:** which optional parts a community actually uses.

**How to approach a new standard:**

1. Find the **base standard** and the **implementation guide (IG)** your partners actually use. Partners almost never use the base standard as published. Retailers publish EDI guides; healthcare uses national IGs (US Core); banks publish ISO 20022 usage guidelines (CBPR+).
2. Get **real sample messages**, including edge cases.
3. Use a **validator** (EDI translators, the FHIR validator, SWIFT MyStandards).
4. Learn the **acknowledgement model**: how will you know a message was received, accepted or rejected?
5. Build a **mapping** from the standard to your canonical model (Chapter 4), with a test suite of samples.

---

## 13.2 EDI: Electronic Data Interchange

### The two major standards

| | ANSI ASC X12 | UN/EDIFACT |
|---|---|---|
| Region | North America (also used elsewhere) | International, Europe, Asia |
| Governing body | Accredited Standards Committee X12 | UN/CEFACT |
| Documents called | Transaction sets (numbered) | Messages (named) |
| Versions | e.g. 004010, 005010, 008030 | e.g. D.96A, D.01B, D.21A |

Common documents:

| Business document | X12 | EDIFACT |
|---|---|---|
| Purchase order | **850** | ORDERS |
| PO acknowledgement | 855 | ORDRSP |
| PO change | 860 | ORDCHG |
| Advance ship notice (ASN) | **856** | DESADV |
| Invoice | **810** | INVOIC |
| Remittance advice | 820 | REMADV |
| Warehouse shipping order | 940 | (various) |
| Warehouse shipping advice | 945 | (various) |
| Inventory advice | 846 | INVRPT |
| Functional acknowledgement | **997** / 999 | CONTRL |
| Motor carrier load tender / status | 204 / 214 | IFTMIN / IFTSTA |
| Healthcare claim | 837 (HIPAA) | — |

### Anatomy of an X12 message

X12 uses **segments** (terminated by a segment terminator, often `~`), **elements** (separated by an element separator, often `*`) and **sub-elements** (often `:` or `>`). The separators are declared in the ISA header itself.

```
ISA*00*          *00*          *ZZ*ACMESUPPLIER   *ZZ*BIGRETAILER    *261009*1403*U*00401*000000123*0*P*>~
GS*PO*BIGRETAILER*ACMESUPPLIER*20261009*1403*123*X*004010~
ST*850*0001~
BEG*00*SA*PO-778812**20261009~
REF*DP*042~
DTM*002*20261020~
N1*ST*BIGRETAILER DC 7*92*0007~
PO1*1*24*EA*4.75**UP*012345678905*VN*TSHIRT-M~
PID*F****T-SHIRT MEDIUM BLUE~
PO1*2*12*EA*4.75**UP*012345678912*VN*TSHIRT-L~
CTT*2~
SE*10*0001~
GE*1*123~
IEA*1*000000123~
```

Structure:

- **ISA/IEA:** the *interchange* envelope (sender and receiver IDs, control number, test or production indicator `T`/`P`).
- **GS/GE:** the *functional group* (groups transactions of the same type, with its own control number).
- **ST/SE:** the *transaction set*: one business document. `SE` contains the segment count, a built-in integrity check.
- Inside: segments such as `BEG` (beginning of PO), `REF` (reference), `DTM` (date/time), `N1` (name/party), `PO1` (line item), `PID` (description) and `CTT` (totals).
- **Qualifiers** give elements meaning: in `PO1*…*UP*012345678905*VN*TSHIRT-M`, `UP` means "UPC code follows" and `VN` means "vendor part number follows".
- **Loops** and **hierarchical levels** (the 856 ASN's `HL` segments nest shipment → order → pack → item) make some documents hard to map.

### Acknowledgements

1. **Transport-level receipt:** an AS2 **MDN** (Message Disposition Notification), signed, proves the file arrived intact.
2. **Syntax-level acknowledgement:** **997 Functional Acknowledgement** (or **999** in HIPAA) reports whether each functional group or transaction set was syntactically accepted, accepted with errors, or rejected. Trading partners usually require you to send 997s within hours and to monitor the ones you receive.
3. **Business-level response:** for example the **855** PO acknowledgement (accept, reject or change lines), or a **TA1** interchange acknowledgement.

Missing acknowledgements must raise alerts. Retailers impose **chargebacks** (financial penalties) for late or incorrect ASNs and invoices.

### Transports

- **AS2** (RFC 4130): HTTP(S) with S/MIME signing and encryption and signed MDNs. The dominant retail transport (Walmart popularised it in the early 2000s). Certificates must be exchanged and rotated with every partner.
- **VAN** (Value-Added Network): a mailbox service (OpenText, SPS Commerce, IBM Sterling, Kleinschmidt, Loren Data and others) that routes documents between partners for a per-document or per-kilocharacter fee.
- **SFTP / FTPS:** common with logistics providers and smaller partners.
- **AS4:** web-services-based, used in Peppol and European energy and customs.
- **API-based EDI:** newer providers (Stedi, Orderful) expose EDI as JSON APIs with validation, which simplifies development but not the semantics.

### Trading-partner onboarding

Onboarding a new EDI partner typically involves:

1. Exchanging **partner profiles**: ISA/GS IDs and qualifiers, transport details, certificates, and the partner's **implementation guide** (often a PDF, sometimes published on platforms such as SPS Commerce).
2. Building and testing **maps** per document type and per partner (partners customise the standard).
3. **Connectivity testing** (AS2 handshake, MDNs).
4. **Certification testing** with the partner's test scenarios (some retailers run formal testing portals).
5. **Go-live** with close monitoring of acknowledgements and chargebacks.

EDI translators (IBM Sterling B2B Integrator, OpenText, Cleo, Boomi B2B, MuleSoft B2B, SAP Integration Advisor, Azure Logic Apps Integration Accounts, AWS B2B Data Interchange, and open-source libraries such as `pyx12`, `bots` and Smooks) parse, validate and map EDI.

---

## 13.3 Healthcare

Healthcare integration is large, regulated and full of specialised standards. In the US it is shaped by HIPAA, the 21st Century Cures Act, ONC/ASTP certification rules and CMS interoperability rules. Similar programmes exist elsewhere (the NHS in England, Canada Health Infoway, Australia's Digital Health Agency, and the European Health Data Space).

### HL7 version 2

**HL7 v2** (first released in 1989; v2.5.1 and v2.8+ common) is still the most widely deployed clinical messaging standard inside hospitals. It is pipe-delimited:

```
MSH|^~\&|LAB|HOSP|EHR|HOSP|20261009140311||ORU^R01|MSG00001|P|2.5.1
PID|1||123456^^^HOSP^MR||DOE^JANE^A||19800517|F
OBR|1||LAB7788|85025^CBC^CPT
OBX|1|NM|718-7^Hemoglobin^LN||13.2|g/dL|12.0-15.5|N|||F
```

- **Segments** (`MSH` header, `PID` patient, `PV1` visit, `OBR` order, `OBX` result), **fields** (`|`), **components** (`^`), **repetitions** (`~`), **escape** (`\`) and **sub-components** (`&`).
- **Message types and trigger events:** `ADT^A01` (admit), `ADT^A08` (update patient), `ORM^O01` / `OML` (orders), `ORU^R01` (results), `SIU` (scheduling), `DFT` (financial), `MDM` (documents).
- Transport is usually **MLLP** (Minimal Lower Layer Protocol) over TCP, with **ACK/NAK** responses.
- Every hospital customises v2 ("if you've seen one HL7 v2 interface, you've seen one HL7 v2 interface"). Expect `Z`-segments (custom segments) and local code tables.
- **Interface engines** (Rhapsody, InterSystems HealthShare / Health Connect, Infor Cloverleaf, NextGen Mirth Connect, Corepoint, Iguana) route and transform HL7 traffic in hospitals. Mirth Connect moved to a commercial licence from version 4.6 in 2025, which led to community forks such as Open Integration Engine.

### FHIR

**FHIR** (Fast Healthcare Interoperability Resources) is HL7's modern RESTful standard.

- Data is modelled as **resources**: `Patient`, `Practitioner`, `Encounter`, `Observation`, `Condition`, `MedicationRequest`, `AllergyIntolerance`, `Appointment`, `Claim`, `ExplanationOfBenefit` and roughly 150 more.
- Exchanged as JSON or XML over **REST** (`GET [base]/Patient/123`, `GET [base]/Observation?patient=123&code=http://loinc.org|718-7`), or as **messages**, **documents** (`Bundle` of type `document`) and **subscriptions** (topic-based in R5, backported to R4).
- **Bulk Data Access** (`$export`, NDJSON output) provides population-level exports.
- **Terminologies** are essential: LOINC (observations), SNOMED CT (clinical terms), RxNorm (medications, US), ICD-10 (diagnoses), CPT (procedures, US).

**Versions *(October 2026)*:**

| Version | Status |
|---|---|
| **R4** (4.0.1, 2019) | First release with normative content; **the version used in production and in US regulations.** |
| R4B (2022) | Minor update. |
| **R5** (2023) | Trial use for most resources; limited production adoption. |
| **R6** | Balloted in January 2026, aiming to make most core resources normative (stable). Publication is expected around late 2026 or 2027; check hl7.org for the final date. |

**Implementation guides** constrain FHIR for specific uses: **US Core** (the US baseline; version 9.0.0 is R4-based and aligned to USCDI v6, though certification rules reference specific earlier versions), **Da Vinci** IGs (payer–provider exchange, including prior authorisation), **CARIN Blue Button** (consumer access to claims), **International Patient Summary (IPS)** and national IGs elsewhere.

**SMART on FHIR** layers OAuth 2.0 and OIDC on FHIR, so apps can launch from an EHR (Epic, Oracle Health, MEDITECH) with user context and scopes such as `patient/Observation.rs` (SMART v2 scopes). **SMART Backend Services** uses `client_credentials` with `private_key_jwt` for system-to-system access. **CDS Hooks** lets EHRs call external decision-support services at workflow moments (`patient-view`, `order-select`).

### US regulatory drivers *(as of October 2026)*

- **CMS Interoperability and Prior Authorization Final Rule (CMS-0057-F):** requires impacted payers (Medicare Advantage, Medicaid and CHIP programmes and managed-care plans, and qualified health plans on federally facilitated exchanges) to implement Patient Access, Provider Access, Payer-to-Payer and Prior Authorization **FHIR R4 APIs**, with most API requirements due from **1 January 2027**. Operational prior-authorisation requirements (decision timeframes, denial reasons) began on 1 January 2026.
- **TEFCA** (Trusted Exchange Framework and Common Agreement): a national network-of-networks run through **Qualified Health Information Networks (QHINs)**, coordinated by the Sequoia Project as Recognized Coordinating Entity. By late 2025 ONC had designated more than ten QHINs (including eHealth Exchange, Epic Nexus, Health Gorilla, KONZA, MedAllies, CommonWell, Kno2, eClinicalWorks, Surescripts, Netsmart and Oracle Health). TEFCA traffic today is largely document-based (IHE profiles), with a FHIR roadmap.
- **Information blocking rules** (21st Century Cures Act) penalise unreasonable interference with access to electronic health information.

### X12 HIPAA transactions

US healthcare *administrative* transactions are mandated X12 version 005010 documents: **837** (claims: professional, institutional, dental), **835** (remittance/payment), **270/271** (eligibility inquiry and response), **276/277** (claim status), **278** (prior authorisation), **834** (benefit enrolment) and **820** (premium payment). Clearinghouses (Change Healthcare, part of Optum; Availity; Waystar and others) sit in the middle. The February 2024 ransomware attack on Change Healthcare disrupted claims processing across the US for weeks, a vivid lesson in integration concentration risk.

### Other healthcare standards

- **DICOM** for medical imaging (and DICOMweb for REST access).
- **IHE profiles** (XDS, XCA, PIX/PDQ) for document sharing.
- **CDA / C-CDA** for clinical documents (XML), still common in exchange networks.
- **NCPDP SCRIPT** for e-prescribing in the US.
- **openEHR** for clinical data modelling (strong in parts of Europe).

### Healthcare integration essentials

- HIPAA applies: **BAAs** with every vendor, minimum necessary data, audit logs (Chapter 10).
- **Patient identity matching** (no universal patient ID in the US) is a hard problem; MPIs (Master Patient Indexes) do probabilistic matching.
- Clinical safety: a wrong mapping of a lab unit (mg/dL versus mmol/L) can harm patients. Test with clinicians involved.

---

## 13.4 Finance and payments

### ISO 20022

**ISO 20022** is the global XML (and increasingly JSON) messaging standard for financial services. Messages are identified by business area and number:

| Area | Examples | Use |
|---|---|---|
| `pain` (payments initiation) | `pain.001` (customer credit transfer initiation), `pain.002` (status report), `pain.008` (direct debit initiation) | Corporate → bank |
| `pacs` (payments clearing and settlement) | `pacs.008` (FI-to-FI customer credit transfer), `pacs.009`, `pacs.004` (return), `pacs.002` (status) | Bank ↔ bank |
| `camt` (cash management) | `camt.053` (bank-to-customer statement), `camt.052` (intraday report), `camt.054` (debit/credit notification), `camt.056` (cancellation request) | Bank → corporate; investigations |
| `acmt`, `reda`, `sese`, `semt`, `setr` | Accounts, reference data, securities | |

**Migration status *(October 2026)*:**

- **SWIFT cross-border payments:** the MT/MX coexistence period for FI-to-FI cross-border payment instructions **ended on 22 November 2025**. MT103 and MT202 payment instructions are no longer carried on FIN for these flows; SWIFT offers chargeable contingency conversion for a limited period. Under the CBPR+ guidelines, **unstructured postal addresses are no longer accepted after November 2026**; structured or "hybrid" addresses are required.
- **Market infrastructures:** the Eurosystem's T2 (March 2023), the Bank of England's CHAPS (June 2023), Fedwire Funds Service in the US (**July 2025**), and many instant-payment schemes (SEPA Instant, FedNow, the UK's planned new payments architecture, India's UPI-adjacent systems, Australia's NPP) use ISO 20022.
- **Corporate-to-bank** flows (`pain.001`, `camt.053`) are widely used; many banks are retiring older formats such as MT940 statements and proprietary files.

**Why it matters to integration engineers:** ISO 20022 messages carry far richer, structured data (structured remittance information, ultimate debtor and creditor, purpose codes, legal entity identifiers). Mapping ERP payment runs and bank statements to and from ISO 20022 correctly is a common and valuable integration skill. Watch for truncation when richer data passes through systems that still store MT-length fields.

### SWIFT MT (legacy)

Tag-based text messages (`:20:` reference, `:32A:` value date/currency/amount, `:50K:` ordering customer, `:59:` beneficiary). Still used for some categories (for example certain trade-finance and securities messages, until their own retirement dates), and still present in many corporate systems as MT940/MT942 statements.

### Other payment and capital-markets standards

- **NACHA ACH** (US): fixed-width 94-character records for ACH batches (file header, batch header, entry detail, addenda, controls). Same Day ACH limits, return codes (`R01` insufficient funds and so on).
- **BAI2:** a US bank statement format, being replaced by `camt`.
- **SEPA** (EU): ISO 20022-based credit transfers and direct debits; SEPA Instant became mandatory for euro-area payment service providers in 2025 under the Instant Payments Regulation.
- **Card networks:** **ISO 8583** messages between acquirers, networks and issuers; **PCI DSS** for card data (Chapter 10). Merchants usually integrate through payment service providers' REST APIs (Stripe, Adyen, Checkout.com, Worldpay) rather than directly.
- **FIX protocol** (Financial Information eXchange): tag=value messages (`35=D` new order single) for trading; FIXML and Simple Binary Encoding variants for high performance.
- **FpML** for OTC derivatives; **XBRL** for financial reporting (SEC, ESMA ESEF).

### Open banking and open finance

- **EU PSD2** (2018) required banks to expose account information and payment initiation APIs to licensed third parties with strong customer authentication. Its successors (**PSD3** and the **Payment Services Regulation**) and the proposed **FIDA** (Financial Data Access) regulation were still in the EU legislative process in 2026. The **Berlin Group NextGenPSD2** framework is a common API standard in Europe.
- **UK Open Banking** (OBIE standards, now overseen by Open Banking Limited and the transition to a future entity) provides standardised APIs; Variable Recurring Payments (VRPs) are expanding.
- **FAPI 2.0** (OpenID Foundation) is the high-security OAuth profile used by many open-banking regimes (Brazil, UK, Australia, Saudi Arabia and others): PAR, PKCE, sender-constrained tokens (mTLS or DPoP) and `private_key_jwt`.
- **United States:** the **Financial Data Exchange (FDX)** API is the industry standard. The CFPB's **Section 1033 Personal Financial Data Rights** rule was finalised in late 2024 with phased compliance dates, but was placed under reconsideration in 2025, with an advance notice of proposed rulemaking in August 2025 and enforcement enjoined by a federal court pending reconsideration. As of October 2026 its final shape and timing remain uncertain. Check the CFPB's current position before relying on any date.
- Aggregators (Plaid, MX, Finicity/Mastercard, Tink/Visa, TrueLayer, Yapily) provide unified access across banks.

---

## 13.5 E-invoicing and tax reporting

Governments are mandating structured electronic invoices and real-time tax reporting worldwide. This drives large integration projects between ERPs and government or network platforms.

- **EN 16931** is the European semantic standard for e-invoices, expressed in two syntaxes: **UBL 2.1** and **UN/CEFACT CII**.
- **Peppol** is an international network (four-corner model with certified **access points**) using the **Peppol BIS Billing 3.0** profile of EN 16931 over AS4. It is mandated or widely used for B2G and increasingly B2B in Belgium, Norway, Singapore, Australia, New Zealand, Japan and elsewhere.
- **Germany:** since **1 January 2025** all businesses must be able to *receive* structured e-invoices (XRechnung, or ZUGFeRD 2.x hybrid PDF/A-3 with embedded CII XML; a plain PDF no longer counts); *issuing* becomes mandatory from **1 January 2027** for businesses with more than €800,000 prior-year turnover and from **1 January 2028** for all others.
- **France:** the B2B e-invoicing and e-reporting reform began on **1 September 2026**: all businesses must be able to receive e-invoices through accredited platforms (*plateformes agréées*), and large and mid-sized companies must issue them, with smaller companies following from September 2027. The tax authority announced a graduated enforcement approach for the start-up phase.
- **EU ViDA (VAT in the Digital Age):** adopted by the Council in March 2025. It allows member states to introduce domestic e-invoicing mandates without derogation, and introduces mandatory e-invoicing with near-real-time digital reporting for intra-EU B2B transactions from **1 July 2030**.
- **Clearance and continuous transaction control (CTC) models** elsewhere: Italy (SdI, since 2019), Spain (SII; Verifactu and B2B e-invoicing under the Crea y Crece law, on a phased timeline), Poland (KSeF, mandatory from February 2026), Mexico (CFDI), Brazil (NF-e), India (e-invoicing via IRP), Saudi Arabia (FATOORA/ZATCA), Egypt, Malaysia and many more.

Integration work here involves ERP-to-provider mappings, real-time submission with clearance responses, error handling for rejected invoices, archiving rules, and frequent regulatory schema updates. Most organisations use a specialised compliance provider (Sovos, Avalara, Pagero (Thomson Reuters), Vertex, Comarch, SAP Document and Reporting Compliance, Storecove, among others), so the integration is ERP → provider API.

---

## 13.6 Other domains

| Domain | Standards |
|---|---|
| **Retail and supply chain** | GS1 identifiers (GTIN, GLN, SSCC), **GS1 EDI** (EANCOM, GS1 XML), **EPCIS 2.0** (event-based traceability, JSON-LD and REST), GS1 Digital Link; ASC X12 and EDIFACT; FDA DSCSA (pharma traceability, with phased enforcement 2024–2026). |
| **Logistics** | X12 204/210/214/990; EDIFACT IFTMIN/IFTSTA; carrier APIs (UPS, FedEx, DHL; FedEx and UPS retired legacy SOAP and web-services APIs in favour of REST/OAuth APIs in 2024–2026); DCSA standards for container shipping; IATA ONE Record for air cargo. |
| **Insurance** | **ACORD** XML/JSON standards and forms; Lloyd's market messaging. |
| **Telecommunications** | **TM Forum Open APIs** (over 100 REST APIs for product catalogue, ordering, trouble tickets); CAMARA (Linux Foundation) network APIs exposed by operators. |
| **Energy and utilities** | IEC CIM (Common Information Model, IEC 61968/61970); ENTSO-E and EDI@Energy formats in Europe; Green Button (US smart meter data); OpenADR (demand response); OCPP and OCPI for EV charging. |
| **Government** | National e-government interoperability frameworks; NIEM (US); EU **Once-Only Technical System**; X-Road (Estonia and others). |
| **Automotive and manufacturing** | VDA and Odette standards; OPC UA and MQTT for industrial IoT; ISA-95 (enterprise–control integration, the B2MML XML implementation). |
| **Education** | 1EdTech (formerly IMS Global): LTI, OneRoster, Caliper. |
| **HR and payroll** | HR Open Standards; national payroll reporting formats (e.g. UK RTI, Australia STP). |
| **Travel** | IATA NDC (New Distribution Capability, XML APIs for airline offers and orders); OpenTravel Alliance; HTNG for hospitality. |

---

## Summary

- Industry standards turn bilateral chaos into shared document types, code lists and acknowledgements. Always work from the implementation guide your partners actually use, with real samples and validators.
- EDI (X12, EDIFACT) over AS2, VANs and SFTP remains the backbone of retail, logistics and healthcare administration. Master envelopes, qualifiers, loops and acknowledgements.
- Healthcare runs on HL7 v2 inside hospitals and FHIR R4 for modern and regulated APIs, with SMART on FHIR for authorisation. CMS-0057-F drives payer FHIR APIs from January 2027.
- Payments run on ISO 20022: SWIFT cross-border coexistence ended in November 2025, and structured addresses are required from November 2026.
- E-invoicing mandates (Germany 2025–2028, France from September 2026, EU ViDA by 2030, and many CTC regimes) are a growing source of integration work.

## Exercises

See [`exercises/13-industry-standards.md`](../exercises/13-industry-standards.md).

## Further reading

- X12 (x12.org) and UN/CEFACT (unece.org/trade/uncefact) standards portals.
- HL7 FHIR specification (hl7.org/fhir) and the SMART App Launch IG; Tim Benson and Grahame Grieve, *Principles of Health Interoperability: FHIR, HL7 and SNOMED CT*, 4th edition (Springer, 2021).
- SWIFT ISO 20022 programme pages and CBPR+ usage guidelines (via MyStandards).
- OpenID Foundation FAPI 2.0 specifications.
- European Commission e-invoicing and ViDA pages; OpenPeppol (peppol.org).
