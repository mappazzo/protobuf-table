# Protobuf-Table

A high-performance, cross-language table serialization library using Protocol Buffers. Efficiently compress and transmit tabular data with support for transforms, statistics, and cross-platform compatibility.

## 🚀 Features

- **Cross-Language Support**: JavaScript and Python implementations with full compatibility
- **High Compression**: 2-4x compression ratios with intelligent transforms
- **Advanced Transforms**: Offset, multiplication, decimal precision, and sequence (delta) encoding
- **Random Access**: Extract specific rows without full deserialization
- **Statistics**: Automatic calculation and preservation of field statistics
- **Dual Formats**: Support for both array-based and object-based data representations
- **Production Ready**: Comprehensive error handling and validation

## 📊 Performance

```
JSON → Protobuf-Table Compression Results:
• Complex dataset: 2.31:1 ratio (56.7% reduction)
• Transform dataset: 3.08:1 ratio (67.5% reduction)
• Space savings: 900-1000 bytes per 1.6KB dataset
```

## 🛠 Installation

### JavaScript (Node.js)
```bash
npm install protobuf-table
```

### Python
```bash
pip install protobuf-table
# or
python -m pip install -r python/requirements.txt
```

## 📖 Quick Start

### JavaScript
```javascript
const { encode, decode } = require('./javascript/src/pbTable');

// Your table data
const table = {
  header: [
    { name: 'id', type: 'uint' },
    { name: 'name', type: 'string' },
    { name: 'value', type: 'float' }
  ],
  data: [
    [1, 'sensor1', 23.5],
    [2, 'sensor2', 24.1],
    [3, 'sensor3', 22.8]
  ]
};

// Encode to binary
const encoded = encode(table);
console.log(`Compressed: ${encoded.length} bytes`);

// Decode back to table
const decoded = decode(encoded);
console.log('Data restored:', decoded.data);
```

### Python
```python
from python.pb_table import encode_table, decode_table

# Your table data
table = {
    'header': [
        {'name': 'id', 'type': 'uint'},
        {'name': 'name', 'type': 'string'},
        {'name': 'value', 'type': 'float'}
    ],
    'data': [
        [1, 'sensor1', 23.5],
        [2, 'sensor2', 24.1],
        [3, 'sensor3', 22.8]
    ]
}

# Encode to binary
encoded = encode_table(table)
print(f"Compressed: {len(encoded)} bytes")

# Decode back to table
decoded = decode_table(encoded)
print("Data restored:", decoded['data'])
```

## 🔧 Advanced Features

### Transform Optimization
Use the Python compression optimizer to find the best transform settings:

```bash
# Analyze your data for optimal compression
python python/pb_table_optimizer.py your_data.json

# Save optimal configuration
python python/pb_table_optimizer.py your_data.json --output-config config.json
```

### Transforms for Better Compression
```javascript
// Time-series data with sequence transforms
const timeSeriesTable = {
  header: [
    { 
      name: 'timestamp', 
      type: 'uint',
      transform: { offset: 0, multip: 1, decimals: 0, sequence: true }
    },
    { 
      name: 'temperature', 
      type: 'float',
      transform: { offset: 20, multip: 100, decimals: 2, sequence: false }
    }
  ],
  data: [
    [1609459200, 23.45],
    [1609459260, 23.67],  // Delta: +60 seconds
    [1609459320, 23.89]   // Delta: +60 seconds
  ]
};
```

### Random Access
```python
# Get specific rows without full decoding
from python.pb_table import encode_table, get_table

encoded = encode_table(table)

# Get single row
row = get_table(encoded, 1)  # Second row

# Get multiple rows
rows = get_table(encoded, [0, 2])  # First and third rows
```

## 📁 Project Structure

```
protobuf-table/
├── README.md                    # This file
├── javascript/                  # JavaScript implementation
│   ├── src/pbTable.js          # Main library
│   ├── test/                   # Test suite
│   └── README.md               # JavaScript-specific docs
├── python/                     # Python implementation
│   ├── pb_table.py             # Main library
│   ├── pb_table_optimizer.py   # Compression optimizer
│   ├── test/                   # Test suite
│   └── README.md               # Python-specific docs
├── testdata/                   # Sample data files
└── examples/                   # Usage examples
```

## 🧪 Testing

### JavaScript
```bash
cd javascript
npm test
```

### Python
```bash
cd python
python test/test_pb_table.py
```

### Cross-Platform Compatibility
```bash
# Test JavaScript → Python compatibility
python python/test/test_pb_table.py cross
```

## 📈 Compression Optimization

The library includes an intelligent compression optimizer that analyzes your data and recommends optimal transform settings:

### Automatic Analysis
```bash
python python/pb_table_optimizer.py testdata/complex_test_suite.json --verbose
```

### Results Example
```
🏆 Best configuration: timestamp_sequence
   Achieves 2.31:1 compression ratio
   Saves 938 bytes (56.7% reduction)
   0.3% better than baseline (2 bytes saved)
   Recommended transforms: {'timestamp': {'offset': 0, 'multip': 1, 'decimals': 0, 'sequence': True}}
```

## 🔄 Cross-Language Compatibility

Full compatibility between JavaScript and Python implementations:

- ✅ **JavaScript → Python**: Decode JavaScript-encoded data with Python
- ✅ **Python → JavaScript**: Decode Python-encoded data with JavaScript
- ✅ **Wire Format**: Identical binary format across languages
- ✅ **Data Integrity**: Perfect round-trip fidelity

## 📊 Data Types Supported

| Type | JavaScript | Python | Description |
|------|------------|--------|-------------|
| `uint` | number | int | Unsigned integer |
| `int` | number | int | Signed integer |
| `float` | number | float | Floating point |
| `string` | string | str | Text data |
| `bool` | boolean | bool | True/false |

## 🎯 Use Cases

- **IoT Data**: Compress sensor readings with time-series optimization
- **Analytics**: Efficient storage and transmission of tabular data
- **APIs**: Reduce bandwidth with binary table formats
- **Data Pipelines**: Cross-language data exchange
- **Real-time Systems**: Fast serialization/deserialization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure cross-language compatibility
5. Submit a pull request

## 📄 License

"THE BEER-WARE LICENSE" (Revision 42):
Mappazzo (info@mappazzo.com) wrote this file. As long as you retain this notice you can do whatever you want with this stuff. If we meet some day, and you think this stuff is worth it, you can buy me a beer in return.

## 🔗 Links

- [JavaScript Documentation](javascript/README.md)
- [Python Documentation](python/README.md)
- [Examples](examples/)
- [Test Data](testdata/)

---

**Built with ❤️ for efficient data serialization**
