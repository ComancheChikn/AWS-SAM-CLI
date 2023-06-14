"""
This file contains validations remote invoke options
"""
import logging
import sys
from functools import wraps
from io import TextIOWrapper
from typing import cast

import click

from samcli.commands._utils.option_validator import Validator

LOG = logging.getLogger(__name__)


def event_and_event_file_options_validation(func):
    """
    This function validates the cases when both --event and --event-file are provided and
    neither option is provided

    Parameters
    ----------
    func :
        Command that would be executed, in this case it is 'sam remote invoke'

    Returns
    -------
        A wrapper function which will first validate options and will execute command if validation succeeds
    """

    @wraps(func)
    def wrapped(*args, **kwargs):
        ctx = click.get_current_context()

        event = ctx.params.get("event")
        event_file = ctx.params.get("event_file")

        validator = Validator(
            validation_function=lambda: event and event_file,
            exception=click.BadOptionUsage(
                option_name="--event-file",
                ctx=ctx,
                message="Both '--event-file' and '--event' cannot be provided. "
                "Please check that you don't have both specified in the command or in a configuration file",
            ),
        )

        validator.validate()

        # if no event nor event_file arguments are given, read from stdin
        if not event and not event_file:
            LOG.debug("Neither --event nor --event-file options have been provided, reading from stdin")
            kwargs["event_file"] = cast(TextIOWrapper, sys.stdin)
        return func(*args, **kwargs)

    return wrapped


def stack_name_or_resource_id_atleast_one_option_validation(func):
    """
    This function validates that atleast one of --stack-name or --resource-id should is be provided

    Parameters
    ----------
    func :
        Command that would be executed, in this case it is 'sam remote invoke'

    Returns
    -------
        A wrapper function which will first validate options and will execute command if validation succeeds
    """

    @wraps(func)
    def wrapped(*args, **kwargs):
        ctx = click.get_current_context()

        stack_name = ctx.params.get("stack_name")
        resource_id = ctx.params.get("resource_id")

        validator = Validator(
            validation_function=lambda: not (stack_name or resource_id),
            exception=click.BadOptionUsage(
                option_name="--resource-id",
                ctx=ctx,
                message="Atleast 1 of --stack-name or --resource-id parameters should be provided.",
            ),
        )

        validator.validate()

        return func(*args, **kwargs)

    return wrapped