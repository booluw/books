# Interface Agreement: <Party A> ↔ <Party B>: <Interface name>

| | |
|---|---|
| Version / effective date | |
| Party A contacts (business, technical, support, escalation) | |
| Party B contacts | |

## 1. Purpose and scope

## 2. Business process and triggers

## 3. Transport and connectivity

| Item | Production | Test |
|---|---|---|
| Protocol (HTTPS/SFTP/AS2/Kafka/…) | | |
| Endpoint / host / port | | |
| Source IPs to allow-list | | |
| Certificates (owner, expiry, rotation process) | | |
| Authentication | | |

## 4. Messages / documents

| Message | Direction | Format & version | Schema / IG link | Max size | Frequency / volume | Sample |
|---|---|---|---|---|---|---|

## 5. Acknowledgements and responses

*Transport receipts (e.g. MDN), syntax acks (e.g. 997), business responses; timing expectations.*

## 6. Error handling

| Error | Detected by | Notification | Correction process | Resend rules |
|---|---|---|---|---|

## 7. Service levels

- Hours of operation; maintenance windows and notice periods
- Latency / turnaround targets
- Availability targets
- Support response times by severity

## 8. Security and data protection

- Data categories; legal basis / agreements (DPA, BAA)
- Encryption (transport, message-level)
- Retention and deletion

## 9. Change management

- Notice period for changes (breaking: …; non-breaking: …)
- Versioning and deprecation policy
- Test cycle required before changes go live

## 10. Testing and go-live criteria

| Test case | Expected result | Status |
|---|---|---|

## 11. Sign-off

| Party | Name | Role | Date |
|---|---|---|---|
