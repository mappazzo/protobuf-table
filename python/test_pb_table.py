#!/usr/bin/env python3
"""
Test suite for protobuf-table Python implementation

Tests the Python implementation against the same test cases used in the JavaScript version
to ensure API equivalence and data compatibility.
"""

import sys
import traceback
from typing import Dict, List, Any

try:
    from pb_table import (
        encode_table, decode_table, encode_verbose, decode_verbose,
        encode, decode, ProtobufTableError
    )
except ImportError as e:
    print(f"Error importing pb_table: {e}")
    print("Make sure to install requirements: pip install -r requirements_pb_table.txt")
    sys.exit(1)

def test_basic_array_format():
    """Test basic encoding/decoding with array format (equivalent to JavaScript basic test)."""
    print("Testing basic array format...")
    
    # Test data similar to JavaScript smallTable
    test_table = {
        'header': [
            {'name': 'id', 'type': 'uint'},
            {'name': 'name', 'type': 'string'},
            {'name': 'value', 'type': 'float'},
            {'name': 'active', 'type': 'bool'}
        ],
        'data': [
            [1, 'test', 3.14, True],
            [2, 'example', 2.71, False],
            [3, 'sample', 1.41, True]
        ]
    }
    
    try:
        # Test encoding
        encoded = encode_table(test_table)
        print(f"✓ Encoded {len(test_table['data'])} rows to {len(encoded)} bytes")
        
        # Test decoding
        decoded = decode_table(encoded)
        print(f"✓ Decoded {len(decoded['data'])} rows")
        
        # Verify data integrity
        if test_table['data'] == decoded['data']:
            print("✓ Round-trip data integrity verified")
        else:
            print("✗ Data mismatch after round-trip")
            print(f"Original: {test_table['data']}")
            print(f"Decoded:  {decoded['data']}")
            return False
            
        # Test alias functions
        encoded_alias = encode(test_table)
        decoded_alias = decode(encoded_alias)
        
        if test_table['data'] == decoded_alias['data']:
            print("✓ Alias functions work correctly")
        else:
            print("✗ Alias functions failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Basic array format test failed: {e}")
        traceback.print_exc()
        return False

def test_verbose_object_format():
    """Test encoding/decoding with object format (verbose)."""
    print("\nTesting verbose object format...")
    
    # Test data with object format
    test_table = {
        'header': [
            {'name': 'id', 'type': 'uint'},
            {'name': 'name', 'type': 'string'},
            {'name': 'temperature', 'type': 'float'},
            {'name': 'active', 'type': 'bool'}
        ],
        'data': [
            {'id': 1, 'name': 'sensor1', 'temperature': 23.5, 'active': True},
            {'id': 2, 'name': 'sensor2', 'temperature': 24.1, 'active': False},
            {'id': 3, 'name': 'sensor3', 'temperature': 22.8, 'active': True}
        ]
    }
    
    try:
        # Test encoding
        encoded = encode_verbose(test_table)
        print(f"✓ Encoded {len(test_table['data'])} rows to {len(encoded)} bytes")
        
        # Test decoding
        decoded = decode_verbose(encoded)
        print(f"✓ Decoded {len(decoded['data'])} rows")
        
        # Verify data integrity
        if test_table['data'] == decoded['data']:
            print("✓ Round-trip data integrity verified")
        else:
            print("✗ Data mismatch after round-trip")
            print(f"Original: {test_table['data']}")
            print(f"Decoded:  {decoded['data']}")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Verbose object format test failed: {e}")
        traceback.print_exc()
        return False

def test_transforms():
    """Test data transforms for compression (equivalent to JavaScript compress test)."""
    print("\nTesting data transforms...")
    
    # Test data with transforms similar to JavaScript compressTable
    test_table = {
        'header': [
            {
                'name': 'timestamp',
                'type': 'uint',
                'transform': {
                    'offset': 1609459200,  # Unix timestamp base
                    'multip': 1,
                    'decimals': 0
                }
            },
            {
                'name': 'latitude',
                'type': 'int',
                'transform': {
                    'offset': -42,
                    'multip': 1000000,
                    'decimals': 6,
                    'sequence': False
                }
            },
            {
                'name': 'temperature',
                'type': 'int',
                'transform': {
                    'offset': 0,
                    'multip': 100,
                    'decimals': 2
                }
            }
        ],
        'data': [
            [1609459260, -41.123456, 23.45],
            [1609459320, -41.123789, 23.67],
            [1609459380, -41.124012, 23.89]
        ]
    }
    
    try:
        # Test encoding with transforms
        encoded = encode_table(test_table)
        print(f"✓ Encoded {len(test_table['data'])} rows with transforms to {len(encoded)} bytes")
        
        # Test decoding with transforms
        decoded = decode_table(encoded)
        print(f"✓ Decoded {len(decoded['data'])} rows with transforms")
        
        # Verify data integrity (allowing for small floating point differences)
        data_matches = True
        for i, (orig_row, dec_row) in enumerate(zip(test_table['data'], decoded['data'])):
            for j, (orig_val, dec_val) in enumerate(zip(orig_row, dec_row)):
                if isinstance(orig_val, float):
                    if abs(orig_val - dec_val) > 1e-6:
                        print(f"✗ Float mismatch at row {i}, col {j}: {orig_val} != {dec_val}")
                        data_matches = False
                else:
                    if orig_val != dec_val:
                        print(f"✗ Value mismatch at row {i}, col {j}: {orig_val} != {dec_val}")
                        data_matches = False
        
        if data_matches:
            print("✓ Transform round-trip data integrity verified")
        else:
            print("✗ Transform data mismatch after round-trip")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Transform test failed: {e}")
        traceback.print_exc()
        return False

