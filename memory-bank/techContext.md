# Technical Context: protobuf-table

## Technology Stack

### JavaScript Implementation
#### Core Dependencies
- **protobufjs**: `^6.8.0` - Protocol Buffer implementation for JavaScript
  - Purpose: Binary serialization engine
  - Features: Dynamic schema generation, Reader/Writer classes
  - Why chosen: Mature, well-maintained, JavaScript-native

#### Development Dependencies
- **Babel**: ES6+ transpilation and minification
  - `babel-cli`: `^6.26.0` - Command line interface
  - `babel-preset-env`: `^1.6.0` - Environment-specific transpilation
  - `babel-preset-minify`: `^0.2.0` - Code minification
  - `babel-minify`: `^0.2.0` - Minification plugin
- **ESLint**: `^4.5.0` - Code linting and style enforcement
- **cross-env**: `^5.0.5` - Cross-platform environment variables
- **autoprefixer**: `^6` - CSS vendor prefixing (legacy dependency)

#### Runtime Environment
- **Target**: Node.js (primary), Browser (secondary)
- **JavaScript Version**: ES5 (transpiled from ES6+)
- **Module System**: CommonJS (`module.exports`)
- **Callback Pattern**: Node.js error-first callbacks

### Python Implementation
#### Core Dependencies
- **protobuf**: `>=4.21.0` - Google's Protocol Buffer library for Python
  - Purpose: Binary serialization engine and dynamic schema generation
  - Features: DescriptorProto, MessageFactory, DescriptorPool
  - Why chosen: Official Google implementation, comprehensive feature set

#### Runtime Environment
- **Target**: Python 3.7+ (type hints support required)
- **Module System**: Standard Python imports
- **API Pattern**: Function-based with optional callback support
- **Type Safety**: Full type hints for better IDE support and validation

## Development Setup

### JavaScript Build System
```json
{
  "build-dev": "babel javascript/src/pbTable.js -o javascript/dist/pbTable.js",
  "build-min": "cross-env BABEL_ENV=production babel javascript/src/pbTable.js -o javascript/dist/pbTable-min.js",
  "build": "npm run build-dev && npm run build-min",
  "test": "node javascript/test/index.js"
}
```

### Python Development Setup
```bash
# Install dependencies
cd python
pip install -r requirements.txt

# Run tests
python test_pb_table.py

# Run basic functionality test
python pb_table.py
```

### File Structure
```
protobuf-table/
├── javascript/         # JavaScript implementation
│   ├── src/
│   │   ├── pbTable.js  # Main JavaScript implementation
│   │   └── head.proto  # Protocol Buffer schema
│   ├── dist/           # Built files (generated)
│   │   ├── pbTable.js  # Development build
│   │   └── pbTable-min.js # Production build
│   ├── test/
│   │   ├── index.js    # JavaScript test runner
│   │   ├── basic-test.js # Core functionality tests
│   │   ├── compress-test.js # Compression tests
│   │   ├── smallTable.js # Simple test data
│   │   └── compressTable.js # Complex test data
│   ├── package.json    # Node.js package configuration
│   ├── .babelrc        # Babel transpilation config
│   ├── .eslintrc.js    # ESLint configuration
│   └── .eslintignore   # ESLint ignore patterns
├── python/             # Python implementation
│   ├── pb_table.py     # Main Python implementation
│   ├── test_pb_table.py # Python test suite
│   ├── README.md       # Python documentation
│   └── requirements.txt # Python dependencies
├── examples/           # Usage examples
└── memory-bank/        # Documentation
```

### JavaScript Configuration
#### Babel Configuration
```javascript
// .babelrc
{
  "presets": ["env"],
  "env": {
    "production": {
      "presets": ["minify"]
    }
  }
}
```

#### ESLint Configuration
```javascript
// .eslintrc.js
module.exports = {
  "extends": "standard",
  "rules": {
    // Custom rules for project consistency
  }
}
```

### Python Configuration
#### Requirements
```
# requirements.txt
protobuf>=4.21.0
```

#### Type Checking Support
- Full type hints throughout codebase
- Compatible with mypy for static type checking
- IDE support for autocompletion and error detection

## Technical Constraints

