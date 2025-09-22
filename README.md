# protobuf-table
## A dynamic protobuf implementation for structured table data

[software by mappazzo](https://www.mappazzo.com)

A JavaScript and Python library that provides dynamic Protocol Buffer implementation specifically designed for structured table data compression and serialization.

## Language Support

- **JavaScript/Node.js**: Full implementation with all features (see `javascript/` directory)
- **Python**: ✅ **Complete implementation** with full feature parity (see `python/` directory)

Both implementations provide identical functionality and maintain perfect data compatibility.

## Purpose

Enable efficient binary serialization of tabular data using Google's Protocol Buffers, with built-in compression optimizations for numeric data through transforms and delta encoding.

## Key Features

- **Dynamic Schema Generation**: Create protobuf schemas at runtime based on table headers
- **Multiple Data Formats**: Support both array-based and object-based data representations  
- **Compression Features**: Implement data transforms (offset, multiplication, decimals, sequencing) for optimal storage
- **Random Access**: Allow extraction of specific rows without full deserialization
- **Cross-Language Compatibility**: Data encoded in one language can be decoded in the other
- **Extensibility**: Support metadata and custom key-value pairs

## Quick Start

### JavaScript/Node.js
```bash
npm install --save protobuf-table
```

```javascript
const pbTable = require('protobuf-table');

const table = {
  header: [
    { name: 'location', type: 'string' },
    { name: 'total', type: 'uint' },
    { name: 'latitude', type: 'float' }
  ],
  data: [
    ['east street', 34324, -42.559355],
    ['work', 7344, -41.546799]
  ]
};

pbTable.encodeTable(table, (err, buffer) => {
  if (err) return console.log(err);
  console.log(`Encoded to ${buffer.length} bytes`);
  
  pbTable.decodeTable(buffer, (err, decoded) => {
    if (err) return console.log(err);
    console.log('Decoded:', decoded);
  });
});
```

### Python
```bash
cd python
pip install -r requirements.txt
```

```python
from pb_table import encode_table, decode_table, get_table, add_table

table = {
    'header': [
        {'name': 'location', 'type': 'string'},
        {'name': 'total', 'type': 'uint'},
        {'name': 'latitude', 'type': 'float'}
    ],
    'data': [
        ['east street', 34324, -42.559355],
        ['work', 7344, -41.546799]
    ]
}

# Encode and decode
encoded = encode_table(table)
decoded = decode_table(encoded)
print(f"Encoded to {len(encoded)} bytes")

# Random access - get specific row
first_row = get_table(encoded, 0)
print(f"First row: {first_row}")

# Add new data
new_data = [['home', 12345, -41.123456]]
expanded = add_table(encoded, new_data)
print(f"Added data, new size: {len(decode_table(expanded)['data'])} rows")
```

## Documentation

- **JavaScript**: See `javascript/README.md` for detailed JavaScript/Node.js documentation
- **Python**: See `python/README.md` for detailed Python documentation

## Language Compatibility

| Feature | JavaScript | Python | Status |
|---------|------------|--------|--------|
| Array format encoding/decoding | ✅ | ✅ | **Fully Compatible** |
| Object format encoding/decoding | ✅ | ✅ | **Fully Compatible** |
| Data transforms | ✅ | ✅ | **Fully Compatible** |
| Sequence transforms | ✅ | ✅ | **Fully Compatible** |
| Metadata support | ✅ | ✅ | **Fully Compatible** |
| Error handling | ✅ | ✅ | **Fully Compatible** |
| Callback API | ✅ | ✅ | **Fully Compatible** |
| Random access (`get`) | ✅ | ✅ | **Fully Compatible** |
| Data appending (`add`) | ✅ | ✅ | **Fully Compatible** |
| Buffer indexing | ✅ | ✅ | **Fully Compatible** |

Data encoded with either implementation maintains perfect data integrity and cross-language compatibility.

## Building and Testing

### JavaScript
```bash
cd javascript
npm install
npm run build
npm run test
```

### Python
```bash
cd python
pip install -r requirements.txt
python test_pb_table.py
```

## License

"THE BEER-WARE LICENSE" (Revision 42):
[Mappazzo](mailto:info@mappazzo.com) wrote this file. As long as you retain this notice you
can do whatever you want with this stuff. If we meet some day, and you think
this stuff is worth it, you can buy me a beer in return. Cheers, Kelly Norris
