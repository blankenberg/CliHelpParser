import inspect
import tempfile
from io import IOBase, StringIO, TextIOBase
from os import PathLike
from pathlib import Path
from typing import Generator, List

from dataclasses import dataclass

import galaxyxml.tool as gxt
import galaxyxml.tool.parameters as gxtp
from acclimatise import cli_types
from acclimatise.converter import NamedArgument, WrapperGenerator
from acclimatise.model import CliArgument, Command, Flag, Positional
from acclimatise.yaml import yaml
from galaxy.tool_util.lint import LEVEL_ALL, LEVEL_ERROR, LEVEL_WARN, lint_tool_source
from galaxy.tool_util.parser import get_tool_source


@dataclass
class GalaxyGenerator(WrapperGenerator):
    case = "snake"

    @classmethod
    def format(cls) -> str:
        return "galaxy"

    @property
    def suffix(self) -> str:
        return ".xml"

    @staticmethod
    def to_gxy_class(typ: cli_types.CliType):
        if isinstance(typ, cli_types.CliFile):
            return gxtp.DataParam
        elif isinstance(typ, cli_types.CliDir):
            return gxtp.DataParam  # can make composite datatype
        elif isinstance(typ, cli_types.CliString):
            return gxtp.TextParam
        elif isinstance(typ, cli_types.CliFloat):
            return gxtp.FloatParam
        elif isinstance(typ, cli_types.CliInteger):
            return gxtp.IntegerParam
        elif isinstance(typ, cli_types.CliBoolean):
            return gxtp.BooleanParam
        # elif isinstance(typ, cli_types.CliEnum):
        #    return gxtp.BooleanParam
        # elif isinstance(typ, cli_types.CliList):
        #    return CwlGenerator.to_cwl_type(typ.value) + "[]"
        # elif isinstance(typ, cli_types.CliTuple):
        #    return [CwlGenerator.to_cwl_type(subtype) for subtype in set(typ.values)]
        else:
            raise Exception(f"Invalid type {typ}!")

    def save_to_string(self, cmd: Command) -> str:
        # Some current limits?:
        # No package name information
        # No version information
        # No outputs

        inputs: List[CliArgument] = [*cmd.named] + (
            [] if self.ignore_positionals else [*cmd.positional]
        )
        names = self.choose_variable_names(inputs)

        tool_name = cmd.as_filename
        tool_id = cmd.as_filename
        tool_version = "0.0.1"
        tool_description = ""
        tool_executable = " ".join(cmd.command)
        version_command = "%s %s" % (tool_executable, cmd.version_flag.full_name())
        tool = gxt.Tool(
            tool_name,
            tool_id,
            tool_version,
            tool_description,
            tool_executable,
            hidden=False,
            tool_type=None,
            URL_method=None,
            workflow_compatible=True,
            interpreter=None,
            version_command=version_command,
        )

        tool.inputs = gxtp.Inputs()
        tool.outputs = gxtp.Outputs()
        tool.help = self._format_help(cmd.help_text)

        tool.tests = gxtp.Tests()  # ToDo: add tests
        tool.citations = gxtp.Citations()  # ToDo: add citations

        # Add requirements
        requirements = gxtp.Requirements()
        requirements.append(gxtp.Requirement("package", tool_executable, version=None))
        tool.requirements = requirements

        for arg in names:
            assert arg.name != "", arg
            param_cls = self.to_gxy_class(arg.arg.get_type())
            # not yet handled:
            # default values?
            # ints & floats: min, max
            param = param_cls(
                arg.name,
                label=arg.arg.description,
                positional=isinstance(arg.arg, Positional),
                help=arg.arg.description,
                value=None,
                num_dashes=len(arg.arg.longest_synonym)
                - len(arg.arg.longest_synonym.lstrip("-")),
                optional=arg.arg.optional,
            )
            # output or input?
            tool.inputs.append(param)
        return tool.export()

    @classmethod
    def validate(cls, wrapper: str, cmd: Command = None, explore=True):
        # ToDo: Tests? What level to validate?
        # Is wrapper assumed to be generated here, or should we also compare to result of output of save_to_string (as if wrapper was being generated externally)
        # Raise value error if validation fails
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".xml") as fh:
            fh.write(wrapper)
            fh.flush()
            tool_source = get_tool_source(config_file=fh.name)
            if not lint_tool_source(
                tool_source, level=LEVEL_ALL, fail_level=LEVEL_WARN
            ):
                raise ValueError("Linting Failed")
        return True

    def _format_help(self, help_text):
        # Just cheat and make it a huge block quote
        rval = "::\n"
        for line in help_text.split("\n"):
            rval = "%s\n  %s" % (rval, line.rstrip())
        return "%s\n\n" % (rval)