### 1. Protocol Buffer Limitations
- **Schema Flexibility**: Must work within protobuf type system
- **Field Numbering**: Sequential field IDs required
- **Type Mapping**: Limited language → protobuf type conversions
- **Backward Compatibility**: Schema changes must not break existing buffers
- **Cross-Language Compatibility**: Wire format must be identical between implementations

### 2. JavaScript Environment
- **Memory Management**: No manual memory control
- **Number Precision**: IEEE 754 floating point limitations
- **Integer Range**: Safe integer limits for transforms
- **Callback Hell**: Nested callback complexity

### 3. Python Environment
- **Performance Overhead**: Generally slower than JavaScript for I/O operations
- **Memory Usage**: Higher memory overhead than JavaScript
- **GIL Limitations**: Global Interpreter Lock affects threading
- **Protobuf Library Differences**: Different API patterns than JavaScript protobufjs

### 4. Performance Constraints
- **Single-threaded**: No parallel processing in either language
- **Memory Pressure**: Large datasets must stream
- **CPU Intensive**: Transform calculations on main thread
- **I/O Blocking**: Synchronous operations block event loop (JavaScript)

### 5. Compatibility Requirements
- **Node.js Versions**: Support LTS versions
- **Python Versions**: Support 3.7+ (type hints requirement)
- **Browser Support**: IE11+ for browser builds (JavaScript only)
- **Module Systems**: CommonJS (JavaScript), standard imports (Python)
- **API Stability**: Maintain backward compatibility
- **Cross-Language Data**: Buffers must be interchangeable between languages

## Development Patterns

### 1. JavaScript Error Handling Strategy
```javascript
// Consistent error-first callback pattern
function operation(input, callback) {
  try {
    // Validate input
    if (!input) {
      return callback(new Error('Invalid input'));
    }
    
    // Perform operation
    const result = processInput(input);
    callback(null, result);
  } catch (error) {
    callback(error);
  }
}
```

### 2. Python Error Handling Strategy
```python
# Exception-based with optional callback support
def operation(input_data, callback=None):
    try:
        # Validate input
        if not input_data:
            raise ProtobufTableError('Invalid input')
        
        # Perform operation
        result = process_input(input_data)
        
        if callback:
            callback(None, result)
        return result
    except Exception as e:
        if callback:
            callback(e, None)
            return None
        raise
```

### 3. Cross-Language Validation Pattern
```javascript
// JavaScript validation
function validateTable(table) {
  if (!table.header || !Array.isArray(table.header)) {
    throw new Error('Table must have header array');
  }
  
  if (!table.data || !Array.isArray(table.data)) {
    throw new Error('Table must have data array');
  }
}
```

```python
# Python validation (equivalent)
def validate_table(table):
    if not table.get('header') or not isinstance(table['header'], list):
        raise ProtobufTableError('Table must have header array')
    
    if not table.get('data') or not isinstance(table['data'], list):
        raise ProtobufTableError('Table must have data array')
```

### 4. Transform Application (Cross-Language)
```javascript
// JavaScript transform processing
function applyTransform(value, lastValue, transform) {
  if (!transform) return value;
  
  let result = value;
  
  // Apply offset
  if (transform.offset !== undefined) {
    result -= transform.offset;
  }
  
  // Apply sequence delta
  if (transform.sequence && lastValue !== null) {
    result -= lastValue;
  }
  
  // Apply multiplication and decimals
  if (transform.multip) {
    result *= transform.multip;
  }
  
  if (transform.decimals) {
    result *= Math.pow(10, transform.decimals);
  }
  
  return parseInt(result);
}
```

```python
# Python transform processing (equivalent)
@staticmethod
def parse(value, last_val, transform):
    if value is None:
        value = 0
    
    offset = transform.get('offset', 0)
    multip = transform.get('multip', 1)
    decimals = transform.get('decimals', 0)
    sequence = transform.get('sequence', False)
    
    if sequence and last_val is not None:
        value -= last_val
    else:
        value -= offset
        
    stored_value = value * multip
    stored_value = stored_value * (10 ** decimals)
    return int(stored_value)
```

## Tool Usage Patterns

