// Mappazzo (c) 2017
// protocol buffer implimentation for variable format structured tables

import pbuf from 'protobufjs'
import _ from 'lodash'

var Root = pbuf.Root
var Reader = pbuf.Reader
var Writer = pbuf.Writer

var types = {
  'string': 'string',
  'uint': 'int32',
  'int': 'sint32',
  'float': 'float'
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
  pbuf.load('static/pbTableHeader.proto', function (err, root) {
    if (err) return cb(err)
    var headMsg = root.lookupType('pbTableHeader.tableHead')
    var head = headMsg.decodeDelimited(reader)
    cb(null, head)
  })
}
var encodeHeader = function (obj, writer, cb) {
  pbuf.load('static/pbTableHeader.proto', function (err, root) {
    if (err) return cb(err)
    var headMsg = root.lookupType('pbTableHeader.tableHead')
    var verifyError = headMsg.verify(obj)
    if (verifyError) {
      var vErr = new Error(verifyError)
      cb(vErr)
    } else {
      if (!writer) writer = new Writer()
      headMsg.encodeDelimited(obj, writer)
      cb(null, writer)
    }
  })
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
      var count = 0
      obj.data.forEach(function (data, row) {
        var dataObj = { data: [{}] }
        obj.header.forEach(function (header, col) {
          dataObj.data[0][header.name] = data[col]
        })
        encodeData(protocol, dataObj, writer, function (err, writer) {
          if (err) return cb(err)
          count++
        })
      })
      console.log('encoded rows: ', count)
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
        var headInfo = {}
        headObj.header.forEach(function (head, ind) {
          headInfo[head.name] = {}
          headInfo[head.name].ind = ind
          headInfo[head.name].transform = head.transform
        })
        dataObj.data.forEach(function (obj, row) {
          result.data[row] = []
          _.forEach(obj, function (value, key, obj) {
            var col = headInfo[key].ind
            result.data[row][col] = value
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

export default {
  encodeVerbose,
  decodeVerbose,
  addVerbose,
  encodeTable,
  decodeTable,
  addTable,
  types
}