def test_sequence_transforms():
    """Test sequence transforms (delta encoding)."""
    print("\nTesting sequence transforms...")
    
    # Test data with sequence transforms
    test_table = {
        'header': [
            {
                'name': 'counter',
                'type': 'uint',
                'transform': {
                    'sequence': True
                }
            },
            {
                'name': 'value',
                'type': 'int',
                'transform': {
                    'offset': 1000,
                    'sequence': True
                }
            }
        ],
        'data': [
            [100, 1010],
            [105, 1015],
            [112, 1008],
            [120, 1025]
        ]
    }
    
    try:
        # Test encoding with sequence transforms
        encoded = encode_table(test_table)
        print(f"✓ Encoded {len(test_table['data'])} rows with sequence transforms to {len(encoded)} bytes")
        
        # Test decoding with sequence transforms
        decoded = decode_table(encoded)
        print(f"✓ Decoded {len(decoded['data'])} rows with sequence transforms")
        
        # Verify data integrity
        if test_table['data'] == decoded['data']:
            print("✓ Sequence transform round-trip data integrity verified")
        else:
            print("✗ Sequence transform data mismatch after round-trip")
            print(f"Original: {test_table['data']}")
            print(f"Decoded:  {decoded['data']}")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Sequence transform test failed: {e}")
        traceback.print_exc()
        return False

def test_metadata():
    """Test metadata and custom keys support."""
    print("\nTesting metadata support...")
    
    # Test data with metadata
    test_table = {
        'header': [
            {'name': 'id', 'type': 'uint'},
            {'name': 'value', 'type': 'float'}
        ],
        'meta': {
            'filename': 'test_data.pb',
            'owner': 'test_user',
            'comment': 'Test dataset for validation'
        },
        'custom_key': 'custom_value',
        'data': [
            [1, 1.1],
            [2, 2.2]
        ]
    }
    
    try:
        # Test encoding with metadata
        encoded = encode_table(test_table)
        print(f"✓ Encoded table with metadata to {len(encoded)} bytes")
        
        # Test decoding with metadata
        decoded = decode_table(encoded)
        print(f"✓ Decoded table with metadata")
        
        # Verify metadata preservation
        if 'meta' in decoded and decoded['meta'] == test_table['meta']:
            print("✓ Metadata preserved correctly")
        else:
            print("✗ Metadata not preserved correctly")
            print(f"Original meta: {test_table.get('meta')}")
            print(f"Decoded meta:  {decoded.get('meta')}")
            return False
            
        # Verify data integrity
        if test_table['data'] == decoded['data']:
            print("✓ Data integrity verified with metadata")
        else:
            print("✗ Data mismatch with metadata")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Metadata test failed: {e}")
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling for invalid inputs."""
    print("\nTesting error handling...")
    
    try:
        # Test invalid table format
        try:
            encode_table({'invalid': 'format'})
            print("✗ Should have raised error for invalid format")
            return False
        except ProtobufTableError:
            print("✓ Correctly raised error for invalid format")
        
        # Test invalid data type
        try:
            encode_table({
                'header': [{'name': 'test', 'type': 'invalid_type'}],
                'data': [[1]]
            })
            print("✗ Should have raised error for invalid type")
            return False
        except ProtobufTableError:
            print("✓ Correctly raised error for invalid type")
        
        # Test non-array data for encode_table
        try:
            encode_table({
                'header': [{'name': 'test', 'type': 'uint'}],
                'data': 'not_an_array'
            })
            print("✗ Should have raised error for non-array data")
            return False
        except ProtobufTableError:
            print("✓ Correctly raised error for non-array data")
        
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        traceback.print_exc()
        return False

def test_callback_support():
    """Test callback-style API (JavaScript compatibility)."""
    print("\nTesting callback support...")
    
    test_table = {
        'header': [
            {'name': 'id', 'type': 'uint'},
            {'name': 'name', 'type': 'string'}
        ],
        'data': [
            [1, 'test'],
            [2, 'example']
        ]
    }
    
    try:
        # Test successful callback
        callback_result = {'error': None, 'result': None}
        
        def success_callback(error, result):
            callback_result['error'] = error
            callback_result['result'] = result
        
        encode_table(test_table, success_callback)
        
        if callback_result['error'] is None and callback_result['result'] is not None:
            print("✓ Success callback works correctly")
        else:
            print("✗ Success callback failed")
            return False
        
        # Test error callback
        error_callback_result = {'error': None, 'result': None}
        
        def error_callback(error, result):
            error_callback_result['error'] = error
            error_callback_result['result'] = result
        
        encode_table({'invalid': 'format'}, error_callback)
        
        if error_callback_result['error'] is not None and error_callback_result['result'] is None:
            print("✓ Error callback works correctly")
        else:
            print("✗ Error callback failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Callback support test failed: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all test cases and report results."""
    print("=" * 60)
    print("PROTOBUF-TABLE PYTHON IMPLEMENTATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_basic_array_format,
        test_verbose_object_format,
        test_transforms,
        test_sequence_transforms,
        test_metadata,
        test_error_handling,
        test_callback_support
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All tests passed! Python implementation is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
