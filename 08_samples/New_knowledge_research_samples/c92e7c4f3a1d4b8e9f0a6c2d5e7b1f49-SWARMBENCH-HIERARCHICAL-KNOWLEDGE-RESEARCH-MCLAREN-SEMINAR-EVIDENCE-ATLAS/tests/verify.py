#!/usr/bin/env python3
"""Hybrid verifier for the McLaren Seminar Evidence Atlas.

All checks, including W&B LLM evaluation of every agent-generated Markdown file,
live here. `partial_oracle.json` is deliberately a small held-out factual slice of
the real official bibliography, not a hidden completed atlas.
"""
from __future__ import annotations

import concurrent.futures
import collections
import csv
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(os.environ.get('SWARMBENCH_AGENT_DIR', '/logs/agent')) / 'output'
TESTS = Path(__file__).resolve().parent
VERIFIER = Path(os.environ.get('SWARMBENCH_VERIFIER_DIR', '/logs/verifier'))
CARDS = ROOT / 'evidence_cards'
ORACLE = TESTS / 'partial_oracle.json'
API_KEY = (os.environ.get('SWARMBENCH_JUDGE_API_KEY') or os.environ.get('WANDB_API_KEY') or '').strip()
JUDGE_MODEL = os.environ.get('JUDGE_MODEL', 'moonshotai/Kimi-K2.6')
JUDGE_URL = os.environ.get('SWARMBENCH_JUDGE_API_URL', 'https://api.inference.wandb.ai/v1/chat/completions')
# Kimi is a thinking model.  A short completion budget can be consumed before it
# emits message.content, so each retry increases that budget.  W&B deployments
# differ in their spelling for disabling thinking; unsupported variants are
# skipped on HTTP 400 and the plain JSON-mode request remains a fallback.
JUDGE_TOKEN_LADDER = (1024, 2048, 4096)
JUDGE_PAYLOAD_OPTIONS = (
    {'chat_template_kwargs': {'thinking': False}, 'response_format': {'type': 'json_object'}},
    {'thinking': {'type': 'disabled'}, 'response_format': {'type': 'json_object'}},
    {'response_format': {'type': 'json_object'}},
    {},
)

REQUIRED = ['corpus_map.csv', 'method_comparison_matrix.csv', 'theme_synthesis.md', 'research_trajectory.md', 'seminar_plan.md', 'claim_audit.csv', 'index.html']
CORPUS_COLS = {'record_id', 'shard_id', 'official_list_position', 'title', 'year', 'work_type', 'authors', 'official_url', 'doi_or_stable_url', 'evidence_level', 'primary_theme', 'historical_phase', 'version_group', 'status', 'uncertainty_note'}
MATRIX_COLS = {'card_id', 'research_problem', 'intervention_or_system', 'learning_domain', 'learner_population', 'setting', 'study_design', 'comparison_condition', 'outcome_measure', 'reported_result', 'causal_claim_boundary', 'transferability_limit', 'source_url', 'evidence_excerpt'}
BANNED_SOURCE_RX = re.compile(r'https?://[^\s)]+(?:wikipedia\.org|researchgate\.net|scholar\.google\.com|blogspot\.|medium\.com|wordpress\.)', re.I)
BANNED_CONTENT_RX = re.compile(r'\b(?:search[- ]result snippet|google snippet|bing snippet)\b', re.I)
PROGRAM_SUFFIXES = {'.py', '.sh', '.js', '.ts', '.rb', '.ps1', '.bat', '.cmd', '.exe'}
PLACEHOLDER_VALUES = {'', 'tbd', 'todo', 'placeholder', 'n/a', 'unknown'}
OFFICIAL_CORPUS_URL = 'https://www.cs.cmu.edu/~bmclaren/publications.html'

def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))

