# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from argparse import Namespace

from fabric_cli.commands.fs.impor import fab_fs_import_direct_api as import_direct_api
from fabric_cli.commands.fs.impor import fab_fs_import_cicd as import_cicd
from fabric_cli.core.hiearchy.fab_hiearchy import FabricElement, Item
from fabric_cli.utils import fab_util as utils


def exec_command(args: Namespace, context: FabricElement) -> None:
    if hasattr(args, 'validate_args'):
        args.validate_args(args)

    # Direct API flow
    if args.path and args.input:
        args.input = utils.process_nargs(args.input)
        if isinstance(context, Item):
            import_direct_api.import_single_item(context, args)

    # CI/CD flow
    elif args.config_file:
        import_cicd.import_with_config_file(args)
