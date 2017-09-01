var pbTable = require('../dist/pbTable.js')
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
})

console.log('.')
