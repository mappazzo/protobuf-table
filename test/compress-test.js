var pbTable = require('../src/pbTable.js')
var compressTable = require('./compressTable.js')
console.log('.')
console.log('COMPRESS TEST')
console.log('.')

pbTable.encodeTable(compressTable, function (err, pbuff) {
  if (err) return console.log(err)
  console.log('pbuff length', pbuff.length)
  console.log('encodeTable... success')
  pbTable.decodeVerbose(pbuff, function (err, obj) {
    if (err) return console.log(err)
    console.log('decodeVerbose... success')
    // console.log('decodedVerbose', obj)
    pbTable.encodeVerbose(obj, function (err, pbuff) {
      if (err) return console.log(err)
      console.log('encodeVerbose, success')
    })
  })
  pbTable.decodeTable(pbuff, function (err, obj) {
    if (err) return console.log(err)
    console.log('decodeTable... success')
    // console.log('decodedTable', obj)
  })
})
