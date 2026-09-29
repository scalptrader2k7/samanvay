"""Bounded candidate retrieval; proposals only, never identity decisions."""
from collections import Counter, defaultdict
import re
import time

RETRIEVAL_VERSION = "lexical-retrieval-v0.1"
TOKEN_RE = re.compile(r"[a-z0-9]+(?:[./-][a-z0-9]+)*", re.I)
STOPWORDS = frozenset({
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "including",
    "is", "of", "on", "or", "the", "to", "up", "with", "supply", "nos",
    "no", "qty", "item", "items", "spare", "spares",
})


def useful_tokens(text):
    tokens = []
    for token in TOKEN_RE.findall(text.casefold()):
        if token in STOPWORDS or (len(token) == 1 and token.isalpha()):
            continue
        tokens.append(token)
    return frozenset(tokens)


def character_ngrams(text, size=3):
    compact = re.sub(r"\s+", " ", text.casefold()).strip()
    if len(compact) <= size:
        return frozenset((compact,)) if compact else frozenset()
    return frozenset(compact[index:index + size] for index in range(len(compact) - size + 1))


class CandidateIndex:
    def __init__(self, records, *, max_rare_tokens=8, posting_cap=250, pool_cap=500):
        if not records:
            raise ValueError("At least one record is required")
        self.records = {r["source_record_id"]: r for r in records}
        if len(self.records) != len(records) or None in self.records:
            raise ValueError("Records require unique nonblank source_record_id values")
        self.max_rare_tokens = max_rare_tokens
        self.posting_cap = posting_cap
        self.pool_cap = pool_cap
        self.exact = defaultdict(list)
        self.identifiers = defaultdict(list)
        self.postings = defaultdict(list)
        self.tokens = {}
        self.ngrams = {}
        for record in records:
            source_id = record["source_record_id"]
            norm = record["description_normalized"].casefold()
            self.exact[norm].append(source_id)
            tokens = useful_tokens(record["description_normalized"])
            self.tokens[source_id] = tokens
            self.ngrams[source_id] = character_ngrams(record["description_normalized"])
            for token in tokens:
                self.postings[token].append(source_id)
            for field, value in record.get("source_identifiers", {}).items():
                if field == "corpus_id" or not value.strip():
                    continue
                self.identifiers[(field, value)].append(source_id)
        for index in (self.exact, self.identifiers, self.postings):
            for values in index.values():
                values.sort()

    def base_candidates(self, query_id):
        """Return bounded IDs/evidence and diagnostics without fuzzy comparison."""
        started = time.perf_counter()
        query = self.records[query_id]
        evidence = defaultdict(lambda: {"exact_normalized_text": False,
                                        "shared_identifiers": [], "shared_tokens": set()})
        norm = query["description_normalized"].casefold()
        for candidate_id in self.exact.get(norm, []):
            if candidate_id != query_id:
                evidence[candidate_id]["exact_normalized_text"] = True
        for field, value in query.get("source_identifiers", {}).items():
            if field == "corpus_id" or not value.strip():
                continue
            for candidate_id in self.identifiers.get((field, value), []):
                if candidate_id != query_id:
                    evidence[candidate_id]["shared_identifiers"].append(
                        {"field": field, "value": value})
        query_tokens = self.tokens[query_id]
        selected = sorted(query_tokens, key=lambda t: (len(self.postings[t]), t))[:self.max_rare_tokens]
        postings_visited = 0
        for token in selected:
            posting = self.postings[token]
            if len(posting) > self.posting_cap:
                continue
            postings_visited += len(posting)
            for candidate_id in posting:
                if candidate_id != query_id:
                    evidence[candidate_id]["shared_tokens"].add(token)
        if len(evidence) > self.pool_cap:
            ordered = sorted(evidence, key=lambda candidate_id: (
                not evidence[candidate_id]["exact_normalized_text"],
                -len(evidence[candidate_id]["shared_identifiers"]),
                -len(evidence[candidate_id]["shared_tokens"]), candidate_id))
            evidence = {candidate_id: evidence[candidate_id] for candidate_id in ordered[:self.pool_cap]}
        for item in evidence.values():
            item["shared_tokens"] = sorted(item["shared_tokens"])
        return evidence, {
            "query_id": query_id, "selected_tokens": selected,
            "postings_visited": postings_visited, "candidate_pool_size": len(evidence),
            "max_rare_tokens": self.max_rare_tokens, "posting_cap": self.posting_cap,
            "pool_cap": self.pool_cap,
            "elapsed_ms": (time.perf_counter() - started) * 1000,
            "all_pairs_compared": False,
        }

    def retrieve(self, query_id, *, top_k=10, cross_organization_only=False):
        if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 50:
            raise ValueError("top_k must be an integer from 1 to 50")
        started = time.perf_counter()
        query = self.records[query_id]
        evidence, diagnostic = self.base_candidates(query_id)
        results = []
        comparisons = 0
        for candidate_id, signals in evidence.items():
            candidate = self.records[candidate_id]
            if cross_organization_only and candidate["source_organization"] == query["source_organization"]:
                continue
            query_tokens, candidate_tokens = self.tokens[query_id], self.tokens[candidate_id]
            union = query_tokens | candidate_tokens
            token_jaccard = len(query_tokens & candidate_tokens) / len(union) if union else 0.0
            query_grams, candidate_grams = self.ngrams[query_id], self.ngrams[candidate_id]
            fuzzy = (2 * len(query_grams & candidate_grams) /
                     (len(query_grams) + len(candidate_grams))) if query_grams or candidate_grams else 0.0
            comparisons += 1
            score = (1.0 if signals["exact_normalized_text"] else
                     min(0.999999, 0.62 * fuzzy + 0.33 * token_jaccard +
                         (0.05 if signals["shared_identifiers"] else 0.0)))
            reasons = []
            if signals["exact_normalized_text"]:
                reasons.append({"method": "exact_normalized_text",
                                "value": query["description_normalized"]})
            reasons.extend({"method": "exact_source_identifier", **item}
                           for item in signals["shared_identifiers"])
            if signals["shared_tokens"]:
                reasons.append({"method": "shared_useful_tokens",
                                "tokens": signals["shared_tokens"],
                                "token_jaccard": round(token_jaccard, 6)})
            reasons.append({"method": "fuzzy_character_trigrams", "score": round(fuzzy, 6)})
            results.append({
                "status": "candidate_only", "retrieval_version": RETRIEVAL_VERSION,
                "query_source_record_id": query_id, "candidate_source_record_id": candidate_id,
                "candidate_organization": candidate["source_organization"],
                "candidate_description_original": candidate["description_original"],
                "candidate_family": candidate.get("family"),
                "candidate_attributes": candidate.get("attributes", {}),
                "retrieval_score": round(score, 6), "reasons": reasons,
            })
        results.sort(key=lambda item: (-item["retrieval_score"], item["candidate_source_record_id"]))
        results = results[:top_k]
        for rank, result in enumerate(results, 1):
            result["rank"] = rank
        diagnostic.update({"fuzzy_comparisons": comparisons, "returned": len(results),
                           "top_k": top_k, "cross_organization_only": cross_organization_only,
                           "total_elapsed_ms": (time.perf_counter() - started) * 1000})
        return results, diagnostic
