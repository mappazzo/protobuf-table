# protobuf-table JavaScript Implementation

JavaScript/Node.js implementation of the protobuf-table library for structured table data compression and serialization.

## Features

- **Dynamic Schema Generation**: Create protobuf schemas at runtime based on table headers
- **Multiple Data Formats**: Support both array-based and object-based data representations
- **Compression Features**: Implement data transforms (offset, multiplication, decimals, sequencing) for optimal storage
- **Random Access**: Allow extraction of specific rows without full deserialization
- **Data Appending**: Add new rows to existing encoded buffers
- **Node.js Compatibility**: Callback-based API following Node.js conventions

## Installation

### NPM Package
```bash
npm install --save protobuf-table
```

```javascript
const pbTable = require('protobuf-table');
```

### Standalone
```javascript
const pbTable = require('./dist/pbTable-min.js');
```

## API Reference

### Core Functions

#### Array Format (Default)

**`encodeTable(obj, callback)`** / **`encode(obj, callback)`**
- Encode table data in array format to protobuf buffer
- **Parameters:**
  - `obj`: Object with 'header' and 'data' keys
  - `callback`: Function (error, buffer)
- **Returns:** Buffer containing encoded data

**`decodeTable(buffer, callback)`** / **`decode(buffer, callback)`**
- Decode table data from protobuf buffer to array format
- **Parameters:**
  - `buffer`: Buffer containing encoded data
  - `callback`: Function (error, table)
- **Returns:** Object with decoded table data

#### Object Format (Verbose)

**`encodeVerbose(obj, callback)`**
- Encode table data in object format to protobuf buffer
- **Parameters:**
  - `obj`: Object with 'header' and 'data' keys (data as array of objects)
  - `callback`: Function (error, buffer)
- **Returns:** Buffer containing encoded data

**`decodeVerbose(buffer, callback)`**
- Decode table data from protobuf buffer to object format
- **Parameters:**
  - `buffer`: Buffer containing encoded data
  - `callback`: Function (error, table)
- **Returns:** Object with decoded table data (data as array of objects)

#### Random Access

**`get(buffer, request, callback)`** / **`getTable(buffer, request, callback)`**
- Extract specific rows from encoded buffer (array format)
- **Parameters:**
  - `buffer`: Buffer containing encoded data
  - `request`: Integer or array of integers (row indices)
  - `callback`: Function (error, data)
- **Returns:** Array of requested rows

**`getVerbose(buffer, request, callback)`**
- Extract specific rows from encoded buffer (object format)
- **Parameters:**
  - `buffer`: Buffer containing encoded data
  - `request`: Integer or array of integers (row indices)
  - `callback`: Function (error, data)
- **Returns:** Array of requested rows as objects

#### Data Appending

**`add(buffer, data, callback)`** / **`addTable(buffer, data, callback)`**
- Append new rows to existing encoded buffer (array format)
- **Parameters:**
  - `buffer`: Buffer containing encoded data
  - `data`: Array of new rows to append
  - `callback`: Function (error, newBuffer)
- **Returns:** New buffer with appended data

**`addVerbose(buffer, data, callback)`**
- Append new rows to existing encoded buffer (object format)
- **Parameters:**
  - `buffer`: Buffer containing encoded data
  - `data`: Array of new row objects to append
  - `callback`: Function (error, newBuffer)
- **Returns:** New buffer with appended data

#### Indexing

**`getIndex(buffer, callback)`**
- Generate byte-position index for random access
- **Parameters:**
  - `buffer`: Buffer containing encoded data
  - `callback`: Function (error, index)
- **Returns:** Index mapping row numbers to byte positions

## Usage Examples

### Basic Array Format

