# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import argparse

import pytest
from argparse import Namespace

from fabric_cli.core import fab_constant
from fabric_cli.core.fab_exceptions import FabricCLIError
from fabric_cli.errors import ErrorMessages
from fabric_cli.parsers import fab_parser_validators


def test_validate_positive_int_with_valid_positive_integers():
    # Test various valid positive integers
    test_cases = [
        ("1", 1),
        ("10", 10),
        ("100", 100),
        ("999999", 999999),
    ]
    
    for input_value, expected in test_cases:
        result = fab_parser_validators.validate_positive_int(input_value)
        assert result == expected
        assert isinstance(result, int)


def test_validate_positive_int_with_zero_raises_error():
    with pytest.raises(argparse.ArgumentTypeError) as exc_info:
        fab_parser_validators.validate_positive_int("0")
    
    assert "'0' must be a positive integer" in str(exc_info.value)


def test_validate_positive_int_with_negative_integers_raises_error():
    with pytest.raises(argparse.ArgumentTypeError) as exc_info:
        fab_parser_validators.validate_positive_int("-1")
    
    assert "'-1' must be a positive integer" in str(exc_info.value)


def test_validate_positive_int_with_non_numeric_strings_raises_error():
    invalid_values = ["abc", "12.5", "1.0", "text", "12abc", "", " "]
    
    for value in invalid_values:
        with pytest.raises(argparse.ArgumentTypeError) as exc_info:
            fab_parser_validators.validate_positive_int(value)
        
        assert f"'{value}' is not a valid integer" in str(exc_info.value)


def test_validate_positive_int_with_none_raises_error():
    with pytest.raises(TypeError):
        fab_parser_validators.validate_positive_int(None)


# Import validation tests
def test_import_direct_api_flow_valid_args_success():
    """Test Direct API flow with valid arguments succeeds."""
    args = create_args(
        path=["ws1.Workspace/nb1.Notebook"],
        input=["/path/to/input"]
    )

    try:
        validated_args = fab_parser_validators.validate_import_args(args)
        assert validated_args == args
        assert validated_args.path == ["ws1.Workspace/nb1.Notebook"]
        assert validated_args.input == ["/path/to/input"]
    except FabricCLIError:
        pytest.fail(
            "validate_import_args() should not have raised FabricCLIError for valid Direct API flow")


def test_import_direct_api_flow_with_format_success():
    """Test Direct API flow with optional format parameter succeeds."""
    args = create_args(
        path=["ws1.Workspace/nb1.Notebook"],
        input=["/path/to/input"],
        format=".ipynb"
    )

    try:
        validated_args = fab_parser_validators.validate_import_args(args)
        assert validated_args == args
        assert args.format == ".ipynb"
    except FabricCLIError:
        pytest.fail(
            "validate_import_args() should not have raised FabricCLIError for valid Direct API flow with format")


def create_args(**kwargs):
    """Helper function to create Namespace with all values set to None, then override specific values."""
    defaults = {
        'path': None,
        'input': None,
        'format': None,
        'config_file': None,
        'env': None,
        'params': None
    }
    defaults.update(kwargs)
    return Namespace(**defaults)


@pytest.mark.parametrize("args,param_display_name", [
    (create_args(input=["/path/to/input"]), "path"),
    (create_args(path=["ws1.Workspace/nb1.Notebook"]), "-i/--input")
])
def test_import_direct_api_flow_missing_required_params_fails(args, param_display_name):
    """Test Direct API flow fails when required parameters are missing."""
    flow_name = "Direct API"
    flow_syntax = "fab import <path> -i <input_path> [--format <format>]"

    with pytest.raises(FabricCLIError) as exc_info:
        fab_parser_validators.validate_import_args(args)

    expected_message = ErrorMessages.Common.import_required_param_missing(
        param_display_name, flow_name, flow_syntax)
    assert exc_info.value.message == expected_message
    assert exc_info.value.status_code == fab_constant.ERROR_IMPORT_VALIDATION


def test_import_cicd_flow_valid_args_success():
    """Test CICD flow with valid arguments succeeds."""
    args = create_args(
        config_file="/path/to/config.yml",
        env="production"
    )

    try:
        validated_args = fab_parser_validators.validate_import_args(args)
        assert validated_args == args
        assert args.config_file == "/path/to/config.yml"
        assert args.env == "production"
    except FabricCLIError:
        pytest.fail(
            "validate_import_args() should not have raised FabricCLIError for valid CICD flow")


def test_import_cicd_flow_with_params_success():
    """Test CICD flow with optional params parameter succeeds."""
    args = create_args(
        config_file="/path/to/config.yml",
        env="production",
        params='[{"param1": "value1"}]'
    )

    try:
        validated_args = fab_parser_validators.validate_import_args(args)
        assert validated_args == args
        assert args.params == '[{"param1": "value1"}]'
    except FabricCLIError:
        pytest.fail(
            "validate_import_args() should not have raised FabricCLIError for valid CICD flow with params")


