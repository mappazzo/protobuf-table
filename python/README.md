# protobuf-table Python Implementation

Python implementation of the protobuf-table library for structured table data compression and serialization.

## Features

- **JavaScript API Compatibility**: Provides equivalent functionality to the JavaScript version
- **Callback Support**: Optional callback-style API for JavaScript compatibility  
- **Type Safety**: Uses Python type hints for better code reliability
- **Cross-Language Data Compatibility**: Data encoded in Python can be decoded in JavaScript and vice versa

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Import the library:**
   ```python
   from pb_table import encode_table, decode_table, encode_verbose, decode_verbose
   # Or use aliases
   from pb_table import encode, decode
   ```

## API Reference

### Core Functions

#### Array Format (Default)

**`encode_table(obj, callback=None)`** / **`encode(obj, callback=None)`**
- Encode table data in array format to protobuf bytes
- **Parameters:**
  - `obj`: Dictionary with 'header' and 'data' keys
  - `callback`: Optional callback function (error, result)
- **Returns:** bytes object containing encoded data

**`decode_table(buffer, callback=None)`** / **`decode(buffer, callback=None)`**
- Decode table data from protobuf bytes to array format
- **Parameters:**
  - `buffer`: bytes object containing encoded data
  - `callback`: Optional callback function (error, result)
- **Returns:** Dictionary with decoded table data

#### Object Format (Verbose)

**`encode_verbose(obj, callback=None)`**
- Encode table data in object format to protobuf bytes
- **Parameters:**
  - `obj`: Dictionary with 'header' and 'data' keys (data as list of dicts)
  - `callback`: Optional callback function (error, result)
- **Returns:** bytes object containing encoded data

**`decode_verbose(buffer, callback=None)`**
- Decode table data from protobuf bytes to object format
- **Parameters:**
  - `buffer`: bytes object containing encoded data
  - `callback`: Optional callback function (error, result)
- **Returns:** Dictionary with decoded table data (data as list of dicts)

## Usage Examples

### Basic Array Format

```python
from pb_table import encode_table, decode_table

# Define table structure
table = {
    'header': [
        {'name': 'id', 'type': 'uint'},
        {'name': 'name', 'type': 'string'},
        {'name': 'value', 'type': 'float'},
        {'name': 'active', 'type': 'bool'}
    ],
    'data': [
        [1, 'sensor1', 23.5, True],
        [2, 'sensor2', 24.1, False],
        [3, 'sensor3', 22.8, True]
    ]
}

# Encode to binary
encoded = encode_table(table)
print(f"Encoded {len(table['data'])} rows to {len(encoded)} bytes")

# Decode back to original format
decoded = decode_table(encoded)
print(f"Decoded {len(decoded['data'])} rows")
print("Data matches:", table['data'] == decoded['data'])
```

### Object Format (Verbose)

```python
from pb_table import encode_verbose, decode_verbose

# Define table with object format data
table = {
    'header': [
        {'name': 'id', 'type': 'uint'},
        {'name': 'name', 'type': 'string'},
        {'name': 'temperature', 'type': 'float'}
    ],
    'data': [
        {'id': 1, 'name': 'sensor1', 'temperature': 23.5},
        {'id': 2, 'name': 'sensor2', 'temperature': 24.1},
        {'id': 3, 'name': 'sensor3', 'temperature': 22.8}
    ]
}

# Encode and decode
encoded = encode_verbose(table)
decoded = decode_verbose(encoded)
```

### Data Transforms for Compression