```javascript
const pbTable = require('protobuf-table');

const table = {
  header: [
    { name: 'id', type: 'uint' },
    { name: 'name', type: 'string' },
    { name: 'value', type: 'float' },
    { name: 'active', type: 'bool' }
  ],
  data: [
    [1, 'sensor1', 23.5, true],
    [2, 'sensor2', 24.1, false],
    [3, 'sensor3', 22.8, true]
  ]
};

pbTable.encodeTable(table, (err, buffer) => {
  if (err) return console.log(err);
  console.log(`Encoded ${table.data.length} rows to ${buffer.length} bytes`);
  
  pbTable.decodeTable(buffer, (err, decoded) => {
    if (err) return console.log(err);
    console.log(`Decoded ${decoded.data.length} rows`);
    console.log('Data matches:', JSON.stringify(table.data) === JSON.stringify(decoded.data));
  });
});
```

### Object Format (Verbose)

```javascript
const table = {
  header: [
    { name: 'id', type: 'uint' },
    { name: 'name', type: 'string' },
    { name: 'temperature', type: 'float' }
  ],
  data: [
    { id: 1, name: 'sensor1', temperature: 23.5 },
    { id: 2, name: 'sensor2', temperature: 24.1 },
    { id: 3, name: 'sensor3', temperature: 22.8 }
  ]
};

pbTable.encodeVerbose(table, (err, buffer) => {
  if (err) return console.log(err);
  
  pbTable.decodeVerbose(buffer, (err, decoded) => {
    if (err) return console.log(err);
    console.log('Decoded verbose data:', decoded.data);
  });
});
```

### Data Transforms for Compression

```javascript
const table = {
  header: [
    {
      name: 'timestamp',
      type: 'uint',
      transform: {
        offset: 1609459200,  // Base timestamp
        multip: 1,
        decimals: 0
      }
    },
    {
      name: 'latitude',
      type: 'int',
      transform: {
        offset: -42,
        multip: 1000000,  // Store as micro-degrees
        decimals: 6,
        sequence: false
      }
    },
    {
      name: 'temperature',
      type: 'int',
      transform: {
        offset: 0,
        multip: 100,  // Store as centi-degrees
        decimals: 2
      }
    }
  ],
  data: [
    [1609459260, -41.123456, 23.45],
    [1609459320, -41.123789, 23.67],
    [1609459380, -41.124012, 23.89]
  ]
};

pbTable.encodeTable(table, (err, buffer) => {
  if (err) return console.log(err);
  
  pbTable.decodeTable(buffer, (err, decoded) => {
    if (err) return console.log(err);
    console.log('Transform round-trip successful:', 
      JSON.stringify(table.data) === JSON.stringify(decoded.data));
  });
});
```

### Sequence Transforms (Delta Encoding)

```javascript
const table = {
  header: [
    {
      name: 'counter',
      type: 'uint',
      transform: {
        sequence: true  // Delta encoding
      }
    },
    {
      name: 'value',
      type: 'int',
      transform: {
        offset: 1000,
        sequence: true
      }
    }
  ],
  data: [
    [100, 1010],  // Stored as: 100, 10
    [105, 1015],  // Stored as: 5, 5
    [112, 1008],  // Stored as: 7, -7
    [120, 1025]   // Stored as: 8, 17
  ]
};

pbTable.encodeTable(table, (err, buffer) => {
  if (err) return console.log(err);
  
  pbTable.decodeTable(buffer, (err, decoded) => {
    if (err) return console.log(err);
    console.log('Sequence transform successful');
  });
});
```

### Metadata Support

```javascript
const table = {
  meta: {
    filename: 'sensor_data.pb',
    owner: 'data_team',
    link: 'www.example.com',
    comment: 'Hourly sensor readings'
  },
  header: [
    { name: 'id', type: 'uint' },
    { name: 'value', type: 'float' }
  ],
  custom_key: 'custom_value',
  data: [
    [1, 1.1],
    [2, 2.2]
  ]
};

pbTable.encodeTable(table, (err, buffer) => {
  if (err) return console.log(err);
  
  pbTable.decodeTable(buffer, (err, decoded) => {
    if (err) return console.log(err);
    console.log('Metadata preserved:', decoded.meta);
    console.log('Custom key preserved:', decoded.custom_key);
  });
});
```

