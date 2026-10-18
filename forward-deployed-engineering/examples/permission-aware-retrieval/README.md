# Permission-aware retrieval (Chapters 12 and 14)

## The problem

Woodgrove Bank wants an assistant that answers staff questions from internal documents. Most documents are for everyone; some are not. The Leeds office restructuring plan is for HR leadership only. If an analyst asks "what are the Leeds office redundancy plans?" and the assistant answers from that plan, you have built a data leak with a chat interface.

**Retrieval-augmented generation (RAG)** means finding documents relevant to a question and giving them to a language model as context, so it answers from the organisation's own material rather than from memory. In an enterprise, retrieval must respect the same **access control lists (ACLs)**, the lists of who may read each document, as the source systems do. This is the single most common security finding in enterprise AI deployments, and a question every customer security reviewer will ask (Chapter 14).

## Terms

- **BM25** ("best match 25"): a long-established ranking formula for keyword search. A document scores higher when it contains the query's words often (with diminishing returns), when those words are rare across the collection, and when it is not padded with unrelated text. Production systems often combine it with **vector search** (similarity of embeddings); the permission logic is the same.
- **Security trimming:** removing documents the user may not read from search results. The crucial design choice is *when*.
- **Citation:** a reference in the answer, here `[doc:ID]`, to the document that supports a statement.

## How `retrieval.py` works

1. **Trim first, then rank.** `BM25Index.search()` first selects the documents this user may read (`can_read()`: the user must share a group with the document) and scores only those. Restricted documents never enter results, context or citations.
2. **Statistics from the permitted set.** BM25 uses collection statistics (how many documents contain a word, average length). These are computed over the permitted documents only; otherwise a user could infer that a hidden document mentions "redundancy" from how scores shift. A test proves the analyst's scores are identical whether or not the HR documents exist.
3. **Deny by default.** A document with no groups is readable by nobody, so a missing ACL fails closed.
4. **Build context with labels.** `build_context()` labels each document `[doc:ID]` and stops at a character budget.
5. **Check citations.** `check_citations()` passes an answer only if it cites at least one document and every cited ID was in the context shown to this user. That catches invented citations and, as defence in depth, any path by which a restricted ID reached the answer.

Why not filter after ranking? Taking the top 3 and then removing restricted ones leaves the user with fewer (or zero) results, and the ranking statistics have already been shaped by documents they cannot see. A test shows that trimming first still returns a full top 3.

## The demo

```text
analyst asks 'Leeds office redundancy plans'      -> OPS-LEEDS (office guide) only
hr_director asks the same                         -> HR-RESTRUCT, OPS-LEEDS, HR-PAY
analyst answer citing HR-RESTRUCT                 -> citation check fails
```

## Run it

```bash
python3 retrieval.py
python3 -m unittest -v
```

## Extending it

- **Sync ACLs from the source.** In production, read permissions from SharePoint, Google Drive or the document system at index time *and* re-check at query time, because permissions change. Know how stale your ACL copy can be and tell the customer.
- **Group expansion.** Real groups nest (a team inside a department). Resolve a user's effective groups from the identity provider.
- **Hybrid retrieval.** Add vector search and merge the rankings; apply the same filter to both before ranking.
- **Chunking.** Split long documents into passages that each inherit the document's ACL.
- **Audit.** Log who asked what, which documents were retrieved and which were cited.

## Limitations

- The tokeniser is deliberately crude (lower-case, stop words, strip a trailing `s`). Use a proper analyser for real search quality.
- Scoring only permitted documents costs work per query proportional to the permitted set. Search engines do the same thing efficiently with filtered indexes.
- Trimming protects documents. It does not stop a model leaking what it learned in training, or an authorised user pasting restricted text into a shared chat.
