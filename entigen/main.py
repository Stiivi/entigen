"""The main part of the entigen tool."""

import argparse

from .model import Model
from .readers.csv import CSVReader
from .writers.python import PythonWriter

FILENAME = "properties.csv"

READERS = {
    "csv": CSVReader
}

WRITERS = {
    "python": PythonWriter        
}


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('model', nargs='+',
                    help='Model source')

parser.add_argument('-r', '--reader', dest='reader', 
                    default="csv",
                    help="Reader type")
parser.add_argument('-w', '--writer', dest='writer', 
                    default="python",
                    help="Writer type")


def main() -> None:

    args = parser.parse_args()


    model = Model()
    reader = READERS[args.reader](model=model)

    for path in args.model:
        reader.read_model(path)

    writer = WRITERS[args.writer](model=model)

    # TODO: This is just for playground purposes
    for ent in reader.model.entities:
        b = writer.write_class_file(ent)
        print(b)
