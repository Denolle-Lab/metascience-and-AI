"""Offline integration: python3 -m ai_readiness --help (PYTHONPATH=tools)."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from . import adapter, core


def comparison(args):
    reports={name:core.read_json(path) for name,path in [('earth',args.earth),('cs',args.cs)]}
    protocol=core.read_json(args.protocol) if args.protocol else {}
    required=['matched_years','matched_article_eligibility','matched_annotation_codebook','full_text_coverage_audited','frozen_source_frames']
    gates=protocol.get('comparability',{})
    ready=all(isinstance(gates.get(k),dict) and gates[k].get('confirmed') is True and bool(gates[k].get('evidence')) for k in required)
    result={'comparison_ready':ready,'comparability_protocol':protocol,
        'interpretation':'Separate cohort estimates; no automatic pooling, significance test, trend or causal claim.',
        'modality_definitions_comparable':bool(reports['earth'].get('modality_ontology')) and reports['earth'].get('modality_ontology')==reports['cs'].get('modality_ontology'),
        'cohorts':reports,'warning':None if ready else 'Do not make cross-field adoption comparisons until source/eligibility/coverage/codebook gates are documented.'}
    core.atomic_json(args.out,result)


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('import',help='Import existing OpenAlex/DOI/corpus metadata locally; never retrieve.')
    q.add_argument('--input',required=True);q.add_argument('--out',required=True);q.add_argument('--cohort',required=True)
    q.add_argument('--ontology',choices=['earth_measurement_families','cs_information_channels'],required=True);q.set_defaults(function=adapter.import_metadata)
    q=sub.add_parser('screen',help='Candidate mentions only; does not infer actual use.')
    q.add_argument('--input',required=True);q.add_argument('--out',required=True);q.set_defaults(function=core.screen)
    q=sub.add_parser('bind-selection',help='Bind verified existing select_dois/Nature random weights to exact IDs.')
    q.add_argument('--run',required=True);q.add_argument('--metadata',required=True);q.add_argument('--out',required=True);q.set_defaults(function=adapter.bind_selection)
    q=sub.add_parser('attach-design',help='Attach original assignments to all screens, without resampling.')
    q.add_argument('--input',required=True);q.add_argument('--design',required=True);q.add_argument('--out',required=True);q.set_defaults(function=adapter.attach_design)
    q=sub.add_parser('sample',help='Sample ONLY a verified complete census/frame; never a legacy selected cohort.')
    q.add_argument('--input',required=True);q.add_argument('--manifest',required=True);q.add_argument('--out',required=True);q.add_argument('--design',required=True)
    q.add_argument('--n-per-stratum',type=int,default=10);q.add_argument('--seed',default='ai-readiness-v1');q.set_defaults(function=core.sample)
    q=sub.add_parser('template',help='Blank human annotations; all actual-use labels remain unknown.')
    q.add_argument('--input',required=True);q.add_argument('--out',required=True);q.set_defaults(function=core.template)
    q=sub.add_parser('report',help='Reviewed counts and, with a bound design, weighted estimates.')
    q.add_argument('--input',required=True);q.add_argument('--design');q.add_argument('--out',required=True);q.add_argument('--endpoint-protocol');q.set_defaults(function=core.report)
    q=sub.add_parser('bridge',help='Local PDF/coding evidence queue and optional legacy semantic manifest; no client calls.')
    q.add_argument('--run',required=True);q.add_argument('--repo',default='.');q.add_argument('--queue');q.add_argument('--codings');q.add_argument('--assets',help='Existing downloader CSV/JSONL asset manifest (DOI/status/path).')
    q.add_argument('--out',required=True);q.add_argument('--semantic-manifest');q.set_defaults(function=adapter.bridge)
    q=sub.add_parser('compare',help='Keep Earth/CS reports separate; require recorded comparison gates.')
    q.add_argument('--earth',required=True);q.add_argument('--cs',required=True);q.add_argument('--protocol');q.add_argument('--out',required=True);q.set_defaults(function=comparison)
    return p


def main(argv=None):
    args=parser().parse_args(argv)
    try:
        # Analysis outputs are dated/private by convention; refuse accidental overwrites.
        outputs=[getattr(args,k,None) for k in ['out','semantic_manifest']]
        if args.command=='sample': outputs.append(args.design)
        for destination in outputs:
            if destination and Path(destination).exists():
                raise ValueError('Output already exists; choose a new dated path to preserve prior annotations/results.')
        args.function(args)
    except (ValueError,KeyError,TypeError,OSError,json.JSONDecodeError) as exc:
        print(f'ai_readiness: {exc}',file=sys.stderr)
        return 2
    return 0


if __name__=='__main__':
    raise SystemExit(main())
