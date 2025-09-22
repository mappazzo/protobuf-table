// Test statistics functionality in JavaScript protobuf-table implementation

var pbTable = require('../src/pbTable')

function testStatsCalculation() {
  console.log('Testing JavaScript statistics calculation...')
  
  // Test table with numeric data
  var testTable = {
    header: [
      { name: 'id', type: 'uint' },
      { name: 'name', type: 'string' },
      { name: 'temperature', type: 'float' },
      { name: 'count', type: 'int' }
    ],
    data: [
      [1, 'sensor1', 20.5, 100],
      [2, 'sensor2', 25.0, 150],
      [3, 'sensor3', 18.2, 75],
      [4, 'sensor4', 30.1, 200],
      [5, 'sensor5', 22.8, 125]
    ],
    meta: {
      name: 'sensor_data.pb',
      owner: 'test_user',
      comment: 'Temperature sensor readings'
    }
  }
  
  // Test statistics calculation directly
  var statsResult = pbTable.statsCalculator.calculateAllStats(testTable)
  console.log('Statistics calculated for', statsResult.header.length, 'fields')
  
  // Check statistics for numeric fields
  statsResult.header.forEach(function (field) {
    console.log('\nField:', field.name, '(type:', field.type + ')')
    if (field.stats) {
      console.log('  Start:', field.stats.start)
      console.log('  End:', field.stats.end)
      console.log('  Min:', field.stats.min)
      console.log('  Max:', field.stats.max)
      console.log('  Mean:', field.stats.mean.toFixed(2))
    } else {
      console.log('  No statistics (non-numeric field)')
    }
  })
  
  // Test encoding with automatic statistics
  pbTable.encodeTable(testTable, function (err, encoded) {
    if (err) {
      console.error('Encoding error:', err)
      return
    }
    
    console.log('\nEncoded table to', encoded.length, 'bytes')
    
    // Test decoding to verify statistics are preserved
    pbTable.decodeTable(encoded, function (err, decoded) {
      if (err) {
        console.error('Decoding error:', err)
        return
      }
      
      console.log('Decoded table with', decoded.data.length, 'rows')
      console.log('Row count in meta:', decoded.meta.row_count)
      
      // Verify specific statistics
      var tempField = decoded.header.find(function (f) { return f.name === 'temperature' })
      if (tempField && tempField.stats) {
        var expectedMean = (20.5 + 25.0 + 18.2 + 30.1 + 22.8) / 5
        console.log('\nTemperature statistics verification:')
        console.log('Expected mean:', expectedMean.toFixed(2))
        console.log('Actual mean:', tempField.stats.mean.toFixed(2))
        console.log('Statistics match:', Math.abs(tempField.stats.mean - expectedMean) < 0.01)
      }
      
      // Test verbose format
      console.log('\nTesting verbose format...')
      var verboseTable = {
        header: decoded.header, // Use the header with statistics from the decoded table
        meta: testTable.meta,
        data: [
          { id: 1, name: 'sensor1', temperature: 20.5, count: 100 },
          { id: 2, name: 'sensor2', temperature: 25.0, count: 150 },
          { id: 3, name: 'sensor3', temperature: 18.2, count: 75 }
        ]
      }
      
      pbTable.encodeVerbose(verboseTable, function (err, encodedVerbose) {
        if (err) {
          console.error('Verbose encoding error:', err)
          return
        }
        
        console.log('Verbose format encoded to', encodedVerbose.length, 'bytes')
        
        pbTable.decodeVerbose(encodedVerbose, function (err, decodedVerbose) {
          if (err) {
            console.error('Verbose decoding error:', err)
            return
          }
          
          console.log('Verbose format has', decodedVerbose.data.length, 'rows')
          
          // Check that verbose format also has statistics
          var tempFieldVerbose = decodedVerbose.header.find(function (f) { return f.name === 'temperature' })
          if (tempFieldVerbose && tempFieldVerbose.stats) {
            console.log('✓ Statistics preserved in verbose format')
          } else {
            console.log('✗ Statistics missing in verbose format')
          }
          
          console.log('\n✓ JavaScript statistics functionality test completed successfully!')
        })
      })
    })
  })
}

// Run the test
testStatsCalculation()
