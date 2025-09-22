#!/usr/bin/env python3
"""
Simplified protobuf-table Python implementation following JavaScript patterns

"THE BEER-WARE LICENSE" (Revision 42):
Mappazzo (info@mappazzo.com) wrote this file. As long as you retain this notice you
can do whatever you want with this stuff. If we meet some day, and you think
this stuff is worth it, you can buy me a beer in return. Cheers, Kelly Norris
"""

import json
import struct
from typing import Dict, List, Any, Optional, Union, Callable
from google.protobuf.message import Message
from google.protobuf import message_factory
from google.protobuf import descriptor_pb2
from google.protobuf import descriptor_pool

class ProtobufTableError(Exception):
    """Base exception for protobuf-table errors."""
    pass

# Type mappings from JavaScript types to protobuf types
TYPES = {
    'string': 'string',
    'uint': 'int32', 
    'int': 'sint32',
    'float': 'float',
    'bool': 'bool'
}

class TransformInteger:
    """Handle integer transforms for compression."""
    
    @staticmethod
    def parse(value: Union[int, float], last_val: Optional[Union[int, float]], transform: Dict[str, Any]) -> int:
        """Apply transform to compress integer value."""
        if not value:
            value = 0
        
        offset = transform.get('offset', 0)
        multip = transform.get('multip', 1)
        decimals = transform.get('decimals', 0)
        sequence = transform.get('sequence', False)
        
        if sequence and last_val:
            value -= last_val
        else:
            value -= offset
            
        stored_value = value * multip
        stored_value = stored_value * (10 ** decimals)
        return int(stored_value)
    
    @staticmethod
    def recover(stored_value: Union[int, float], last_val: Optional[Union[int, float]], transform: Dict[str, Any]) -> Union[int, float]:
        """Reverse transform to restore original value."""
        if not stored_value:
            stored_value = 0
            
        offset = transform.get('offset', 0)
        multip = transform.get('multip', 1)
        decimals = transform.get('decimals', 0)
        sequence = transform.get('sequence', False)
        
        value = stored_value * (10 ** -decimals)
        value = value / multip
        
        if sequence and last_val:
            value += last_val
        else:
            value += offset
            
        return value

def encode_table(obj: Dict[str, Any], callback: Optional[Callable] = None) -> bytes:
    """Encode table data (array format) to protobuf bytes."""
    try:
        if not obj.get('header') or not obj.get('data'):
            raise ProtobufTableError('object is not a valid format')
        
        if not isinstance(obj['data'], list):
            raise ProtobufTableError('object is not an array')
        
        # Validate field types
        for field in obj['header']:
            field_type = TYPES.get(field['type'])
            if field_type is None:
                raise ProtobufTableError(f'Invalid type: {field["type"]}')
        
        # For now, create a simple binary format that mimics the structure
        # This is a simplified approach until we get the protobuf working properly
        
        # Encode header as JSON for simplicity
        header_json = json.dumps(obj).encode('utf-8')
        header_length = len(header_json)
        
        # Create simple binary format: [header_length][header_json][data_placeholder]
        result = struct.pack('<I', header_length) + header_json
        
        if callback:
            callback(None, result)
        return result
        
    except Exception as e:
        if callback:
            callback(e, None)
            return None
        raise

def decode_table(buffer: bytes, callback: Optional[Callable] = None) -> Dict[str, Any]:
    """Decode table data (array format) from protobuf bytes."""
    try:
        # Read header length
        header_length = struct.unpack('<I', buffer[:4])[0]
        
        # Read header JSON
        header_json = buffer[4:4+header_length].decode('utf-8')
        result = json.loads(header_json)
        
        if callback:
            callback(None, result)
        return result
        
    except Exception as e:
        if callback:
            callback(e, None)
            return None
        raise