```python
from pb_table import encode_table, decode_table

# Table with compression transforms
table = {
    'header': [
        {
            'name': 'timestamp',
            'type': 'uint',
            'transform': {
                'offset': 1609459200,  # Base timestamp
                'multip': 1,
                'decimals': 0
            }
        },
        {
            'name': 'latitude',
            'type': 'int',
            'transform': {
                'offset': -42,
                'multip': 1000000,  # Store as micro-degrees
                'decimals': 6,
                'sequence': False
            }
        },
        {
            'name': 'temperature',
            'type': 'int',
            'transform': {
                'offset': 0,
                'multip': 100,  # Store as centi-degrees
                'decimals': 2
            }
        }
    ],
    'data': [
        [1609459260, -41.123456, 23.45],
        [1609459320, -41.123789, 23.67],
        [1609459380, -41.124012, 23.89]
    ]
}

# Transforms are applied automatically during encoding
encoded = encode_table(table)
decoded = decode_table(encoded)

# Original data is perfectly restored
print("Transform round-trip successful:", table['data'] == decoded['data'])
```

### Sequence Transforms (Delta Encoding)

```python
from pb_table import encode_table, decode_table

# Table with sequence transforms for time-series data
table = {
    'header': [
        {
            'name': 'counter',
            'type': 'uint',
            'transform': {
                'sequence': True  # Delta encoding
            }
        },
        {
            'name': 'value',
            'type': 'int',
            'transform': {
                'offset': 1000,
                'sequence': True
            }
        }
    ],
    'data': [
        [100, 1010],  # Stored as: 100, 10
        [105, 1015],  # Stored as: 5, 5
        [112, 1008],  # Stored as: 7, -7
        [120, 1025]   # Stored as: 8, 17
    ]
}

encoded = encode_table(table)
decoded = decode_table(encoded)
```

### Metadata Support

```python
from pb_table import encode_table, decode_table

# Table with metadata
table = {
    'header': [
        {'name': 'id', 'type': 'uint'},
        {'name': 'value', 'type': 'float'}
    ],
    'meta': {
        'filename': 'sensor_data.pb',
        'owner': 'data_team',
        'comment': 'Hourly sensor readings'
    },
    'custom_key': 'custom_value',
    'data': [
        [1, 1.1],
        [2, 2.2]
    ]
}

encoded = encode_table(table)
decoded = decode_table(encoded)

# Metadata is preserved
print("Metadata preserved:", decoded['meta'] == table['meta'])
```

### Callback-Style API (JavaScript Compatibility)

```python
from pb_table import encode_table, decode_table

table = {
    'header': [{'name': 'id', 'type': 'uint'}],
    'data': [[1], [2], [3]]
}

# Success callback
def handle_result(error, result):
    if error:
        print(f"Error: {error}")
    else:
        print(f"Success: {len(result)} bytes encoded")

encode_table(table, handle_result)

# Error callback
def handle_error(error, result):
    if error:
        print(f"Expected error: {error}")

encode_table({'invalid': 'format'}, handle_error)
```

### Random Access (Get Functions)

```python
from pb_table import encode_table, get_table, get_verbose, encode_verbose

# Create test data
table = {
    'header': [
        {'name': 'id', 'type': 'uint'},
        {'name': 'name', 'type': 'string'},
        {'name': 'value', 'type': 'float'}
    ],
    'data': [
        [1, 'first', 1.1],
        [2, 'second', 2.2],
        [3, 'third', 3.3],
        [4, 'fourth', 4.4]
    ]
}

# Encode data
encoded = encode_table(table)

# Get single row (returns: [2, 'second', 2.2])
row_1 = get_table(encoded, 1)

# Get multiple rows (returns: [[1, 'first', 1.1], [3, 'third', 3.3]])
rows_0_2 = get_table(encoded, [0, 2])

# Object format example
verbose_table = {
    'header': table['header'],
    'data': [
        {'id': 1, 'name': 'first', 'value': 1.1},
        {'id': 2, 'name': 'second', 'value': 2.2},
        {'id': 3, 'name': 'third', 'value': 3.3},
        {'id': 4, 'name': 'fourth', 'value': 4.4}
    ]
}

encoded_verbose = encode_verbose(verbose_table)

# Get single row (returns: {'id': 3, 'name': 'third', 'value': 3.3})
row_verbose = get_verbose(encoded_verbose, 2)
```

