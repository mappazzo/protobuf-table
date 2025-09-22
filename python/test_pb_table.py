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
        get_table, get_verbose, add_table, add_verbose, get_index,
        encode, decode, get, add, ProtobufTableError
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

def test_random_access():
    """Test random access functions (get_table and get_verbose)."""
    print("\nTesting random access functions...")
    
    # Test data for array format
    test_table = {
        'header': [
            {'name': 'id', 'type': 'uint'},
            {'name': 'name', 'type': 'string'},
            {'name': 'value', 'type': 'float'}
        ],
        'data': [
            [1, 'first', 1.1],
            [2, 'second', 2.2],
            [3, 'third', 3.3],
            [4, 'fourth', 4.4]
        ]
    }
    
    # Test data for object format
    test_verbose = {
        'header': [
            {'name': 'id', 'type': 'uint'},
            {'name': 'name', 'type': 'string'},
            {'name': 'value', 'type': 'float'}
        ],
        'data': [
            {'id': 1, 'name': 'first', 'value': 1.1},
            {'id': 2, 'name': 'second', 'value': 2.2},
            {'id': 3, 'name': 'third', 'value': 3.3},
            {'id': 4, 'name': 'fourth', 'value': 4.4}
        ]
    }
    
    try:
        # Test array format random access
        encoded = encode_table(test_table)
        
        # Test single row access
        row_1 = get_table(encoded, 1)
        if row_1 == test_table['data'][1]:
            print("✓ Single row access (array format) works correctly")
        else:
            print(f"✗ Single row access failed: {row_1} != {test_table['data'][1]}")
            return False
        
        # Test multiple row access
        rows_0_2 = get_table(encoded, [0, 2])
        expected = [test_table['data'][0], test_table['data'][2]]
        if rows_0_2 == expected:
            print("✓ Multiple row access (array format) works correctly")
        else:
            print(f"✗ Multiple row access failed: {rows_0_2} != {expected}")
            return False
        
        # Test alias function
        row_alias = get(encoded, 0)
        if row_alias == test_table['data'][0]:
            print("✓ get() alias function works correctly")
        else:
            print("✗ get() alias function failed")
            return False
        
        # Test object format random access
        encoded_verbose = encode_verbose(test_verbose)
        
        # Test single row access (verbose)
        row_verbose = get_verbose(encoded_verbose, 2)
        if row_verbose == test_verbose['data'][2]:
            print("✓ Single row access (object format) works correctly")
        else:
            print(f"✗ Single row access (verbose) failed: {row_verbose} != {test_verbose['data'][2]}")
            return False
        
        # Test multiple row access (verbose)
        rows_verbose = get_verbose(encoded_verbose, [1, 3])
        expected_verbose = [test_verbose['data'][1], test_verbose['data'][3]]
        if rows_verbose == expected_verbose:
            print("✓ Multiple row access (object format) works correctly")
        else:
            print(f"✗ Multiple row access (verbose) failed: {rows_verbose} != {expected_verbose}")
            return False
        
        # Test error handling for out of bounds
        try:
            get_table(encoded, 10)
            print("✗ Should have raised error for out of bounds access")
            return False
        except ProtobufTableError:
            print("✓ Correctly raised error for out of bounds access")
        
        return True
        
    except Exception as e:
        print(f"✗ Random access test failed: {e}")
        traceback.print_exc()
        return False

def test_sequence_access_restriction():
    """Test that random access is properly restricted for sequence transforms."""
    print("\nTesting sequence transform access restrictions...")
    
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
                'type': 'int'
            }
        ],
        'data': [
            [100, 1000],
            [105, 1100],
            [112, 1200]
        ]
    }
    
    try:
        encoded = encode_table(test_table)
        
        # Test that random access is blocked for sequence data
        try:
            get_table(encoded, 1)
            print("✗ Should have raised error for sequence data access")
            return False
        except ProtobufTableError as e:
            if 'sequenced data' in str(e):
                print("✓ Correctly blocked random access for sequence transforms")
            else:
                print(f"✗ Wrong error message: {e}")
                return False
        
        # Test verbose format as well
        test_verbose = {
            'header': test_table['header'],
            'data': [
                {'counter': 100, 'value': 1000},
                {'counter': 105, 'value': 1100},
                {'counter': 112, 'value': 1200}
            ]
        }
        
        encoded_verbose = encode_verbose(test_verbose)
        
        try:
            get_verbose(encoded_verbose, 0)
            print("✗ Should have raised error for sequence data access (verbose)")
            return False
        except ProtobufTableError as e:
            if 'sequenced data' in str(e):
                print("✓ Correctly blocked random access for sequence transforms (verbose)")
            else:
                print(f"✗ Wrong error message (verbose): {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Sequence access restriction test failed: {e}")
        traceback.print_exc()
        return False

