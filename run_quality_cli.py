"""run quality checks against the COVID Tracker's human-generated datasets"""

import sys
from loguru import logger
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter

from app.util import read_config_file
from app.qc_config import QCConfig
from app.data.data_source import DataSource
from app.check_dataset import check_current, check_working, check_history


def load_args_parser(config) -> ArgumentParser:
    " load arguments parser "

    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('state', metavar='state', type=str, nargs='*',
        help='states to check')

    parser.add_argument(
        '-w', '--working', dest='check_working', action='store_true', default=False,
        help='check the working results (only)')

    parser.add_argument(
        '-d', '--current', dest='check_current', action='store_true', default=False,
        help='check the current (only)')

    parser.add_argument(
        '-x', '--history', dest='check_history', action='store_true', default=False,
        help='check the history (only)')

    save_results = config["CHECKS"]["save_results"] == "True"
    enable_experimental = config["CHECKS"]["enable_experimental"] == "True"
    enable_debug = config["CHECKS"]["enable_debug"] == "True"
    plot_models = config["MODEL"]["plot_models"] == "True"

    parser.add_argument(
        '--save', dest='save_results', action='store_true', default=save_results,
        help='save results to file')

    parser.add_argument(
        '-exp', '--experimental', dest='enable_experimental', action='store_true', default=enable_experimental,
        help='enable experimental checks')

    parser.add_argument(
        '--debug', dest='enable_debug', action='store_true', default=enable_debug,
        help='enable debug traces')

    parser.add_argument(
        '--plot', dest='plot_models', action='store_true', default=plot_models,
        help='plot the model curves')


    parser.add_argument(
        '--results_dir',
        default=config["CHECKS"]["results_dir"],
        help='directory for results files')
    parser.add_argument(
        '--images_dir',
        default=config["MODEL"]["images_dir"],
        help='directory for model curves')

    return parser

def main() -> None:

    # pylint: disable=no-member

    config = read_config_file("quality-control")
    parser = load_args_parser(config)
    args = parser.parse_args(sys.argv[1:])

    if not args.check_working and not args.check_current and not args.check_history:
        logger.info("  [default to all sources]")
        args.check_working = True
        args.check_current = True
        args.check_history = True

    config = QCConfig(
        results_dir=args.results_dir,
        save_results=args.save_results,
        enable_experimental=args.enable_experimental,
        enable_debug=args.enable_debug,
        images_dir=args.images_dir,
        plot_models=args.plot_models,
    )
    if config.save_results:
        logger.warning(f"  [save results to {args.results_dir}]")
    if config.plot_models:
        logger.warning(f"  [save forecast curves to {args.images_dir}]")

    if len(args.state) != 0:
        logger.error("  [states filter not implemented]")

    ds = DataSource()

    if args.check_working:
        logger.info("--| QUALITY CONTROL --- GOOGLE WORKING SHEET |------")
        log = check_working(ds, config=config)
        if log is None:
            ds.log.print()
        else:
            log.print()

    if args.check_current:
        logger.info("--| QUALITY CONTROL --- CURRENT |------")
        log = check_current(ds, config=config)
        if log is None:
            ds.log.print()
        else:
            log.print()

    if args.check_history:
        logger.info("--| QUALITY CONTROL --- HISTORY |------")
        log = check_history(ds)
        if log is None:
            ds.log.print()
        else:
            log.print()


if __name__ == "__main__":
    main()