### 1. JavaScript protobufjs Integration
```javascript
// Dynamic schema creation
const Root = pbuf.Root;
const root = new Root();
root.addJSON(schemaDefinition);
const MessageType = root.lookupType('MessageName');

// Encoding
const message = MessageType.create(data);
const buffer = MessageType.encode(message).finish();

// Decoding
const decoded = MessageType.decode(buffer);
```

### 2. Python protobuf Integration
```python
# Dynamic schema creation
from google.protobuf.descriptor_pb2 import DescriptorProto, FieldDescriptorProto
from google.protobuf.message_factory import MessageFactory
from google.protobuf.descriptor_pool import DescriptorPool

pool = DescriptorPool()
factory = MessageFactory(pool)

# Create descriptor programmatically
desc = DescriptorProto()
desc.name = 'MessageName'
# Add fields...

pool.Add(desc)
MessageType = factory.GetPrototype(pool.FindMessageTypeByName('MessageName'))

# Encoding
message = MessageType()
# Set fields...
buffer = message.SerializeToString()

# Decoding
decoded = MessageType()
decoded.ParseFromString(buffer)
```

### 3. Buffer Management
#### JavaScript
```javascript
// Reader for parsing
const Reader = pbuf.Reader;
const reader = new Reader(buffer);

// Writer for building
const Writer = pbuf.Writer;
const writer = new Writer();
MessageType.encode(data, writer);
const result = writer.finish();
```

#### Python
```python
# Buffer handling with length delimiters
from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32

# Encoding with length delimiter
data = message.SerializeToString()
delimited_data = _VarintBytes(len(data)) + data

# Decoding with length delimiter
length, offset = _DecodeVarint32(buffer, 0)
message_data = buffer[offset:offset + length]
```

### 4. Type System Mapping
#### JavaScript
```javascript
const types = {
  'string': 'string',
  'uint': 'int32',      // Unsigned → signed for protobuf
  'int': 'sint32',      // Signed with zigzag encoding
  'float': 'float',     // 32-bit floating point
  'bool': 'bool'        // Boolean type
};
```

#### Python
```python
from google.protobuf.descriptor_pb2 import FieldDescriptorProto

TYPES = {
    'string': FieldDescriptorProto.TYPE_STRING,
    'uint': FieldDescriptorProto.TYPE_INT32,
    'int': FieldDescriptorProto.TYPE_SINT32,
    'float': FieldDescriptorProto.TYPE_FLOAT,
    'bool': FieldDescriptorProto.TYPE_BOOL
}
```

## Testing Strategy

### 1. Test Structure
- **Unit Tests**: Individual function testing
- **Integration Tests**: End-to-end encode/decode cycles
- **Compression Tests**: Transform validation
- **Performance Tests**: Large dataset handling

### 2. Test Data Patterns
```javascript
// Simple table for basic tests
const smallTable = {
  header: [
    { name: 'id', type: 'uint' },
    { name: 'name', type: 'string' }
  ],
  data: [
    [1, 'test'],
    [2, 'example']
  ]
};

// Complex table with transforms
const compressTable = {
  header: [
    {
      name: 'latitude',
      type: 'int',
      transform: {
        offset: -42,
        multip: 1000000,
        sequence: true
      }
    }
  ],
  data: [/* compressed data */]
};
```

### 3. Validation Approach
```javascript
// Round-trip testing
pbTable.encode(input, (err, buffer) => {
  pbTable.decode(buffer, (err, output) => {
    assert.deepEqual(input, output);
  });
});
```

## Deployment Considerations

### 1. Distribution Formats
- **Development**: `dist/pbTable.js` - Readable, debuggable
- **Production**: `dist/pbTable-min.js` - Minified, optimized
- **NPM Package**: Both formats included

### 2. Version Management
- **Semantic Versioning**: Major.Minor.Patch
- **Backward Compatibility**: Maintain API stability
- **Buffer Compatibility**: Old buffers readable by new versions

### 3. Performance Monitoring
- **Bundle Size**: Track minified size growth
- **Memory Usage**: Monitor heap allocation patterns
- **Encoding Speed**: Benchmark typical operations
- **Compression Ratio**: Measure effectiveness vs JSON
