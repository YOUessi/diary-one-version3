import argparse
import json
from pathlib import Path

from .bundle import load_any_bundle, run_bundle_e00
from .core import run_smoke
from .production_v1 import ProductionPipelineV1, load_production_manifest
from .validation_cases_v01 import build_reference_suite
from .validation_v01 import (
    load_validation_suite,
    validate_validation_suite,
    write_validation_scorecard,
    write_validation_suite,
)


def main() -> None:
    parser = argparse.ArgumentParser(prog="diary-one-ci")
    sub = parser.add_subparsers(dest="command", required=True)
    smoke = sub.add_parser("smoke", help="run the E00 smoke path")
    smoke.add_argument("--source", type=Path, help="portrait 3:4 video, or fixture manifest")
    smoke.add_argument("--artifacts", type=Path, default=Path("artifacts"))
    bundle = sub.add_parser("bundle", help="validate or run an App research export bundle")
    bundle_sub = bundle.add_subparsers(dest="bundle_command", required=True)
    validate = bundle_sub.add_parser("validate", help="run Experiment Bundle V01 gates")
    validate.add_argument("manifest", type=Path)
    run = bundle_sub.add_parser("run-e00", help="validate a bundle and run E00")
    run.add_argument("manifest", type=Path)
    run.add_argument("--artifacts", type=Path, default=Path("artifacts"))
    production = sub.add_parser(
        "production-v1",
        help="validate or run the S00-S13 Production-shaped V1 reference",
    )
    production_sub = production.add_subparsers(
        dest="production_command", required=True
    )
    production_validate = production_sub.add_parser(
        "validate", help="validate the V1 full-flow contract without writing artifacts"
    )
    production_validate.add_argument("manifest", type=Path)
    production_validate.add_argument(
        "--registry",
        type=Path,
        default=Path("contracts/canonical_concept_registry_v1.json"),
    )
    production_run = production_sub.add_parser(
        "run", help="run the deterministic media-free V1 reference"
    )
    production_run.add_argument("manifest", type=Path)
    production_run.add_argument(
        "--registry",
        type=Path,
        default=Path("contracts/canonical_concept_registry_v1.json"),
    )
    production_run.add_argument("--artifacts", type=Path, default=Path("artifacts"))
    validation = sub.add_parser(
        "validation-v01",
        help="materialize, validate, or run the day-level V01/V02 suite",
    )
    validation_sub = validation.add_subparsers(
        dest="validation_command", required=True
    )
    validation_materialize = validation_sub.add_parser(
        "materialize-reference",
        help="write the deterministic 12-day reference suite",
    )
    validation_materialize.add_argument(
        "--output",
        type=Path,
        default=Path("fixtures/validation_v01/semantic_day_suite_v01.json"),
    )
    validation_validate = validation_sub.add_parser(
        "validate", help="validate a V01 suite without writing artifacts"
    )
    validation_validate.add_argument("suite", type=Path)
    validation_run = validation_sub.add_parser(
        "run", help="run V01 evaluation and write a deterministic scorecard"
    )
    validation_run.add_argument("suite", type=Path)
    validation_run.add_argument(
        "--artifacts", type=Path, default=Path("artifacts")
    )
    args = parser.parse_args()
    if args.command == "smoke":
        print(run_smoke(args.source, args.artifacts).resolve())
    elif args.command == "bundle":
        if args.bundle_command == "validate":
            print(
                json.dumps(
                    load_any_bundle(args.manifest).validation,
                    indent=2,
                    ensure_ascii=False,
                )
            )
        elif args.bundle_command == "run-e00":
            print(run_bundle_e00(args.manifest, args.artifacts).resolve())
    elif args.command == "production-v1":
        pipeline = ProductionPipelineV1.from_registry_path(args.registry)
        manifest = load_production_manifest(args.manifest)
        if args.production_command == "validate":
            print(json.dumps(pipeline.validate(manifest), indent=2, ensure_ascii=False))
        elif args.production_command == "run":
            print(pipeline.run(manifest, args.artifacts).resolve())
    elif args.command == "validation-v01":
        if args.validation_command == "materialize-reference":
            print(
                write_validation_suite(build_reference_suite(), args.output).resolve()
            )
        elif args.validation_command == "validate":
            print(
                json.dumps(
                    validate_validation_suite(load_validation_suite(args.suite)),
                    indent=2,
                    ensure_ascii=False,
                )
            )
        elif args.validation_command == "run":
            print(
                write_validation_scorecard(
                    load_validation_suite(args.suite), args.artifacts
                ).resolve()
            )



if __name__ == "__main__":
    main()
