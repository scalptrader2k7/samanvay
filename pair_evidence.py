"""Traceable Phase 5 attribute comparison and safety gates."""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, InvalidOperation
import re

from candidate_retrieval import character_ngrams, useful_tokens


COMPARISON_VERSION = "pair-evidence-v0.2"
ATTRIBUTE_FIELDS = (
    "size_dimension", "material_grade", "standard", "pressure", "voltage", "model_part"
)
CRITICAL_FIELDS = frozenset(("size_dimension", "material_grade", "standard", "pressure", "voltage"))


def _compact(value):
    return re.sub(r"[^A-Z0-9./]+", "", value.upper())


def _decimal(text):
    try:
        return Decimal(text.replace(",", ""))
    except InvalidOperation:
        return None


def _with_source(item, record):
    start, end = item.get("start"), item.get("end")
    raw = item.get("value_raw")
    if not isinstance(start, int) or not isinstance(end, int):
        raise ValueError("Attribute evidence requires integer source offsets")
    if record["description_original"][start:end] != raw:
        raise ValueError(f"Evidence span does not reproduce {record['source_record_id']} source text")
    return {**item, "source_record_id": record["source_record_id"]}


def _size_value(item):
    value = item["value_normalized"].upper().strip()
    compact = re.sub(r"\s+", "", value)
    rule = item["rule_id"]
    match = re.search(r"(\d+(?:\.\d+)?)", compact)
    number = _decimal(match.group(1)) if match else None
    if rule == "size.metric":
        if re.search(r"(?:SQMM|MM2|MMÂ²)$", compact):
            return ("cross_section_area_mm2", number)
        if compact.endswith("MM"):
            return ("linear_dimension_mm", number)
        if compact.endswith("CM"):
            return ("linear_dimension_mm", number * 10 if number is not None else None)
        return ("uncertain_size", None)
    if rule == "size.nominal":
        return ("nominal_bore_mm", number)
    if rule == "size.schedule":
        schedule = re.sub(r"^(?:SCHEDULE|SCH)", "", compact)
        return ("pipe_schedule", schedule)
    if rule == "size.inch":
        # Decimal inches are safe; mixed forms such as 2.1/16 remain uncertain.
        decimal_match = re.fullmatch(r"(\d+(?:\.\d+)?)(?:\"|''|INCH|INCHES)", compact)
        return ("diameter_inch", _decimal(decimal_match.group(1))) if decimal_match else ("uncertain_size", None)
    return ("uncertain_size", None)


def _pressure_value(item):
    compact = _compact(item["value_normalized"])
    number_match = re.search(r"\d[\d,]*(?:\.\d+)?", item["value_normalized"])
    number = _decimal(number_match.group(0)) if number_match else None
    rule = item["rule_id"]
    if rule.startswith("pressure.class"):
        return ("pressure_class", number)
    if rule == "pressure.pn":
        return ("pn_designation", number)
    if "PSI" in compact:
        return ("pressure_psi", number)
    if "BAR" in compact:
        return ("pressure_psi", number * Decimal("14.5037738") if number is not None else None)
    return ("uncertain_pressure", None)


def _voltage_value(item):
    compact = _compact(item["value_normalized"])
    match = re.match(r"(\d+(?:\.\d+)?)(KV|VOLTS?|V)$", compact)
    if not match:
        return ("uncertain_voltage", None)
    number = _decimal(match.group(1))
    return ("voltage_v", number * 1000 if match.group(2) == "KV" else number)


def _standard_value(item):
    compact = _compact(item["value_normalized"])
    scheme_match = re.match(r"(API|ASTM|ASME|IEC|ISO|DIN|ANSI|BS|EN|IS)", compact)
    return ((f"standard_{scheme_match.group(1).lower()}", compact) if scheme_match
            else ("uncertain_standard", None))


def _canonical(field, item):
    if field == "size_dimension":
        return _size_value(item)
    if field == "pressure":
        return _pressure_value(item)
    if field == "voltage":
        return _voltage_value(item)
    if field == "standard":
        return _standard_value(item)
    if field == "material_grade":
        return ("material_grade", _compact(item["value_normalized"]))
    if field == "model_part":
        return ("model_part", _compact(item["value_normalized"]))
    raise KeyError(field)


def _group(field, values, record):
    grouped = defaultdict(list)
    uncertain = []
    seen = set()
    for original in values:
        item = _with_source(original, record)
        kind, value = _canonical(field, item)
        marker = (kind, value, item["start"], item["end"])
        if marker in seen:
            continue
        seen.add(marker)
        enriched = {**item, "comparison_type": kind,
                    "canonical_value": str(value) if value is not None else None}
        if kind.startswith("uncertain_") or value is None:
            uncertain.append(enriched)
        else:
            grouped[kind].append(enriched)
    return grouped, uncertain


