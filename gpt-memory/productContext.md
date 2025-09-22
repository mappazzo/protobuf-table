# Product Context: protobuf-table

## Why This Project Exists

### Problem Statement
JavaScript applications often need to store and transmit large amounts of structured tabular data. Traditional approaches like JSON serialization result in:
- **Large file sizes**: JSON's verbose text format includes repeated field names
- **Slow parsing**: Text-based formats require string parsing overhead
- **Memory inefficiency**: Full data structures must be loaded into memory
- **Limited compression**: Standard compression doesn't leverage data patterns

### Target Use Cases
1. **Time-series Data**: Sensor readings, financial data, IoT measurements
2. **Scientific Datasets**: Research data with repeated measurements
3. **Analytics Data**: Large datasets for processing and analysis
4. **Data Archival**: Long-term storage of structured information
5. **Data Transmission**: Efficient network transfer of tabular data

### User Problems Solved
- **Data Scientists**: Need efficient storage for large datasets
- **IoT Developers**: Require compact data transmission formats
- **Backend Engineers**: Want fast serialization for database storage
- **Analytics Teams**: Need quick access to specific data subsets

## How It Should Work

### User Experience Goals
1. **Simple API**: Intuitive encode/decode operations
2. **Flexible Input**: Accept data as arrays or objects
3. **Efficient Storage**: Significant size reduction over JSON
4. **Fast Access**: Quick retrieval of specific data rows
5. **Reliable**: Perfect data integrity after encode/decode cycles

### Core User Journey
```javascript
// 1. User defines table structure
const table = {
  header: [
    { name: 'timestamp', type: 'uint' },
    { name: 'temperature', type: 'float' },
    { name: 'location', type: 'string' }
  ],
  data: [
    [1634567890, 23.5, 'sensor_01'],
    [1634567950, 24.1, 'sensor_01'],
    [1634568010, 23.8, 'sensor_01']
  ]
};

// 2. Encode to binary format
pbTable.encode(table, (err, buffer) => {
  // 3. Store or transmit compact binary data
  console.log('Size reduction:', originalSize / buffer.length);
  
  // 4. Later: decode when needed
  pbTable.decode(buffer, (err, restored) => {
    // 5. Use restored data identical to original
  });
});
```

### Advanced Usage Patterns
```javascript
// Compression for numeric data
header: [{
  name: 'latitude',
  type: 'int',
  transform: {
    offset: -42.0,      // Shift values closer to zero
    multip: 1000000,    // Convert to integers
    sequence: true      // Store deltas between values
  }
}]

// Random access without full decode
pbTable.get(buffer, [0, 5, 10], (err, rows) => {
  // Only requested rows are decoded
});

// Append data to existing buffer
pbTable.add(buffer, newRows, (err, expandedBuffer) => {
  // Original buffer + new data
});
```

## Value Proposition

### Primary Benefits
1. **Storage Efficiency**: 50-90% size reduction typical
2. **Performance**: Fast binary serialization vs JSON parsing
3. **Memory Optimization**: Decode only needed data rows
4. **Data Integrity**: Built-in validation and error handling
5. **Flexibility**: Multiple data formats and access patterns

### Competitive Advantages
- **Dynamic Schemas**: No need to predefine .proto files
- **JavaScript Native**: Designed specifically for JS/Node.js ecosystem
- **Table Optimized**: Purpose-built for tabular data patterns
- **Transform System**: Built-in numeric compression strategies
- **Random Access**: Efficient partial data retrieval

## Success Metrics

### Technical Performance
- **Compression Ratio**: Target 2-10x size reduction vs JSON
- **Encoding Speed**: Sub-millisecond for typical table sizes
- **Memory Usage**: Constant memory overhead regardless of table size
- **Decode Performance**: Fast restoration of original data

### User Experience
- **API Simplicity**: Single-function encode/decode operations
- **Error Clarity**: Descriptive error messages for debugging
- **Documentation Quality**: Clear examples and usage patterns
- **Reliability**: Zero data loss in encode/decode cycles

### Adoption Indicators
- **GitHub Stars**: Community interest and validation
- **NPM Downloads**: Active usage in production applications
- **Issue Resolution**: Responsive maintenance and bug fixes
- **Feature Requests**: User-driven enhancement priorities

## Integration Philosophy

### Design Principles
1. **Convention over Configuration**: Sensible defaults, minimal setup
2. **Backward Compatibility**: Existing buffers remain readable
3. **Error Transparency**: Clear feedback when operations fail
4. **Performance First**: Optimize for speed and memory efficiency
5. **Developer Experience**: Intuitive API that "just works"

### Ecosystem Fit
- **Node.js Standard**: Follows established callback patterns
- **Protocol Buffers**: Leverages proven serialization technology
- **JavaScript Idioms**: Natural integration with existing codebases
- **Testing Culture**: Comprehensive test coverage for reliability
