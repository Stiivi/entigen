# Entigen

_Meta-model entity generator_

Generator that takes an entity-relationship-like model as input and generates
various blocks of source files that either describe the model in the target
language or perform some functionality with the structures of the model.

The tool's goals are:

* Reduce boilerplate while maintaining transparency
* Reduce points where error might be manually introduced
* Respect multiple languages and preserve type consistency

Example uses: class definition, initialization methods, comparators, database
storage/retrieval operations, protocol specifications, documentation, etc.

This tool is to be used when language magic is not desired and when transparent
code and ability to diagnose is prefered. Examples of language magic: Python
metaclasses, synthesized properties and methods.


## Requirements

The `entigen` tool requires Python >= 3.6


## Usage

	usage: entigen [-h] [-b BLOCK_TYPE] [-f READER] [-t WRITER] [-V VARIABLES]
				   model [entities [entities ...]]

	Process some integers.

	positional arguments:
	  model                 Model source
	  entities              Entities to be included

	optional arguments:
	  -h, --help            show this help message and exit
	  -b BLOCK_TYPE, --block BLOCK_TYPE
							Block type the writer writes
	  -f READER, --from READER
							Metamodel input format
	  -t WRITER, --to WRITER
							Text output format
	  -V VARIABLES, --variable VARIABLES
							Text output format


Example: go to the `examples` directory and run:

    entigen thing.model > thing.py

Then see the generated `thing.py` file.

## Writers and Blocks

The following writers are available:

* `python` – Python source file or snippet writer
* `info` – Text output writer


### Python Writer

The Python writer writes type-annotated Python 3.6 source code. Blocks:

* `class` – class with instance variable annotations and the
  `__init__` and `__eq__` method
* `class_file` – file with classes of specified entities

`__init__` – method takes one argument per entity property and then assigns
it to the corresponding instance variable. If a variable is composite, such as
list, and has a default value, then the default value is assigned within the
method, not in the argument list.

`__eq__` – method takes other object, then compares whether the other object is
of the same subclass as the entity. All properties of the entity are compared
with the properties of the other entity.


### Info Writer

The `info` writer can be used by shell scripts to learn more about the moden
and the have better control over overal output generation using other writers.

To list names of all entities in a model, one per line, use:

    entigen -w info model

Variables:

* `decamelize` – write entity names as lower-case identifiers


## Readers

The default reader is a `csv` reader. The meta-model is a directory with CSV
files describing meta-model entities. Files:

* `properties.csv` – list of entity properties. Fields: category, entity, name,
  type, optional, tag, label, description
* `entities.csv` – list of entities.

The main reason for the CSV input format is that it is structured and can be
edited as text or as a spreadsheet. Spreadsheet applications are wide-spread
enough and they have quite comfortable user interface for editing structured
data.


## Data Types

The generator comes with it's own very simple data types. The variety of types
is intentionally limited so we are able to cover wide variety of outputs with
easy type and type handling translation.

The base types are:

* `string`
* `int`
* `identifier` - internally same as string, but writers can implement checks
    for content beign valid identifier

The complex types are:

* `list<BASETYPE>` - list of base-type objects


### Special default values

The following special values should be compared as whole strings for their
corresponding types.

* `[]` is a special default value for a string meaning an empty list


# Development

Some things to keep in mind while working on this tool:

* The generated source should be as human-readable as possible, it should be
    nicely formatted and not far from how a person with a good style would
    write it.
* When adding a core data type its availability or convertibility to other
    languages (programming or modelling) should be strongly considered.

# Author and License

Author: Stefan Urbanek stefan.urbanek@gmail.com

License: MIT