def test_data_addition():
    """Test data addition functions (add_table and add_verbose)."""
    print("\nTesting data addition functions...")
    
    # Test data for array format
    initial_table = {
        'header': [
            {'name': 'id', 'type': 'uint'},
            {'name': 'name', 'type': 'string'},
            {'name': 'value', 'type': 'float'}
        ],
        'data': [
            [1, 'first', 1.1],
            [2, 'second', 2.2]
        ]
    }
    
    additional_data = [
        [3, 'third', 3.3],
        [4, 'fourth', 4.4]
    ]
    
    # Test data for object format
    initial_verbose = {
        'header': [
            {'name': 'id', 'type': 'uint'},
            {'name': 'name', 'type': 'string'},
            {'name': 'value', 'type': 'float'}
        ],
        'data': [
            {'id': 1, 'name': 'first', 'value': 1.1},
            {'id': 2, 'name': 'second', 'value': 2.2}
        ]
    }
    
    additional_verbose_data = [
        {'id': 3, 'name': 'third', 'value': 3.3},
        {'id': 4, 'name': 'fourth', 'value': 4.4}
    ]
    
    try:
        # Test array format data addition
        encoded = encode_table(initial_table)
        expanded = add_table(encoded, additional_data)
        decoded = decode_table(expanded)
        
        expected_data = initial_table['data'] + additional_data
        if decoded['data'] == expected_data:
            print("✓ Data addition (array format) works correctly")
        else:
            print(f"✗ Data addition failed: {decoded['data']} != {expected_data}")
            return False
        
        # Test alias function
        expanded_alias = add(encoded, additional_data)
        decoded_alias = decode(expanded_alias)
        if decoded_alias['data'] == expected_data:
            print("✓ add() alias function works correctly")
        else:
            print("✗ add() alias function failed")
            return False
        
        # Test object format data addition
        encoded_verbose = encode_verbose(initial_verbose)
        expanded_verbose = add_verbose(encoded_verbose, additional_verbose_data)
        decoded_verbose = decode_verbose(expanded_verbose)
        
        expected_verbose_data = initial_verbose['data'] + additional_verbose_data
        if decoded_verbose['data'] == expected_verbose_data:
            print("✓ Data addition (object format) works correctly")
        else:
            print(f"✗ Data addition (verbose) failed: {decoded_verbose['data']} != {expected_verbose_data}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Data addition test failed: {e}")
        traceback.print_exc()
        return False

def test_indexing():
    """Test buffer indexing function (get_index)."""
    print("\nTesting buffer indexing...")
    
    test_table = {
        'header': [
            {'name': 'id', 'type': 'uint'},
            {'name': 'name', 'type': 'string'}
        ],
        'data': [
            [1, 'first'],
            [2, 'second'],
            [3, 'third'],
            [4, 'fourth']
        ]
    }
    
    try:
        encoded = encode_table(test_table)
        index = get_index(encoded)
        
        # Verify index has correct number of entries
        if len(index) == len(test_table['data']):
            print(f"✓ Index has correct number of entries: {len(index)}")
        else:
            print(f"✗ Index length mismatch: {len(index)} != {len(test_table['data'])}")
            return False
        
        # Verify index entries are integers (byte positions)
        if all(isinstance(pos, int) for pos in index):
            print("✓ Index entries are valid byte positions")
        else:
            print("✗ Index entries are not valid integers")
            return False
        
        # Verify index positions are increasing
        if all(index[i] < index[i+1] for i in range(len(index)-1)):
            print("✓ Index positions are in increasing order")
        else:
            print("✗ Index positions are not in increasing order")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Indexing test failed: {e}")
        traceback.print_exc()
        return False

def test_comprehensive_api():
    """Test comprehensive API compatibility with all new functions."""
    print("\nTesting comprehensive API compatibility...")
    
    test_table = {
        'header': [
            {'name': 'id', 'type': 'uint'},
            {'name': 'name', 'type': 'string'},
            {'name': 'score', 'type': 'float'}
        ],
        'data': [
            [1, 'alice', 95.5],
            [2, 'bob', 87.2]
        ]
    }
    
    try:
        # Test full workflow: encode -> get -> add -> decode
        encoded = encode_table(test_table)
        
        # Get specific row
        first_row = get_table(encoded, 0)
        if first_row == test_table['data'][0]:
            print("✓ Random access retrieval works")
        else:
            print("✗ Random access retrieval failed")
            return False
        
        # Add new data
        new_data = [[3, 'charlie', 92.8]]
        expanded = add_table(encoded, new_data)
        
        # Verify expansion
        final_decoded = decode_table(expanded)
        expected_final = test_table['data'] + new_data
        if final_decoded['data'] == expected_final:
            print("✓ Full workflow (encode->get->add->decode) works correctly")
        else:
            print("✗ Full workflow failed")
            return False
        
        # Test indexing on expanded data
        index = get_index(expanded)
        if len(index) == 3:  # Original 2 + 1 new
            print("✓ Indexing works on expanded data")
        else:
            print(f"✗ Indexing failed on expanded data: {len(index)} != 3")
            return False
        
        # Test callback versions
        callback_results = {}
        
        def test_callback(name):
            def callback(error, result):
                callback_results[name] = {'error': error, 'result': result}
            return callback
        
        # Test all callback versions
        get_table(encoded, 1, test_callback('get'))
        add_table(encoded, new_data, test_callback('add'))
        get_index(encoded, test_callback('index'))
        
        # Verify callbacks worked
        for name, result in callback_results.items():
            if result['error'] is None and result['result'] is not None:
                print(f"✓ {name} callback works correctly")
            else:
                print(f"✗ {name} callback failed")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Comprehensive API test failed: {e}")
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
        test_callback_support,
        test_random_access,
        test_sequence_access_restriction,
        test_data_addition,
        test_indexing,
        test_comprehensive_api
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