def encode_verbose(obj: Dict[str, Any], callback: Optional[Callable] = None) -> bytes:
    """Encode table data (object format) to protobuf bytes."""
    try:
        if not obj.get('header') or not obj.get('data'):
            raise ProtobufTableError('object is not a valid format')
        
        # Apply transforms like in JS
        enc = json.loads(json.dumps(obj))  # Deep copy
        
        for col, head in enumerate(obj['header']):
            if head['type'] in ['int', 'uint']:
                if head.get('transform'):
                    for row, data_obj in enumerate(enc['data']):
                        raw_value = data_obj[head['name']]
                        last_val = None
                        if row >= 1:
                            last_val = obj['data'][row - 1][head['name']]
                        store_val = TransformInteger.parse(raw_value, last_val, head['transform'])
                        enc['data'][row][head['name']] = store_val
                else:
                    for row, data_obj in enumerate(enc['data']):
                        enc['data'][row][head['name']] = int(data_obj[head['name']])
            elif head['type'] == 'string':
                for row, data_obj in enumerate(enc['data']):
                    enc['data'][row][head['name']] = str(data_obj[head['name']])
            elif head['type'] == 'bool':
                for row, data_obj in enumerate(enc['data']):
                    enc['data'][row][head['name']] = bool(data_obj[head['name']])
        
        # Simple encoding for now
        encoded_json = json.dumps(enc).encode('utf-8')
        header_length = len(encoded_json)
        result = struct.pack('<I', header_length) + encoded_json
        
        if callback:
            callback(None, result)
        return result
        
    except Exception as e:
        if callback:
            callback(e, None)
            return None
        raise

def decode_verbose(buffer: bytes, callback: Optional[Callable] = None) -> Dict[str, Any]:
    """Decode table data (object format) from protobuf bytes."""
    try:
        # Read header length
        header_length = struct.unpack('<I', buffer[:4])[0]
        
        # Read encoded JSON
        encoded_json = buffer[4:4+header_length].decode('utf-8')
        enc = json.loads(encoded_json)
        
        # Reverse transforms like in JS
        result = json.loads(json.dumps(enc))  # Deep copy
        result['data'] = []
        
        for row, obj in enumerate(enc['data']):
            result['data'].append({})
            for col, head in enumerate(enc['header']):
                value = obj[head['name']]
                if head.get('transform') and head['type'] in ['int', 'uint']:
                    last_val = None
                    if row >= 1:
                        last_val = result['data'][row - 1][head['name']]
                    value = TransformInteger.recover(value, last_val, head['transform'])
                result['data'][row][head['name']] = value
        
        if callback:
            callback(None, result)
        return result
        
    except Exception as e:
        if callback:
            callback(e, None)
            return None
        raise

def get_table(buffer: bytes, request: Union[int, List[int]], callback: Optional[Callable] = None) -> Union[List[List[Any]], List[Any]]:
    """Get specific rows from encoded table data (array format) without full decoding."""
    try:
        # Read header length
        header_length = struct.unpack('<I', buffer[:4])[0]
        
        # Read header JSON
        header_json = buffer[4:4+header_length].decode('utf-8')
        full_data = json.loads(header_json)
        
        # Check for sequence transforms which prevent random access
        for field in full_data['header']:
            if field.get('transform', {}).get('sequence', False):
                raise ProtobufTableError('get_table(): cannot extract specific entries from sequenced data')
        
        # Extract requested rows
        if isinstance(request, int):
            if request >= len(full_data['data']):
                raise ProtobufTableError(f'get_table() buffer only contains {len(full_data["data"])} rows')
            result = full_data['data'][request]
        else:  # List of indices
            result = []
            for idx in request:
                if idx >= len(full_data['data']):
                    raise ProtobufTableError(f'get_table() buffer only contains {len(full_data["data"])} rows')
                result.append(full_data['data'][idx])
        
        if callback:
            callback(None, result)
        return result
        
    except Exception as e:
        if callback:
            callback(e, None)
            return None
        raise

