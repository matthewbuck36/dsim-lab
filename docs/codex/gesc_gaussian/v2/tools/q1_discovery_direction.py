#!/usr/bin/env python3
"""Freeze or execute the finite discovery-only direction diagnostic.

Numerical work stays in the existing bag analyzer. The evaluate command must
be called once under an external timeout300s after the release checkpoint.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analysis
from ros_esc.plotting_scripts.v2_enclosure import atomic_exclusive_json
from q1_environment import installed_entry_points, selected_environment


REPOSITORY = Path('/home/mattb/dsim-lab')
EXPERIMENTS = Path('/home/mattb/Experiments/GESC-Gaussian/v2')
ORIGINAL = EXPERIMENTS / 'qualification/q1_primary_shadow_v1_recovery4'
OUTPUT = EXPERIMENTS / 'qualification/q1_discovery_direction_diagnostic_v1'
CHECKPOINT = EXPERIMENTS / 'checkpoints/q1_closed_v1/manifest.json'
OWNER = REPOSITORY / 'ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py'
PLAN = REPOSITORY / 'docs/codex/gesc_gaussian/v2/q1_discovery_direction_plan.md'
TEST = REPOSITORY / 'ros2_ws/src/ros_esc/test/test_q1_discovery_direction_diagnostic.py'
HISTORICAL = {
    ORIGINAL / 'preflight/contract.json':
        '8cd4db25ef3c70528df3b52066af18429cf554fe4aabb0eb370bf08c55619c64',
    ORIGINAL / 'study_closed.json':
        '090a5b11c803cb0bd0b69b740f02630dacc19f9b84af3172687ba6cf978f61b7',
    ORIGINAL / 'analysis/discovery_targets/targets.json':
        'b5d84cf2bb4f8900a940389ec16e5aa2608cbd76222907cdfeecb9a64cc4b1aa',
    CHECKPOINT: '78659061686d43c75217ba1ade254ead9b0474cccbab681cc5c59e8741f6dd7b',
}

OBSERVED_OUTPUT = EXPERIMENTS / 'qualification/q1_observed_phase_direction_diagnostic_v1'
OBSERVED_CHECKPOINT = EXPERIMENTS / 'checkpoints/q1_discovery_direction_closed_v1/manifest.json'
NUMERIC_OWNER = OWNER.with_name('v2_direction_reference.py')
OBSERVED_NEW_SOURCES = tuple(REPOSITORY / name for name in (
    'docs/codex/gesc_gaussian/v2/q1_observed_phase_reference_plan.md',
    'docs/codex/gesc_gaussian/v2/q1_observed_phase_reference_design.md',
    'ros2_ws/src/ros_esc/test/test_v2_observed_phase_reference.py',
    'ros2_ws/src/ros_esc/test/test_q1_observed_phase_diagnostic.py'))
OBSERVED_HISTORICAL = {
    **HISTORICAL,
    OUTPUT / 'preflight/contract.json':
        '2957ddfedf24b6c41df87f781df9e02958a5514291edac76b5d4b2179923fcd7',
    OUTPUT / 'diagnostic_closed.json':
        '91188431df0160ca89da42c91d2785f7ff05cead0184cdeda265cbb787f913cc',
    OBSERVED_CHECKPOINT:
        '6eb47b32197fa21c5800a49332a47f42783d240203468e2f94e5a2b3f7b17e4c',
    OUTPUT / 'diagnostics/cycle_confidence_v1/result.json':
        '4a2c39e84c1c6ada74b5b4cc193af83f928b9f49e8ea12be07f4e77a32293edf',
    OUTPUT / 'diagnostics/cycle_confidence_v1/manifest.json':
        '58581ea042cd37e91eefed15bb349fe15cb967d0e16387a8a442225192227b6f',
}


def receipt(path):
    path = Path(path).resolve()
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def checked(reference):
    path = Path(reference['path'])
    if receipt(path)['sha256'] != reference['sha256']:
        raise ValueError(f'Diagnostic receipt changed: {path}')
    return path


def freeze():
    """Create an exclusive prospective contract without any field evaluation."""
    branch = subprocess.check_output(
        ['git', '-C', str(REPOSITORY), 'branch', '--show-current'], text=True).strip()
    if branch != 'feature/gesc-gaussian-robustness-v2':
        raise ValueError('Discovery diagnostic requires the V2 checkout')
    contract_path = OUTPUT / 'preflight/contract.json'
    if contract_path.exists() or (OUTPUT / 'analysis').exists():
        raise FileExistsError('This fixed diagnostic contract or result already exists')
    for path, digest in HISTORICAL.items():
        checked({'path': str(path), 'sha256': digest})
    old_path = ORIGINAL / 'preflight/contract.json'
    old = json.loads(old_path.read_text())
    old_sources = {item['path']: item for item in old['source_files']}
    if len(old_sources) != len(old['source_files']):
        raise ValueError('Original source population contains duplicates')
    for path, item in old_sources.items():
        if Path(path) != OWNER:
            checked(item)
    closed_path = ORIGINAL / 'study_closed.json'
    closed = json.loads(closed_path.read_text())
    if (closed['status'] != 'CLOSED_EVIDENCE_UNAVAILABLE'
            or closed['scientific_confirmation'] != 'SEALED_NOT_OPENED'):
        raise ValueError('Original Q1 scientific boundary differs')
    targets_path = ORIGINAL / 'analysis/discovery_targets/targets.json'
    targets = json.loads(targets_path.read_text())
    checkpoint = json.loads(CHECKPOINT.read_text())
    for item in checkpoint['artifacts']:
        checked(item)
    old_digest = old_sources[str(OWNER)]['sha256']
    relative_owner = str(OWNER.relative_to(REPOSITORY))
    entry = next(item for item in checkpoint['files'] if item['path'] == relative_owner)
    if entry['sha256'] != old_digest:
        raise ValueError('Closed checkpoint does not bind the original analyzer')
    archive_ref = next(item for item in checkpoint['artifacts']
                       if Path(item['path']).name == 'source_and_evidence.tar.gz')
    with tarfile.open(checked(archive_ref)) as archive:
        original_source = archive.extractfile(relative_owner).read()
    if hashlib.sha256(original_source).hexdigest() != old_digest:
        raise ValueError('Archived analyzer differs from the original receipt')
    current_sources = {path: receipt(Path(path)) for path in old_sources}
    for path in (Path(__file__).resolve(), PLAN, TEST):
        current_sources[str(path)] = receipt(path)
    new_digest = current_sources[str(OWNER)]['sha256']
    if new_digest == old_digest:
        raise ValueError('Diagnostic analytical extension has not been implemented')
    snapshot = OUTPUT / 'preflight/original_analyzer.py'
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    if snapshot.exists():
        if snapshot.read_bytes() != original_source:
            raise ValueError('Existing original-source snapshot differs')
    else:
        with snapshot.open('xb') as stream:
            stream.write(original_source)
    document = {
        'version': 'q1-discovery-direction-diagnostic-v1',
        'original_contract': receipt(old_path),
        'study_closed': receipt(closed_path),
        'checkpoint': receipt(CHECKPOINT),
        'old_analyzer_snapshot': receipt(snapshot),
        'frozen_targets': receipt(targets_path),
        'analyzer_transition': {'path': str(OWNER), 'old_sha256': old_digest,
                                'new_sha256': new_digest},
        'current_source_files': [current_sources[path] for path in sorted(current_sources)],
        'input_traces': [{'path': item['path'], 'sha256': item['sha256']}
                         for item in targets['input_traces']],
        'partition': 'discovery', 'seeds': [26090911, 26090912],
        'target_numbers': list(range(1, 13)), 'fixed_anchor_count': 24,
        'job_timeout_sec': 300, 'reference': old['reference'],
    }
    atomic_exclusive_json(contract_path, document)
    # This validates provenance/inputs only; it constructs no model or output job.
    analysis._q1_discovery_direction_contract(
        receipt(contract_path), receipt(old_path), [receipt(targets_path)])
    binding = {'status': 'PREFLIGHT_VALID', 'contract': receipt(contract_path),
               'environment': selected_environment(),
               'installed_entry_points': installed_entry_points(),
               'field_evaluated': False, 'confirmation_opened': False,
               'pilot_released': False}
    atomic_exclusive_json(OUTPUT / 'preflight/installed_preflight.json', binding)
    return {'status': binding['status'], 'contract': binding['contract'],
            'source_files': len(current_sources), 'fixed_anchor_count': 24}


def evaluate():
    """Dispatch the existing owner after exact release/source checks."""
    contract_path = OUTPUT / 'preflight/contract.json'
    release = json.loads((OUTPUT / 'preflight/dispatch_release.json').read_text())
    if (release.get('status') != 'RELEASED'
            or not release.get('validation_evidence')
            or release['contract'] != receipt(contract_path)
            or release['environment'] != selected_environment()
            or release['installed_entry_points'] != installed_entry_points()
            or release['job_timeout_sec'] != 300):
        raise ValueError('Diagnostic release differs from this environment or contract')
    checked(release['checkpoint'])
    for reference in release['validation_evidence']:
        checked(reference)
    document = json.loads(contract_path.read_text())
    result = analysis.evaluate_q1_direction_references(
        [document['frozen_targets']['path']], OUTPUT / 'analysis',
        contract_path=document['original_contract']['path'],
        diagnostic_contract_path=contract_path)
    return {'status': result['status'], 'version': result['version'],
            'qualification_status': result['qualification_status'],
            'fixed_anchor_count': result['all']['fixed_anchor_count']}


def _observed_phase_source_transition():
    """Bind the completed diagnostic and snapshot the three declared owners.

    This only hashes source/evidence and reads the closed source archive. It
    never constructs a field model or follows confirmation recording receipts.
    """
    branch = subprocess.check_output(
        ['git', '-C', str(REPOSITORY), 'branch', '--show-current'], text=True).strip()
    if branch != 'feature/gesc-gaussian-robustness-v2':
        raise ValueError('Observed-phase diagnostic requires the V2 checkout')
    contract_path = OBSERVED_OUTPUT / 'preflight/contract.json'
    if contract_path.exists() or (OBSERVED_OUTPUT / 'analysis').exists():
        raise FileExistsError('This fixed observed-phase contract or result already exists')
    for path, digest in OBSERVED_HISTORICAL.items():
        checked({'path': str(path), 'sha256': digest})
    prior = json.loads((OUTPUT / 'preflight/contract.json').read_text())
    old_sources = {item['path']: item for item in prior['current_source_files']}
    if len(old_sources) != len(prior['current_source_files']):
        raise ValueError('Prior diagnostic source population contains duplicates')
    owners = (OWNER, NUMERIC_OWNER, Path(__file__).resolve())
    for path, item in old_sources.items():
        if Path(path) not in owners:
            checked(item)
    checkpoint = json.loads(OBSERVED_CHECKPOINT.read_text())
    for item in checkpoint['artifacts']:
        checked(item)
    entries = {item['path']: item for item in checkpoint['files']}
    archive_ref = next(item for item in checkpoint['artifacts']
                       if Path(item['path']).name == 'source_and_evidence.tar.gz')
    snapshots = []
    with tarfile.open(checked(archive_ref)) as archive:
        for owner in owners:
            relative = str(owner.relative_to(REPOSITORY))
            digest = old_sources[str(owner)]['sha256']
            if entries[relative]['sha256'] != digest:
                raise ValueError('Closed checkpoint differs from prior source: ' + relative)
            source = archive.extractfile(relative).read()
            if hashlib.sha256(source).hexdigest() != digest:
                raise ValueError('Archived source differs from prior receipt: ' + relative)
            current = receipt(owner)
            if current['sha256'] == digest:
                raise ValueError('Declared observed-phase transition is unimplemented: ' + relative)
            snapshot = OBSERVED_OUTPUT / 'preflight/previous_sources' / relative
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            if snapshot.exists():
                if snapshot.read_bytes() != source:
                    raise ValueError('Existing prior-source snapshot differs: ' + relative)
            else:
                with snapshot.open('xb') as stream:
                    stream.write(source)
            snapshots.append({'path': str(owner), 'old_sha256': digest,
                              'new_sha256': current['sha256'],
                              'old_snapshot': receipt(snapshot)})
    current_sources = {path: receipt(Path(path)) for path in old_sources}
    for path in OBSERVED_NEW_SOURCES:
        current_sources[str(path)] = receipt(path)
    return prior, snapshots, [current_sources[path] for path in sorted(current_sources)]


def freeze_observed_phase():
    """Freeze the separately declared measured-phase method and sensitivity."""
    prior, transitions, sources = _observed_phase_source_transition()
    document = {
        'version': 'q1-observed-phase-direction-diagnostic-v1',
        'original_contract': prior['original_contract'],
        'study_closed': prior['study_closed'],
        'preceding_diagnostic_contract': receipt(OUTPUT / 'preflight/contract.json'),
        'preceding_diagnostic_closed': receipt(OUTPUT / 'diagnostic_closed.json'),
        'preceding_diagnostic_checkpoint': receipt(OBSERVED_CHECKPOINT),
        'frozen_targets': prior['frozen_targets'],
        'source_transitions': transitions, 'current_source_files': sources,
        'input_traces': prior['input_traces'],
        'confidence_audit': receipt(OUTPUT / 'diagnostics/cycle_confidence_v1/result.json'),
        'confidence_audit_manifest': receipt(OUTPUT / 'diagnostics/cycle_confidence_v1/manifest.json'),
        'partition': 'discovery', 'seeds': [26090911, 26090912],
        'target_numbers': list(range(1, 13)), 'fixed_anchor_count': 24,
        'job_timeout_sec': 300, 'reference': prior['reference'],
        'observed_phase_reference': dict(analysis.Q1_OBSERVED_PHASE_METHOD),
        'latent_blend': dict(analysis.Q1_OBSERVED_PHASE_LATENT),
    }
    # Retain a content-addressed prospective draft while checking actual inputs.
    # A failed preflight must not publish an apparently frozen final contract.
    draft_digest = hashlib.sha256(json.dumps(document, sort_keys=True).encode()).hexdigest()
    draft_path = OBSERVED_OUTPUT / 'preflight/candidates' / (draft_digest + '.json')
    draft_path.parent.mkdir(parents=True, exist_ok=True)
    if draft_path.exists():
        if json.loads(draft_path.read_text()) != document:
            raise ValueError('Existing prospective observed-phase draft differs')
    else:
        atomic_exclusive_json(draft_path, document)
    effective, supplement = analysis._q1_observed_phase_contract(
        receipt(draft_path), document['original_contract'], [document['frozen_targets']])
    targets = json.loads(checked(document['frozen_targets']).read_text())
    traces = {}
    for item in targets['input_traces']:
        analysis._q1_verify_run(item['run'], effective)
        traces[item['run']['run_id']] = json.loads(checked(item).read_text())
    for target in targets['targets']:
        index = target['observation_index']
        row = None if index is None else traces[target['run_id']]['observations'][index]
        analysis._q1_observed_phase_latent(target, row, supplement[target['seed'], target['number']])
    environment = selected_environment()
    installed = installed_entry_points()
    analysis._q1_observed_phase_contract(
        receipt(draft_path), document['original_contract'], [document['frozen_targets']])
    contract_path = OBSERVED_OUTPUT / 'preflight/contract.json'
    atomic_exclusive_json(contract_path, document)
    binding = {'status': 'PREFLIGHT_VALID', 'contract': receipt(contract_path),
               'environment': environment, 'installed_entry_points': installed,
               'verified_recorded_discovery_bindings': len(targets['input_traces']),
               'verified_supplement_slots': len(supplement),
               'field_evaluated': False, 'confirmation_opened': False,
               'pilot_released': False}
    atomic_exclusive_json(OBSERVED_OUTPUT / 'preflight/installed_preflight.json', binding)
    return {'status': binding['status'], 'contract': binding['contract'],
            'source_files': len(sources), 'fixed_anchor_count': 24,
            'verified_supplement_slots': len(supplement)}


def evaluate_observed_phase():
    """Dispatch the existing shared owner with explicit measured-phase scope."""
    contract_path = OBSERVED_OUTPUT / 'preflight/contract.json'
    release = json.loads((OBSERVED_OUTPUT / 'preflight/dispatch_release.json').read_text())
    if (release.get('status') != 'RELEASED'
            or not release.get('validation_evidence')
            or release['contract'] != receipt(contract_path)
            or release['environment'] != selected_environment()
            or release['installed_entry_points'] != installed_entry_points()
            or release['job_timeout_sec'] != 300):
        raise ValueError('Observed-phase release differs from this environment or contract')
    checked(release['checkpoint'])
    for reference in release['validation_evidence']:
        checked(reference)
    document = json.loads(contract_path.read_text())
    result = analysis.evaluate_q1_direction_references(
        [document['frozen_targets']['path']], OBSERVED_OUTPUT / 'analysis',
        contract_path=document['original_contract']['path'],
        observed_phase_contract_path=contract_path)
    return {'status': result['status'], 'version': result['version'],
            'qualification_status': result['qualification_status'],
            'fixed_anchor_count': result['all']['fixed_anchor_count']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=('freeze', 'evaluate'))
    parser.add_argument('--reference-version', choices=('stationary-v1', 'observed-phase-v1'),
                        default='stationary-v1')
    arguments = parser.parse_args()
    stages = ((freeze_observed_phase, evaluate_observed_phase)
              if arguments.reference_version == 'observed-phase-v1' else (freeze, evaluate))
    print(json.dumps(stages[0 if arguments.stage == 'freeze' else 1]()), flush=True)


if __name__ == '__main__':
    main()
