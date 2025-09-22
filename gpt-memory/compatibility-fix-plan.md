# Cross-Language Compatibility Fix Plan

## Problem Analysis

The main compatibility issue is **data row encoding mismatch**:
- **Python**: Uses JSON encoding for row data (simplified approach)
- **JavaScript**: Uses proper protobuf Row message encoding

This prevents cross-language data exchange and causes decoding errors.

## Solution Strategy: Option 2 - Standardize on Full Protobuf Approach

**Rationale**: 
- More efficient and truly protobuf-compliant
- Better performance for large datasets
- Maintains the "protobuf-table" name integrity
- JavaScript implementation is already correct

## Implementation Plan

### Phase 0: JavaScript Browser Compatibility (High Priority)

#### 0.1 Convert .proto to JSON Schema
- **Issue**: Browser environments can't load .proto files directly
- **Solution**: Convert `head.proto` to JSON descriptor for browser use
- **Tool**: Use protobuf.js CLI to generate JSON from .proto file

#### 0.2 Environment Detection
- Detect Node.js vs Browser environment
- Load .proto file in Node.js, JSON descriptor in browser
- Maintain single codebase with conditional loading

#### 0.3 Build Process Updates
- Add build step to generate JSON from .proto
- Ensure JSON stays synchronized with .proto changes
- Update package.json scripts

### Phase 1: Update Python Row Encoding (High Priority)

#### 1.1 Create Dynamic Row Message Generation
- **Current**: Python uses JSON for row data
- **Target**: Generate dynamic protobuf Row messages like JavaScript
- **Files**: `python/pb_table.py`

#### 1.2 Update Encoding Functions
- Modify `encode_table()` to create proper protobuf Row messages
- Update data serialization to use protobuf instead of JSON
- Ensure transforms are applied before protobuf encoding

#### 1.3 Update Decoding Functions  
- Modify `decode_table()` to decode protobuf Row messages
- Remove JSON parsing, use protobuf deserialization
- Apply reverse transforms after protobuf decoding

### Phase 2: Implement Dynamic Schema Generation

#### 2.1 Row Message Factory
```python
def create_row_message_type(header_fields):
    """Create dynamic Row message type based on header fields"""
    # Generate protobuf message definition
    # Similar to JavaScript's protocolFromHeader function
```

#### 2.2 Message Type Caching
- Cache generated message types to avoid recreation
- Key by header field signature for efficiency

### Phase 3: Testing and Validation

#### 3.1 Unit Tests
- Test Python encoding/decoding with new approach
- Verify statistics preservation
- Test transform operations

#### 3.2 Cross-Language Tests
- JavaScript → Python data exchange
- Python → JavaScript data exchange
- Verify identical results from both implementations

#### 3.3 Performance Testing
- Compare new vs old Python performance
- Benchmark against JavaScript implementation
- Measure encoding/decoding speeds

### Phase 4: Backward Compatibility (Optional)

#### 4.1 Format Detection
- Add magic bytes or version headers
- Detect JSON vs protobuf row encoding
- Graceful fallback for old data

#### 4.2 Migration Utilities
- Tool to convert old JSON-encoded files
- Documentation for migration process

## Detailed Implementation Steps

### Step 1: Create Dynamic Row Message Generator

```python
def _create_dynamic_row_schema(header_fields):
    """Create dynamic protobuf schema for row data"""
    from google.protobuf.descriptor_pb2 import DescriptorProto, FieldDescriptorProto
    from google.protobuf.message_factory import MessageFactory
    from google.protobuf.descriptor_pool import DescriptorPool
    
    # Create Row message descriptor
    row_descriptor = DescriptorProto()
    row_descriptor.name = "Row"
    
    # Add fields based on header
    for i, field_def in enumerate(header_fields):
        field_descriptor = row_descriptor.field.add()
        field_descriptor.name = field_def['name']
        field_descriptor.number = i + 1
        field_descriptor.type = _get_protobuf_type(field_def['type'])
        field_descriptor.label = FieldDescriptorProto.LABEL_OPTIONAL
    
    # Create message factory
    pool = DescriptorPool()
    factory = MessageFactory(pool)
    
    # Register and return message class
    return factory.GetPrototype(pool.Add(row_descriptor))
```

