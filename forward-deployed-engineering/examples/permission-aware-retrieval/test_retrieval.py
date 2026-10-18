import unittest

from retrieval import (CORPUS, USERS, BM25Index, Context, Document, User, build_context,
                       can_read, check_citations, tokenise)

RESTRICTED = {"HR-RESTRUCT", "HR-PAY", "SEC-INC-42", "DRAFT-NOACL"}


class AccessTests(unittest.TestCase):
    def setUp(self):
        self.index = BM25Index(CORPUS)
        self.analyst = USERS["analyst"]

    def test_user_without_access_never_gets_restricted_documents(self):
        # Query with every word from every document, including the restricted ones.
        words = {w for d in CORPUS for w in tokenise(d.title + " " + d.text)}
        queries = list(words) + [d.title for d in CORPUS] + [d.text for d in CORPUS]
        for q in queries:
            for hit in self.index.search(q, self.analyst, k=10):
                self.assertNotIn(hit.doc.id, RESTRICTED, q)

    def test_authorised_user_does_get_the_restricted_document(self):
        hits = self.index.search("Leeds office redundancy plans", USERS["hr_director"])
        self.assertEqual(hits[0].doc.id, "HR-RESTRUCT")

    def test_document_without_acl_is_visible_to_nobody(self):
        everyone = User("root", frozenset({"all-staff", "hr", "hr-leadership", "security"}))
        draft = next(d for d in CORPUS if d.id == "DRAFT-NOACL")
        self.assertFalse(can_read(everyone, draft))
        ids = [h.doc.id for h in self.index.search("redundancy notes draft", everyone, k=10)]
        self.assertNotIn("DRAFT-NOACL", ids)

    def test_user_with_no_groups_gets_nothing(self):
        self.assertEqual(self.index.search("expenses", User("guest", frozenset())), [])

    def test_restricted_documents_do_not_change_permitted_scores(self):
        # Ranking statistics come from the permitted set only, so adding hidden
        # documents must not change what the analyst sees, or the scores.
        public_only = BM25Index([d for d in CORPUS if d.id not in RESTRICTED])
        for q in ["Leeds office", "expenses claim receipts", "redundancy"]:
            a = [(h.doc.id, h.score) for h in self.index.search(q, self.analyst, k=10)]
            b = [(h.doc.id, h.score) for h in public_only.search(q, self.analyst, k=10)]
            self.assertEqual(a, b, q)

    def test_trimming_before_ranking_still_fills_top_k(self):
        # Filtering after taking the top k would leave the analyst with fewer
        # results (the HR documents rank highest); filtering first does not.
        hits = self.index.search("Leeds office salary redundancy travel expenses", self.analyst, k=3)
        self.assertEqual(len(hits), 3)


class RankingTests(unittest.TestCase):
    def test_tokenise(self):
        self.assertEqual(tokenise("The Claims, and the CLAIM!"), ["claim", "claim"])
        self.assertEqual(tokenise("access class"), ["access", "class"])

    def test_bm25_prefers_relevant_and_rare_terms(self):
        docs = [Document("a", "Hotels", "hotel limits for London hotel stays", frozenset({"g"})),
                Document("b", "Rail", "rail travel and hotel", frozenset({"g"})),
                Document("c", "Food", "meals and drinks", frozenset({"g"}))]
        user = User("u", frozenset({"g"}))
        hits = BM25Index(docs).search("hotel London", user)
        self.assertEqual([h.doc.id for h in hits], ["a", "b"])        # c has no query terms
        self.assertGreater(hits[0].score, hits[1].score)


class ContextAndCitationTests(unittest.TestCase):
    def setUp(self):
        index = BM25Index(CORPUS)
        self.ctx = build_context(index.search("Leeds office redundancy plans", USERS["analyst"]))

    def test_context_labels_documents(self):
        self.assertEqual(self.ctx.doc_ids, ["OPS-LEEDS"])
        self.assertIn("[doc:OPS-LEEDS] Leeds office guide", self.ctx.text)

    def test_context_budget(self):
        hits = BM25Index(CORPUS).search("office travel expenses", USERS["analyst"], k=3)
        self.assertEqual(len(build_context(hits, max_chars=50).doc_ids), 1)

    def test_citation_checker(self):
        self.assertTrue(check_citations("Open 8am to 6pm [doc:OPS-LEEDS].", self.ctx).ok)
        leak = check_citations("Forty roles at risk [doc:HR-RESTRUCT].", self.ctx)
        self.assertFalse(leak.ok)
        self.assertEqual(leak.unknown, ["HR-RESTRUCT"])
        self.assertFalse(check_citations("No citations here.", self.ctx).ok)
        self.assertFalse(check_citations("x [doc:OPS-LEEDS] [doc:MADE-UP]", Context("", ["OPS-LEEDS"])).ok)


if __name__ == "__main__":
    unittest.main()
