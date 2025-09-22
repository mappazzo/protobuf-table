
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
        console.log(`\nTransform Data:`);
        console.log(`  JSON size: ${transformJsonSize} bytes`);
        console.log(`  JavaScript PB size: ${transformBuffer.length} bytes`);
        console.log(`  Compression ratio: ${(transformJsonSize / transformBuffer.length).toFixed(2)}x`);
        
        // Save for Python comparison
        fs.writeFileSync('../python/js_transform_test.pb', transformBuffer);
        
        console.log('\n📊 JavaScript compression test completed!');
        console.log('Saved encoded data for cross-comparison.');
    });
});
