#!/usr/bin/env python3
"""
Test suite for protobuf-table Python implementation

Tests the Python implementation against the same test cases used in the JavaScript version
to ensure API equivalence and data compatibility.
"""

import sys
import traceback
import json
import os
from typing import Dict, List, Any

# Add parent directory to path to import pb_table
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_project_root():
    """Get the project root directory."""
    # Start from current working directory and look for package.json or .git
    current = os.getcwd()
    while current != os.path.dirname(current):  # Not at filesystem root
        if (os.path.exists(os.path.join(current, 'package.json')) or 
            os.path.exists(os.path.join(current, '.git'))):
            return current
        current = os.path.dirname(current)
    
    # Fallback: assume we're in project structure and go up from this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(current_dir))

def load_test_data(filename: str) -> Dict:
    """Load test data from JSON file in testdata directory."""
    project_root = get_project_root()
    testdata_path = os.path.join(project_root, 'testdata', filename)
    
    with open(testdata_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['test_table']

try:
    from pb_table import (
        encode_table, decode_table, encode_verbose, decode_verbose,
        get_table, get_verbose, add_table, add_verbose, get_index,
        encode, decode, get, add, ProtobufTableError
    )
except ImportError as e:
    print(f"Error importing pb_table: {e}")
    print("Make sure pb_table.py is in the parent directory")
    sys.exit(1)

def test_basic_array_format():
    """Test basic encoding/decoding with array format (equivalent to JavaScript basic test)."""
    print("Testing basic array format...")
    
    # Load test data from JSON file
    test_table = load_test_data('basic_array_format.json')
    
    try:
        # Test encoding
        encoded = encode_table(test_table)
        print(f"✓ Encoded {len(test_table['data'])} rows to {len(encoded)} bytes")
        
        # Test decoding
        decoded = decode_table(encoded)
        print(f"✓ Decoded {len(decoded['data'])} rows")
        
        # Verify data integrity with float tolerance
        data_matches = True
        if len(test_table['data']) != len(decoded['data']):
            data_matches = False
            print("✗ Row count mismatch")
        else:
            for i, (orig_row, dec_row) in enumerate(zip(test_table['data'], decoded['data'])):
                if len(orig_row) != len(dec_row):
                    data_matches = False
                    print(f"✗ Row {i} field count mismatch")
                    break
                
                for j, (orig_val, dec_val) in enumerate(zip(orig_row, dec_row)):
                    if isinstance(orig_val, float) and isinstance(dec_val, float):
                        if abs(orig_val - dec_val) > 1e-6:
                            data_matches = False
                            print(f"✗ Row {i}, field {j}: float precision difference too large")
                            break
                    elif orig_val != dec_val:
                        data_matches = False
                        print(f"✗ Row {i}, field {j}: {orig_val} != {dec_val}")
                        break
        
        if data_matches:
            print("✓ Round-trip data integrity verified (with float tolerance)")
        else:
            print("✗ Data mismatch after round-trip")
            print(f"Original: {test_table['data']}")
            print(f"Decoded:  {decoded['data']}")
            return False
            
        # Test alias functions with float tolerance
        encoded_alias = encode(test_table)
        decoded_alias = decode(encoded_alias)
        
        # Compare with float tolerance
        alias_matches = True
        if len(test_table['data']) != len(decoded_alias['data']):
            alias_matches = False
        else:
            for i, (orig_row, dec_row) in enumerate(zip(test_table['data'], decoded_alias['data'])):
                if len(orig_row) != len(dec_row):
                    alias_matches = False
                    break
                
                for j, (orig_val, dec_val) in enumerate(zip(orig_row, dec_row)):
                    if isinstance(orig_val, float) and isinstance(dec_val, float):
                        if abs(orig_val - dec_val) > 1e-6:
                            alias_matches = False
                            break
                    elif orig_val != dec_val:
                        alias_matches = False
                        break
        
        if alias_matches:
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
    
    # Load test data from JSON file
    test_table = load_test_data('verbose_object_format.json')
    
    try:
        # Test encoding
        encoded = encode_verbose(test_table)
        print(f"✓ Encoded {len(test_table['data'])} rows to {len(encoded)} bytes")
        
        # Test decoding
        decoded = decode_verbose(encoded)
        print(f"✓ Decoded {len(decoded['data'])} rows")
        
        # Verify data integrity with float tolerance
        data_matches = True
        if len(test_table['data']) != len(decoded['data']):
            data_matches = False
            print("✗ Row count mismatch")
        else:
            for i, (orig_row, dec_row) in enumerate(zip(test_table['data'], decoded['data'])):
                for orig_key, orig_val in orig_row.items():
                    if orig_key not in dec_row:
                        data_matches = False
                        print(f"✗ Row {i}: missing key {orig_key}")
                        break
                    
                    dec_val = dec_row[orig_key]
                    if isinstance(orig_val, float) and isinstance(dec_val, float):
                        if abs(orig_val - dec_val) > 1e-6:
                            data_matches = False
                            print(f"✗ Row {i}, key {orig_key}: float precision difference too large")
                            break
                    elif orig_val != dec_val:
                        data_matches = False
                        print(f"✗ Row {i}, key {orig_key}: {orig_val} != {dec_val}")
                        break
        
        if data_matches:
            print("✓ Round-trip data integrity verified (with float tolerance)")
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
    
    # Load test data from JSON file
    test_table = load_test_data('transforms.json')
    
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
    
    # Load test data from JSON file
    test_table = load_test_data('sequence_transforms.json')
    
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
    
    # Load test data from JSON file
    test_table = load_test_data('metadata.json')
    
    try:
        # Test encoding with metadata
        encoded = encode_table(test_table)
        print(f"✓ Encoded table with metadata to {len(encoded)} bytes")
        
        # Test decoding with metadata
        decoded = decode_table(encoded)
        print(f"✓ Decoded table with metadata")
        
        # Verify metadata preservation (allowing for extra fields like 'link')
        if 'meta' in decoded:
            orig_meta = test_table['meta']
            dec_meta = decoded['meta']
            
            # Check that all original fields are preserved
            meta_matches = True
            for key, value in orig_meta.items():
                if key not in dec_meta or dec_meta[key] != value:
                    meta_matches = False
                    break
            
            if meta_matches:
                print("✓ Metadata preserved correctly")
            else:
                print("✗ Metadata not preserved correctly")
                print(f"Original meta: {orig_meta}")
                print(f"Decoded meta:  {dec_meta}")
                return False
        else:
            print("✗ Metadata not found in decoded data")
            return False
            
        # Verify data integrity with float tolerance
        data_matches = True
        if len(test_table['data']) != len(decoded['data']):
            data_matches = False
        else:
            for i, (orig_row, dec_row) in enumerate(zip(test_table['data'], decoded['data'])):
                if len(orig_row) != len(dec_row):
                    data_matches = False
                    break
                
                for j, (orig_val, dec_val) in enumerate(zip(orig_row, dec_row)):
                    if isinstance(orig_val, float) and isinstance(dec_val, float):
                        if abs(orig_val - dec_val) > 1e-6:
                            data_matches = False
                            break
                    elif orig_val != dec_val:
                        data_matches = False
                        break
        
        if data_matches:
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
    
    test_table = load_test_data('basic_array_format.json')
    
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
    test_table = load_test_data('basic_array_format.json')
    
    # Test data for object format
    test_verbose = load_test_data('verbose_object_format.json')
    
    try:
        # Test array format random access
        encoded = encode_table(test_table)
        
        # Test single row access with float tolerance
        row_1 = get_table(encoded, 1)
        expected_row = test_table['data'][1]
        
        # Compare with float tolerance
        row_matches = True
        if len(row_1) != len(expected_row):
            row_matches = False
        else:
            for i, (actual, expected) in enumerate(zip(row_1, expected_row)):
                if isinstance(expected, float) and isinstance(actual, float):
                    if abs(actual - expected) > 1e-6:
                        row_matches = False
                        break
                elif actual != expected:
                    row_matches = False
                    break
        
        if row_matches:
            print("✓ Single row access (array format) works correctly")
        else:
            print(f"✗ Single row access failed: {row_1} != {expected_row}")
            return False
        
        # Test multiple row access with float tolerance
        rows_0_2 = get_table(encoded, [0, 2])
        expected = [test_table['data'][0], test_table['data'][2]]
        
        # Compare with float tolerance
        multi_matches = True
        if len(rows_0_2) != len(expected):
            multi_matches = False
        else:
            for i, (actual_row, expected_row) in enumerate(zip(rows_0_2, expected)):
                if len(actual_row) != len(expected_row):
                    multi_matches = False
                    break
                for j, (actual, expected_val) in enumerate(zip(actual_row, expected_row)):
                    if isinstance(expected_val, float) and isinstance(actual, float):
                        if abs(actual - expected_val) > 1e-6:
                            multi_matches = False
                            break
                    elif actual != expected_val:
                        multi_matches = False
                        break
        
        if multi_matches:
            print("✓ Multiple row access (array format) works correctly")
        else:
            print(f"✗ Multiple row access failed: {rows_0_2} != {expected}")
            return False
        
        # Test alias function with float tolerance
        row_alias = get(encoded, 0)
        expected_alias = test_table['data'][0]
        
        # Compare with float tolerance
        alias_matches = True
        if len(row_alias) != len(expected_alias):
            alias_matches = False
        else:
            for i, (actual, expected) in enumerate(zip(row_alias, expected_alias)):
                if isinstance(expected, float) and isinstance(actual, float):
                    if abs(actual - expected) > 1e-6:
                        alias_matches = False
                        break
                elif actual != expected:
                    alias_matches = False
                    break
        
        if alias_matches:
            print("✓ get() alias function works correctly")
        else:
            print("✗ get() alias function failed")
            return False
        
        # Test object format random access
        encoded_verbose = encode_verbose(test_verbose)
        
        # Test single row access (verbose) with float tolerance
        row_verbose = get_verbose(encoded_verbose, 2)
        expected_verbose = test_verbose['data'][2]
        
        # Compare with float tolerance
        verbose_matches = True
        for key, expected_val in expected_verbose.items():
            if key not in row_verbose:
                verbose_matches = False
                break
            actual_val = row_verbose[key]
            if isinstance(expected_val, float) and isinstance(actual_val, float):
                if abs(actual_val - expected_val) > 1e-6:
                    verbose_matches = False
                    break
            elif actual_val != expected_val:
                verbose_matches = False
                break
        
        if verbose_matches:
            print("✓ Single row access (object format) works correctly")
        else:
            print(f"✗ Single row access (verbose) failed: {row_verbose} != {expected_verbose}")
            return False
        
        # Test multiple row access (verbose) with float tolerance
        rows_verbose = get_verbose(encoded_verbose, [0, 2])
        expected_verbose = [test_verbose['data'][0], test_verbose['data'][2]]
        
        # Compare with float tolerance
        multi_verbose_matches = True
        if len(rows_verbose) != len(expected_verbose):
            multi_verbose_matches = False
        else:
            for i, (actual_row, expected_row) in enumerate(zip(rows_verbose, expected_verbose)):
                for key, expected_val in expected_row.items():
                    if key not in actual_row:
                        multi_verbose_matches = False
                        break
                    actual_val = actual_row[key]
                    if isinstance(expected_val, float) and isinstance(actual_val, float):
                        if abs(actual_val - expected_val) > 1e-6:
                            multi_verbose_matches = False
                            break
                    elif actual_val != expected_val:
                        multi_verbose_matches = False
                        break
        
        if multi_verbose_matches:
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
    test_table = load_test_data('sequence_transforms.json')
    
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
    initial_table = load_test_data('basic_array_format.json')
    
    additional_data = [
        [4, "test", 3.14, True],
        [5, "example", 2.71, False],
    ]
    
    # Test data for object format
    initial_verbose = load_test_data('verbose_object_format.json')
    
    additional_verbose_data = [
        {"id": 2, "name": "sensor2", "temperature": 24.1, "active": False },
        {"id": 3, "name": "sensor3", "temperature": 22.8, "active": True }
    ]
    
    try:
        # Test array format data addition
        encoded = encode_table(initial_table)
        expanded = add_table(encoded, additional_data)
        decoded = decode_table(expanded)
        
        expected_data = initial_table['data'] + additional_data
        
        # Compare with float tolerance
        data_matches = True
        if len(decoded['data']) != len(expected_data):
            data_matches = False
        else:
            for i, (actual_row, expected_row) in enumerate(zip(decoded['data'], expected_data)):
                if len(actual_row) != len(expected_row):
                    data_matches = False
                    break
                for j, (actual, expected_val) in enumerate(zip(actual_row, expected_row)):
                    if isinstance(expected_val, float) and isinstance(actual, float):
                        if abs(actual - expected_val) > 1e-6:
                            data_matches = False
                            break
                    elif actual != expected_val:
                        data_matches = False
                        break
        
        if data_matches:
            print("✓ Data addition (array format) works correctly")
        else:
            print(f"✗ Data addition failed: {decoded['data']} != {expected_data}")
            return False
        
        # Test alias function with float tolerance
        expanded_alias = add(encoded, additional_data)
        decoded_alias = decode(expanded_alias)
        
        # Compare with float tolerance
        alias_data_matches = True
        if len(decoded_alias['data']) != len(expected_data):
            alias_data_matches = False
        else:
            for i, (actual_row, expected_row) in enumerate(zip(decoded_alias['data'], expected_data)):
                if len(actual_row) != len(expected_row):
                    alias_data_matches = False
                    break
                for j, (actual, expected_val) in enumerate(zip(actual_row, expected_row)):
                    if isinstance(expected_val, float) and isinstance(actual, float):
                        if abs(actual - expected_val) > 1e-6:
                            alias_data_matches = False
                            break
                    elif actual != expected_val:
                        alias_data_matches = False
                        break
        
        if alias_data_matches:
            print("✓ add() alias function works correctly")
        else:
            print("✗ add() alias function failed")
            return False
        
        # Test object format data addition
        encoded_verbose = encode_verbose(initial_verbose)
        expanded_verbose = add_verbose(encoded_verbose, additional_verbose_data)
        decoded_verbose = decode_verbose(expanded_verbose)
        
        expected_verbose_data = initial_verbose['data'] + additional_verbose_data
        
        # Compare with float tolerance
        verbose_data_matches = True
        if len(decoded_verbose['data']) != len(expected_verbose_data):
            verbose_data_matches = False
        else:
            for i, (actual_row, expected_row) in enumerate(zip(decoded_verbose['data'], expected_verbose_data)):
                for key, expected_val in expected_row.items():
                    if key not in actual_row:
                        verbose_data_matches = False
                        break
                    actual_val = actual_row[key]
                    if isinstance(expected_val, float) and isinstance(actual_val, float):
                        if abs(actual_val - expected_val) > 1e-6:
                            verbose_data_matches = False
                            break
                    elif actual_val != expected_val:
                        verbose_data_matches = False
                        break
        
        if verbose_data_matches:
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
    
    test_table = load_test_data('complex_test_suite.json')
    
    try:
        encoded = encode_table(test_table)
        index = get_index(encoded)
        print("Index", index)
        
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

def test_statistics_calculation():
    """Test statistics calculation for numerical columns."""
    print("\nTesting statistics calculation...")
    
    # Test data with numerical columns
    test_table = load_test_data('complex_test_suite.json')
    
    # Test verbose format data
    test_verbose = load_test_data('verbose_object_format.json')
    
    try:
        # Test array format with statistics
        encoded = encode_table(test_table, calculate_stats=True)
        decoded = decode_table(encoded)
        
        # Verify statistics were calculated
        if 'statistics' not in decoded:
            print("✗ Statistics not found in decoded data")
            return False
        
        stats = decoded['statistics']
        print(f"✓ Statistics calculated for {len(stats)} numerical columns")
        
        # Verify statistics for temperature column
        if 'temperature' in stats:
            temp_stats = stats['temperature']
            expected_min = 21.8
            expected_max = 26.1
            expected_start = 23.5
            expected_end = 22.3
            
            if (temp_stats['min'] == expected_min and 
                temp_stats['max'] == expected_max and
                temp_stats['start'] == expected_start and
                temp_stats['end'] == expected_end):
                print("✓ Temperature statistics calculated correctly")
            else:
                print(f"✗ Temperature statistics incorrect: {temp_stats}")
                return False
        else:
            print("✗ Temperature statistics not found")
            return False
        
        # Verify statistics for pressure column
        if 'pressure' in stats:
            pressure_stats = stats['pressure']
            expected_min = 1010
            expected_max = 1018
            expected_start = 1013
            expected_end = 1012
            
            if (pressure_stats['min'] == expected_min and 
                pressure_stats['max'] == expected_max and
                pressure_stats['start'] == expected_start and
                pressure_stats['end'] == expected_end):
                print("✓ Pressure statistics calculated correctly")
            else:
                print(f"✗ Pressure statistics incorrect: {pressure_stats}")
                return False
        else:
            print("✗ Pressure statistics not found")
            return False
        
        # Verify no statistics for non-numerical columns
        if 'name' in stats or 'active' in stats:
            print("✗ Statistics calculated for non-numerical columns")
            return False
        else:
            print("✓ Statistics correctly excluded non-numerical columns")
        
        # Test verbose format with statistics
        encoded_verbose = encode_verbose(test_verbose, calculate_stats=True)
        decoded_verbose = decode_verbose(encoded_verbose)
        
        if 'statistics' in decoded_verbose and 'value' in decoded_verbose['statistics']:
            value_stats = decoded_verbose['statistics']['value']
            if (value_stats['min'] == 1.5 and 
                value_stats['max'] == 3.7 and
                value_stats['start'] == 1.5 and
                value_stats['end'] == 2.1):
                print("✓ Verbose format statistics calculated correctly")
            else:
                print(f"✗ Verbose format statistics incorrect: {value_stats}")
                return False
        else:
            print("✗ Verbose format statistics not found")
            return False
        
        # Test encoding without statistics
        encoded_no_stats = encode_table(test_table, calculate_stats=False)
        decoded_no_stats = decode_table(encoded_no_stats)
        
        if 'statistics' not in decoded_no_stats:
            print("✓ Statistics correctly omitted when calculate_stats=False")
        else:
            print("✗ Statistics included when calculate_stats=False")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Statistics calculation test failed: {e}")
        traceback.print_exc()
        return False

def test_statistics_updates():
    """Test statistics updates when appending data."""
    print("\nTesting statistics updates...")
    
    # Initial data
    initial_table = load_test_data('basic_array_data.json')
    
    # Additional data
    additional_data = [
        [3, "test", 0.14, True], # New min for value
        [4, "example", 10, False] # New max for value
    ]
    
    # Verbose format data
    initial_verbose = load_test_data('verbose_object_format.json')
    
    additional_verbose = [
        {"id": 2, "name": "sensor2", "temperature": 10.1, "active": False}, # New min
        {"id": 3, "name": "sensor3", "temperature": 45.8, "active": True}  # New max
    ]
    
    try:
        # Test array format statistics updates
        encoded = encode_table(initial_table, calculate_stats=True)
        initial_decoded = decode_table(encoded)
        
        # Verify initial statistics
        initial_stats = initial_decoded['statistics']
        if (initial_stats['value']['min'] == 10.5 and 
            initial_stats['value']['max'] == 15.2 and
            initial_stats['count']['min'] == 100 and
            initial_stats['count']['max'] == 150):
            print("✓ Initial statistics calculated correctly")
        else:
            print(f"✗ Initial statistics incorrect: {initial_stats}")
            return False
        
        # Add data and check updated statistics
        expanded = add_table(encoded, additional_data)
        final_decoded = decode_table(expanded)
        
        if 'statistics' not in final_decoded:
            print("✗ Statistics lost after adding data")
            return False
        
        final_stats = final_decoded['statistics']
        
        # Check updated statistics
        if (final_stats['value']['min'] == 8.7 and    # New min
            final_stats['value']['max'] == 18.9 and   # New max
            final_stats['value']['start'] == 10.5 and # Original start
            final_stats['value']['end'] == 18.9 and   # New end
            final_stats['count']['min'] == 80 and     # New min
            final_stats['count']['max'] == 200 and    # New max
            final_stats['count']['start'] == 100 and  # Original start
            final_stats['count']['end'] == 200):      # New end
            print("✓ Statistics updated correctly after adding data")
        else:
            print(f"✗ Statistics not updated correctly: {final_stats}")
            return False
        
        # Test verbose format statistics updates
        encoded_verbose = encode_verbose(initial_verbose, calculate_stats=True)
        expanded_verbose = add_verbose(encoded_verbose, additional_verbose)
        final_verbose = decode_verbose(expanded_verbose)
        
        if 'statistics' in final_verbose and 'score' in final_verbose['statistics']:
            score_stats = final_verbose['statistics']['score']
            if (score_stats['min'] == 78.1 and    # New min
                score_stats['max'] == 96.7 and    # New max
                score_stats['start'] == 85.5 and  # Original start
                score_stats['end'] == 96.7):      # New end
                print("✓ Verbose format statistics updated correctly")
            else:
                print(f"✗ Verbose format statistics not updated correctly: {score_stats}")
                return False
        else:
            print("✗ Verbose format statistics not found after update")
            return False
        
        # Test adding data to table without initial statistics
        no_stats_encoded = encode_table(initial_table, calculate_stats=False)
        no_stats_expanded = add_table(no_stats_encoded, additional_data)
        no_stats_final = decode_table(no_stats_expanded)
        
        if 'statistics' not in no_stats_final:
            print("✓ No statistics created when adding to table without initial statistics")
        else:
            print("✗ Statistics unexpectedly created when adding to table without initial statistics")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Statistics updates test failed: {e}")
        traceback.print_exc()
        return False

def test_comprehensive_api():
    """Test comprehensive API compatibility with all new functions."""
    print("\nTesting comprehensive API compatibility...")
    
    test_table = load_test_data('api_test_suite.json')
    
    try:
        # Test full workflow: encode -> get -> add -> decode
        encoded = encode_table(test_table)
        
        # Get specific row with float tolerance
        first_row = get_table(encoded, 0)
        expected_first = test_table['data'][0]
        
        # Compare with float tolerance
        first_row_matches = True
        if len(first_row) != len(expected_first):
            first_row_matches = False
        else:
            for i, (actual, expected) in enumerate(zip(first_row, expected_first)):
                if isinstance(expected, float) and isinstance(actual, float):
                    if abs(actual - expected) > 1e-6:
                        first_row_matches = False
                        break
                elif actual != expected:
                    first_row_matches = False
                    break
        
        if first_row_matches:
            print("✓ Random access retrieval works")
        else:
            print("✗ Random access retrieval failed")
            return False
        
        # Add new data
        new_data = [[1609459480, -41.124230, 24.12, 120, 1025, "sensor_06", False]]
        expanded = add_table(encoded, new_data)
        
        # Verify expansion with float tolerance
        final_decoded = decode_table(expanded)
        expected_final = test_table['data'] + new_data
        
        # Compare with float tolerance
        workflow_matches = True
        if len(final_decoded['data']) != len(expected_final):
            workflow_matches = False
        else:
            for i, (actual_row, expected_row) in enumerate(zip(final_decoded['data'], expected_final)):
                if len(actual_row) != len(expected_row):
                    workflow_matches = False
                    break
                for j, (actual, expected_val) in enumerate(zip(actual_row, expected_row)):
                    if isinstance(expected_val, float) and isinstance(actual, float):
                        if abs(actual - expected_val) > 1e-6:
                            workflow_matches = False
                            break
                    elif actual != expected_val:
                        workflow_matches = False
                        break
        
        if workflow_matches:
            print("✓ Full workflow (encode->get->add->decode) works correctly")
        else:
            print("✗ Full workflow failed")
            return False
        
        # Test indexing on expanded data
        index = get_index(expanded)
        if len(index) == len(test_table['data']) + 1:  # Original 2 + 1 new
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

def export_complex_test_data():
    """Export the most complex test data for cross-language testing."""
    print("\nExporting complex test data for cross-language testing...")
    
    # Create the most complex test case combining multiple features
    complex_test_table = load_test_data('complex_test_suite.json')
    
    try:
        # Encode with Python
        encoded = encode_table(complex_test_table)
        print(f"✓ Python encoded complex test: {len(complex_test_table['data'])} rows → {len(encoded)} bytes")
        
        # Save for JavaScript testing
        project_root = get_project_root()
        output_path = os.path.join(project_root, 'testdata', 'complex_test_suite_python.pb')
        with open(output_path, 'wb') as f:
            f.write(encoded)
        print("✓ Saved as complex_test_suite_python.pb")
        
        # Test Python can decode its own data
        decoded = decode_table(encoded)
        print(f"✓ Python self-decode: {len(decoded['data'])} rows")
        
        return True
        
    except Exception as e:
        print(f"✗ Error exporting complex test data: {e}")
        import traceback
        traceback.print_exc()
        return False
    
def cross_platform_test():
    try:
        project_root = get_project_root()
        js_file_path = os.path.join(project_root, 'testdata', 'complex_test_suite_js.pb')
        
        # Load original JSON for compression ratio calculation
        json_file_path = os.path.join(project_root, 'testdata', 'complex_test_suite.json')
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = f.read()
        json_size = len(json_data.encode('utf-8'))
        
        # Load JavaScript binary
        with open(js_file_path, 'rb') as f:
            js_data = f.read()
        js_binary_size = len(js_data)
        
        # Load Python binary for comparison
        py_file_path = os.path.join(project_root, 'testdata', 'complex_test_suite_python.pb')
        try:
            with open(py_file_path, 'rb') as f:
                py_data = f.read()
            py_binary_size = len(py_data)
        except FileNotFoundError:
            py_binary_size = None
        
        # Calculate compression ratios
        js_compression_ratio = json_size / js_binary_size if js_binary_size > 0 else 0
        js_compression_percent = ((json_size - js_binary_size) / json_size * 100) if json_size > 0 else 0
        
        print(f'📊 Compression Analysis:')
        print(f'  Original JSON: {json_size:,} bytes')
        print(f'  JavaScript binary: {js_binary_size:,} bytes')
        if py_binary_size is not None:
            py_compression_ratio = json_size / py_binary_size if py_binary_size > 0 else 0
            py_compression_percent = ((json_size - py_binary_size) / json_size * 100) if json_size > 0 else 0
            print(f'  Python binary: {py_binary_size:,} bytes')
            print(f'  JS compression ratio: {js_compression_ratio:.2f}:1 ({js_compression_percent:.1f}% reduction)')
            print(f'  Python compression ratio: {py_compression_ratio:.2f}:1 ({py_compression_percent:.1f}% reduction)')
            size_diff = abs(js_binary_size - py_binary_size)
            if js_binary_size == py_binary_size:
                print(f'  ✅ Binary formats identical: {js_binary_size:,} bytes')
            elif js_binary_size < py_binary_size:
                print(f'  📈 JavaScript binary smaller by {size_diff:,} bytes')
            else:
                print(f'  📈 Python binary smaller by {size_diff:,} bytes')
        else:
            print(f'  Compression ratio: {js_compression_ratio:.2f}:1')
            print(f'  Size reduction: {js_compression_percent:.1f}%')
        print(f'  Space saved: {json_size - js_binary_size:,} bytes')
        
        # Try to decode with Python
        decoded = decode_table(js_data)
        print(f'✓ Successfully decoded JavaScript data with Python!')
        print(f'  Rows: {len(decoded["data"])}')
        print(f'  Fields: {len(decoded["header"])}')
        if len(decoded["data"]) > 0:
            print(f'  First row: {decoded["data"][0]}')
        else:
            print('  No data rows found')
                                      
    except Exception as e:
        print(f'✗ Failed to decode JavaScript data with Python: {e}')
        import traceback
        traceback.print_exc()

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
        test_comprehensive_api,
        export_complex_test_data
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
    
    args = sys.argv
    if len(args) == 1 or args[1] != 'cross':
        success = run_all_tests()
    else:
        success = cross_platform_test()

    if success:
        print("\n" + "🎉" * 20)
        print("All tests passed! Now exporting complex test data...")
        export_success = export_complex_test_data()
        if export_success:
            print("✅ Complex test data exported successfully!")
        else:
            print("❌ Failed to export complex test data.")
            success = False
    
    sys.exit(0 if success else 1)
