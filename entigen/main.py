"""The main part of the entigen tool."""

import argparse

from .model import Model
from .readers.csv import CSVReader
from .writers.python import PythonWriter

from .extensible import Extensible


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


def main() -> None:

    args = parser.parse_args()

    model = Model()
    reader = Extensible.readers[args.reader](model=model)

    reader.read_model(args.model)

    writer = Extensible.writers[args.writer](model=model)

    # If no block type is specified then default is used
    block_type = args.block_type or writer.block_types[0]
    block = writer.create_block(block_type, args.entities)

    print(block)
