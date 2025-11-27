// protobuf-table
// implementation of googles protocol buffer for variable format structured tables
// Updated version using compiled JSON schema for browser and Node.js compatibility

// "THE BEER-WARE LICENSE" (Revision 42):
// Mappazzo (info@mappazzo.com) wrote this file. As long as you retain this notice you
// can do whatever you want with this stuff. If we meet some day, and you think
// this stuff is worth it, you can buy me a beer in return. Cheers, Kelly Norris

var pbuf = require('protobufjs')
var headJson = require('./head.json')

var types = {
  'string': 'string',
  'uint': 'int32',
  'int': 'sint32',
  'float': 'float',
  'bool': 'bool'
}

// Load the compiled JSON schema (works in both Node.js and browser)
var headerRoot = pbuf.Root.fromJSON(headJson)

// Statistics calculator
var statsCalculator = {
  calculateFieldStats: function (data, fieldIndex, fieldType) {
    if (fieldType !== 'int' && fieldType !== 'uint' && fieldType !== 'float') {
      return null
    }
    
    var values = []
    for (var i = 0; i < data.length; i++) {
      var row = data[i]
      if (fieldIndex < row.length && row[fieldIndex] != null) {
        var val = parseFloat(row[fieldIndex])
        if (!isNaN(val)) {
          values.push(val)
        }
      }
    }
    
    if (values.length === 0) {
      return null
    }
    
    var sum = values.reduce(function (a, b) { return a + b }, 0)
    var min = Math.min.apply(Math, values)
    var max = Math.max.apply(Math, values)
    
    return {
      start: values[0],
      end: values[values.length - 1],
      min: min,
      max: max,
      mean: sum / values.length
    }
  },
  
  calculateAllStats: function (obj) {
    var result = JSON.parse(JSON.stringify(obj))
    
    // Calculate field statistics
    for (var i = 0; i < result.header.length; i++) {
      var fieldDef = result.header[i]
      var stats = this.calculateFieldStats(obj.data, i, fieldDef.type)
      if (stats) {
        fieldDef.stats = stats
      }
    }
    
    // Update meta with row count
    if (!result.meta) {
      result.meta = {}
    }
    result.meta.row_count = obj.data.length
    
    return result
  }
}

// Protocol buffer interface using loaded schema
function protocolFromHeader(obj, cb) {
  var dataJSON = {
    DataArray: {
      nested: {
        Row: {
          fields: {}
        },
        Data: {
          fields: {
            data: { id: 1, rule: 'repeated', type: 'Row' }
          }
        }
      }
    }
  }
  var fields = {}
  var err = null
  obj.header.forEach(function (field, index) {
    var type = types[field.type]
    if (typeof type === 'undefined') err = new Error('Invalid type: ' + field.type)
    fields[field.name] = {
      id: index + 1,
      type: type,
      rule: field.rule || 'optional'
    }
  })
  if (err) {
    cb(err)
  } else {
    dataJSON.DataArray.nested.Row.fields = fields
    var root = new pbuf.Root()
    root.addJSON(dataJSON)
    cb(null, root)
  }
}

var decodeData = function (protocol, reader, cb) {
  var dataProtocol = protocol.lookupType('DataArray.Data')
  var data = dataProtocol.decode(reader)
  cb(null, data)
}

var encodeData = function (protocol, obj, writer, cb) {
  var dataProtocol = protocol.lookupType('DataArray.Data')
  var verifyError = dataProtocol.verify(obj)
  if (verifyError) {
    var vErr = new Error(verifyError)
    console.log(vErr.message)
    cb(vErr)
  } else {
    if (!writer) writer = new pbuf.Writer()
    dataProtocol.encode(obj, writer)
    cb(null, writer)
  }
}

var decodeHeader = function (reader, cb) {
  var headMsg = headerRoot.lookupType('pbTableHeader.tableHead')
  var head = headMsg.decodeDelimited(reader)
  
  // Convert protobuf field names to match expected format
  if (head.meta && head.meta.rowCount !== undefined) {
    head.meta.row_count = head.meta.rowCount
    delete head.meta.rowCount
  }
  
  
  cb(null, head)
}

var encodeHeader = function (obj, writer, cb) {
  var headMsg = headerRoot.lookupType('pbTableHeader.tableHead')
  
  // Convert field names to match protobuf schema
  var objCopy = JSON.parse(JSON.stringify(obj))
  if (objCopy.meta && objCopy.meta.row_count !== undefined) {
    objCopy.meta.rowCount = objCopy.meta.row_count
    delete objCopy.meta.row_count
  }
  
  var verifyError = headMsg.verify(objCopy)
  if (verifyError) {
    var vErr = new Error(verifyError)
    cb(vErr)
  } else {
    if (!writer) writer = new pbuf.Writer()
    headMsg.encodeDelimited(objCopy, writer)
    cb(null, writer)
  }
}

