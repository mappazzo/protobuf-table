# protobuf-table Python Implementation

A Python library that provides dynamic Protocol Buffer implementation specifically designed for structured table data compression and serialization. This is the Python equivalent of the JavaScript protobuf-table library.

## Features

- **Dynamic Schema Generation**: Create protobuf schemas at runtime based on table headers
- **Multiple Data Formats**: Support both array-based and object-based data representations
- **Compression Features**: Implement data transforms (offset, multiplication, decimals, sequencing) for optimal storage
- **JavaScript API Compatibility**: Provides equivalent functionality to the JavaScript version
- **Callback Support**: Optional callback-style API for JavaScript compatibility
- **Type Safety**: Uses Python type hints for better code reliability

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements_pb_table.txt
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
| `encode()` | `encode()` | Alias for encode_table |
| `decode()` | `decode()` | Alias for decode_table |

### Missing Features (To Be Implemented)

The following JavaScript functions are not yet implemented in Python:

- `get_table()` / `get_verbose()` - Random access to specific rows
- `add_table()` / `add_verbose()` - Append data to existing buffers
- `get_index()` - Generate byte-position index for random access

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