def compare_field(field, left, right):
    left_values = left.get("attributes", {}).get(field, [])
    right_values = right.get("attributes", {}).get(field, [])
    left_groups, left_uncertain = _group(field, left_values, left)
    right_groups, right_uncertain = _group(field, right_values, right)
    missing = []
    if not left_values:
        missing.append("left")
    if not right_values:
        missing.append("right")
    compatible, conflicts, not_comparable = [], [], []
    shared_types = sorted(set(left_groups) & set(right_groups))
    for kind in shared_types:
        left_set = {item["canonical_value"] for item in left_groups[kind]}
        right_set = {item["canonical_value"] for item in right_groups[kind]}
        if left_set == right_set:
            compatible.append({"comparison_type": kind,
                               "values": sorted(left_set),
                               "left_evidence": left_groups[kind],
                               "right_evidence": right_groups[kind]})
        else:
            conflicts.append({"reason_code": f"{field}.different_{kind}",
                              "comparison_type": kind,
                              "left_values": sorted(left_set), "right_values": sorted(right_set),
                              "left_evidence": left_groups[kind],
                              "right_evidence": right_groups[kind]})
    left_only = sorted(set(left_groups) - set(right_groups))
    right_only = sorted(set(right_groups) - set(left_groups))
    if left_only or right_only:
        entry = {"reason_code": f"{field}.different_semantic_types",
                 "left_types": left_only, "right_types": right_only,
                 "left_evidence": [x for kind in left_only for x in left_groups[kind]],
                 "right_evidence": [x for kind in right_only for x in right_groups[kind]]}
        # Different pressure designation systems are a conservative safety conflict.
        if field == "pressure" and left_groups and right_groups and not shared_types:
            entry["reason_code"] = "pressure.incompatible_rating_bases"
            conflicts.append(entry)
        else:
            not_comparable.append(entry)
    uncertain = left_uncertain + right_uncertain
    if conflicts:
        status = "conflict"
    elif uncertain or not_comparable:
        status = "uncertain"
    elif missing:
        status = "unknown"
    elif compatible:
        status = "compatible"
    else:
        status = "unknown"
    return {"field": field, "status": status, "compatible": compatible,
            "conflicts": conflicts, "missing": missing, "uncertain": uncertain,
            "not_comparable": not_comparable}


def compare_family(left, right):
    left_family, right_family = left.get("family"), right.get("family")
    missing = [side for side, value in (("left", left_family), ("right", right_family)) if not value]
    if left_family and right_family and left_family != right_family:
        status, conflicts = "conflict", [{"reason_code": "family.different_explicit_family",
                                           "left_value": left_family, "right_value": right_family}]
    elif left_family and left_family == right_family:
        status, conflicts = "compatible", []
    else:
        status, conflicts = "unknown", []
    return {"field": "family", "status": status, "compatible": left_family == right_family and bool(left_family),
            "left_value": left_family, "right_value": right_family, "conflicts": conflicts,
            "missing": missing,
            "left_evidence": _with_source(left["family_evidence"], left) if left.get("family_evidence") else None,
            "right_evidence": _with_source(right["family_evidence"], right) if right.get("family_evidence") else None}


def compare_attributes(left, right):
    """Compare supported evidence without making a pair outcome decision."""
    fields = {"family": compare_family(left, right)}
    fields.update({field: compare_field(field, left, right) for field in ATTRIBUTE_FIELDS})
    critical_conflicts = [conflict for field in CRITICAL_FIELDS
                          for conflict in fields[field]["conflicts"]]
    uncertain_fields = [name for name, result in fields.items()
                        if result["status"] in ("unknown", "uncertain")]
    return {"comparison_version": COMPARISON_VERSION, "fields": fields,
            "critical_conflicts": critical_conflicts,
            "identity_merge_blocked": bool(critical_conflicts),
            "uncertain_or_missing_fields": uncertain_fields,
            "review_required": bool(critical_conflicts or uncertain_fields)}


def _text_evidence(left, right):
    left_normalized = left["description_normalized"].casefold()
    right_normalized = right["description_normalized"].casefold()
    left_tokens, right_tokens = useful_tokens(left_normalized), useful_tokens(right_normalized)
    token_union = left_tokens | right_tokens
    left_grams, right_grams = character_ngrams(left_normalized), character_ngrams(right_normalized)
    gram_total = len(left_grams) + len(right_grams)
    return {
        "exact_normalized_text": left_normalized == right_normalized,
        "shared_useful_tokens": sorted(left_tokens & right_tokens),
        "token_jaccard": round(len(left_tokens & right_tokens) / len(token_union), 6) if token_union else 0.0,
        "character_trigram_dice": round(2 * len(left_grams & right_grams) / gram_total, 6) if gram_total else 0.0,
        "left_normalized_text": left["description_normalized"],
        "right_normalized_text": right["description_normalized"],
    }


