# System Patterns: protobuf-table

## System Architecture

### High-Level Design
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Data     │───▶│  protobuf-table  │───▶│  Binary Buffer  │
│  (JS Objects)   │    │    Library       │    │   (Compressed)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   protobufjs     │
                       │  (Core Engine)   │
                       └──────────────────┘
```

### Core Components

#### 1. Header Management System
- **Purpose**: Define and serialize table schemas
- **Key Functions**: `encodeHeader()`, `decodeHeader()`
- **Protocol**: Static protobuf schema for header structure
- **Features**: Metadata support, custom key-value pairs

#### 2. Dynamic Protocol Generation
- **Purpose**: Create protobuf schemas at runtime
- **Key Function**: `protocolFromHeader()`
- **Process**: Header → JSON Schema → protobuf Root
- **Validation**: Type checking and field verification

#### 3. Data Transformation Engine
- **Purpose**: Compress numeric data before encoding
- **Key Object**: `transformInteger`
- **Operations**: Offset, multiplication, decimal handling, sequencing
- **Reversibility**: Perfect reconstruction of original values

#### 4. Buffer Management
- **Purpose**: Handle binary data operations
- **Components**: Reader/Writer from protobufjs
- **Features**: Delimited encoding, buffer concatenation
- **Indexing**: Byte-position tracking for random access

## Key Technical Decisions

### 1. Dynamic Schema Generation
**Decision**: Generate protobuf schemas at runtime instead of static .proto files
**Rationale**: 
- Flexibility for varying table structures
- No build-time compilation required
- JavaScript-native development experience
**Trade-offs**: Slight runtime overhead vs development simplicity

### 2. Dual Data Format Support
**Decision**: Support both array and object data representations
**Implementation**:
- Array format: `[value1, value2, value3]`
- Object format: `{field1: value1, field2: value2}`
**Rationale**: Different use cases prefer different formats
**API Pattern**: Separate methods (`encodeTable` vs `encodeVerbose`)

### 3. Transform System Architecture
**Decision**: Built-in numeric compression transforms
**Components**:
```javascript
transform: {
  offset: number,    // Baseline subtraction
  multip: number,    // Multiplication factor  
  decimals: number,  // Decimal precision
  sequence: boolean  // Delta encoding
}
```
**Benefits**: Significant compression for numeric data
**Limitation**: Sequence transforms prevent random access

### 4. Callback-Based API
**Decision**: Node.js-style error-first callbacks
**Pattern**: `function(error, result)`
**Rationale**: Consistency with Node.js ecosystem
**Alternative Considered**: Promises (rejected for backward compatibility)

## Design Patterns

### 1. Protocol Factory Pattern
```javascript
// Dynamic protocol creation
protocolFromHeader(headerObj, (err, protocol) => {
  // Use generated protocol for encoding/decoding
});
```
**Benefits**: Runtime flexibility, type safety
**Usage**: Core to all encoding/decoding operations

### 2. Transform Strategy Pattern
```javascript
const transformInteger = {
  parse: (value, lastval, transform) => { /* compress */ },
  recover: (storedValue, lastval, transform) => { /* decompress */ }
};
```
**Benefits**: Pluggable compression strategies
**Extension Point**: Additional transform types possible

### 3. Buffer Builder Pattern
```javascript
// Incremental buffer construction
const writer = new Writer();
encodeHeader(obj, writer, callback);
encodeData(protocol, obj, writer, callback);
const buffer = writer.finish();
```
**Benefits**: Memory efficient, streaming capable
**Usage**: All encoding operations

### 4. Reader State Pattern
```javascript
// Sequential buffer parsing
const reader = new Reader(buffer);
decodeHeader(reader, (err, header) => {
  // Reader position advanced automatically
  decodeData(protocol, reader, callback);
});
```
**Benefits**: Stateful parsing, error recovery
**Usage**: All decoding operations

## Component Relationships

### 1. Header → Protocol → Data Flow
```
Table Header ──┐
               ├─▶ Dynamic Protocol ──▶ Data Encoding
Transform Spec ─┘
```

### 2. Encoding Pipeline
```
Raw Data ──▶ Transform ──▶ Validate ──▶ Encode ──▶ Buffer
```

### 3. Decoding Pipeline
```
Buffer ──▶ Parse Header ──▶ Generate Protocol ──▶ Decode Data ──▶ Reverse Transform
```

## Critical Implementation Paths

### 1. Encoding Path
1. **Validate Input**: Check table structure and data types
2. **Encode Header**: Serialize schema with metadata
3. **Generate Protocol**: Create dynamic protobuf schema
4. **Transform Data**: Apply compression transforms
5. **Encode Data**: Serialize using generated protocol
6. **Combine Buffers**: Header + Data in single buffer

### 2. Decoding Path
1. **Parse Header**: Extract schema from buffer
2. **Generate Protocol**: Recreate protobuf schema
3. **Decode Data**: Deserialize using protocol
4. **Reverse Transforms**: Restore original values
5. **Format Output**: Convert to requested format

### 3. Random Access Path
1. **Parse Header**: Get schema information
2. **Index Buffer**: Map row positions
3. **Seek to Row**: Jump to specific byte position
4. **Decode Row**: Deserialize single row
5. **Transform**: Apply reverse transforms

## Error Handling Patterns

### 1. Validation Errors
- **Source**: Invalid table structure or data types
- **Pattern**: Early validation with descriptive messages
- **Recovery**: Fail fast with clear error context

### 2. Protocol Errors
- **Source**: protobufjs validation failures
- **Pattern**: Wrap protobuf errors with context
- **Recovery**: Provide debugging information

### 3. Transform Errors
- **Source**: Invalid transform parameters or data
- **Pattern**: Validate transforms before application
- **Recovery**: Clear error messages about transform issues

## Performance Considerations

### 1. Memory Management
- **Streaming**: Use Reader/Writer for large datasets
- **Lazy Loading**: Decode only requested data
- **Buffer Reuse**: Minimize allocation overhead

### 2. CPU Optimization
- **Transform Caching**: Reuse calculated values
- **Protocol Caching**: Cache generated schemas
- **Batch Operations**: Process multiple rows efficiently

### 3. I/O Patterns
- **Sequential Access**: Optimized for full table operations
- **Random Access**: Indexed access for specific rows
- **Append Operations**: Efficient buffer concatenation
