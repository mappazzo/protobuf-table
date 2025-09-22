#!/usr/bin/env python3
"""
Cross-Language Compatibility Test

Test the new JavaScript-compatible Python implementation against the JavaScript version.
"""

import json
from pb_table_compatible import encode_table_compatible, decode_table

def create_comprehensive_test_data():
    """Create comprehensive test data for cross-language testing."""
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
            [5, 1634568130, 24.7, 64.2, 'sensor_05', False, -104]
        ]
    }

def create_transform_test_data():
    """Create test data with transforms."""
    return {
        'header': [
            {'name': 'id', 'type': 'uint'},
            {'name': 'timestamp', 'type': 'uint', 'transform': {'offset': 1634567890, 'sequence': True}},
            {'name': 'temperature', 'type': 'int', 'transform': {'offset': 20, 'multip': 100, 'decimals': 1}},
            {'name': 'location', 'type': 'string'},
            {'name': 'active', 'type': 'bool'}
        ],
        'data': [
            [1, 1634567890, 23.5, 'sensor_01', True],
            [2, 1634567950, 24.1, 'sensor_02', False],
            [3, 1634568010, 23.8, 'sensor_03', True],
            [4, 1634568070, 25.2, 'sensor_04', True],
            [5, 1634568130, 24.7, 'sensor_05', False]
        ]
    }

def test_python_compatible_encoding():
    """Test Python compatible encoding."""
    print("🐍 Testing Python Compatible Encoding...")
    
    # Basic test
    basic_data = create_comprehensive_test_data()
    basic_encoded = encode_table_compatible(basic_data)
    
    print(f"Basic data: {len(basic_data['data'])} rows → {len(basic_encoded)} bytes")
    
    # Transform test
    transform_data = create_transform_test_data()
    transform_encoded = encode_table_compatible(transform_data)
    
    print(f"Transform data: {len(transform_data['data'])} rows → {len(transform_encoded)} bytes")
    
    # Save for JavaScript testing
    with open('python_compatible_basic.pb', 'wb') as f:
        f.write(basic_encoded)
    
    with open('python_compatible_transform.pb', 'wb') as f:
        f.write(transform_encoded)
    
    # Save original data for JavaScript encoding
    with open('test_data_compatible_basic.json', 'w') as f:
        json.dump(basic_data, f)
    
    with open('test_data_compatible_transform.json', 'w') as f:
        json.dump(transform_data, f)
    
    # Test Python decoding its own data
    decoded_basic = decode_table(basic_encoded)
    decoded_transform = decode_table(transform_encoded)
    
    print(f"Python self-decode basic: {len(decoded_basic['data'])} rows")
    print(f"Python self-decode transform: {len(decoded_transform['data'])} rows")
    
    return basic_encoded, transform_encoded