def compare_pair(left, right, retrieval=None):
    """Return a proposed, reviewable outcome; never mutate or merge either record."""
    if left["source_record_id"] == right["source_record_id"]:
        raise ValueError("A source record cannot be compared with itself")
    comparison = compare_attributes(left, right)
    fields = comparison["fields"]
    text = _text_evidence(left, right)
    family_conflict = fields["family"]["status"] == "conflict"
    technical_support = [name for name in ATTRIBUTE_FIELDS
                         if fields[name]["status"] == "compatible"]
    family_support = fields["family"]["status"] == "compatible"
    strong_text = text["character_trigram_dice"] >= 0.78 or text["token_jaccard"] >= 0.65
    moderate_text = bool(text["shared_useful_tokens"]) and (
        text["character_trigram_dice"] >= 0.25 or text["token_jaccard"] >= 0.20)

    if comparison["critical_conflicts"]:
        label = "conflict"
        evidence_disposition = "supported_incompatibility"
        reasons = [item["reason_code"] for item in comparison["critical_conflicts"]]
        explanation = "Supported critical specifications conflict, so an identity merge is blocked."
    elif family_conflict:
        label = "no_match"
        evidence_disposition = "supported_incompatibility"
        reasons = ["family.different_explicit_family"]
        explanation = "The descriptions identify different item families; shared wording cannot support a match."
    elif text["exact_normalized_text"]:
        label = "exact_duplicate"
        evidence_disposition = "supported_duplicate_text"
        reasons = ["text.exact_normalized_description"]
        explanation = "The normalized descriptions are identical and no supported critical conflict was found."
    elif strong_text and (family_support or technical_support):
        label = "near_duplicate"
        evidence_disposition = "supported_near_duplicate"
        reasons = ["text.strong_variant"] + (["family.compatible"] if family_support else [])
        reasons += [f"{name}.compatible" for name in technical_support]
        explanation = "The wording is a strong variant and supported specifications do not conflict."
    elif family_support and moderate_text:
        label = "possible_functional_equivalent"
        evidence_disposition = "reviewer_equivalence_candidate"
        reasons = ["family.compatible", "text.partial_support", "review.qualified_engineer_required"]
        explanation = ("The same item family and partial wording support justify qualified review only; "
                       "engineering equivalence is not established.")
    else:
        label = "no_match"
        evidence_disposition = "insufficient_evidence"
        reasons = ["text.insufficient_material_support"]
        explanation = ("Available text and supported attributes are insufficient to establish either a material "
                       "relationship or a confirmed incompatibility; human review remains pending.")

    critical_unknown = [name for name in CRITICAL_FIELDS
                        if fields[name]["status"] in ("unknown", "uncertain")]
    review_required = (label in {"conflict", "possible_functional_equivalent"} or
                       evidence_disposition == "insufficient_evidence" or
                       (label in {"exact_duplicate", "near_duplicate"} and bool(critical_unknown)))
    identity_blocked = label in {"conflict", "no_match", "possible_functional_equivalent"}
    outcome = {"label": label, "status": "proposed_outcome",
               "evidence_disposition": evidence_disposition, "reason_codes": reasons,
               "explanation": explanation, "review_required": review_required,
               "qualified_reviewer_required": label == "possible_functional_equivalent",
               "identity_merge_blocked": identity_blocked,
               "critical_unknown_or_uncertain_fields": sorted(critical_unknown),
               "automatic_action": None}
    retrieval_block = None
    if retrieval is not None:
        if retrieval.get("candidate_source_record_id") != right["source_record_id"]:
            raise ValueError("Retrieval candidate ID does not match the right record")
        if retrieval.get("query_source_record_id") != left["source_record_id"]:
            raise ValueError("Retrieval query ID does not match the left record")
        retrieval_block = {key: retrieval.get(key) for key in
                           ("status", "retrieval_version", "rank", "retrieval_score", "reasons")}
    return {
        "comparison_version": COMPARISON_VERSION,
        "left": {"source_record_id": left["source_record_id"],
                 "source_organization": left["source_organization"],
                 "description_original": left["description_original"]},
        "right": {"source_record_id": right["source_record_id"],
                  "source_organization": right["source_organization"],
                  "description_original": right["description_original"]},
        "retrieval": retrieval_block,
        "supporting_text_evidence": text,
        "field_comparisons": fields,
        "missing_or_uncertain_attributes": comparison["uncertain_or_missing_fields"],
        "outcome": outcome,
    }
