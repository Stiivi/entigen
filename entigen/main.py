"""The main part of the entigen tool."""

import argparse
import re

from typing import List, Dict, Optional

from .model import Model
from .readers.csv import CSVReader
from .writers.python import PythonWriter
from .writers.info import InfoWriter

from .extensible import Extensible

# Pattern for parsing argument-defined variables for writers
VARIABLE_PATTERN = r"(\w+)(=.*)?"

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('model',
                    help='Model source')

parser.add_argument('entities', nargs='*',
                    help='Entities to be included')

parser.add_argument('-b', '--block', dest='block_type', 
                    help="Block type the writer writes")

parser.add_argument('-f', '--from', dest='reader', 
                    default="csv",
                    help="Metamodel input format")

parser.add_argument('-t', '--to', dest='writer', 
                    default="python",
                    help="Text output format")

parser.add_argument('-V', '--variable', dest='variables', 
                    action="append",
                    help="Text output format")


def parse_variables(vars: Optional[List[str]]) -> Dict[str,str]:
    """Parse command line defined variables in the form ``name=value``. Returns
    a dictionary where keys are variable names and values are variable values
    parsed from the `vars`. If a variable name without value is specified (no
    ``=`` character) then value `True` is assumed to mark the variable as
    "present" or as "flag".
    """

    variables: Dict[str,str] = {}

    if vars is None:
        return variables

    for var in vars:
        match = re.match(VARIABLE_PATTERN, var)

        if not match:
            continue

        name = match.groups()[0]
        value = match.groups()[1]

        if value is None:
            variables[name] = True
        else:
            # Strip the leading `=`
            variables[name] = value[1:]

    return variables


def main() -> None:

    args = parser.parse_args()

    variables = parse_variables(args.variables)

    model = Model()
    reader = Extensible.readers[args.reader](model=model)

    reader.read_model(args.model)

    writer_factory = Extensible.writers[args.writer]
    writer = writer_factory(model=model, variables=variables)

    # If no block type is specified then default is used
    block_type = args.block_type or writer.block_types[0]
    block = writer.create_block(block_type, args.entities)

    print(block)
