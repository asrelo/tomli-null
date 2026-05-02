[![Build Status](https://github.com/asrelo/tomli-null/actions/workflows/tests.yaml/badge.svg?branch=master)](https://github.com/asrelo/tomli-null/actions?query=workflow%3ATests+branch%3Amaster+event%3Apush)

[![PyPI version](https://img.shields.io/pypi/v/tomli-null)](https://pypi.org/project/tomli-null)

# tomli-null

> A lil' TOML parser with support for non-standard `null` values (fork of `tomli`)

**Table of Contents** *generated with [mdformat-toc](https://github.com/hukkin/mdformat-toc)*

<!-- mdformat-toc start --slug=github --maxlevel=6 --minlevel=2 -->

- [Intro](#intro)
- [Installation](#installation)
- [Usage](#usage)
  - [Parse a TOML string](#parse-a-toml-string)
  - [Parse a TOML file](#parse-a-toml-file)
  - [Handle invalid TOML](#handle-invalid-toml)
  - [Construct `decimal.Decimal`s from TOML floats](#construct-decimaldecimals-from-toml-floats)
  - [Parsing `null` values](#parsing-null-values)
- [Conversion table](#conversion-table)
- [Exceptions](#exceptions)
- [FAQ](#faq)
  - [Why this parser?](#why-this-parser)
  - [Is comment preserving round-trip parsing supported?](#is-comment-preserving-round-trip-parsing-supported)
  - [Is there a `dumps`, `write` or `encode` function?](#is-there-a-dumps-write-or-encode-function)
- [Performance](#performance)
  - [Pure Python](#pure-python)
- [License](#license)

<!-- mdformat-toc end -->

## Intro<a name="intro"></a>

`tomli-null` is a Python library for parsing [TOML](https://toml.io),
based on [`tomli`](https://github.com/hukkin/tomli). It extends the parser with support
for the `null` value, mapping it to Python's `None`. All other features of `tomli` are preserved.

Unlike with `tomli`, `mypyc` wheels are **not** provided.

Version 1.0.0 and later are compatible with [TOML v1.1.0](https://toml.io/en/v1.1.0).

## Installation<a name="installation"></a>

```bash
pip install tomli-null
```

## Usage<a name="usage"></a>

### Parse a TOML string<a name="parse-a-toml-string"></a>

```python
import tomli_null

toml_str = """
[[players]]
name = "Lehtinen"
number = 26

[[players]]
name = "Numminen"
number = 27
"""

toml_dict = tomli_null.loads(toml_str)
assert toml_dict == {
    "players": [{"name": "Lehtinen", "number": 26}, {"name": "Numminen", "number": 27}]
}
```

### Parse a TOML file<a name="parse-a-toml-file"></a>

```python
import tomli_null

with open("path_to_file/conf.toml", "rb") as f:
    toml_dict = tomli_null.load(f)
```

The file must be opened in binary mode (with the `"rb"` flag).
Binary mode will enforce decoding the file as UTF-8 with universal newlines disabled,
both of which are required to correctly parse TOML.

### Handle invalid TOML<a name="handle-invalid-toml"></a>

```python
import tomli_null

try:
    toml_dict = tomli_null.loads("]] this is invalid TOML [[")
except tomli_null.TOMLDecodeError:
    print("Yep, definitely not valid.")
```

Note that error messages are considered informational only.
They should not be assumed to stay constant across `tomli-null` versions.

### Construct `decimal.Decimal`s from TOML floats<a name="construct-decimaldecimals-from-toml-floats"></a>

```python
from decimal import Decimal
import tomli_null

toml_dict = tomli_null.loads("precision-matters = 0.982492", parse_float=Decimal)
assert isinstance(toml_dict["precision-matters"], Decimal)
assert toml_dict["precision-matters"] == Decimal("0.982492")
```

Note that `decimal.Decimal` can be replaced with another callable that converts a TOML float
from string to a Python type. The `decimal.Decimal` is, however, a practical choice for use cases
where float inaccuracies can not be tolerated.

Illegal types are `dict` and `list`, and their subtypes.
A `ValueError` will be raised if `parse_float` produces illegal types.

### Parsing `null` values<a name="parsing-null-values"></a>

```python
import tomli_null

toml_str = """
value = null
items = [1, null, 3]
"""

toml_dict = tomli_null.loads(toml_str)
assert toml_dict == {"value": None, "items": [1, None, 3]}
```

The `null` keyword is parsed case-sensitively (lowercase only, just like `true` / `false`
in standard TOML) and is mapped to Python's `None`.

## Conversion table<a name="conversion-table"></a>

| TOML             | Python                                                                   |
| ---------------- | ------------------------------------------------------------------------ |
| TOML document    | `dict`                                                                   |
| key              | `str`                                                                    |
| string           | `str`                                                                    |
| integer          | `int`                                                                    |
| float            | `float` (configurable with *parse_float*)                                |
| boolean          | `bool`                                                                   |
| **null**         | **`None`** (not standard TOML)                                           |
| offset Date-Time | `datetime.datetime` (`tzinfo` set to an instance of `datetime.timezone`) |
| local Date-Time  | `datetime.datetime` (`tzinfo` set to `None`)                             |
| local Date       | `datetime.date`                                                          |
| local Time       | `datetime.time`                                                          |
| array            | `list`                                                                   |
| table            | `dict`                                                                   |
| inline table     | `dict`                                                                   |
| array of tables  | `list` of `dict`s                                                        |

## Exceptions<a name="exceptions"></a>

`tomli_null.TOMLDecodeError` is a subclass of `ValueError` with the following attributes:

| Attribute | Description                          |
| --------- | ------------------------------------ |
| `msg`     | The unformatted error message        |
| `doc`     | The TOML document being parsed       |
| `pos`     | Index in *doc* where parsing failed  |
| `lineno`  | Line number corresponding to *pos*   |
| `colno`   | Column number corresponding to *pos* |

## FAQ<a name="faq"></a>

### Why this parser?<a name="why-this-parser"></a>

- it's lil'
- pure Python with zero dependencies
- the fastest pure Python parser (inherited from `tomli`) [\*](#pure-python):
  14x as fast as [tomlkit](https://pypi.org/project/tomlkit/),
  2.1x as fast as [toml](https://pypi.org/project/toml/)
- outputs [basic data types](#conversion-table) only
- thoroughly tested: 100% branch coverage
- **supports non-standard `null` values**, mapped to Python `None`

### Is comment preserving round-trip parsing supported?<a name="is-comment-preserving-round-trip-parsing-supported"></a>

No.

The `tomli_null.loads` function returns a plain `dict` that is populated with builtin types
and types from the standard library only. Preserving comments requires a custom type to be returned
so will not be supported, at least not by the `tomli_null.loads` and `tomli_null.load` functions.

Look into [TOML Kit](https://github.com/sdispater/tomlkit) if preservation of style is what you
need, but note that TOML Kit does not support extensions provided by this library.

### Is there a `dumps`, `write` or `encode` function?<a name="is-there-a-dumps-write-or-encode-function"></a>

[tomli-w](https://github.com/hukkin/tomli-w) is the write-only counterpart of `tomli`, providing
`dump` and `dumps` functions, but note that it does not support extensions provided by this
library.

The core library does not include write capability, as most TOML use cases are read-only,
and `tomli-null` intends to be minimal.

## Performance<a name="performance"></a>

*`tomli-null`'s performance is identical to `tomli`'s – the null addition introduces negligible
overhead.* The benchmark below is reproduced from `tomli`.

The `benchmark/` folder in this repository contains a performance benchmark for comparing
the various Python TOML parsers. Note that **data for the benchmark do not contain `null` values**,
since none of alternative parsers under comparison support them.

Below are the results for commit
[064e492](https://github.com/asrelo/tomli_null/tree/064e492919b2338def788753b8c981c9131334c0).

### Pure Python<a name="pure-python"></a>

```console
foo@bar:~/dev/tomli$ python benchmark/run.py
Parsing data.toml 5000 times:
------------------------------------------------------
    parser |  exec time | performance (more is better)
-----------+------------+-----------------------------
     rtoml |    0.323 s | baseline (100%)
  pytomlpp |    0.365 s | 88.40%
     tomli |     1.44 s | 22.36%
      toml |     3.03 s | 10.65%
   tomlkit |     20.6 s | 1.57%
```

## License<a name="license"></a>

`tomli-null` is distributed under the terms of the MIT license, see `LICENSE`. For detailed
copyright and licensing information, refer to `NOTICE`.