@pytest.mark.parametrize("args,param_display_name", [
    (create_args(config_file="/path/to/config.yml"), "--env"),
    (create_args(env="production"), "--config-file")
])
def test_import_cicd_flow_missing_required_params_fails(args, param_display_name):
    """Test CICD flow fails when required parameters are missing."""
    flow_name = "CICD"
    flow_syntax = "fab import --config-file <config_path> --env <env_name> [-P <params>]"

    with pytest.raises(FabricCLIError) as exc_info:
        fab_parser_validators.validate_import_args(args)

    expected_message = ErrorMessages.Common.import_required_param_missing(
        param_display_name, flow_name, flow_syntax)
    assert exc_info.value.message == expected_message
    assert exc_info.value.status_code == fab_constant.ERROR_IMPORT_VALIDATION


def test_import_no_flow_specified_fails():
    """Test that no flow specified results in error."""
    args = create_args()

    with pytest.raises(FabricCLIError) as exc_info:
        fab_parser_validators.validate_import_args(args)

    expected_message = ErrorMessages.Common.import_no_flow_specified_error()
    assert exc_info.value.message == expected_message
    assert exc_info.value.status_code == fab_constant.ERROR_IMPORT_VALIDATION


def test_import_mixed_flows_fails():
    """Test that mixing Direct API and CICD parameters fails."""
    args = create_args(
        path=["ws1.Workspace/nb1.Notebook"],  # Direct API
        input=["/path/to/input"],  # Direct API
        config_file="/path/to/config.yml",  # CICD
        env="production"  # CICD
    )

    with pytest.raises(FabricCLIError) as exc_info:
        fab_parser_validators.validate_import_args(args)

    expected_message = ErrorMessages.Common.import_mixed_flows_error()
    assert exc_info.value.message == expected_message
    assert exc_info.value.status_code == fab_constant.ERROR_IMPORT_VALIDATION


def test_import_error_messages_include_syntax_examples():
    """Test that error messages include correct syntax examples."""
    args = create_args(path=["ws1.Workspace/nb1.Notebook"])

    with pytest.raises(FabricCLIError) as exc_info:
        fab_parser_validators.validate_import_args(args)

    assert "-i/--input is required for Direct API flow" in exc_info.value.message
    assert "Correct syntax: fab import <path> -i <input_path> [--format <format>]" in exc_info.value.message
    assert exc_info.value.status_code == fab_constant.ERROR_IMPORT_VALIDATION


def test_import_cicd_error_messages_include_syntax_examples():
    """Test that CICD flow error messages include correct syntax examples."""
    args = create_args(config_file="/path/to/config.yml")

    with pytest.raises(FabricCLIError) as exc_info:
        fab_parser_validators.validate_import_args(args)

    assert "--env is required for CICD flow" in exc_info.value.message
    assert "Correct syntax: fab import --config-file <config_path> --env <env_name> [-P <params>]" in exc_info.value.message
    assert exc_info.value.status_code == fab_constant.ERROR_IMPORT_VALIDATION


def test_import_path_only_triggers_direct_api_validation():
    """Test that providing only path triggers Direct API flow validation."""
    args = create_args(path=["ws1.Workspace/nb1.Notebook"])

    with pytest.raises(FabricCLIError) as exc_info:
        fab_parser_validators.validate_import_args(args)

    assert "-i/--input is required for Direct API flow" in exc_info.value.message
    assert exc_info.value.status_code == fab_constant.ERROR_IMPORT_VALIDATION


def test_import_input_only_triggers_direct_api_validation():
    """Test that providing only input triggers Direct API flow validation."""
    args = create_args(input=["/path/to/input"])

    with pytest.raises(FabricCLIError) as exc_info:
        fab_parser_validators.validate_import_args(args)

    assert "path is required for Direct API flow" in exc_info.value.message
    assert exc_info.value.status_code == fab_constant.ERROR_IMPORT_VALIDATION


def test_import_format_only_triggers_direct_api_validation():
    """Test that providing only format triggers Direct API flow validation."""
    args = create_args(format=".ipynb")

    with pytest.raises(FabricCLIError) as exc_info:
        fab_parser_validators.validate_import_args(args)

    assert "path is required for Direct API flow" in exc_info.value.message
    assert exc_info.value.status_code == fab_constant.ERROR_IMPORT_VALIDATION


def test_import_env_only_triggers_cicd_validation():
    """Test that providing only env triggers CICD flow validation."""
    args = create_args(env="production")

    with pytest.raises(FabricCLIError) as exc_info:
        fab_parser_validators.validate_import_args(args)

    assert "--config-file is required for CICD flow" in exc_info.value.message
    assert exc_info.value.status_code == fab_constant.ERROR_IMPORT_VALIDATION


def test_import_params_only_triggers_cicd_validation():
    """Test that providing only params triggers CICD flow validation."""
    args = create_args(params='[{"key": "value"}]')

    with pytest.raises(FabricCLIError) as exc_info:
        fab_parser_validators.validate_import_args(args)

    assert "--config-file is required for CICD flow" in exc_info.value.message
    assert exc_info.value.status_code == fab_constant.ERROR_IMPORT_VALIDATION
