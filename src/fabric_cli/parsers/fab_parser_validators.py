# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import argparse
from fabric_cli.core import fab_constant
from fabric_cli.core.fab_exceptions import FabricCLIError
from fabric_cli.errors import ErrorMessages


def validate_positive_int(value):
    """Validate that the value is a positive integer."""
    try:
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError(f"'{value}' must be a positive integer")
        return ivalue
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid integer")


def validate_import_args(args):
    """
    Validate import command arguments based on two distinct flows:
    
    Flow 1 (Direct API): path + input (--format optional)
    Flow 2 (CICD): config-file + env (-P optional)
    """

    def _check_required_param(args, attr_name, param_display_name, flow_name, flow_syntax):
        """Check if required parameter is provided for the specified flow."""
        param_value = getattr(args, attr_name, None)
        if not param_value:
            error_message = ErrorMessages.Common.import_required_param_missing(param_display_name, flow_name, flow_syntax)
            raise FabricCLIError(error_message, fab_constant.ERROR_IMPORT_VALIDATION)

    is_direct_api_flow = args.path or args.input or args.format
    is_cicd_flow = args.config_file or args.env or args.params

    if is_direct_api_flow and is_cicd_flow:
        error_message = ErrorMessages.Common.import_mixed_flows_error()
        raise FabricCLIError(error_message, fab_constant.ERROR_IMPORT_VALIDATION)

    if is_direct_api_flow:
        flow_syntax = "fab import <path> -i <input_path> [--format <format>]"
        _check_required_param(args, 'path', 'path', 'Direct API', flow_syntax)
        _check_required_param(args, 'input', '-i/--input',
                              'Direct API', flow_syntax)

    elif is_cicd_flow:
        flow_syntax = "fab import --config-file <config_path> --env <env_name> [-P <params>]"
        _check_required_param(args, 'config_file',
                              '--config-file', 'CICD', flow_syntax)
        _check_required_param(args, 'env', '--env', 'CICD', flow_syntax)

    else:
        error_message = ErrorMessages.Common.import_no_flow_specified_error()
        raise FabricCLIError(error_message, fab_constant.ERROR_IMPORT_VALIDATION)

    return args