var indexData = function (reader, cb) {
  var index = []
  var bInd = reader.pos
  while (bInd < reader.len) {
    var t = reader.uint32()
    var type = (t & 7)
    var tag = (t >>> 3)
    if (type === 2 || tag === 1) {
      index.push(bInd)
      var len = reader.uint32()
      bInd = reader.pos + len
      if (bInd < reader.len) reader.skip(len)
    } else {
      var err = new Error('getIndex() Unexpected message type')
      return cb(err)
    }
  }
  cb(null, index)
}

var decodeRow = function (protocol, reader, request, cb) {
  var bInd = reader.pos
  var ind = 0
  var err = null
  var data
  if (Array.isArray(request)) data = []
  while (bInd < reader.len) {
    var t = reader.uint32()
    var type = (t & 7)
    var tag = (t >>> 3)
    if (type === 2 || tag === 1) {
      if (Array.isArray(request)) {
        var found = false
        request.forEach(function (val, ri) {
          if (ind === val) {
            found = true
            var rowBytes = reader.bytes()
            var rowProtocol = protocol.lookupType('DataArray.Row')
            data[ri] = rowProtocol.decode(rowBytes)
            bInd = reader.pos
          }
        })
      } else if (ind === request) {
        var rowBytes = reader.bytes()
        var rowProtocol = protocol.lookupType('DataArray.Row')
        data = rowProtocol.decode(rowBytes)
        return cb(null, data)
      }
      if (!found) {
        var len = reader.uint32()
        bInd = reader.pos + len
        if (bInd < reader.len) reader.skip(len)
      }
      ind++
    } else {
      err = new Error('getRow() Unexpected message type')
      return cb(err)
    }
  }
  if (!data) {
    err = new Error('getRow() buffer only contains ' + ind + ' rows')
    return cb(err)
  } else {
    cb(null, data)
  }
}

// Transform data (unchanged - matches Python exactly)
var transformInteger = {
  parse: function (value, lastval, transform) {
    if (!value) value = 0
    if (!transform.offset) transform.offset = 0
    if (!transform.multip) transform.multip = 1
    if (!transform.decimals) transform.decimals = 0
    if (transform.sequence && lastval) {
      value -= lastval
    } else {
      value -= transform.offset
    }
    var storedValue = value * transform.multip
    storedValue = storedValue * Math.pow(10, transform.decimals)
    return parseInt(storedValue)
  },
  recover: function (storedValue, lastval, transform) {
    if (!storedValue) storedValue = 0
    if (!transform.offset) transform.offset = 0
    if (!transform.multip) transform.multip = 1
    if (!transform.decimals) transform.decimals = 0
    var value = storedValue * Math.pow(10, -transform.decimals)
    value = value / transform.multip
    if (transform.sequence && lastval) {
      value += lastval
    } else {
      value += transform.offset
    }
    return value
  }
}

// Verbose data format (with automatic statistics calculation)
var encodeVerbose = function (obj, cb) {
  if (!obj.header || !obj.data) {
    var err = new Error('object is not a valid format')
    return cb(err)
  }
  
  // Calculate statistics automatically
  var objWithStats = statsCalculator.calculateAllStats(obj)
  
  encodeHeader(objWithStats, null, function (err, writer) {
    if (err) return cb(err)
    protocolFromHeader(objWithStats, function (err, protocol) {
      if (err) return cb(err)
      var enc = JSON.parse(JSON.stringify(objWithStats))
      objWithStats.header.forEach(function (head, col) {
        if (head.type === 'int' || head.type === 'uint') {
          if (head.transform) {
            enc.data.forEach(function (dataObj, row) {
              var rawValue = dataObj[head.name]
              var lastVal = null
              if (row >= 1) lastVal = obj.data[row - 1][head.name]
              var storeVal = transformInteger.parse(rawValue, lastVal, head.transform)
              enc.data[row][head.name] = storeVal
            })
          } else {
            enc.data.forEach(function (dataObj, row) {
              enc.data[row][head.name] = parseInt(dataObj[head.name])
            })
          }
        } else if (head.type === 'string') {
          enc.data.forEach(function (dataObj, row) {
            enc.data[row][head.name] = String(dataObj[head.name])
          })
        } else if (head.type === 'bool') {
          enc.data.forEach(function (dataObj, row) {
            enc.data[row][head.name] = Boolean(dataObj[head.name])
          })
        }
      })
      encodeData(protocol, enc, writer, function (err, writer) {
        if (err) return cb(err)
        var encoded = writer.finish()
        cb(null, encoded)
      })
    })
  })
}

