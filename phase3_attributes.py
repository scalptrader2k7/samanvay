"""Conservative, evidence-bearing derivations from original material text."""
import re
import unicodedata

NORMALIZATION_VERSION = "description-normalization-v0.1"
PARSER_VERSION = "technical-attributes-v0.1"

FAMILY_RULES = {
    "pipe": re.compile(r"\b(?:pipe|pipes|piping|tube|tubes|tubing|casing|casings)\b", re.I),
    "valve": re.compile(r"\b(?:valve|valves|vlv|vlvs)\b", re.I),
    "cable": re.compile(r"\b(?:cable|cables)\b", re.I),
    "pump": re.compile(r"\b(?:pump|pumps|pumping|pmp)\b", re.I),
}

ATTRIBUTE_RULES = {
    "size_dimension": (
        ("size.metric", re.compile(r"\b\d+(?:\.\d+)?\s*(?:sq\s*mm|sqmm|mm2|mm²|mm|cm|micron)\b", re.I)),
        ("size.nominal", re.compile(r"\b(?:DN\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?\s*NB)\b", re.I)),
        ("size.inch", re.compile(r"\b\d+(?:\.\d+)?(?:\s+\d+/\d+|/\d+)?\s*(?:\"|''|inch(?:es)?)", re.I)),
        ("size.dimension", re.compile(r"\b\d+(?:\.\d+)?\s*[xX]\s*\d+(?:\.\d+)?(?:\s*[xX]\s*\d+(?:\.\d+)?)?\b")),
        ("size.schedule", re.compile(r"\b(?:SCH(?:EDULE)?\s*\d+[A-Z]?|\d+S)\b", re.I)),
    ),
    "material_grade": (
        ("grade.stainless", re.compile(r"\b(?:SS\s*-?\s*3\d{2}[A-Z]*|TP\s*-?\s*3\d{2}[A-Z]*)\b", re.I)),
        ("grade.designation", re.compile(r"\b(?:FE\s*-?\s*\d{3}|A\d{2,4}\s*-\s*TP\s*\d{3}[A-Z]*|A\d{2,4}\s*GR\s*\d+[A-Z]*)\b", re.I)),
        ("grade.explicit", re.compile(r"\bGRADE\s*[:=-]?\s*[A-Z0-9][A-Z0-9._/-]*\b", re.I)),
        ("material.controlled", re.compile(r"\b(?:CS|GLV|CORTEN|DUPLEX)\b", re.I)),
    ),
    "standard": (
        ("standard.api", re.compile(r"\bAPI\s*(?:SPEC\.?|STD\.?)?\s*\d+[A-Z]?(?:\.\d+)?\b", re.I)),
        ("standard.astm", re.compile(r"\bASTM\s*[A-Z]\s*\d+[A-Z]?\b", re.I)),
        ("standard.is", re.compile(r"\bIS\s*[: -]?\s*\d+(?:-\d+)?\b", re.I)),
        ("standard.asme", re.compile(r"\bASME\s*[A-Z]?\s*\d+(?:\.\d+)*\b", re.I)),
        ("standard.other", re.compile(r"\b(?:IEC|ISO|DIN|ANSI|BS|EN)\s*[: -]?\s*\d+(?:[.-]\d+)*\b", re.I)),
    ),
    "pressure": (
        ("pressure.class", re.compile(r"\b(?:CLASS|CL\.?)\s*[>:=-]?\s*\d+\b", re.I)),
        ("pressure.class.reversed", re.compile(r"\b\d+\s*CLASS\b", re.I)),
        ("pressure.pn", re.compile(r"\bPN\s*[:=-]?\s*\d+\b", re.I)),
        ("pressure.unit", re.compile(r"\b\d[\d,]*(?:\.\d+)?\s*(?:PSI|BAR)\b", re.I)),
        ("pressure.rating", re.compile(r"\bPRESSURE\s+RATING\s*[:=-]?\s*\d[\d,]*(?:\.\d+)?\s*(?:PSI|BAR)\b", re.I)),
    ),
    "voltage": (
        ("voltage.explicit", re.compile(r"\b\d+(?:\.\d+)?\s*(?:KV|VOLTS?|V)\b", re.I)),
    ),
    "model_part": (
        ("model.explicit", re.compile(r"\bMODEL\s*[:#=-]?\s*[A-Z0-9][A-Z0-9._/-]*(?:\s+[A-Z0-9][A-Z0-9._/-]*){0,4}", re.I)),
        ("part.explicit", re.compile(r"\b(?:PART\s*(?:NO\.?|NUMBER)|P/N)\s*[:#=-]?\s*[A-Z0-9][A-Z0-9._/-]*", re.I)),
    ),
}


def normalize_description(value):
    """Normalize presentation conservatively; source text remains separately intact."""
    if not isinstance(value, str):
        raise TypeError("description must be text")
    text = unicodedata.normalize("NFKC", value).replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s*,\s*", ", ", text)
    text = re.sub(r"\s*:\s*", ": ", text)
    text = re.sub(r"\b(\d+(?:\.\d+)?)\s*[xX]\s*(?=\d)", r"\1 x ", text)
    return text


def _evidence(match, rule_id, normalized=None):
    raw = match.group(0)
    return {"value_raw": raw, "value_normalized": normalized or raw.upper(),
            "start": match.start(), "end": match.end(), "rule_id": rule_id}


def extract_family(description):
    hits = []
    for family, rule in FAMILY_RULES.items():
        matches = list(rule.finditer(description))
        if matches:
            hits.append((family, _evidence(matches[0], f"family.{family}.explicit", family)))
    if len(hits) == 1:
        return hits[0][0], hits[0][1], []
    if len(hits) > 1:
        return None, None, [{"reason": "ambiguous_family", "families": [h[0] for h in hits],
                             "evidence": [h[1] for h in hits]}]
    return None, None, []


def _normalize_attribute(kind, raw):
    value = re.sub(r"\s+", " ", raw.strip()).upper()
    value = re.sub(r"\s*([:=-])\s*", r"\1", value)
    return value


def extract_attributes(description):
    attributes = {key: [] for key in ATTRIBUTE_RULES}
    for kind, rules in ATTRIBUTE_RULES.items():
        seen = set()
        for rule_id, pattern in rules:
            for match in pattern.finditer(description):
                key = (match.start(), match.end(), match.group(0).casefold())
                if key in seen:
                    continue
                seen.add(key)
                attributes[kind].append(_evidence(
                    match, rule_id, _normalize_attribute(kind, match.group(0))))
        attributes[kind].sort(key=lambda item: (item["start"], item["end"], item["rule_id"]))
    return attributes


def derive_description(record):
    """Return a new enriched dictionary; never mutate the Phase 2 record."""
    description = record.get("description_original")
    if not isinstance(description, str):
        raise ValueError("description_original must be source text")
    family, evidence, issues = extract_family(description)
    result = dict(record)
    result.update({"normalization_version": NORMALIZATION_VERSION,
                   "description_normalized": normalize_description(description),
                   "family": family, "family_evidence": evidence,
                   "attributes": extract_attributes(description),
                   "derivation_issues": issues, "attribute_parser_version": PARSER_VERSION})
    return result


def assert_evidence_integrity(record):
    evidence = ([record["family_evidence"]] if record.get("family_evidence") else [])
    evidence += [item for values in record.get("attributes", {}).values() for item in values]
    for issue in record.get("derivation_issues", []):
        evidence += issue.get("evidence", [])
    for item in evidence:
        if record["description_original"][item["start"]:item["end"]] != item["value_raw"]:
            raise ValueError("Evidence span does not reproduce source text")