### Random Access

```javascript
// First encode some data
const table = {
  header: [
    { name: 'id', type: 'uint' },
    { name: 'value', type: 'string' }
  ],
  data: [
    [1, 'first'],
    [2, 'second'],
    [3, 'third'],
    [4, 'fourth'],
    [5, 'fifth']
  ]
};

pbTable.encodeTable(table, (err, buffer) => {
  if (err) return console.log(err);
  
  // Get single row
  pbTable.get(buffer, 2, (err, row) => {
    if (err) return console.log(err);
    console.log('Row 2:', row); // [3, 'third']
  });
  
  // Get multiple rows
  pbTable.get(buffer, [0, 2, 4], (err, rows) => {
    if (err) return console.log(err);
    console.log('Rows 0, 2, 4:', rows);
    // [[1, 'first'], [3, 'third'], [5, 'fifth']]
  });
  
  // Get verbose format
  pbTable.getVerbose(buffer, [1, 3], (err, rows) => {
    if (err) return console.log(err);
    console.log('Verbose rows:', rows);
    // [{ id: 2, value: 'second' }, { id: 4, value: 'fourth' }]
  });
});
```

### Data Appending

```javascript
// Start with initial data
const initialTable = {
  header: [
    { name: 'id', type: 'uint' },
    { name: 'name', type: 'string' }
  ],
  data: [
    [1, 'first'],
    [2, 'second']
  ]
};

pbTable.encodeTable(initialTable, (err, buffer) => {
  if (err) return console.log(err);
  
  // Add more rows
  const newRows = [
    [3, 'third'],
    [4, 'fourth']
  ];
  
  pbTable.add(buffer, newRows, (err, newBuffer) => {
    if (err) return console.log(err);
    
    pbTable.decodeTable(newBuffer, (err, decoded) => {
      if (err) return console.log(err);
      console.log('Total rows after append:', decoded.data.length); // 4
      console.log('All data:', decoded.data);
    });
  });
});
```

### Buffer Indexing

```javascript
pbTable.encodeTable(table, (err, buffer) => {
  if (err) return console.log(err);
  
  pbTable.getIndex(buffer, (err, index) => {
    if (err) return console.log(err);
    console.log('Row byte positions:', index);
    // { 0: 45, 1: 67, 2: 89, ... }
  });
});
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

**Note**: Sequence transforms prevent random access to specific rows.

## Error Handling

All functions use Node.js-style error-first callbacks:

```javascript
pbTable.encodeTable(invalidData, (err, buffer) => {
  if (err) {
    console.log('Encoding error:', err.message);
    return;
  }
  // Success case
});
```

## Building and Testing

### Build
```bash
npm run build
```

### Test
```bash
npm run test
```

### Development
```bash
npm install
npm run build
npm run test
```

## Performance Considerations

- **Memory Usage**: Large datasets are processed in memory; consider chunking for very large tables
- **Transform Overhead**: Numeric transforms add CPU overhead but provide significant compression
- **Random Access**: Most efficient with indexed buffers; use `getIndex()` for repeated access
- **Sequence Limitations**: Sequence transforms prevent random access to specific rows

## Browser Compatibility

The library is primarily designed for Node.js but can be used in browsers with appropriate bundling:

- Uses CommonJS modules (require/exports)
- Babel transpilation available for ES5 compatibility
- Minified version available in `dist/` directory

## License

"THE BEER-WARE LICENSE" (Revision 42):
Mappazzo (info@mappazzo.com) wrote this file. As long as you retain this notice you can do whatever you want with this stuff. If we meet some day, and you think this stuff is worth it, you can buy me a beer in return. Cheers, Kelly Norris

## Contributing

When contributing to the JavaScript implementation:

- Follow existing code style and patterns
- Ensure all tests pass
- Add tests for new features
- Maintain API compatibility with Python implementation
- Update documentation for new features
