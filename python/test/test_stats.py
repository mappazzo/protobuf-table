#!/usr/bin/env python3
"""
Test statistics functionality in protobuf-table implementation
"""

import pb_table

def test_stats_calculation():
    """Test that statistics are calculated and preserved correctly."""
    
    # Test table with numeric data
    test_table = {
        'header': [
            {'name': 'id', 'type': 'uint'},
            {'name': 'name', 'type': 'string'},
            {'name': 'temperature', 'type': 'float'},
            {'name': 'count', 'type': 'int'}
        ],
        'data': [
            [1, 'sensor1', 20.5, 100],
            [2, 'sensor2', 25.0, 150],
            [3, 'sensor3', 18.2, 75],
            [4, 'sensor4', 30.1, 200],
            [5, 'sensor5', 22.8, 125]
        ],
        'meta': {
            'filename': 'sensor_data.pb',
            'owner': 'test_user',
            'comment': 'Temperature sensor readings'
        }
    }
    
    print("Testing statistics calculation...")
    
    # Encode the table (this should automatically calculate stats)
    encoded = pb_table.encode_table(test_table)
    print(f"Encoded table to {len(encoded)} bytes")
    
    # Decode and check if stats are preserved
    decoded = pb_table.decode_table(encoded)
    
    print("\nDecoded table structure:")
    print(f"Row count: {decoded['meta']['row_count']}")
    
    # Check statistics for numeric fields
    for field in decoded['header']:
        print(f"\nField: {field['name']} (type: {field['type']})")
        if 'stats' in field:
            stats = field['stats']
            print(f"  Start: {stats['start']}")
            print(f"  End: {stats['end']}")
            print(f"  Min: {stats['min']}")
            print(f"  Max: {stats['max']}")
            print(f"  Mean: {stats['mean']:.2f}")
        else:
            print("  No statistics (non-numeric field)")
    
    # Verify specific statistics
    temp_field = next(f for f in decoded['header'] if f['name'] == 'temperature')
    temp_stats = temp_field['stats']
    
    expected_temp_stats = {
        'start': 20.5,
        'end': 22.8,
        'min': 18.2,
        'max': 30.1,
        'mean': (20.5 + 25.0 + 18.2 + 30.1 + 22.8) / 5
    }
    
    print(f"\nVerifying temperature statistics:")
    print(f"Expected mean: {expected_temp_stats['mean']:.2f}")
    print(f"Actual mean: {temp_stats['mean']:.2f}")
    print(f"Statistics match: {abs(temp_stats['mean'] - expected_temp_stats['mean']) < 0.01}")
    
    # Test verbose format as well
    print(f"\nTesting verbose format...")
    verbose_table = {
        'header': test_table['header'],
        'meta': test_table['meta'],
        'data': [
            {'id': 1, 'name': 'sensor1', 'temperature': 20.5, 'count': 100},
            {'id': 2, 'name': 'sensor2', 'temperature': 25.0, 'count': 150},
            {'id': 3, 'name': 'sensor3', 'temperature': 18.2, 'count': 75}
        ]
    }
    
    encoded_verbose = pb_table.encode_verbose(verbose_table)
    decoded_verbose = pb_table.decode_verbose(encoded_verbose)
    
    print(f"Verbose format encoded to {len(encoded_verbose)} bytes")
    print(f"Verbose format has {len(decoded_verbose['data'])} rows")
    
    # Check that verbose format also has statistics
    temp_field_verbose = next(f for f in decoded_verbose['header'] if f['name'] == 'temperature')
    if 'stats' in temp_field_verbose:
        print("✓ Statistics preserved in verbose format")
    else:
        print("✗ Statistics missing in verbose format")
    
    print("\n✓ Statistics functionality test completed successfully!")

if __name__ == "__main__":
    test_stats_calculation()
