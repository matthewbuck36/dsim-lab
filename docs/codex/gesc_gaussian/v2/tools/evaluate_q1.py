#!/usr/bin/env python3
"""Fixed Q1/Q2 analysis orchestration through existing analytical owners.

Use one600s label/nomination invocation and, only after its input freezes,
one300s reference invocation. Never overwrite or automatically retry outputs.
"""
import argparse
import hashlib
import json
from pathlib import Path

from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analysis
from ros_esc.plotting_scripts import q1_study
from ros_esc.plotting_scripts.v2_enclosure import atomic_exclusive_json
from q1_acquisition_layout import validate_acquisition_layout


def receipt(path):
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def _q2_reference_target_paths(root, contract_ref):
    """Use the analytical owner's full authority before any confirmation read."""
    job_path = root / 'analysis/label_job.json'
    branch = analysis._q2_reference_branch(job_path, contract_ref)
    paths = [root / 'analysis/discovery_targets/targets.json']
    if branch['branch'] == 'qualification48':
        paths.append(root / 'analysis/confirmation_targets/targets.json')
    return paths, job_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=('labels', 'references'))
    parser.add_argument('--contract', required=True, type=Path)
    arguments = parser.parse_args()
    contract_path = arguments.contract
    root = validate_acquisition_layout(json.loads(contract_path.read_text()), contract_path)
    contract = analysis._q1_contract(receipt(contract_path))
    manifest = root / 'study_manifest.json'
    if arguments.stage == 'references':
        if contract['version'] in analysis.Q2_VERSIONS:
            paths, qualification_path = _q2_reference_target_paths(root, receipt(contract_path))
            return analysis.evaluate_q1_direction_references(
                paths, root / 'analysis/references', contract_path=contract_path,
                qualification_result_path=qualification_path)
        return analysis.evaluate_q1_direction_references(
            [root / 'analysis/discovery_targets/targets.json',
             root / 'analysis/confirmation_targets/targets.json'],
            root / 'analysis/references', contract_path=contract_path)
    output = root / 'analysis'
    output.mkdir(parents=True, exist_ok=False)
    common = {'version': contract['version'], 'contract': receipt(contract_path),
              'acquisition_version': contract.get('acquisition_version', contract['version']),
              'acquisition_root': str(root),
              'study_manifest': receipt(manifest)}
    atomic_exclusive_json(output / 'label_job_started.json', {**common, 'status': 'INCOMPLETE'})
    q1_study.freeze_q1_study_labels(manifest, output / 'discovery_labels', partition='discovery')
    analysis.freeze_q1_direction_targets(manifest, output / 'discovery_targets', partition='discovery')
    discovery = q1_study.evaluate_q1_study_partition(
        output / 'discovery_labels/labels_manifest.json', output / 'discovery_nomination')
    if (contract['version'] in analysis.Q2_VERSIONS
            and discovery['status'] not in ('PASS', 'FAIL', 'EVIDENCE_UNAVAILABLE')):
        raise ValueError('Q2 discovery did not complete; no reference branch authorized')
    if discovery['status'] != 'PASS':
        result = {**common, 'status': discovery['status'], 'discovery': discovery,
                  'confirmation': 'SEALED_NOT_OPENED', 'pilot_released': False}
    else:
        nomination = receipt(output / 'discovery_nomination/nomination.json')
        q1_study.freeze_q1_study_labels(manifest, output / 'confirmation_labels',
                                       partition='confirmation', nomination_manifest=nomination)
        analysis.freeze_q1_direction_targets(manifest, output / 'confirmation_targets',
                                             partition='confirmation', nomination_manifest=nomination)
        confirmation = q1_study.evaluate_q1_study_partition(
            output / 'confirmation_labels/labels_manifest.json', output / 'confirmation_evaluation',
            nomination_manifest=nomination)
        if (contract['version'] in analysis.Q2_VERSIONS
                and confirmation['status'] not in ('PASS', 'FAIL', 'EVIDENCE_UNAVAILABLE')):
            raise ValueError('Q2 confirmation did not complete; no reference branch authorized')
        result = {**common, 'status': confirmation['status'], 'discovery': discovery,
                  'confirmation': confirmation, 'pilot_released': False}
    if contract['version'] in analysis.Q2_VERSIONS:
        result.update(
            completed=True, integrity_errors=[],
            discovery_nomination=receipt(output / 'discovery_nomination/nomination.json'),
            confirmation_evaluation=(receipt(output / 'confirmation_evaluation/confirmation.json')
                                     if discovery['status'] == 'PASS' else None),
            reference_branch=('qualification48' if discovery['status'] == 'PASS'
                              else 'discovery24_diagnostic'))
    atomic_exclusive_json(output / 'label_job.json', result)
    return result


if __name__ == '__main__':
    result = main()
    print(json.dumps({'status': result['status'], 'version': result['version']}), flush=True)