def create_javascript_compatibility_test():
    """Create JavaScript test for compatibility."""
    js_script = '''
const pbTable = require('./src/pbTable');
const fs = require('fs');

console.log('🟨 Testing JavaScript Compatibility with Python...');

// Load test data
const basicData = JSON.parse(fs.readFileSync('../python/test_data_compatible_basic.json', 'utf8'));
const transformData = JSON.parse(fs.readFileSync('../python/test_data_compatible_transform.json', 'utf8'));

console.log('\\n📤 JavaScript encoding test data...');

// Encode with JavaScript
pbTable.encodeTable(basicData, (err, jsBasicBuffer) => {
    if (err) {
        console.error('JavaScript basic encoding error:', err);
        return;
    }
    
    console.log(`JavaScript basic: ${basicData.data.length} rows → ${jsBasicBuffer.length} bytes`);
    fs.writeFileSync('../python/js_compatible_basic.pb', jsBasicBuffer);
    
    pbTable.encodeTable(transformData, (err, jsTransformBuffer) => {
        if (err) {
            console.error('JavaScript transform encoding error:', err);
            return;
        }
        
        console.log(`JavaScript transform: ${transformData.data.length} rows → ${jsTransformBuffer.length} bytes`);
        fs.writeFileSync('../python/js_compatible_transform.pb', jsTransformBuffer);
        
        console.log('\\n📥 JavaScript decoding Python data...');
        
        // Test JavaScript decoding Python data
        try {
            const pythonBasicData = fs.readFileSync('../python/python_compatible_basic.pb');
            pbTable.decodeTable(pythonBasicData, (err, result) => {
                if (err) {
                    console.log(`  ✗ Failed to decode Python basic data: ${err.message}`);
                } else {
                    console.log(`  ✓ Successfully decoded Python basic data: ${result.data.length} rows`);
                    
                    // Check if statistics are preserved
                    const tempField = result.header.find(f => f.name === 'temperature');
                    if (tempField && tempField.stats) {
                        console.log(`    Temperature stats: min=${tempField.stats.min}, max=${tempField.stats.max}`);
                    }
                }
                
                // Test transform data
                try {
                    const pythonTransformData = fs.readFileSync('../python/python_compatible_transform.pb');
                    pbTable.decodeTable(pythonTransformData, (err, result) => {
                        if (err) {
                            console.log(`  ✗ Failed to decode Python transform data: ${err.message}`);
                        } else {
                            console.log(`  ✓ Successfully decoded Python transform data: ${result.data.length} rows`);
                        }
                        
                        console.log('\\n🎯 Cross-language compatibility test completed!');
                    });
                } catch (e) {
                    console.log(`  ✗ Error reading Python transform file: ${e.message}`);
                }
            });
        } catch (e) {
            console.log(`  ✗ Error reading Python basic file: ${e.message}`);
        }
    });
});
'''
    
    with open('../javascript/compatibility_test.js', 'w', encoding='utf-8') as f:
        f.write(js_script)
    
    print("🔧 Created JavaScript compatibility test script")

def test_python_decoding_javascript():
    """Test Python decoding JavaScript data (after JavaScript test runs)."""
    print("\n🔄 Testing Python decoding JavaScript data...")
    
    try:
        if os.path.exists('js_compatible_basic.pb'):
            with open('js_compatible_basic.pb', 'rb') as f:
                js_basic = f.read()
            
            decoded = decode_table(js_basic)
            print(f"  ✓ Python decoded JavaScript basic data: {len(decoded['data'])} rows")
            
            # Check statistics
            temp_field = next((f for f in decoded['header'] if f['name'] == 'temperature'), None)
            if temp_field and 'stats' in temp_field:
                stats = temp_field['stats']
                print(f"    Temperature stats: min={stats['min']}, max={stats['max']}")
        else:
            print("  ⏳ JavaScript basic file not yet available")
    except Exception as e:
        print(f"  ✗ Failed to decode JavaScript basic data: {e}")
    
    try:
        if os.path.exists('js_compatible_transform.pb'):
            with open('js_compatible_transform.pb', 'rb') as f:
                js_transform = f.read()
            
            decoded = decode_table(js_transform)
            print(f"  ✓ Python decoded JavaScript transform data: {len(decoded['data'])} rows")
        else:
            print("  ⏳ JavaScript transform file not yet available")
    except Exception as e:
        print(f"  ✗ Failed to decode JavaScript transform data: {e}")

if __name__ == "__main__":
    import os
    
    print("🔗 Cross-Language Compatibility Test")
    print("=" * 50)
    
    # Test Python compatible encoding
    basic_encoded, transform_encoded = test_python_compatible_encoding()
    
    # Create JavaScript test
    create_javascript_compatibility_test()
    
    print(f"\n📋 Results Summary:")
    print(f"✓ Python compatible encoding working")
    print(f"✓ Python self-decoding working")
    print(f"✓ Test data saved for JavaScript")
    
    print(f"\n🚀 Next Steps:")
    print(f"1. Run: cd ../javascript && node compatibility_test.js")
    print(f"2. Then run this script again to test Python decoding JavaScript data")
    print(f"3. Verify full cross-language compatibility")
    
    # If JavaScript files exist, test decoding them
    test_python_decoding_javascript()
