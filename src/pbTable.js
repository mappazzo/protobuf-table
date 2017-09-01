// Mappazzo (c) 2017
// protocol buffer implimentation for variable format structured tables

//* global pbuf */
var pbuf = require('protobufjs')
var Root = pbuf.Root
var Reader = pbuf.Reader
var Writer = pbuf.Writer

var types = {
  'string': 'string',
  'uint': 'int32',
  'int': 'sint32',
  'float': 'float'
}

// Header protocol
var headProto = {
  TableHeader: {
    nested: {
      Transform: {
        fields: {
          offset: { id: 1, rule: 'optional', type: 'int32' },
          multip: { id: 2, rule: 'optional', type: 'int32' },
          decimals: { id: 3, rule: 'optional', type: 'int32' },
          sequence: { id: 4, rule: 'optional', type: 'bool' }
        }
      },
      Field: {
        fields: {
          name: { id: 1, rule: 'required', type: 'string' },
          type: { id: 2, rule: 'required', type: 'string' },
          transform: { id: 3, rule: 'optional', type: 'Transform' }
        }
      },
      Meta: {
        fields: {
          name: { id: 1, rule: 'optional', type: 'string' },
          owner: { id: 2, rule: 'optional', type: 'string' },
          link: { id: 3, rule: 'optional', type: 'string' },
          comment: { id: 4, rule: 'optional', type: 'string' }
        }
      },
      Header: {
        fields: {
          header: { id: 1, rule: 'repeated', type: 'Field' },
          meta: { id: 2, rule: 'optional', type: 'Meta' }
        }
      }
    }
  }
}

// Protocol buffer interface
var protocolFromHeader = function (obj, cb) {
  var dataJSON = {
    // nested: {
    DataArray: {
      nested: {
        Row: {
          fields: {
          }
        },
        Data: {
          fields: {
            data: {
              id: 1,
              rule: 'repeated',
              type: 'Row'
            }
          }
        }
      }
    }
    // }
  }
  var fields = {}
  obj.header.forEach(function (field, index) {
    var type = types[field.type]
    fields[field.name] = {
      id: index + 1,
      type,
      rule: field.rule || 'optional'
    }
  })
  dataJSON.DataArray.nested.Row.fields = fields
  var root = new Root()
  root.addJSON(dataJSON)
  cb(null, root)
}
var decodeData = function (protocol, reader, cb) {
  var dataArray = protocol.lookupType('DataArray.Data')
  var data = dataArray.decode(reader)
  cb(null, data)
}
var encodeData = function (protocol, obj, writer, cb) {
  var dataArray = protocol.lookupType('DataArray.Data')
  var verifyError = dataArray.verify(obj)
  if (verifyError) {
    var vErr = new Error(verifyError)
    cb(vErr)
  } else {
    if (!writer) writer = new Writer()
    dataArray.encode(obj, writer)
    cb(null, writer)
  }
}
var decodeHeader = function (reader, cb) {
  var root = new Root()
  root.addJSON(headProto)
  var headMsg = root.lookupType('TableHeader.Header')
  var head = headMsg.decodeDelimited(reader)
  cb(null, head)
}
var encodeHeader = function (obj, writer, cb) {
  var root = new Root()
  root.addJSON(headProto)
  var headMsg = root.lookupType('TableHeader.Header')
  var verifyError = headMsg.verify(obj)
  if (verifyError) {
    var vErr = new Error(verifyError)
    cb(vErr)
  } else {
    if (!writer) writer = new Writer()
    headMsg.encodeDelimited(obj, writer)
    cb(null, writer)
  }
}

// Transform data
var transformInteger = {
  parse: function (value, lastval, transform) {
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

// Verbose data format
var encodeVerbose = function (obj, cb) {
  if (!obj.header || !obj.data) {
    var err = new Error('object is not a valid format')
    return cb(err)
  }
  encodeHeader(obj, null, function (err, writer) {
    if (err) return cb(err)
    protocolFromHeader(obj, function (err, protocol) {
      if (err) return cb(err)
      encodeData(protocol, obj, writer, function (err, writer) {
        if (err) return cb(err)
        var encoded = writer.finish()
        cb(null, encoded)
      })
    })
  })
}
var decodeVerbose = function (buff, cb) {
  var reader = new Reader(buff)
  decodeHeader(reader, function (err, headObj) {
    if (err) return cb(err)
    protocolFromHeader(headObj, function (err, protocol) {
      if (err) return cb(err)
      decodeData(protocol, reader, function (err, dataObj) {
        if (err) return cb(err)
        var result = {
          header: headObj.header,
          data: dataObj.data
        }
        cb(null, JSON.parse(JSON.stringify(result)))
      })
    })
  })
}
var addVerbose = function (buff, data, cb) {
  decodeHeader(buff, function (err, headObj) {
    if (err) return cb(err)
    protocolFromHeader(headObj, function (err, protocol) {
      if (err) return cb(err)
      encodeData(protocol, { data }, null, function (err, writer) {
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

// Array data format
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
  encodeHeader(obj, null, function (err, writer) {
    if (err) return cb(err)
    protocolFromHeader(obj, function (err, protocol) {
      if (err) return cb(err)
      obj.data.forEach(function (data, row) {
        var dataObj = { data: [{}] }
        obj.header.forEach(function (head, col) {
          var storeVal = data[col]
          if (head.transform &&
             (head.type === 'int' || head.type === 'uint')) {
            var lastVal = null
            if (row >= 1) lastVal = obj.data[row - 1][col]
            storeVal = transformInteger.parse(storeVal, lastVal, head.transform)
          }
          dataObj.data[0][head.name] = storeVal
        })
        encodeData(protocol, dataObj, writer, function (err, writer) {
          if (err) return cb(err)
        })
      })
      var encoded = writer.finish()
      cb(null, encoded)
    })
  })
}
var decodeTable = function (buff, cb) {
  var reader = new Reader(buff)
  decodeHeader(reader, function (err, headObj) {
    if (err) return cb(err)
    protocolFromHeader(headObj, function (err, protocol) {
      if (err) return cb(err)
      decodeData(protocol, reader, function (err, dataObj) {
        if (err) return cb(err)
        var result = {
          header: JSON.parse(JSON.stringify(headObj.header)),
          data: []
        }
        dataObj.data.forEach(function (obj, row) {
          result.data[row] = []
          headObj.header.forEach(function (head, col) {
            if (obj[head.name]) {
              var value = obj[head.name]
              if (head.transform &&
                 (head.type === 'int' || head.type === 'uint')) {
                var lastVal = null
                if (row >= 1) lastVal = result.data[row - 1][col]
                value = transformInteger.recover(value, lastVal, head.transform)
              }
              result.data[row][col] = value
            }
          })
        })
        cb(null, result)
      })
    })
  })
}
var addTable = function (buff, data, cb) {
  decodeHeader(buff, function (err, headObj) {
    if (err) return cb(err)
    protocolFromHeader(headObj, function (err, protocol) {
      if (err) return cb(err)
      var writer = new Writer()
      data.forEach(function (rowData, row) {
        var dataObj = [{}]
        rowData.forEach(function (value, ind, obj) {
          dataObj[0][headObj.header[ind].name] = value
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

module.exports = {
  encodeVerbose,
  decodeVerbose,
  addVerbose,
  encodeTable,
  decodeTable,
  addTable,
  types
}
