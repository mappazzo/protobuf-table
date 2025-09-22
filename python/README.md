# Protobuf-Table Python Implementation

A Python implementation of protobuf-table that provides efficient serialization of structured table data using Google Protocol Buffers.

## Features

- **True Protocol Buffer Implementation**: Uses actual protobuf serialization for cross-language compatibility
- **Automatic Statistics Calculation**: Computes min, max, mean, start, and end values for numeric fields
- **Transform Support**: Integer compression with offset, multiplier, decimals, and sequence transforms
- **Multiple Formats**: Support for both array and object (verbose) data formats
- **Cross-Language Compatible**: Wire format compatible with JavaScript implementation

## Installation

### Prerequisites

1. **Python 3.7+** with pip
2. **Protocol Buffer Compiler (protoc)**

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Compile Protocol Buffer Schema

The implementation uses a compiled protobuf schema. To recompile after schema changes:

```bash
# From the python/ directory
protoc --python_out=. head.proto
```

This generates `head_pb2.py` which contains the compiled protobuf message classes.

## Protocol Buffer Schema

The schema is defined in `head.proto`:

```protobuf
syntax = "proto3";
package pbTableHeader;

message Transform {
  int32 offset = 1;      // Base offset for compression
  int32 multip = 2;      // Multiplier for scaling
  int32 decimals = 3;    // Decimal precision handling
  bool sequence = 4;     // Delta encoding for sequences
}

message Stats {
  double start = 1;      // First value in dataset
  double end = 2;        // Last value in dataset
  double min = 3;        // Minimum value
  double max = 4;        // Maximum value
  double mean = 5;       // Average value
}

message Field {
  string name = 1;       // Field name
  string type = 2;       // Data type (string, uint, int, float, bool)
  Transform transform = 6; // Optional compression transform
  Stats stats = 7;       // Automatic statistics for numeric fields
}

message Meta {
  string name = 1;       // Table/file name
  string owner = 2;      // Owner information
  string link = 3;       // Related link/URL
  string comment = 4;    // Description/comments
  int32 row_count = 5;   // Total number of rows
}

message tableHead {
  repeated Field header = 1; // Table schema definition
  Meta meta = 2;            // Table metadata
}
```

## Usage

### Basic Example

```python
import pb_table

# Define table structure and data
table = {
    'header': [
        {'name': 'id', 'type': 'uint'},
        {'name': 'name', 'type': 'string'},
        {'name': 'temperature', 'type': 'float'}
    ],
    'data': [
        [1, 'sensor1', 20.5],
        [2, 'sensor2', 25.0],
        [3, 'sensor3', 18.2]
    ]
}

# Encode to protobuf bytes (automatically calculates statistics)
encoded = pb_table.encode_table(table)

# Decode back to table format
decoded = pb_table.decode_table(encoded)

# Statistics are automatically included
temp_field = next(f for f in decoded['header'] if f['name'] == 'temperature')
print(f"Temperature stats: {temp_field['stats']}")
# Output: {'start': 20.5, 'end': 18.2, 'min': 18.2, 'max': 25.0, 'mean': 21.23}
```

### Verbose Format (Object-based)

```python
# Object format with named fields
verbose_table = {
    'header': [
        {'name': 'id', 'type': 'uint'},
        {'name': 'name', 'type': 'string'}
    ],
    'data': [
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'}
    ]
}

encoded = pb_table.encode_verbose(verbose_table)
decoded = pb_table.decode_verbose(encoded)
```

### Transform Example

```python
# Use transforms for data compression
table_with_transforms = {
    'header': [
        {
            'name': 'timestamp',
            'type': 'uint',
            'transform': {
                'offset': 1609459200,  # Unix timestamp base
                'multip': 1,
                'decimals': 0,
                'sequence': True       # Delta encoding
            }
        },
        {'name': 'value', 'type': 'float'}
    ],
    'data': [
        [1609459260, 100.5],  # Will be stored as delta from previous
        [1609459320, 101.2],
        [1609459380, 99.8]
    ]
}

encoded = pb_table.encode_table(table_with_transforms)
```

## API Reference

### Core Functions

#### `encode_table(obj, callback=None) -> bytes`
Encode table data (array format) to protobuf bytes.
- Automatically calculates statistics for numeric fields
- Applies transforms for data compression

#### `decode_table(buffer, callback=None) -> dict`
Decode table data (array format) from protobuf bytes.
- Restores original values from transforms
- Includes calculated statistics in header

#### `encode_verbose(obj, callback=None) -> bytes`
Encode table data (object format) to protobuf bytes.

#### `decode_verbose(buffer, callback=None) -> dict`
Decode table data (object format) from protobuf bytes.

### Utility Functions

#### `get_table(buffer, request, callback=None)`
Get specific rows without full decoding.
- `request`: int (single row) or list of ints (multiple rows)

#### `add_table(buffer, data, callback=None) -> bytes`
Add new rows to existing encoded data.

#### `get_index(buffer, callback=None) -> list`
Get byte positions for efficient random access.

### Statistics

Statistics are automatically calculated for numeric fields (`int`, `uint`, `float`) during encoding:

- **start**: First value in the dataset
- **end**: Last value in the dataset  
- **min**: Minimum value
- **max**: Maximum value
- **mean**: Average value

These provide bounds information and can be used for data validation or quick analysis without full decoding.

## Data Types

Supported field types:
- `string`: Text data
- `uint`: Unsigned integers (stored as int32 in protobuf)
- `int`: Signed integers (stored as sint32 in protobuf)
- `float`: Floating-point numbers
- `bool`: Boolean values

## Transform System

Transforms enable data compression for numeric fields:

- **offset**: Subtract a base value (useful for timestamps)
- **multip**: Multiply by a factor (useful for fixed-point decimals)
- **decimals**: Handle decimal precision
- **sequence**: Delta encoding (store differences between consecutive values)

## Cross-Language Compatibility

This implementation maintains wire format compatibility with the JavaScript version:
- Same protobuf schema
- Identical transform algorithms
- Compatible statistics calculation
- Matching API signatures

## Testing

Run the test suite:

```bash
python test_pb_table.py      # Basic functionality tests
python test_stats.py         # Statistics functionality tests
python pb_table.py          # Built-in basic test
```

## Development

### Modifying the Schema

1. Edit `head.proto`
2. Recompile: `protoc --python_out=. head.proto`
3. Update Python code if needed
4. Run tests to verify compatibility

### Performance Notes

- Statistics calculation adds minimal overhead during encoding
- Transform operations are optimized for common use cases
- Large datasets benefit from appropriate transforms and indexing

## License

"THE BEER-WARE LICENSE" (Revision 42):
Mappazzo (info@mappazzo.com) wrote this file. As long as you retain this notice you can do whatever you want with this stuff. If we meet some day, and you think this stuff is worth it, you can buy me a beer in return.