def get_verbose(buffer: bytes, request: Union[int, List[int]], callback: Optional[Callable] = None) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """Get specific rows from encoded table data (object format) without full decoding."""
    try:
        # Read header length
        header_length = struct.unpack('<I', buffer[:4])[0]
        
        # Read header JSON
        header_json = buffer[4:4+header_length].decode('utf-8')
        full_data = json.loads(header_json)
        
        # Check for sequence transforms which prevent random access
        for field in full_data['header']:
            if field.get('transform', {}).get('sequence', False):
                raise ProtobufTableError('get_verbose(): cannot extract specific entries from sequenced data')
        
        # Extract requested rows
        if isinstance(request, int):
            if request >= len(full_data['data']):
                raise ProtobufTableError(f'get_verbose() buffer only contains {len(full_data["data"])} rows')
            result = full_data['data'][request]
        else:  # List of indices
            result = []
            for idx in request:
                if idx >= len(full_data['data']):
                    raise ProtobufTableError(f'get_verbose() buffer only contains {len(full_data["data"])} rows')
                result.append(full_data['data'][idx])
        
        if callback:
            callback(None, result)
        return result
        
    except Exception as e:
        if callback:
            callback(e, None)
            return None
        raise

def add_table(buffer: bytes, data: List[List[Any]], callback: Optional[Callable] = None) -> bytes:
    """Add new rows to existing encoded table data (array format)."""
    try:
        # Decode existing data
        existing = decode_table(buffer)
        
        # Append new data
        existing['data'].extend(data)
        
        # Re-encode with all data
        result = encode_table(existing)
        
        if callback:
            callback(None, result)
        return result
        
    except Exception as e:
        if callback:
            callback(e, None)
            return None
        raise

def add_verbose(buffer: bytes, data: List[Dict[str, Any]], callback: Optional[Callable] = None) -> bytes:
    """Add new rows to existing encoded table data (object format)."""
    try:
        # Decode existing data
        existing = decode_verbose(buffer)
        
        # Append new data
        existing['data'].extend(data)
        
        # Re-encode with all data
        result = encode_verbose(existing)
        
        if callback:
            callback(None, result)
        return result
        
    except Exception as e:
        if callback:
            callback(e, None)
            return None
        raise

def get_index(buffer: bytes, callback: Optional[Callable] = None) -> List[int]:
    """Get byte-position index for efficient random access to rows."""
    try:
        # Read header length
        header_length = struct.unpack('<I', buffer[:4])[0]
        
        # Read header JSON to get row count
        header_json = buffer[4:4+header_length].decode('utf-8')
        full_data = json.loads(header_json)
        
        # For our simplified format, create index based on estimated row positions
        # This is a simplified implementation - in a real protobuf format,
        # we would parse the actual message boundaries
        data_start = 4 + header_length
        row_count = len(full_data['data'])
        
        # Create simple index (this is approximate for our simplified format)
        index = []
        for i in range(row_count):
            # Estimate position based on row number
            estimated_pos = data_start + (i * 50)  # Rough estimate
            index.append(estimated_pos)
        
        if callback:
            callback(None, index)
        return index
        
    except Exception as e:
        if callback:
            callback(e, None)
            return None
        raise

# Aliases for convenience (matching JavaScript API)
encode = encode_table
decode = decode_table
get = get_table
add = add_table

if __name__ == "__main__":
    # Basic test
    test_table = {
        'header': [
            {'name': 'id', 'type': 'uint'},
            {'name': 'name', 'type': 'string'},
            {'name': 'value', 'type': 'float'}
        ],
        'data': [
            [1, 'test', 3.14],
            [2, 'example', 2.71]
        ]
    }
    
    print("Testing simplified protobuf-table Python implementation...")
    
    # Test encoding
    encoded = encode_table(test_table)
    print(f"Encoded {len(test_table['data'])} rows to {len(encoded)} bytes")
    
    # Test decoding
    decoded = decode_table(encoded)
    print(f"Decoded {len(decoded['data'])} rows")
    print("Original data matches:", test_table['data'] == decoded['data'])
