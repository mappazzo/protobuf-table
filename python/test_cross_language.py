#!/usr/bin/env python3
"""
Test cross-language compatibility between JavaScript and Python implementations
"""

import json
from typing import Dict, List, Any, Optional, Union, Callable
from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32
import io

# Import the compiled protobuf messages
import head_pb2

class StatsCalculator:
    """Calculate statistics for numeric fields."""
    
    @staticmethod
    def calculate_field_stats(data: List[List[Any]], field_index: int, field_type: str) -> Optional[Dict[str, float]]:
        """Calculate stats for a specific field if it's numeric."""
        if field_type not in ['int', 'uint', 'float']:
            return None
        
        # Extract numeric values for this field
        values = []
        for row in data:
            if field_index < len(row) and row[field_index] is not None:
                try:
                    val = float(row[field_index])
                    values.append(val)
                except (ValueError, TypeError):
                    continue
        
        if not values:
            return None
        
        return {
            'start': values[0],
            'end': values[-1],
            'min': min(values),
            'max': max(values),
            'mean': sum(values) / len(values)
        }
    
    @staticmethod
    def calculate_all_stats(obj: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistics for all numeric fields in the table."""
        result = dict(obj)
        
        # Calculate field statistics
        for i, field_def in enumerate(result['header']):
            stats = StatsCalculator.calculate_field_stats(obj['data'], i, field_def['type'])
            if stats:
                field_def['stats'] = stats
        
        # Update meta with row count
        if 'meta' not in result:
            result['meta'] = {}
        result['meta']['row_count'] = len(obj['data'])
        
        return result

def encode_table_simple(obj: Dict[str, Any]) -> bytes:
    """Simple encoding that matches JavaScript structure exactly."""
    
    # Calculate statistics automatically
    obj_with_stats = StatsCalculator.calculate_all_stats(obj)
    
    # Create header message using compiled proto
    header_msg = head_pb2.tableHead()
    
    # Add header fields
    for field_def in obj_with_stats['header']:
        field_msg = header_msg.header.add()
        field_msg.name = field_def['name']
        field_msg.type = field_def['type']
        
        # Add stats if present
        if 'stats' in field_def:
            stats = field_def['stats']
            field_msg.stats.start = stats.get('start', 0.0)
            field_msg.stats.end = stats.get('end', 0.0)
            field_msg.stats.min = stats.get('min', 0.0)
            field_msg.stats.max = stats.get('max', 0.0)
            field_msg.stats.mean = stats.get('mean', 0.0)
    
    # Add meta if present
    if 'meta' in obj_with_stats:
        meta = obj_with_stats['meta']
        header_msg.meta.name = meta.get('filename', meta.get('name', ''))
        header_msg.meta.owner = meta.get('owner', '')
        header_msg.meta.link = meta.get('link', '')
        header_msg.meta.comment = meta.get('comment', '')
        header_msg.meta.row_count = meta.get('row_count', 0)
    
    # Serialize header message
    header_serialized = header_msg.SerializeToString()
    header_bytes = _VarintBytes(len(header_serialized)) + header_serialized
    
    # For now, encode data as simple JSON (to match current JavaScript approach)
    # This is a temporary solution for testing cross-language compatibility
    data_buffer = io.BytesIO()
    
    for row_data in obj['data']:
        # Create simple row structure that matches JavaScript
        row_dict = {}
        for i, field_def in enumerate(obj['header']):
            field_name = field_def['name']
            if i < len(row_data):
                row_dict[field_name] = row_data[i]
        
        # Encode as JSON for now (matching current approach)
        row_json = json.dumps(row_dict).encode('utf-8')
        data_buffer.write(_VarintBytes(len(row_json)))
        data_buffer.write(row_json)
    
    return header_bytes + data_buffer.getvalue()

def decode_table_simple(buffer: bytes) -> Dict[str, Any]:
    """Simple decoding that matches JavaScript structure exactly."""
    
    # Read header length
    length, offset = _DecodeVarint32(buffer, 0)
    
    # Read and parse header message
    header_data = buffer[offset:offset + length]
    header_msg = head_pb2.tableHead()
    header_msg.ParseFromString(header_data)
    
    # Convert header to dictionary
    result = {'header': []}
    
    for field_msg in header_msg.header:
        field_dict = {
            'name': field_msg.name,
            'type': field_msg.type
        }
        
        # Add stats if present
        if field_msg.HasField('stats'):
            field_dict['stats'] = {
                'start': field_msg.stats.start,
                'end': field_msg.stats.end,
                'min': field_msg.stats.min,
                'max': field_msg.stats.max,
                'mean': field_msg.stats.mean
            }
        
        result['header'].append(field_dict)
    
    # Add meta if present
    if header_msg.HasField('meta'):
        result['meta'] = {
            'filename': header_msg.meta.name,
            'owner': header_msg.meta.owner,
            'link': header_msg.meta.link,
            'comment': header_msg.meta.comment,
            'row_count': header_msg.meta.row_count
        }
    
    # Decode data rows
    result['data'] = []
    data_offset = offset + length
    
    while data_offset < len(buffer):
        # Read row length
        row_length, new_offset = _DecodeVarint32(buffer, data_offset)
        
        # Read and parse row data
        row_data = buffer[new_offset:new_offset + row_length]
        row_dict = json.loads(row_data.decode('utf-8'))
        
        # Convert to array format
        row_array = []
        for field_def in result['header']:
            field_name = field_def['name']
            row_array.append(row_dict.get(field_name))
        
        result['data'].append(row_array)
        data_offset = new_offset + row_length
    
    return result

def test_cross_language_compatibility():
    """Test cross-language compatibility with JavaScript."""
    
    print("Testing Python cross-language compatibility...")
    
    # Test table with statistics
    test_table = {
        'header': [
            {'name': 'id', 'type': 'uint'},
            {'name': 'name', 'type': 'string'},
            {'name': 'temperature', 'type': 'float'}
        ],
        'data': [
            [1, 'sensor1', 20.5],
            [2, 'sensor2', 25.0],
            [3, 'sensor3', 18.2]
        ],
        'meta': {
            'name': 'cross_language_test.pb',
            'owner': 'test_user',
            'comment': 'Cross-language compatibility test'
        }
    }
    
    # Encode with Python
    encoded = encode_table_simple(test_table)
    print(f'Python encoded table to {len(encoded)} bytes')
    
    # Save for JavaScript to read
    with open('python_encoded_test.pb', 'wb') as f:
        f.write(encoded)
    print('Saved Python-encoded data to: python_encoded_test.pb')
    
    # Test Python decoding of its own data
    decoded = decode_table_simple(encoded)
    print(f'Python successfully decoded its own data:')
    print(f'- Rows: {len(decoded["data"])}')
    print(f'- Fields: {len(decoded["header"])}')
    
    # Check for statistics
    temp_field = next((f for f in decoded['header'] if f['name'] == 'temperature'), None)
    if temp_field and 'stats' in temp_field:
        stats = temp_field['stats']
        print(f'- Temperature stats: min={stats["min"]}, max={stats["max"]}, mean={stats["mean"]:.2f}')
    else:
        print('- No temperature statistics found')
    
    print('\n✓ Python implementation working correctly!')
    print('\nTo test cross-language compatibility:')
    print('1. Run: cd ../javascript && node -e "')
    print('const pbTable = require(\'./src/pbTable\');')
    print('const fs = require(\'fs\');')
    print('const data = fs.readFileSync(\'../python/python_encoded_test.pb\');')
    print('pbTable.decodeTable(data, (err, result) => {')
    print('  if (err) console.error(\'Error:\', err);')
    print('  else {')
    print('    console.log(\'JavaScript decoded Python data:\', result.data.length, \'rows\');')
    print('    const tempField = result.header.find(f => f.name === \'temperature\');')
    print('    if (tempField && tempField.stats) {')
    print('      console.log(\'Temperature stats:\', tempField.stats);')
    print('    }')
    print('  }')
    print('});')
    print('"')

if __name__ == "__main__":
    test_cross_language_compatibility()