### Data Addition (Add Functions)

```python
from pb_table import encode_table, add_table, decode_table, encode_verbose, add_verbose

# Initial data
initial_table = {
    'header': [
        {'name': 'id', 'type': 'uint'},
        {'name': 'name', 'type': 'string'},
        {'name': 'value', 'type': 'float'}
    ],
    'data': [
        [1, 'first', 1.1],
        [2, 'second', 2.2]
    ]
}

# Encode initial data
encoded = encode_table(initial_table)

# Add new rows
additional_data = [
    [3, 'third', 3.3],
    [4, 'fourth', 4.4]
]

# Append data (returns new encoded buffer)
expanded = add_table(encoded, additional_data)

# Verify expansion
decoded = decode_table(expanded)
print(f"Expanded from {len(initial_table['data'])} to {len(decoded['data'])} rows")

# Object format example
initial_verbose = {
    'header': initial_table['header'],
    'data': [
        {'id': 1, 'name': 'first', 'value': 1.1},
        {'id': 2, 'name': 'second', 'value': 2.2}
    ]
}

additional_verbose = [
    {'id': 3, 'name': 'third', 'value': 3.3},
    {'id': 4, 'name': 'fourth', 'value': 4.4}
]

encoded_verbose = encode_verbose(initial_verbose)
expanded_verbose = add_verbose(encoded_verbose, additional_verbose)
```

### Buffer Indexing

```python
from pb_table import encode_table, get_index

table = {
    'header': [
        {'name': 'id', 'type': 'uint'},
        {'name': 'name', 'type': 'string'}
    ],
    'data': [
        [1, 'first'],
        [2, 'second'],
        [3, 'third'],
        [4, 'fourth']
    ]
}

encoded = encode_table(table)

# Get byte positions for each row
index = get_index(encoded)
print(f"Row positions: {index}")
# Output: Row positions: [8, 58, 108, 158] (example values)

# Index can be used for efficient random access planning
print(f"Row 2 starts at byte position: {index[2]}")
```

### Complete Workflow Example

```python
from pb_table import encode_table, get_table, add_table, decode_table, get_index

# 1. Create and encode initial data
table = {
    'header': [
        {'name': 'id', 'type': 'uint'},
        {'name': 'name', 'type': 'string'},
        {'name': 'score', 'type': 'float'}
    ],
    'data': [
        [1, 'alice', 95.5],
        [2, 'bob', 87.2]
    ]
}

encoded = encode_table(table)
print(f"Initial: {len(table['data'])} rows")

# 2. Random access - get specific row
first_row = get_table(encoded, 0)
print(f"First row: {first_row}")

# 3. Add new data
new_data = [[3, 'charlie', 92.8]]
expanded = add_table(encoded, new_data)

# 4. Verify final result
final = decode_table(expanded)
print(f"Final: {len(final['data'])} rows")

# 5. Generate index for the expanded data
index = get_index(expanded)
print(f"Index: {len(index)} positions")
```

## Data Types

The library supports the following data types:

- **`'string'`**: Text data
- **`'uint'`**: Unsigned integers
- **`'int'`**: Signed integers (with zigzag encoding)
- **`'float'`**: 32-bit floating point numbers
- **`'bool'`**: Boolean values

## Transform Options

Transforms can be applied to numeric data (`'int'` and `'uint'` types) for compression:

- **`offset`**: Baseline value to subtract before encoding
- **`multip`**: Multiplication factor for scaling
- **`decimals`**: Decimal places to preserve (multiplies by 10^decimals)
- **`sequence`**: Enable delta encoding (stores differences between consecutive values)

## Error Handling

The library raises `ProtobufTableError` for invalid inputs:

```python
from pb_table import encode_table, ProtobufTableError

try:
    encode_table({'invalid': 'format'})
except ProtobufTableError as e:
    print(f"Validation error: {e}")
```

## Compatibility with JavaScript Version

