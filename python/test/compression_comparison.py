#!/usr/bin/env python3
"""
Compression Comparison Test

Compare compression efficiency between JavaScript and Python implementations
to determine which provides better compression and should be the basis for compatibility.
"""

import json
from pb_table import encode_table, decode_table
import os

def create_test_data():
    """Create comprehensive test data for compression comparison."""
    return {
        'header': [
            {'name': 'id', 'type': 'uint'},
            {'name': 'timestamp', 'type': 'uint'},
            {'name': 'temperature', 'type': 'float'},
            {'name': 'humidity', 'type': 'float'},
            {'name': 'location', 'type': 'string'},
            {'name': 'active', 'type': 'bool'},
            {'name': 'sensor_id', 'type': 'int'}
        ],
        'data': [
            [1, 1634567890, 23.5, 65.2, 'sensor_01', True, -100],
            [2, 1634567950, 24.1, 64.8, 'sensor_02', False, -101],
            [3, 1634568010, 23.8, 65.5, 'sensor_03', True, -102],
            [4, 1634568070, 25.2, 63.1, 'sensor_04', True, -103],
            [5, 1634568130, 24.7, 64.2, 'sensor_05', False, -104],
            [6, 1634568190, 23.9, 65.8, 'sensor_06', True, -105],
            [7, 1634568250, 24.3, 64.5, 'sensor_07', False, -106],
            [8, 1634568310, 25.1, 63.7, 'sensor_08', True, -107],
            [9, 1634568370, 24.8, 64.9, 'sensor_09', False, -108],
            [10, 1634568430, 23.6, 65.3, 'sensor_10', True, -109]
        ]
    }

def create_transform_test_data():
    """Create test data with transforms for better compression."""
    return {
        'header': [
            {'name': 'id', 'type': 'uint'},
            {'name': 'timestamp', 'type': 'uint', 'transform': {'offset': 1634567890, 'sequence': True}},
            {'name': 'temperature', 'type': 'int', 'transform': {'offset': 20, 'multip': 100, 'decimals': 1}},
            {'name': 'humidity', 'type': 'int', 'transform': {'offset': 60, 'multip': 100, 'decimals': 1}},
            {'name': 'location', 'type': 'string'},
            {'name': 'active', 'type': 'bool'}
        ],
        'data': [
            [1, 1634567890, 23.5, 65.2, 'sensor_01', True],
            [2, 1634567950, 24.1, 64.8, 'sensor_02', False],
            [3, 1634568010, 23.8, 65.5, 'sensor_03', True],
            [4, 1634568070, 25.2, 63.1, 'sensor_04', True],
            [5, 1634568130, 24.7, 64.2, 'sensor_05', False],
            [6, 1634568190, 23.9, 65.8, 'sensor_06', True],
            [7, 1634568250, 24.3, 64.5, 'sensor_07', False],
            [8, 1634568310, 25.1, 63.7, 'sensor_08', True],
            [9, 1634568370, 24.8, 64.9, 'sensor_09', False],
            [10, 1634568430, 23.6, 65.3, 'sensor_10', True]
        ]
    }

def test_python_compression():
    """Test Python implementation compression."""
    print("🐍 Testing Python Implementation Compression...")
    
    # Basic test
    basic_data = create_test_data()
    basic_json = json.dumps(basic_data).encode('utf-8')
    basic_pb = encode_table(basic_data)
    
    print(f"Basic Data:")
    print(f"  JSON size: {len(basic_json)} bytes")
    print(f"  Python PB size: {len(basic_pb)} bytes")
    print(f"  Compression ratio: {len(basic_json) / len(basic_pb):.2f}x")
    
    # Transform test
    transform_data = create_transform_test_data()
    transform_json = json.dumps(transform_data).encode('utf-8')
    transform_pb = encode_table(transform_data)
    
    print(f"\nTransform Data:")
    print(f"  JSON size: {len(transform_json)} bytes")
    print(f"  Python PB size: {len(transform_pb)} bytes")
    print(f"  Compression ratio: {len(transform_json) / len(transform_pb):.2f}x")
    
    # Save test data for JavaScript comparison
    with open('python_basic_test.pb', 'wb') as f:
        f.write(basic_pb)
    
    with open('python_transform_test.pb', 'wb') as f:
        f.write(transform_pb)
    
    # Save original data for JavaScript encoding
    with open('test_data_basic.json', 'w') as f:
        json.dump(basic_data, f)
    
    with open('test_data_transform.json', 'w') as f:
        json.dump(transform_data, f)
    
    return {
        'basic': {'json': len(basic_json), 'pb': len(basic_pb)},
        'transform': {'json': len(transform_json), 'pb': len(transform_pb)}
    }

def create_javascript_test_script():
    """Create JavaScript test script for compression comparison."""
    js_script = '''
const pbTable = require('./src/pbTable');
const fs = require('fs');

console.log('🟨 Testing JavaScript Implementation Compression...');

// Load test data
const basicData = JSON.parse(fs.readFileSync('../python/test_data_basic.json', 'utf8'));
const transformData = JSON.parse(fs.readFileSync('../python/test_data_transform.json', 'utf8'));

// Test basic data
pbTable.encodeTable(basicData, (err, basicBuffer) => {
    if (err) {
        console.error('Basic encoding error:', err);
        return;
    }
    
    const basicJsonSize = JSON.stringify(basicData).length;
    console.log(`Basic Data:`);
    console.log(`  JSON size: ${basicJsonSize} bytes`);
    console.log(`  JavaScript PB size: ${basicBuffer.length} bytes`);
    console.log(`  Compression ratio: ${(basicJsonSize / basicBuffer.length).toFixed(2)}x`);
    
    // Save for Python comparison
    fs.writeFileSync('../python/js_basic_test.pb', basicBuffer);
    
    // Test transform data
    pbTable.encodeTable(transformData, (err, transformBuffer) => {
        if (err) {
            console.error('Transform encoding error:', err);
            return;
        }
        
        const transformJsonSize = JSON.stringify(transformData).length;
        console.log(`\\nTransform Data:`);
        console.log(`  JSON size: ${transformJsonSize} bytes`);
        console.log(`  JavaScript PB size: ${transformBuffer.length} bytes`);
        console.log(`  Compression ratio: ${(transformJsonSize / transformBuffer.length).toFixed(2)}x`);
        
        // Save for Python comparison
        fs.writeFileSync('../python/js_transform_test.pb', transformBuffer);
        
        console.log('\\n📊 JavaScript compression test completed!');
        console.log('Saved encoded data for cross-comparison.');
    });
});
'''
    
    with open('../javascript/compression_test.js', 'w', encoding='utf-8') as f:
        f.write(js_script)

if __name__ == "__main__":
    print("🔍 Compression Comparison Analysis")
    print("=" * 50)
    
    # Test Python compression
    python_results = test_python_compression()
    
    # Create JavaScript test script
    create_javascript_test_script()
    
    print(f"\n📋 Python Results Summary:")
    print(f"Basic compression: {python_results['basic']['json'] / python_results['basic']['pb']:.2f}x")
    print(f"Transform compression: {python_results['transform']['json'] / python_results['transform']['pb']:.2f}x")
    
    print(f"\n🔧 Next steps:")
    print(f"1. Run: cd ../javascript && node compression_test.js")
    print(f"2. Compare compression ratios")
    print(f"3. Test cross-decoding capabilities")
    print(f"4. Determine which implementation to use as compatibility base")
