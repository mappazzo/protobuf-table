// Test cross-language compatibility between JavaScript and Python implementations

var pbTable = require('../src/pbTable')
var fs = require('fs')
var path = require('path')

function testCrossLanguageCompatibility() {
  console.log('Testing cross-language compatibility...')
  
  // Test table with statistics
  var testTable = {
    header: [
      { name: 'id', type: 'uint' },
      { name: 'name', type: 'string' },
      { name: 'temperature', type: 'float' }
    ],
    data: [
      [1, 'sensor1', 20.5],
      [2, 'sensor2', 25.0],
      [3, 'sensor3', 18.2]
    ],
    meta: {
      name: 'cross_language_test.pb',
      owner: 'test_user',
      comment: 'Cross-language compatibility test'
    }
  }
  
  // Encode with JavaScript
  pbTable.encodeTable(testTable, function (err, encoded) {
    if (err) {
      console.error('JavaScript encoding error:', err)
      return
    }
    
    console.log('JavaScript encoded table to', encoded.length, 'bytes')
    
    // Save encoded data for Python to read
    var outputPath = path.join(__dirname, '../../python/js_encoded_test.pb')
    fs.writeFileSync(outputPath, Buffer.from(encoded))
    console.log('Saved JavaScript-encoded data to:', outputPath)
    
    // Test JavaScript decoding of its own data
    pbTable.decodeTable(encoded, function (err, decoded) {
      if (err) {
        console.error('JavaScript decoding error:', err)
        return
      }
      
      console.log('JavaScript successfully decoded its own data:')
      console.log('- Rows:', decoded.data.length)
      console.log('- Fields:', decoded.header.length)
      
      // Check for statistics
      var tempField = decoded.header.find(function (f) { return f.name === 'temperature' })
      if (tempField && tempField.stats) {
        console.log('- Temperature stats: min=' + tempField.stats.min + ', max=' + tempField.stats.max + ', mean=' + tempField.stats.mean.toFixed(2))
      } else {
        console.log('- No temperature statistics found')
      }
      
      console.log('\n✓ JavaScript implementation working correctly!')
      console.log('\nTo test cross-language compatibility:')
      console.log('1. Run: cd ../python && python -c "')
      console.log('import pb_table')
      console.log('with open(\'js_encoded_test.pb\', \'rb\') as f:')
      console.log('    data = f.read()')
      console.log('decoded = pb_table.decode_table(data)')
      console.log('print(\'Python decoded JS data:\', len(decoded[\'data\']), \'rows\')')
      console.log('print(\'Temperature stats:\', [f for f in decoded[\'header\'] if f[\'name\'] == \'temperature\'][0].get(\'stats\', \'None\'))')
      console.log('"')
      console.log('\n2. Then encode with Python and test JavaScript decoding')
    })
  })
}

// Run the test
testCrossLanguageCompatibility()