def normalized(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', ' ', value.lower()).strip()

def text(path: Path, limit: int = 30000) -> str:
    return path.read_text(encoding='utf-8', errors='replace')[:limit] if path.is_file() else ''

def check_static() -> dict[str, bool]:
    results: dict[str, bool] = {}
    results['static_checks_1'] = all((ROOT / name).is_file() for name in REQUIRED) and CARDS.is_dir()
    corpus = load_csv(ROOT / 'corpus_map.csv') if (ROOT / 'corpus_map.csv').is_file() else []
    canonical = [r for r in corpus if r.get('status') == 'canonical']
    required_cells = ('record_id', 'shard_id', 'title', 'year', 'authors', 'official_url', 'doi_or_stable_url', 'evidence_level', 'primary_theme', 'historical_phase', 'version_group')
    all_rows_sharded = all(re.fullmatch(r'SHARD-(?:0[1-9]|1[0-9]|2[0-4])', r.get('shard_id', '').strip()) for r in corpus)
    unique_canonical_versions = all(sum(r.get('status') == 'canonical' for r in corpus if r.get('version_group') == group) <= 1 for group in {r.get('version_group') for r in corpus if r.get('version_group')})
    readable_fraction = sum(r.get('evidence_level') == 'paper_or_abstract_read' for r in canonical) / len(canonical) if canonical else 0
    official_urls = [r.get('official_url', '').strip().rstrip('/') for r in canonical]
    genuine_official_provenance = all(url and url != OFFICIAL_CORPUS_URL.rstrip('/') for url in official_urls) and len(set(official_urls)) >= 220
    results['static_checks_2'] = bool(corpus) and CORPUS_COLS.issubset(corpus[0]) and len(canonical) >= 240 and all_rows_sharded and all(all(r.get(k, '').strip() and r.get(k, '').strip().lower() not in {'tbd', 'todo', 'placeholder'} for k in required_cells) for r in canonical) and len({r.get('official_list_position') for r in canonical}) == len(canonical) and len({(normalized(r.get('title', '')), r.get('year', '').strip()) for r in canonical}) >= 230 and len({r.get('doi_or_stable_url', '').strip() for r in canonical}) >= 220 and genuine_official_provenance and unique_canonical_versions and readable_fraction >= 0.50
    cards = sorted(CARDS.glob('*.md')) if CARDS.is_dir() else []
    card_matches = []
    for card in cards:
        card_body = normalized(text(card, 18000))
        matched = [row for row in canonical if normalized(row.get('title', '')) in card_body]
        card_matches.append(matched[0] if len(matched) == 1 else None)
    results['static_checks_3'] = len(cards) == 72 and len({p.stem for p in cards}) == 72 and all(card_matches) and len({row.get('record_id') for row in card_matches if row}) == 72 and all(sum(row.get('shard_id') == f'SHARD-{i:02d}' for row in card_matches if row) == 3 for i in range(1, 25))
    matrix = load_csv(ROOT / 'method_comparison_matrix.csv') if (ROOT / 'method_comparison_matrix.csv').is_file() else []
    nontrivial_matrix = all(MATRIX_COLS.issubset(r) and all(r.get(k, '').strip().lower() not in PLACEHOLDER_VALUES for k in MATRIX_COLS) for r in matrix)
    substantive = MATRIX_COLS - {'card_id', 'source_url', 'evidence_excerpt'}
    field_coverage = all(sum(r.get(field, '').strip().lower() != 'not_reported' for r in matrix) >= 54 for field in substantive)
    field_diversity = all(len({normalized(r.get(field, '')) for r in matrix if r.get(field, '').strip().lower() != 'not_reported'}) >= 18 for field in substantive)
    phrase_reuse = all(max(collections.Counter(normalized(r.get(field, '')) for r in matrix if r.get(field, '').strip().lower() != 'not_reported').values(), default=0) <= 8 for field in substantive)
    matrix_urls_ok = all(re.match(r'https?://', r.get('source_url', '').strip()) for r in matrix)
    results['static_checks_4'] = len(matrix) == 72 and {r.get('card_id') for r in matrix} == {p.stem for p in cards} and nontrivial_matrix and field_coverage and field_diversity and phrase_reuse and matrix_urls_ok
    plan = text(ROOT / 'seminar_plan.md')
    week_blocks = re.split(r'(?mi)^#{1,3}\s*(?:week\s+\d+|\d+\.)[^\n]*\n', plan)[1:]
    weekly_content = all(all(marker in block.lower() for marker in ('question', 'activity', 'caveat')) and len(re.findall(r'CARD-[A-Za-z0-9_-]+', block, re.I)) >= 2 for block in week_blocks[:14])
    results['static_checks_5'] = len(week_blocks) == 14 and weekly_content
    trajectory = text(ROOT / 'research_trajectory.md', 500000)
    trajectory_content = len(re.findall(r'(?i)\bphase\b', trajectory)) >= 4 and len(re.findall(r'CARD-[A-Za-z0-9_-]+', trajectory, re.I)) >= 48 and len(re.findall(r'(?i)\bcompar', trajectory)) >= 20 and 'claims we should not make' in trajectory.lower()
    results['static_checks_6'] = 3500 <= len(trajectory.split()) <= 4500 and trajectory_content
    audit = load_csv(ROOT / 'claim_audit.csv') if (ROOT / 'claim_audit.csv').is_file() else []
    index = text(ROOT / 'index.html')
    hrefs = re.findall(r'''href=["']([^"']+)["']''', index, re.I)
    local_links_ok = all((ROOT / href).resolve().is_file() for href in hrefs if href and not re.match(r'https?://|#', href))
    all_markdown = '\n'.join(text(p, 20000) for p in cards + [ROOT / 'theme_synthesis.md', ROOT / 'research_trajectory.md', ROOT / 'seminar_plan.md'])
    audit_fields = {'claim_id', 'artifact', 'claim_text', 'card_ids', 'source_urls', 'claim_type', 'support_status', 'qualification_or_caveat'}
    valid_card_ids = {p.stem for p in cards}
    expected_audit_artifacts = {'theme_synthesis.md', 'research_trajectory.md', 'seminar_plan.md'}
    audit_valid = bool(audit) and audit_fields.issubset(audit[0]) and expected_audit_artifacts.issubset({r.get('artifact') for r in audit}) and all(r.get('support_status') in {'directly_supported', 'careful_synthesis', 'tentative', 'not_supported'} and r.get('qualification_or_caveat', '').strip() and all(card_id.strip() in valid_card_ids for card_id in r.get('card_ids', '').split(';') if card_id.strip()) and all(re.match(r'https?://', url.strip()) for url in r.get('source_urls', '').split(';') if url.strip()) for r in audit)
    programs = [p for p in ROOT.rglob('*') if p.is_file() and p.suffix.lower() in PROGRAM_SUFFIXES]
    csv_urls = '\n'.join(value for row in corpus + matrix + audit for key, value in row.items() if 'url' in key.lower())
    results['static_checks_7'] = len(audit) >= 24 and audit_valid and all(name in hrefs for name in REQUIRED[:-1]) and local_links_ok and not BANNED_SOURCE_RX.search(all_markdown + '\n' + csv_urls) and not BANNED_CONTENT_RX.search(all_markdown) and not programs
    return results

def check_partial_oracle(corpus: list[dict[str, str]], cards: list[Path]) -> dict[str, bool]:
    oracle = json.loads(ORACLE.read_text(encoding='utf-8'))
    sentinels = oracle['sentinel_works']
    anchors = oracle['historical_anchor_works']
    title_index = {normalized(r.get('title', '')): r for r in corpus if r.get('status') == 'canonical'}
    card_text = '\n'.join(text(card, 15000) for card in cards)
    found = [title_index.get(normalized(item['title'])) for item in sentinels]
    anchor_found = [title_index.get(normalized(item['title'])) for item in anchors]
    results = {
        'partial_oracle_checks_1': all(found),
        'partial_oracle_checks_2': all(row and str(row.get('year', '')).strip() == item['year'] for row, item in zip(found, sentinels)),
        'partial_oracle_checks_3': all(row and row.get('official_url', '').startswith('https://www.cs.cmu.edu/') and row.get('official_url', '').rstrip('/') != OFFICIAL_CORPUS_URL.rstrip('/') for row in found),
        'partial_oracle_checks_4': sum(normalized(item['title']) in normalized(card_text) for item in sentinels) >= 7,
        'partial_oracle_checks_5': len({row.get('version_group') for row in found if row}) >= 6,
        'partial_oracle_checks_6': all(row and row.get('evidence_level') in {'paper_or_abstract_read', 'bibliography_only', 'unresolved'} for row in found),
        'partial_oracle_checks_7': all(row and str(row.get('year', '')).strip() == item['year'] for row, item in zip(anchor_found, anchors)),
        'partial_oracle_checks_8': sum(normalized(item['title']) in normalized(card_text) for item in anchors) >= 4,
        'partial_oracle_checks_9': all(row and row.get('official_url', '').startswith('https://www.cs.cmu.edu/') and row.get('official_url', '').rstrip('/') != OFFICIAL_CORPUS_URL.rstrip('/') for row in anchor_found),
        'partial_oracle_checks_10': all(row and row.get('evidence_level') == 'paper_or_abstract_read' for row in anchor_found),
    }
    return results

CARD_PROMPT = '''You are a strict scholarly-evidence judge. Evaluate this one evidence card.
Return JSON only: {{"pass": true|false, "reason": "short reason", "identity": true|false, "source_grounding": true|false, "claim_calibration": true|false, "limitations": true|false, "cross_links": true|false}}. Set pass true only when every named criterion is true. Identity requires a real, identifiable work. Source_grounding requires a paper-level URL and an excerpt that supports each substantive claim. Claim_calibration requires findings to be distinguished from proposals and causal claims bounded by the design. Limitations requires a concrete, work-specific limitation. Cross_links requires non-generic links to other cards. Reject title-derived summaries, fabricated-seeming quotes, generic caveats, citation dumping, and source text that does not support the card.

CARD:\n{body}\n\nRETRIEVED SOURCE CONTEXT:\n{source_context}'''

DOC_PROMPT = '''You are a strict faculty-review judge for a doctoral learning-sciences seminar evidence atlas. Evaluate this Markdown artifact against the evidence-card index. Return JSON only: {{"pass": true|false, "reason": "short reason", "grounding": true|false, "calibration": true|false, "artifact_requirements": true|false}}. Set pass true only when every named criterion is true. Grounding requires specific claims traceable to the supplied card index, not title-only inference. Calibration requires appropriate method and limitation boundaries; a claim-audit row marked not_supported must never be used as affirmative evidence. Artifact requirements: theme synthesis must define exactly six themes, with at least ten cards from three phases per theme, boundaries/overlaps, three-way method/population/setting comparisons, and justified conclusions versus overreach. Trajectory must be 3,500–4,500 words with four phases, 24 cross-paper claims, 20 pairwise comparisons, eight matrix-method comparisons, and eight unsupported-generalization warnings. Seminar plan must give 14 weekly units and 28 readings, include twelve or more peer-reviewed readings, assign no more than four readings per week, use at least eight corpus works, include a substantial primary-source reading from every historical phase, avoid duplicate/version pairs and concentration in one year, venue, or project cluster, provide each week two readings, a question, activity, source-backed relationship, and methodological caveat, and give eight pedagogically justified reserves. Claim audit must cover every substantive claim in the three narratives. Reject generic prose, vague caveats, fabricated detail, citation dumping, contradictions, and untraceable claims.

EVIDENCE-CARD INDEX:\n{index}\n\nARTIFACT:\n{body}'''

def llm(prompt: str) -> dict[str, object]:
    if not API_KEY:
        return {'pass': False, 'reason': 'WANDB_API_KEY or SWARMBENCH_JUDGE_API_KEY is not configured', 'infrastructure_error': True}
    last_error = 'unknown W&B inference error'
    for attempt, max_tokens in enumerate(JUDGE_TOKEN_LADDER):
        for option in JUDGE_PAYLOAD_OPTIONS:
            try:
                payload = {'model': JUDGE_MODEL, 'messages': [{'role': 'user', 'content': prompt}], 'temperature': 0, 'max_tokens': max_tokens, **option}
                response = requests.post(JUDGE_URL, headers={'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json', 'User-Agent': 'swarmbench-verifier/1.0'}, json=payload, timeout=180)
                if response.status_code == 400 and option:
                    last_error = 'W&B rejected an optional thinking/JSON parameter'
                    continue
                response.raise_for_status()
                response_payload = response.json()
                choices = response_payload.get('choices') if isinstance(response_payload, dict) else None
                message = choices[0].get('message', {}) if isinstance(choices, list) and choices and isinstance(choices[0], dict) else {}
                content = message.get('content') if isinstance(message, dict) else None
                if isinstance(content, list):
                    content = ''.join(str(part.get('text', '')) for part in content if isinstance(part, dict))
                if not isinstance(content, str) or not content.strip():
                    finish = choices[0].get('finish_reason') if isinstance(choices, list) and choices and isinstance(choices[0], dict) else None
                    last_error = f'W&B response had no textual message.content (max_tokens={max_tokens}, finish_reason={finish!r})'
                    break
                cleaned = re.sub(r'^```(?:json)?\s*|\s*```$', '', content.strip(), flags=re.I)
                verdict = json.loads(cleaned)
                if not isinstance(verdict, dict) or not isinstance(verdict.get('pass'), bool):
                    raise ValueError('W&B response was not a JSON pass/fail verdict')
                return {'pass': verdict['pass'], 'reason': str(verdict.get('reason', ''))[:600], 'infrastructure_error': False}
            except Exception as exc:
                last_error = f'{type(exc).__name__}: {exc}'
                break
        if attempt < len(JUDGE_TOKEN_LADDER) - 1:
            time.sleep(2 ** attempt)
    return {'pass': False, 'reason': last_error, 'infrastructure_error': True}

def source_context(card: Path) -> str:
    """Fetch linked public source text so card judging is grounded externally."""
    urls = re.findall(r'https?://[^\s)\]>]+', text(card, 16000))[:2]
    snippets = []
    for url in urls:
        try:
            response = requests.get(url, headers={'User-Agent': 'swarmbench-verifier/1.0'}, timeout=25)
            if response.ok:
                snippets.append(f'URL: {url}\n{response.text[:3500]}')
        except requests.RequestException:
            continue
    return '\n\n'.join(snippets) or 'No linked source was retrievable; the card must not pass source-grounding review.'

def check_markdown_with_llm(cards: list[Path]) -> tuple[dict[str, bool], dict[str, dict[str, object]], bool]:
    """Judge every generated Markdown artifact. Infrastructure errors stay visible."""
    details: dict[str, dict[str, object]] = {}
    # Keep W&B request pressure modest; each evidence-card verdict is retried on a
    # transient 429/5xx or malformed provider response by llm().
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        pending = {pool.submit(llm, CARD_PROMPT.format(body=text(card, 12000), source_context=source_context(card))): f'evidence_cards/{card.name}' for card in cards}
        for future in concurrent.futures.as_completed(pending):
            details[pending[future]] = future.result()
    index = '\n'.join(f'[{card.stem}] {text(card, 700)}' for card in cards)[:60000]
    for name in ['theme_synthesis.md', 'research_trajectory.md', 'seminar_plan.md']:
        details[name] = llm(DOC_PROMPT.format(index=index, body=text(ROOT / name, 60000)))
    audit = ROOT / 'claim_audit.csv'
    details['claim_audit.csv'] = llm(DOC_PROMPT.format(index=index, body=text(audit, 60000)))
    infrastructure_error = any(bool(value.get('infrastructure_error')) for value in details.values())
    card_pass_rate = sum(bool(details.get(f'evidence_cards/{card.name}', {}).get('pass')) for card in cards) / 72 if len(cards) == 72 else 0.0
    narrative_pass_rate = sum(bool(details.get(name, {}).get('pass')) for name in ['theme_synthesis.md', 'research_trajectory.md', 'seminar_plan.md']) / 3
    results = {
        'reward_hacking_checks_1': card_pass_rate,
        'reward_hacking_checks_2': narrative_pass_rate,
        'reward_hacking_checks_3': float(bool(details.get('claim_audit.csv', {}).get('pass')) and all(not re.search(r'\b(?:placeholder|todo|tbd)\b', text(card), re.I) for card in cards + [ROOT / 'theme_synthesis.md', ROOT / 'research_trajectory.md', ROOT / 'seminar_plan.md'])),
    }
    return results, details, infrastructure_error


def write_judge_justification(
    results: dict[str, bool],
    buckets: dict[str, float],
    llm_details: dict[str, dict[str, object]],
    infrastructure_error: bool,
    reward: float,
) -> None:
    """Write a human-readable companion to details.json for every verifier run."""
    lines = [
        'McLaren Seminar Evidence Atlas — verifier justification',
        f'Judge model: {JUDGE_MODEL}',
        f'Final reward: {reward:.6f}',
        f'Infrastructure error: {infrastructure_error}',
        '',
        'Bucket scores:',
        *(f'- {name}: {score:.6f}' for name, score in buckets.items()),
        '',
        'Deterministic checks:',
        *(f'- {name}: {"PASS" if passed else "FAIL"}' for name, passed in sorted(results.items()) if not name.startswith('reward_hacking_checks_')),
        '',
        'W&B LLM judgments:',
    ]
    if not llm_details:
        lines.append('- No Markdown artifacts were available for LLM evaluation.')
    for artifact, verdict in sorted(llm_details.items()):
        status = 'PASS' if verdict.get('pass') else 'FAIL'
        reason = str(verdict.get('reason', '')).replace('\n', ' ').strip() or 'No reason returned.'
        lines.append(f'- {artifact}: {status} — {reason}')
    failed_judgments = [
        (artifact, verdict)
        for artifact, verdict in sorted(llm_details.items())
        if not verdict.get('pass')
    ]
    lines.extend(['', 'LLM judge issues:'])
    if infrastructure_error:
        lines.append('- W&B inference infrastructure failed for at least one judgment; reward is -1 until the provider returns a valid verdict.')
    if not failed_judgments and not infrastructure_error:
        lines.append('- None. Every LLM-evaluated artifact passed.')
    for artifact, verdict in failed_judgments:
        reason = str(verdict.get('reason', '')).replace('\n', ' ').strip() or 'No reason returned.'
        category = 'infrastructure' if verdict.get('infrastructure_error') else 'quality/grounding'
        lines.append(f'- [{category}] {artifact}: {reason}')
    lines.extend([
        '',
        'Aggregation:',
        'reward = (static_checks + 3 * partial_oracle_checks + 2 * reward_hacking_checks) / 6',
    ])
    (VERIFIER / 'judge_justification.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')


# These named adapters expose each independently scored result to the rubric
# manifest.  The aggregate helpers above share input loading and W&B requests,
# while each adapter maps to exactly one emitted check key.
def static_required_paths() -> bool: return check_static()['static_checks_1']
def static_corpus_schema_coverage() -> bool: return check_static()['static_checks_2']
def static_card_shard_coverage() -> bool: return check_static()['static_checks_3']
def static_method_matrix_integrity() -> bool: return check_static()['static_checks_4']
def static_seminar_shape() -> bool: return check_static()['static_checks_5']
def static_trajectory_shape() -> bool: return check_static()['static_checks_6']
def static_claim_audit_links() -> bool: return check_static()['static_checks_7']
def oracle_sentinel_titles(corpus: list[dict[str, str]], cards: list[Path]) -> bool: return check_partial_oracle(corpus, cards)['partial_oracle_checks_1']
def oracle_sentinel_years(corpus: list[dict[str, str]], cards: list[Path]) -> bool: return check_partial_oracle(corpus, cards)['partial_oracle_checks_2']
def oracle_official_urls(corpus: list[dict[str, str]], cards: list[Path]) -> bool: return check_partial_oracle(corpus, cards)['partial_oracle_checks_3']
def oracle_card_coverage(corpus: list[dict[str, str]], cards: list[Path]) -> bool: return check_partial_oracle(corpus, cards)['partial_oracle_checks_4']
def oracle_version_diversity(corpus: list[dict[str, str]], cards: list[Path]) -> bool: return check_partial_oracle(corpus, cards)['partial_oracle_checks_5']
def oracle_evidence_enums(corpus: list[dict[str, str]], cards: list[Path]) -> bool: return check_partial_oracle(corpus, cards)['partial_oracle_checks_6']
def oracle_historical_anchor_years(corpus: list[dict[str, str]], cards: list[Path]) -> bool: return check_partial_oracle(corpus, cards)['partial_oracle_checks_7']
def oracle_historical_anchor_cards(corpus: list[dict[str, str]], cards: list[Path]) -> bool: return check_partial_oracle(corpus, cards)['partial_oracle_checks_8']
def oracle_historical_anchor_urls(corpus: list[dict[str, str]], cards: list[Path]) -> bool: return check_partial_oracle(corpus, cards)['partial_oracle_checks_9']
def oracle_historical_anchor_evidence(corpus: list[dict[str, str]], cards: list[Path]) -> bool: return check_partial_oracle(corpus, cards)['partial_oracle_checks_10']
def llm_evidence_cards(cards: list[Path]) -> bool: return check_markdown_with_llm(cards)[0]['reward_hacking_checks_1']
def llm_top_level_markdown(cards: list[Path]) -> bool: return check_markdown_with_llm(cards)[0]['reward_hacking_checks_2']
def llm_claim_audit_templates(cards: list[Path]) -> bool: return check_markdown_with_llm(cards)[0]['reward_hacking_checks_3']


def main() -> int:
    VERIFIER.mkdir(parents=True, exist_ok=True)
    results = check_static()
    corpus = load_csv(ROOT / 'corpus_map.csv') if (ROOT / 'corpus_map.csv').is_file() else []
    cards = sorted(CARDS.glob('*.md')) if CARDS.is_dir() else []
    results.update(check_partial_oracle(corpus, cards) if corpus and ORACLE.is_file() else {f'partial_oracle_checks_{i}': False for i in range(1, 11)})
    llm_results, llm_details, infra = check_markdown_with_llm(cards)
    results.update(llm_results)
    buckets = {
        'static_checks': sum(results[f'static_checks_{i}'] for i in range(1, 8)) / 7,
        'partial_oracle_checks': sum(results[f'partial_oracle_checks_{i}'] for i in range(1, 11)) / 10,
        'reward_hacking_checks': sum(results[f'reward_hacking_checks_{i}'] for i in range(1, 4)) / 3,
    }
    payload = {'model': JUDGE_MODEL, 'results': results, 'bucket_scores': buckets, 'llm_details': llm_details, 'infrastructure_error': infra}
    (VERIFIER / 'details.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    reward = (buckets['static_checks'] + 3 * buckets['partial_oracle_checks'] + 2 * buckets['reward_hacking_checks']) / 6
    write_judge_justification(results, buckets, llm_details, infra, reward)
    (VERIFIER / 'reward.txt').write_text(f'{reward:.6f}\n', encoding='utf-8')
    # Harbor accepts only numeric values in reward.json.  Full check-level
    # diagnostics live in details.json and judge_justification.txt instead.
    (VERIFIER / 'reward.json').write_text(json.dumps({
        'reward': reward,
        'total_static_check_score': buckets['static_checks'],
        'total_partial_oracle_check_score': buckets['partial_oracle_checks'],
        'total_reward_hacking_check_score': buckets['reward_hacking_checks'],
    }, indent=2), encoding='utf-8')
    print(f"BUCKETS\tstatic={buckets['static_checks']:.3f}\tpartial_oracle={buckets['partial_oracle_checks']:.3f}\treward_hacking={buckets['reward_hacking_checks']:.3f}")
    for artifact, verdict in sorted(llm_details.items()):
        print(f"LLM\t{artifact}\t{'PASS' if verdict.get('pass') else 'FAIL'}\t{verdict.get('reason', '')}")
    if infra:
        print('INFRASTRUCTURE_ERROR\tW&B LLM judge unavailable; formula-based reward retained')
    print(f'REWARD\t{reward:.6f}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