### Step 2: Update Encoding Logic

```python
def encode_table(obj: Dict[str, Any], callback: Optional[Callable] = None) -> bytes:
    # Calculate statistics
    obj_with_stats = StatsCalculator.calculate_all_stats(obj)
    
    # Encode header
    header_bytes = _encode_header_delimited(obj_with_stats)
    
    # Create dynamic Row message type
    RowMessage = _create_dynamic_row_schema(obj['header'])
    
    # Encode each row using protobuf
    data_buffer = io.BytesIO()
    for row_index, row_data in enumerate(obj['data']):
        # Create Row message instance
        row_msg = RowMessage()
        
        # Apply transforms and set fields
        for col, field_def in enumerate(obj['header']):
            field_name = field_def['name']
            value = row_data[col]
            
            # Apply transforms
            if field_def.get('transform') and field_def['type'] in ['int', 'uint']:
                last_val = None
                if field_def['transform'].get('sequence') and row_index > 0:
                    last_val = obj['data'][row_index - 1][col]
                value = TransformInteger.parse(value, last_val, field_def['transform'])
            
            # Set field value
            setattr(row_msg, field_name, value)
        
        # Serialize row message
        serialized_row = row_msg.SerializeToString()
        data_buffer.write(_VarintBytes(len(serialized_row)))
        data_buffer.write(serialized_row)
    
    return header_bytes + data_buffer.getvalue()
```

### Step 3: Update Decoding Logic

```python
def decode_table(buffer: bytes, callback: Optional[Callable] = None) -> Dict[str, Any]:
    # Decode header
    header_obj, data_offset = _decode_header_delimited(buffer)
    
    # Create dynamic Row message type
    RowMessage = _create_dynamic_row_schema(header_obj['header'])
    
    # Decode row data
    result = dict(header_obj)
    result['data'] = []
    
    offset = data_offset
    while offset < len(buffer):
        # Read message length
        length, new_offset = _DecodeVarint32(buffer, offset)
        
        # Parse protobuf Row message
        message_data = buffer[new_offset:new_offset + length]
        row_msg = RowMessage()
        row_msg.ParseFromString(message_data)
        
        # Convert to array format with reverse transforms
        restored_row = []
        for col, field_def in enumerate(header_obj['header']):
            field_name = field_def['name']
            value = getattr(row_msg, field_name)
            
            # Apply reverse transforms
            if field_def.get('transform') and field_def['type'] in ['int', 'uint']:
                last_val = None
                if field_def['transform'].get('sequence') and len(result['data']) > 0:
                    last_val = result['data'][-1][col]
                value = TransformInteger.recover(value, last_val, field_def['transform'])
            
            restored_row.append(value)
        
        result['data'].append(restored_row)
        offset = new_offset + length
    
    return result
```

## Risk Assessment

### Low Risk
- Header compatibility already achieved
- Statistics functionality working
- Transform operations identical

### Medium Risk
- Dynamic message generation complexity
- Performance impact of message creation
- Memory usage with message factories

### High Risk
- Breaking changes to existing Python data files
- Complex debugging if message generation fails
- Potential performance regression

## Success Criteria

1. **Cross-Language Compatibility**: Data encoded in JavaScript can be decoded in Python and vice versa
2. **Feature Parity**: All features (stats, transforms, meta) work identically
3. **Performance**: New implementation performs comparably to current versions
4. **API Compatibility**: Public API remains unchanged
5. **Test Coverage**: Comprehensive tests for all scenarios

## Timeline Estimate

- **Phase 1**: 2-3 hours (Core implementation)
- **Phase 2**: 1-2 hours (Schema generation)
- **Phase 3**: 2-3 hours (Testing)
- **Phase 4**: 1-2 hours (Documentation)

**Total**: 6-10 hours for complete implementation

## Next Actions

1. Implement dynamic Row message generation in Python
2. Update encoding functions to use protobuf Row messages
3. Update decoding functions to parse protobuf Row messages
4. Test cross-language compatibility
5. Performance benchmark and optimization
6. Update documentation and examples