var decodeVerbose = function (buff, cb) {
  var reader = new pbuf.Reader(buff)
  decodeHeader(reader, function (err, headObj) {
    if (err) return cb(err)
    protocolFromHeader(headObj, function (err, protocol) {
      if (err) return cb(err)
      decodeData(protocol, reader, function (err, dataObj) {
        if (err) return cb(err)
        var result = JSON.parse(JSON.stringify(headObj))
        result.data = []
        dataObj.data.forEach(function (obj, row) {
          result.data[row] = {}
          headObj.header.forEach(function (head, col) {
            var value = obj[head.name]
            if (head.transform &&
               (head.type === 'int' || head.type === 'uint')) {
              var lastVal = null
              if (row >= 1) lastVal = result.data[row - 1][head.name]
              value = transformInteger.recover(value, lastVal, head.transform)
            }
            result.data[row][head.name] = value
          })
        })
        // Ensure statistics are preserved in the result
        cb(null, result)
      })
    })
  })
}

var getVerbose = function (buff, request, cb) {
  var reader = new pbuf.Reader(buff)
  decodeHeader(reader, function (err, headObj) {
    if (err) return cb(err)
    protocolFromHeader(headObj, function (err, protocol) {
      if (err) return cb(err)
      decodeRow(protocol, reader, request, function (err, dataObj) {
        if (err) return cb(err)
        var result
        if (Array.isArray(dataObj)) {
          result = []
          dataObj.forEach(function (obj, row) {
            result[row] = {}
            headObj.header.forEach(function (head, col) {
              if (obj[head.name]) {
                var value = obj[head.name]
                if (head.transform &&
                   (head.type === 'int' || head.type === 'uint')) {
                  var lastVal = null
                  if (head.transform.sequence) {
                    err = new Error('getVerbose(): cannot extract specific entries from sequenced data')
                    return cb(err)
                  }
                  value = transformInteger.recover(value, lastVal, head.transform)
                }
                result[row][head.name] = value
              }
            })
          })
        } else {
          result = {}
          headObj.header.forEach(function (head, col) {
            if (dataObj[head.name]) {
              var value = dataObj[head.name]
              if (head.transform &&
                 (head.type === 'int' || head.type === 'uint')) {
                var lastVal = null
                if (head.transform.sequence) {
                  err = new Error('getVerbose(): cannot extract specific entries from sequenced data')
                  return cb(err)
                }
                value = transformInteger.recover(value, lastVal, head.transform)
              }
              result[head.name] = value
            }
          })
        }
        return cb(null, result)
      })
    })
  })
}

var addVerbose = function (buff, data, cb) {
  decodeHeader(buff, function (err, headObj) {
    if (err) return cb(err)
    protocolFromHeader(headObj, function (err, protocol) {
      if (err) return cb(err)
      encodeData(protocol, { data: data }, null, function (err, writer) {
        if (err) return cb(err)
        var addBuff = writer.finish()
        var totalLength = buff.length + addBuff.length
        var newBuffer = new Uint8Array(totalLength)
        newBuffer.set(buff, 0)
        newBuffer.set(addBuff, buff.length)
        cb(null, newBuffer)
      })
    })
  })
}

// Array data format (with automatic statistics calculation)
var encodeTable = function (obj, cb) {
  var err
  if (!obj.header || !obj.data) {
    err = new Error('object is not a valid format')
    return cb(err)
  }
  if (!Array.isArray(obj.data)) {
    err = new Error('object is not an array')
    return cb(err)
  }
  
  // Calculate statistics automatically
  var objWithStats = statsCalculator.calculateAllStats(obj)
  
  encodeHeader(objWithStats, null, function (err, writer) {
    if (err) return cb(err)
    protocolFromHeader(objWithStats, function (err, protocol) {
      if (err) return cb(err)
      var error = null
      obj.data.forEach(function (data, row) {
        var dataObj = { data: [{}] }
        obj.header.forEach(function (head, col) {
          var storeVal = data[col]
          if (head.type === 'int' || head.type === 'uint') {
            if (head.transform) {
              var lastVal = null
              if (row >= 1) lastVal = obj.data[row - 1][col]
              storeVal = transformInteger.parse(storeVal, lastVal, head.transform)
            } else {
              storeVal = parseInt(storeVal)
            }
          } else if (head.type === 'string') {
            storeVal = String(storeVal)
          } else if (head.type === 'bool') {
            storeVal = Boolean(storeVal)
          }
          dataObj.data[0][head.name] = storeVal
        })
        encodeData(protocol, dataObj, writer, function (err, writer) {
          if (err) error = err
        })
      })
      var encoded = writer.finish()
      cb(error, encoded)
    })
  })
}

