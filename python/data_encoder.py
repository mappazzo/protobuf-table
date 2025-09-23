#!/usr/bin/env python3
"""
Cross-language protobuf encoder/decoder for protobuf-table

This module provides encoding/decoding using the standard protobuf-table
wire format for cross-language compatibility.
"""

import json
from typing import Dict, List, Any, Optional
from google.protobuf.descriptor_pb2 import DescriptorProto, FieldDescriptorProto, FileDescriptorProto
from google.protobuf.descriptor_pool import DescriptorPool
from google.protobuf.message_factory import MessageFactory
from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32
import io

class ProtobufTableError(Exception):
    """Base exception for protobuf-table errors."""
    pass

class DataEncoder:
    """Cross-language protobuf data encoder/decoder"""
    
    # Type mapping to match JavaScript implementation
    TYPE_MAPPING = {
        'string': FieldDescriptorProto.TYPE_STRING,
        'uint': FieldDescriptorProto.TYPE_INT32,
        'int': FieldDescriptorProto.TYPE_SINT32,
        'float': FieldDescriptorProto.TYPE_FLOAT,
        'bool': FieldDescriptorProto.TYPE_BOOL
    }
    
    def __init__(self):
        self._message_cache = {}
    
    def _create_js_compatible_schema(self, header_fields: List[Dict[str, Any]]) -> tuple:
        """Create JavaScript-compatible protobuf schema"""
        
        # Create cache key
        cache_key = json.dumps([(f['name'], f['type']) for f in header_fields], sort_keys=True)
        if cache_key in self._message_cache:
            return self._message_cache[cache_key]
        
        # Create file descriptor
        file_desc = FileDescriptorProto()
        file_desc.name = "data_array.proto"
        file_desc.package = "DataArray"
        
        # Create Row message descriptor
        row_desc = file_desc.message_type.add()
        row_desc.name = "Row"
        
        # Add fields to Row message
        for i, field_def in enumerate(header_fields):
            field_desc = row_desc.field.add()
            field_desc.name = field_def['name']
            field_desc.number = i + 1
            field_desc.type = self.TYPE_MAPPING[field_def['type']]
            field_desc.label = FieldDescriptorProto.LABEL_OPTIONAL
        
        # Create Data message descriptor
        data_desc = file_desc.message_type.add()
        data_desc.name = "Data"
        
        # Add repeated Row field to Data message
        data_field = data_desc.field.add()
        data_field.name = "data"
        data_field.number = 1
        data_field.type = FieldDescriptorProto.TYPE_MESSAGE
        data_field.type_name = ".DataArray.Row"
        data_field.label = FieldDescriptorProto.LABEL_REPEATED
        
        # Create descriptor pool and add file descriptor
        pool = DescriptorPool()
        file_descriptor = pool.Add(file_desc)
        
        # Get message descriptors
        row_descriptor = file_descriptor.message_types_by_name['Row']
        data_descriptor = file_descriptor.message_types_by_name['Data']
        
        # Create message classes using reflection
        from google.protobuf.message import Message
        from google.protobuf.reflection import GeneratedProtocolMessageType
        
        # Create Row message class
        row_class = GeneratedProtocolMessageType(
            'Row',
            (Message,),
            {'DESCRIPTOR': row_descriptor}
        )
        
        # Create Data message class  
        data_class = GeneratedProtocolMessageType(
            'Data',
            (Message,),
            {'DESCRIPTOR': data_descriptor}
        )
        
        # Cache the result
        result = (row_class, data_class)
        self._message_cache[cache_key] = result
        
        return result
    
    def encode_data_section(self, header_fields: List[Dict[str, Any]], data_rows: List[List[Any]]) -> bytes:
        """Encode data section using JavaScript-compatible format"""
        
        # Get message classes
        row_class, data_class = self._create_js_compatible_schema(header_fields)
        
        # Create Data message
        data_msg = data_class()
        
        # Add each row
        for row_data in data_rows:
            row_msg = data_msg.data.add()  # Add new Row to repeated field
            
            # Set field values
            for i, field_def in enumerate(header_fields):
                field_name = field_def['name']
                value = row_data[i]
                
                # Type conversion to match JavaScript behavior
                if field_def['type'] == 'int':
                    value = int(value) if value is not None else 0
                elif field_def['type'] == 'uint':
                    value = int(value) if value is not None else 0
                elif field_def['type'] == 'string':
                    value = str(value) if value is not None else ""
                elif field_def['type'] == 'bool':
                    value = bool(value) if value is not None else False
                elif field_def['type'] == 'float':
                    value = float(value) if value is not None else 0.0
                
                setattr(row_msg, field_name, value)
        
        # Serialize the Data message
        return data_msg.SerializeToString()
    
    def decode_data_section(self, header_fields: List[Dict[str, Any]], data_bytes: bytes) -> List[List[Any]]:
        """Decode data section using JavaScript-compatible format"""
        
        # Get message classes
        row_class, data_class = self._create_js_compatible_schema(header_fields)
        
        # Parse Data message
        data_msg = data_class()
        data_msg.ParseFromString(data_bytes)
        
        # Extract rows
        result = []
        for row_msg in data_msg.data:
            row_data = []
            for field_def in header_fields:
                field_name = field_def['name']
                value = getattr(row_msg, field_name, None)
                row_data.append(value)
            result.append(row_data)
        
        return result
    
    def encode_single_row_messages(self, header_fields: List[Dict[str, Any]], data_rows: List[List[Any]]) -> bytes:
        """Encode data as individual Row messages (JavaScript encodeTable format)"""
        
        # Get message classes
        row_class, data_class = self._create_js_compatible_schema(header_fields)
        
        # Create a writer to accumulate all row messages (like JavaScript does)
        from google.protobuf.internal.encoder import _VarintEncoder
        from google.protobuf.internal.wire_format import WIRETYPE_LENGTH_DELIMITED
        
        buffer = io.BytesIO()
        
        # Encode each row as a separate Data message (matching JavaScript exactly)
        for row_data in data_rows:
            # Create a Data message with single Row (like JavaScript: { data: [{}] })
            data_msg = data_class()
            row_msg = data_msg.data.add()
            
            # Set field values
            for i, field_def in enumerate(header_fields):
                field_name = field_def['name']
                value = row_data[i]
                
                # Type conversion
                if field_def['type'] == 'int':
                    value = int(value) if value is not None else 0
                elif field_def['type'] == 'uint':
                    value = int(value) if value is not None else 0
                elif field_def['type'] == 'string':
                    value = str(value) if value is not None else ""
                elif field_def['type'] == 'bool':
                    value = bool(value) if value is not None else False
                elif field_def['type'] == 'float':
                    value = float(value) if value is not None else 0.0
                
                setattr(row_msg, field_name, value)
            
            # Encode the Data message directly to buffer (like JavaScript encodeData)
            # This matches how JavaScript calls encodeData(protocol, dataObj, writer)
            serialized = data_msg.SerializeToString()
            
            # Write with proper protobuf field encoding (tag + length + data)
            # Tag 1 with WIRETYPE_LENGTH_DELIMITED (like JavaScript does)
            tag = (1 << 3) | WIRETYPE_LENGTH_DELIMITED
            _VarintEncoder()(buffer.write, tag, False)
            _VarintEncoder()(buffer.write, len(serialized), False)
            buffer.write(serialized)
        
        return buffer.getvalue()
    
    def decode_single_row_messages(self, header_fields: List[Dict[str, Any]], data_bytes: bytes) -> List[List[Any]]:
        """Decode individual Row messages (JavaScript decodeTable format)"""
        
        # Get message classes
        row_class, data_class = self._create_js_compatible_schema(header_fields)
        
        result = []
        offset = 0
        
        while offset < len(data_bytes):
            # Read the tag and wire type
            from google.protobuf.internal.decoder import _DecodeVarint32
            from google.protobuf.internal.wire_format import WIRETYPE_LENGTH_DELIMITED
            
            # Read tag
            tag, new_offset = _DecodeVarint32(data_bytes, offset)
            wire_type = tag & 7
            field_number = tag >> 3
            
            if wire_type != WIRETYPE_LENGTH_DELIMITED or field_number != 1:
                raise ProtobufTableError(f'Unexpected wire format: tag={tag}, wire_type={wire_type}, field={field_number}')
            
            # Read length
            length, new_offset = _DecodeVarint32(data_bytes, new_offset)
            
            # Read message data
            message_data = data_bytes[new_offset:new_offset + length]
            
            # Parse Data message
            data_msg = data_class()
            data_msg.ParseFromString(message_data)
            
            # Extract row data (should be single row)
            if len(data_msg.data) > 0:
                row_msg = data_msg.data[0]
                row_data = []
                for field_def in header_fields:
                    field_name = field_def['name']
                    value = getattr(row_msg, field_name, None)
                    row_data.append(value)
                result.append(row_data)
            
            offset = new_offset + length
        
        return result

# Global encoder instance
_data_encoder = DataEncoder()

def encode_data_rows(header_fields: List[Dict[str, Any]], data_rows: List[List[Any]]) -> bytes:
    """Encode data rows using standard protobuf-table format"""
    return _data_encoder.encode_single_row_messages(header_fields, data_rows)

def decode_data_rows(header_fields: List[Dict[str, Any]], data_bytes: bytes) -> List[List[Any]]:
    """Decode data rows using standard protobuf-table format"""
    return _data_encoder.decode_single_row_messages(header_fields, data_bytes)
