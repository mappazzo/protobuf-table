
const pbTable = require('./src/pbTable');
const fs = require('fs');

console.log('🟨 JavaScript decoding Python data...');

// Test decoding Python basic data
try {
    const pythonBasicData = fs.readFileSync('../python/python_basic_test.pb');
    pbTable.decodeTable(pythonBasicData, (err, result) => {
        if (err) {
            console.log('  ✗ Failed to decode Python basic data:', err.message);
        } else {
            console.log(`  ✓ Successfully decoded Python basic data: ${result.data.length} rows`);
        }
        
        // Test decoding Python transform data
        try {
            const pythonTransformData = fs.readFileSync('../python/python_transform_test.pb');
            pbTable.decodeTable(pythonTransformData, (err, result) => {
                if (err) {
                    console.log('  ✗ Failed to decode Python transform data:', err.message);
                } else {
                    console.log(`  ✓ Successfully decoded Python transform data: ${result.data.length} rows`);
                }
                
                console.log('\n📋 Cross-decoding test completed!');
            });
        } catch (e) {
            console.log('  ✗ Error reading Python transform file:', e.message);
        }
    });
} catch (e) {
    console.log('  ✗ Error reading Python basic file:', e.message);
}