var decodeTable = function (buff, cb) {
  var reader = new pbuf.Reader(buff)
  decodeHeader(reader, function (err, headObj) {
    if (err) return cb(err)
    protocolFromHeader(headObj, function (err, protocol) {
      if (err) return cb(err)
      decodeData(protocol, reader, function (err, dataObj) {
        if (err) return cb(err)
        var result = JSON.parse(JSON.stringify(headObj))
        result.data = []
        dataObj.data.forEach(function (obj, row) {
          result.data[row] = []
          headObj.header.forEach(function (head, col) {
            var value = obj[head.name]
            if (head.transform &&
               (head.type === 'int' || head.type === 'uint')) {
              if (!value) value = 0
              var lastVal = null
              if (row >= 1) lastVal = result.data[row - 1][col]
              value = transformInteger.recover(value, lastVal, head.transform)
            }
            result.data[row][col] = value
          })
        })
        cb(null, result)
      })
    })
  })
}

var getTable = function (buff, request, cb) {
  var reader = new pbuf.Reader(buff)
  decodeHeader(reader, function (err, headObj) {
    if (err) return cb(err)
    protocolFromHeader(headObj, function (err, protocol) {
      if (err) return cb(err)
      decodeRow(protocol, reader, request, function (err, dataObj) {
        if (err) return cb(err)
        var result = []
        if (Array.isArray(dataObj)) {
          dataObj.forEach(function (obj, row) {
            result[row] = []
            headObj.header.forEach(function (head, col) {
              if (obj[head.name]) {
                var value = obj[head.name]
                if (head.transform &&
                   (head.type === 'int' || head.type === 'uint')) {
                  var lastVal = null
                  if (head.transform.sequence) {
                    err = new Error('getTable(): cannot extract specific entries from sequenced data')
                    return cb(err)
                  }
                  value = transformInteger.recover(value, lastVal, head.transform)
                }
                result[row][col] = value
              }
            })
          })
        } else {
          headObj.header.forEach(function (head, col) {
            if (dataObj[head.name]) {
              var value = dataObj[head.name]
              if (head.transform &&
                 (head.type === 'int' || head.type === 'uint')) {
                var lastVal = null
                if (head.transform.sequence) {
                  err = new Error('getTable(): cannot extract specific entries from sequenced data')
                  return cb(err)
                }
                value = transformInteger.recover(value, lastVal, head.transform)
              }
              result[col] = value
            }
          })
        }
        return cb(null, result)
      })
    })
  })
}

var addTable = function (buff, data, cb) {
  decodeHeader(buff, function (err, headObj) {
    if (err) return cb(err)
    protocolFromHeader(headObj, function (err, protocol) {
      if (err) return cb(err)
      var writer = new pbuf.Writer()
      data.forEach(function (rowData, row) {
        var dataObj = { data: [{}] }
        rowData.forEach(function (value, ind, obj) {
          dataObj.data[0][headObj.header[ind].name] = value
        })
        encodeData(protocol, dataObj, writer, function (err, writer) {
          if (err) return cb(err)
        })
      })
      var addBuff = writer.finish()
      var totalLength = buff.length + addBuff.length
      var newBuffer = new Uint8Array(totalLength)
      newBuffer.set(buff, 0)
      newBuffer.set(addBuff, buff.length)
      cb(null, newBuffer)
    })
  })
}

// Indexing and lookup
var getIndex = function (buff, cb) {
  var reader = new pbuf.Reader(buff)
  var headLen = reader.uint32()
  var err = null
  if (reader.pos + headLen < reader.len) {
    reader.skip(headLen)
    indexData(reader, function (err, index) {
      if (err) return err
      return cb(null, index)
    })
  } else {
    err = new Error('getIndex(): invalid buffer')
    return cb(err)
  }
}

module.exports = {
  encodeVerbose,
  decodeVerbose,
  getVerbose,
  addVerbose,
  encodeTable,
  decodeTable,
  getTable,
  addTable,
  encode: encodeTable,
  decode: decodeTable,
  get: getTable,
  add: addTable,
  getIndex,
  statsCalculator  // Export for testing
}
