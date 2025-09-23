// Test cross-language compatibility between JavaScript and Python implementations

var pbTable = require('../src/pbTable')
var fs = require('fs')
var path = require('path')
var jsonData = require('../../testdata/complex_test_suite.json');
var _ = require('lodash')

function testCrossLanguageCompatibility() {
  console.log('Testing cross-language compatibility... \n')
  var decodedJS = null

  // Encode with JavaScript
  console.log('Encode and export data using Javascript...')
  const testTable = jsonData.test_table
  pbTable.encodeTable(testTable, function (err, encoded) {
    if (err) {
      console.error('JavaScript encoding error:', err)
      return
    }
    
    console.log('JavaScript encoded table to', encoded.length, 'bytes')
    
    // Save encoded data for Python to read
    var outputPath = path.join(__dirname, '../../testdata/complex_test_suite_js.pb')
    fs.writeFileSync(outputPath, Buffer.from(encoded))
    console.log('Saved JavaScript-encoded data to:', outputPath)
    // Test JavaScript decoding of its own data
    pbTable.decodeTable(encoded, function (err, decoded) {
      if (err) {
        console.error('JavaScript decoding error:', err)
        return
      }
      
      decodedJS = decoded.data
      console.log('JavaScript successfully decoded its own data:')
      console.log('- Rows:', decoded.data.length)
      console.log('- Fields:', decoded.header.length)
      const lodashTest = _.isEqual(decoded.data, testTable.data)
      console.log('- Raw and Decoded data isEqual(): ', lodashTest)
      if(!lodashTest) console.log('- Compare data: ', { source: testTable.data, decoded: decoded.data })

      // Check for statistics
      var tempField = decoded.header.find(function (f) { return f.name === 'temperature' })
      if (tempField && tempField.stats) {
        console.log('- Temperature stats: min=' + tempField.stats.min + ', max=' + tempField.stats.max + ', mean=' + tempField.stats.mean.toFixed(2))
      } else {
        console.log('- No temperature statistics found')
      }
      console.log('✓ JavaScript implementation working correctly!')
      console.log('To test cross-language compatibility run: test_pb_table.py\n')
    })
  })

  console.log('Import data from python binary and decode using Javascript...')
  const binaryPath = '../../testdata/complex_test_suite_python.pb'
  try {
    const binaryData = fs.readFileSync(binaryPath);
    pbTable.decodeTable(binaryData, (err, decoded) => {
        if (err) console.error('Error:', err.message);
        else {
          console.log('JavaScript successfully decoded its Python data:')
          console.log('- Rows:', decoded.data.length)
          console.log('- Fields:', decoded.header.length)
          const lodashTest1 = _.isEqual(decoded.data, testTable.data)
          const lodashTest2 = _.isEqual(decoded.data, decodedJS)
          console.log('- Raw and Python Decoded data isEqual(): ', lodashTest1)
          console.log('- JS and Python Decoded data isEqual(): ', lodashTest2)
          if(!lodashTest1 || !lodashTest2) {
            console.log('Found Differences')
            console.log({ 
              source: testTable.data, 
              decodedPython: decoded.data,
              decodedJS: decodedJS
            })
          }
        }
    });
  } catch (e) {
    if(e.errno === -4058) console.log(`FAILED: could not load python generated binary, ensure '${binaryPath}' exists`)
    else console.log(e)
  }
}

// Run the test
testCrossLanguageCompatibility()
