var pbTable = require('../src/pbTable.js')
var smlTable = require('./smallTable.js')
console.log('.')
console.log('BASIC TEST')
console.log('.')

pbTable.encodeTable(smlTable, function (err, pbuff) {
  if (err) return console.log(err)
  console.log('pbuff length', pbuff.length)
  console.log('encodeTable... success')
  pbTable.decodeVerbose(pbuff, function (err, obj) {
    if (err) return console.log(err)
    console.log('decodeVerbose... success')
    // console.log('smallTableVerbose', obj)
    pbTable.encodeVerbose(obj, function (err, pbuff) {
      if (err) return console.log(err)
      console.log('encodeVerbose, success')
      // console.log('pbuff length', pbuff.length)
    })
  })
  pbTable.decodeTable(pbuff, function (err, obj) {
    if (err) return console.log(err)
    console.log('decodeTable... success')
    // console.log('smallTable', obj)
  })
  pbTable.getVerbose(pbuff, 1, function (err, data) {
    if (err) return console.log(err)
    console.log('getVerbose... success')
    console.log('row 1', data)
  })
  pbTable.getTable(pbuff, [1, 4], function (err, data) {
    if (err) return console.log(err)
    console.log('getTable... success')
    console.log('row 1, 4: ', data)
  })
  pbTable.getIndex(pbuff, function (err, index) {
    if (err) return console.log(err)
    console.log('getIndex... success')
    console.log('index', JSON.stringify(index))
  })
})

console.log('.')