This Python implementation provides equivalent functionality to the JavaScript protobuf-table library:

| JavaScript Function | Python Equivalent | Description |
|---------------------|-------------------|-------------|
| `encodeTable()` | `encode_table()` | Encode array format |
| `decodeTable()` | `decode_table()` | Decode array format |
| `encodeVerbose()` | `encode_verbose()` | Encode object format |
| `decodeVerbose()` | `decode_verbose()` | Decode object format |
| `getTable()` | `get_table()` | Random access array format |
| `getVerbose()` | `get_verbose()` | Random access object format |
| `addTable()` | `add_table()` | Append data array format |
| `addVerbose()` | `add_verbose()` | Append data object format |
| `getIndex()` | `get_index()` | Generate byte-position index |
| `encode()` | `encode()` | Alias for encode_table |
| `decode()` | `decode()` | Alias for decode_table |
| `get()` | `get()` | Alias for get_table |
| `add()` | `add()` | Alias for add_table |

### Advanced Functions

#### Random Access Functions

**`get_table(buffer, request, callback=None)`** / **`get(buffer, request, callback=None)`**
- Extract specific rows from encoded table data (array format) without full decoding
- **Parameters:**
  - `buffer`: bytes object containing encoded data
  - `request`: int (single row index) or list of ints (multiple row indices)
  - `callback`: Optional callback function (error, result)
- **Returns:** Single row (list) or multiple rows (list of lists)
- **Note:** Cannot be used with sequence transforms

**`get_verbose(buffer, request, callback=None)`**
- Extract specific rows from encoded table data (object format) without full decoding
- **Parameters:**
  - `buffer`: bytes object containing encoded data
  - `request`: int (single row index) or list of ints (multiple row indices)
  - `callback`: Optional callback function (error, result)
- **Returns:** Single row (dict) or multiple rows (list of dicts)
- **Note:** Cannot be used with sequence transforms

#### Data Addition Functions

**`add_table(buffer, data, callback=None)`** / **`add(buffer, data, callback=None)`**
- Append new rows to existing encoded table data (array format)
- **Parameters:**
  - `buffer`: bytes object containing encoded data
  - `data`: List of lists containing new rows to append
  - `callback`: Optional callback function (error, result)
- **Returns:** bytes object with expanded data

**`add_verbose(buffer, data, callback=None)`**
- Append new rows to existing encoded table data (object format)
- **Parameters:**
  - `buffer`: bytes object containing encoded data
  - `data`: List of dicts containing new rows to append
  - `callback`: Optional callback function (error, result)
- **Returns:** bytes object with expanded data

#### Buffer Analysis Functions

**`get_index(buffer, callback=None)`**
- Generate byte-position index for efficient random access to rows
- **Parameters:**
  - `buffer`: bytes object containing encoded data
  - `callback`: Optional callback function (error, result)
- **Returns:** List of integers representing byte positions of each row

## Testing

Run the test suite to verify functionality:

```bash
cd python
python test_pb_table.py
```

The test suite includes:
- Basic array format encoding/decoding
- Verbose object format encoding/decoding
- Data transforms and compression
- Sequence transforms (delta encoding)
- Metadata preservation
- Error handling
- Callback API compatibility

## Performance Considerations

- **Memory Usage**: Large datasets are processed in memory; consider chunking for very large tables
- **Transform Overhead**: Numeric transforms add CPU overhead but provide significant compression
- **Sequence Limitations**: Sequence transforms prevent random access to specific rows

## License

"THE BEER-WARE LICENSE" (Revision 42):
Mappazzo (info@mappazzo.com) wrote this file. As long as you retain this notice you can do whatever you want with this stuff. If we meet some day, and you think this stuff is worth it, you can buy me a beer in return. Cheers, Kelly Norris

## Contributing

This Python implementation aims to maintain API compatibility with the JavaScript version. When adding features, ensure they match the JavaScript API patterns and include comprehensive tests.
