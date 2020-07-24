import inspect
import tempfile
from io import IOBase, StringIO, TextIOBase
from os import PathLike
from pathlib import Path
from typing import Generator, List

import galaxyxml.tool as gxt
import galaxyxml.tool.parameters as gxtp

from dataclasses import dataclass

from acclimatise import cli_types
from acclimatise.converter import NamedArgument, WrapperGenerator
from acclimatise.model import CliArgument, Command, Flag, Positional
from acclimatise.yaml import yaml


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
            return gxtp.DataParam # can make composite datatype
        elif isinstance(typ, cli_types.CliString):
            return gxtp.TextParam
        elif isinstance(typ, cli_types.CliFloat):
            return gxtp.FloatParam
        elif isinstance(typ, cli_types.CliInteger):
            return gxtp.IntegerParam
        elif isinstance(typ, cli_types.CliBoolean):
            return gxtp.BooleanParam
        #elif isinstance(typ, cli_types.CliEnum):
        #    return gxtp.BooleanParam
        #elif isinstance(typ, cli_types.CliList):
        #    return CwlGenerator.to_cwl_type(typ.value) + "[]"
        #elif isinstance(typ, cli_types.CliTuple):
        #    return [CwlGenerator.to_cwl_type(subtype) for subtype in set(typ.values)]
        else:
            raise Exception(f"Invalid type {typ}!")

    def save_to_string(self, cmd: Command) -> str:
        # Some limits due to cmd data mondel?:
        # No package name information
        # No version information
        # No outputs


        inputs: List[CliArgument] = [*cmd.named] + (
            [] if self.ignore_positionals else [*cmd.positional]
        )
        names = self.choose_variable_names(inputs)


        tool_name = cmd.as_filename
        tool_id = cmd.as_filename
        tool_version = '0.0.1'
        tool_description = ''
        tool_executable = ' '.join(cmd.command)
        version_command = "%s %s" % (tool_executable, cmd.version_flag.full_name())
        tool = gxt.Tool(tool_name, tool_name, tool_version, tool_description, tool_executable, hidden=False,
            tool_type=None, URL_method=None, workflow_compatible=True,
            interpreter=None, version_command=version_command)

        # Does cmd have a concept of outputs?
        tool.inputs = gxtp.Inputs()
        tool.outputs = gxtp.Outputs()
        tool.help = cmd.help_text

        # Add requirements
        requirements = gxtp.Requirements()
        requirements.append(gxtp.Requirement('package', tool_executable, version=None))
        tool.requirements = requirements

        for arg in names:
            assert arg.name != "", arg
            param_cls = self.to_gxy_class(arg.arg.get_type())
            # not yet handled:
            # default values?
            # ints & floats: min, max
            param = param_cls(arg.name,
                label=arg.arg.description,
                positional=isinstance(arg.arg, Positional),
                help=arg.arg.description,
                value=None,
                num_dashes=len(arg.arg.longest_synonym)-len(arg.arg.longest_synonym.lstrip('-')),
                optional=arg.arg.optional)
            # output or input?
            tool.inputs.append(param)
        return tool.export()

    @classmethod
    def validate(cls, wrapper: str, cmd: Command = None, explore=True):
        # Todo add planemo lint call
        # probably calling the functions in this loop: https://github.com/galaxyproject/planemo/blob/2b659c9a7531f9a973e60d6319898e58ef3ea781/planemo/tool_lint.py#L28
        pass
