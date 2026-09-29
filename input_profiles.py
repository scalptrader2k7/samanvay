"""Serializable mappings for the four inspected local inputs."""
from copy import deepcopy

from load_corpus import CORPUS_COLUMNS, IDENTIFIER_COLUMNS


PROFILES = {
    'corpus': {'mapping_id': 'raw-corpus-v0.1', 'columns': CORPUS_COLUMNS,
               'identifiers': list(IDENTIFIER_COLUMNS)},
    'candidates': {'mapping_id': 'material-candidates-v0.1', 'columns': {
        k: v for k, v in CORPUS_COLUMNS.items() if k not in ('source_system', 'source_section')},
        'identifiers': list(IDENTIFIER_COLUMNS)},
    'ntpc': {'mapping_id': 'raw-ntpc-v0.1', 'columns': {
        'description_original': 'item_text', 'uom_original': 'unit',
        'document_reference': 'doc_name', 'quantity_original': 'quantity'},
        'identifiers': ['nit_id', 'doc_name', 'line_no'],
        'organization_constant': {'value': 'NTPC Limited', 'evidence': 'SOURCES.md section 2.2'}},
    'iocl': {'mapping_id': 'raw-iocl-v0.1', 'columns': {
        'description_original': 'item_description', 'uom_original': 'unit',
        'source_section': 'section', 'document_reference': 'source_pdf',
        'quantity_original': 'quantity'}, 'identifiers': ['source_pdf', 'page', 'sl_no'],
        'organization_constant': {'value': 'Indian Oil Corporation Limited', 'evidence': 'SOURCES.md section 2.3'}},
}


def get_profile(name):
    return deepcopy(PROFILES[name])
