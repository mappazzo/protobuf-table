'use strict';

// "THE BEER-WARE LICENSE" (Revision 42):
// Mappazzo (info@mappazzo.com) wrote this file. As long as you retain this notice you
// can do whatever you want with this stuff. If we meet some day, and you think
// this stuff is worth it, you can buy me a beer in return. Cheers, Kelly Norris

// Protocol buffer implimentation for variable format structured tables

//* global pbuf */
var pbuf = require('protobufjs');

var Root = pbuf.Root;
var Reader = pbuf.Reader;
var Writer = pbuf.Writer;

var types = {
  'string': 'string',
  'uint': 'int32',
  'int': 'sint32',
  'float': 'float'

  // Header protocol
};var headProto = {
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
          filename: { id: 1, rule: 'optional', type: 'string' },
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

  // Protocol buffer interface
};var protocolFromHeader = function protocolFromHeader(obj, cb) {
  var dataJSON = {
    // nested: {
    DataArray: {
      nested: {
        Row: {
          fields: {}
        },
        Data: {
          fields: {
            data: {
              id: 3,
              rule: 'repeated',
              type: 'Row'
            }
          }
        }
      }
      // }
    } };
  var fields = {};
  obj.header.forEach(function (field, index) {
    var type = types[field.type];
    fields[field.name] = {
      id: index + 1,
      type: type,
      rule: field.rule || 'optional'
    };
  });
  dataJSON.DataArray.nested.Row.fields = fields;
  var root = new Root();
  root.addJSON(dataJSON);
  cb(null, root);
};
var decodeData = function decodeData(protocol, reader, cb) {
  var dataProtocol = protocol.lookupType('DataArray.Data');
  var data = dataProtocol.decode(reader);
  cb(null, data);
};
var encodeData = function encodeData(protocol, obj, writer, cb) {
  var dataProtocol = protocol.lookupType('DataArray.Data');
  var verifyError = dataProtocol.verify(obj);
  if (verifyError) {
    console.log('error encoding: ', obj);
    var vErr = new Error(verifyError);
    cb(vErr);
  } else {
    if (!writer) writer = new Writer();
    dataProtocol.encode(obj, writer);
    cb(null, writer);
  }
};
var decodeHeader = function decodeHeader(reader, cb) {
  var root = new Root();
  root.addJSON(headProto);
  var headMsg = root.lookupType('TableHeader.Header');
  var head = headMsg.decodeDelimited(reader);
  cb(null, head);
};
var encodeHeader = function encodeHeader(obj, writer, cb) {
  var root = new Root();
  root.addJSON(headProto);
  var headMsg = root.lookupType('TableHeader.Header');
  var verifyError = headMsg.verify(obj);
  if (verifyError) {
    var vErr = new Error(verifyError);
    cb(vErr);
  } else {
    if (!writer) writer = new Writer();
    headMsg.encodeDelimited(obj, writer);
    cb(null, writer);
  }
};
var indexData = function indexData(reader, cb) {
  var index = [];
  var bInd = reader.pos;
  while (bInd < reader.len) {
    var t = reader.uint32();
    var type = t & 7;
    var tag = t >>> 3;
    if (type === 2 || tag === 3) {
      // all data entries are type 2 'embeded message' and tag 3 'fixed by protocol'
      index.push(bInd);
      var len = reader.uint32();
      bInd = reader.pos + len;
      if (bInd < reader.len) reader.skip(len);
    } else {
      var err = new Error('getIndex() Unexpected message type');
      return cb(err);
    }
  }
  cb(null, index);
};
var decodeRow = function decodeRow(protocol, reader, request, cb) {
  var bInd = reader.pos;
  var ind = 0;
  var err = null;
  var data;
  if (Array.isArray(request)) data = [];
  while (bInd < reader.len) {
    var t = reader.uint32();
    var type = t & 7;
    var tag = t >>> 3;
    if (type === 2 || tag === 3) {
      // all data entries are type 2 'embeded message' and tag 3 'fixed by protocol'
      if (Array.isArray(request)) {
        var found = false;
        request.forEach(function (val, ri) {
          if (ind === val) {
            found = true;
            var rowBytes = reader.bytes();
            var rowProtocol = protocol.lookupType('DataArray.Row');
            data[ri] = rowProtocol.decode(rowBytes);
            bInd = reader.pos;
          }
        });
      } else if (ind === request) {
        var rowBytes = reader.bytes();
        var rowProtocol = protocol.lookupType('DataArray.Row');
        data = rowProtocol.decode(rowBytes);
        return cb(null, data);
      }
      if (!found) {
        var len = reader.uint32();
        bInd = reader.pos + len;
        if (bInd < reader.len) reader.skip(len);
      }
      ind++;
    } else {
      err = new Error('getRow() Unexpected message type');
      return cb(err);
    }
  }
  if (!data) {
    err = new Error('getRow() buffer only contains ' + ind + ' rows');
    return cb(err);
  } else {
    cb(null, data);
  }
};

// Transform data
var transformInteger = {
  parse: function parse(value, lastval, transform) {
    if (!value) value = 0;
    if (!transform.offset) transform.offset = 0;
    if (!transform.multip) transform.multip = 1;
    if (!transform.decimals) transform.decimals = 0;
    if (transform.sequence && lastval) {
      value -= lastval;
    } else {
      value -= transform.offset;
    }
    var storedValue = value * transform.multip;
    storedValue = storedValue * Math.pow(10, transform.decimals);
    return parseInt(storedValue);
  },
  recover: function recover(storedValue, lastval, transform) {
    if (!storedValue) storedValue = 0;
    if (!transform.offset) transform.offset = 0;
    if (!transform.multip) transform.multip = 1;
    if (!transform.decimals) transform.decimals = 0;
    var value = storedValue * Math.pow(10, -transform.decimals);
    value = value / transform.multip;
    if (transform.sequence && lastval) {
      value += lastval;
    } else {
      value += transform.offset;
    }
    return value;
  }

  // Verbose data format
};var encodeVerbose = function encodeVerbose(obj, cb) {
  if (!obj.header || !obj.data) {
    var err = new Error('object is not a valid format');
    return cb(err);
  }
  encodeHeader(obj, null, function (err, writer) {
    if (err) return cb(err);
    protocolFromHeader(obj, function (err, protocol) {
      if (err) return cb(err);
      var enc = JSON.parse(JSON.stringify(obj));
      obj.header.forEach(function (head, col) {
        if (head.transform && (head.type === 'int' || head.type === 'uint')) {
          enc.data.forEach(function (dataObj, row) {
            var rawValue = dataObj[head.name];
            var lastVal = null;
            if (row >= 1) lastVal = obj.data[row - 1][head.name];
            var storeVal = transformInteger.parse(rawValue, lastVal, head.transform);
            enc.data[row][head.name] = storeVal;
          });
        }
      });
      // console.log('encodeVerbose obj', enc)
      encodeData(protocol, enc, writer, function (err, writer) {
        if (err) return cb(err);
        var encoded = writer.finish();
        cb(null, encoded);
      });
    });
  });
};
var decodeVerbose = function decodeVerbose(buff, cb) {
  var reader = new Reader(buff);
  decodeHeader(reader, function (err, headObj) {
    if (err) return cb(err);
    protocolFromHeader(headObj, function (err, protocol) {
      if (err) return cb(err);
      decodeData(protocol, reader, function (err, dataObj) {
        if (err) return cb(err);
        var result = JSON.parse(JSON.stringify(headObj));
        result.data = [];
        dataObj.data.forEach(function (obj, row) {
          result.data[row] = {};
          headObj.header.forEach(function (head, col) {
            var value = obj[head.name];
            if (head.transform && (head.type === 'int' || head.type === 'uint')) {
              var lastVal = null;
              if (row >= 1) lastVal = result.data[row - 1][head.name];
              value = transformInteger.recover(value, lastVal, head.transform);
            }
            result.data[row][head.name] = value;
          });
        });
        cb(null, JSON.parse(JSON.stringify(result)));
      });
    });
  });
};
var getVerbose = function getVerbose(buff, request, cb) {
  var reader = new Reader(buff);
  decodeHeader(reader, function (err, headObj) {
    if (err) return cb(err);
    protocolFromHeader(headObj, function (err, protocol) {
      if (err) return cb(err);
      decodeRow(protocol, reader, request, function (err, dataObj) {
        if (err) return cb(err);
        var result;
        if (Array.isArray(dataObj)) {
          result = [];
          dataObj.forEach(function (obj, row) {
            result[row] = {};
            headObj.header.forEach(function (head, col) {
              if (obj[head.name]) {
                var value = obj[head.name];
                if (head.transform && (head.type === 'int' || head.type === 'uint')) {
                  var lastVal = null;
                  if (head.transform.sequence) {
                    err = new Error('getVerbose(): cannot extract specific entries from sequenced data');
                    return cb(err);
                  }
                  value = transformInteger.recover(value, lastVal, head.transform);
                }
                result[row][head.name] = value;
              }
            });
          });
        } else {
          result = {};
          headObj.header.forEach(function (head, col) {
            if (dataObj[head.name]) {
              var value = dataObj[head.name];
              if (head.transform && (head.type === 'int' || head.type === 'uint')) {
                var lastVal = null;
                if (head.transform.sequence) {
                  err = new Error('getVerbose(): cannot extract specific entries from sequenced data');
                  return cb(err);
                }
                value = transformInteger.recover(value, lastVal, head.transform);
              }
              result[head.name] = value;
            }
          });
        }
        return cb(null, result);
      });
    });
  });
};
var addVerbose = function addVerbose(buff, data, cb) {
  decodeHeader(buff, function (err, headObj) {
    if (err) return cb(err);
    protocolFromHeader(headObj, function (err, protocol) {
      if (err) return cb(err);
      encodeData(protocol, { data: data }, null, function (err, writer) {
        if (err) return cb(err);
        var addBuff = writer.finish();
        var totalLength = buff.length + addBuff.length;
        var newBuffer = new Uint8Array(totalLength);
        newBuffer.set(buff, 0);
        newBuffer.set(addBuff, buff.length);
        cb(null, newBuffer);
      });
    });
  });
};

// Array data format
var encodeTable = function encodeTable(obj, cb) {
  var err;
  if (!obj.header || !obj.data) {
    err = new Error('object is not a valid format');
    return cb(err);
  }
  if (!Array.isArray(obj.data)) {
    err = new Error('object is not an array');
    return cb(err);
  }
  encodeHeader(obj, null, function (err, writer) {
    if (err) return cb(err);
    protocolFromHeader(obj, function (err, protocol) {
      if (err) return cb(err);
      obj.data.forEach(function (data, row) {
        var dataObj = { data: [{}] };
        obj.header.forEach(function (head, col) {
          var storeVal = data[col];
          if (head.transform && (head.type === 'int' || head.type === 'uint')) {
            var lastVal = null;
            if (row >= 1) lastVal = obj.data[row - 1][col];
            storeVal = transformInteger.parse(storeVal, lastVal, head.transform);
          }
          dataObj.data[0][head.name] = storeVal;
        });
        encodeData(protocol, dataObj, writer, function (err, writer) {
          if (err) return cb(err);
        });
      });
      var encoded = writer.finish();
      cb(null, encoded);
    });
  });
};
var decodeTable = function decodeTable(buff, cb) {
  var reader = new Reader(buff);
  decodeHeader(reader, function (err, headObj) {
    if (err) return cb(err);
    protocolFromHeader(headObj, function (err, protocol) {
      if (err) return cb(err);
      decodeData(protocol, reader, function (err, dataObj) {
        if (err) return cb(err);
        var result = JSON.parse(JSON.stringify(headObj));
        result.data = [];
        dataObj.data.forEach(function (obj, row) {
          result.data[row] = [];
          headObj.header.forEach(function (head, col) {
            var value = obj[head.name];
            if (head.transform && (head.type === 'int' || head.type === 'uint')) {
              if (!value) value = 0;
              var lastVal = null;
              if (row >= 1) lastVal = result.data[row - 1][col];
              value = transformInteger.recover(value, lastVal, head.transform);
            }
            result.data[row][col] = value;
          });
        });
        cb(null, result);
      });
    });
  });
};
var getTable = function getTable(buff, request, cb) {
  var reader = new Reader(buff);
  decodeHeader(reader, function (err, headObj) {
    if (err) return cb(err);
    protocolFromHeader(headObj, function (err, protocol) {
      if (err) return cb(err);
      decodeRow(protocol, reader, request, function (err, dataObj) {
        if (err) return cb(err);
        var result = [];
        if (Array.isArray(dataObj)) {
          dataObj.forEach(function (obj, row) {
            result[row] = [];
            headObj.header.forEach(function (head, col) {
              if (obj[head.name]) {
                var value = obj[head.name];
                if (head.transform && (head.type === 'int' || head.type === 'uint')) {
                  var lastVal = null;
                  if (head.transform.sequence) {
                    err = new Error('getTable(): cannot extract specific entries from sequenced data');
                    return cb(err);
                  }
                  value = transformInteger.recover(value, lastVal, head.transform);
                }
                result[row][col] = value;
              }
            });
          });
        } else {
          headObj.header.forEach(function (head, col) {
            if (dataObj[head.name]) {
              var value = dataObj[head.name];
              if (head.transform && (head.type === 'int' || head.type === 'uint')) {
                var lastVal = null;
                if (head.transform.sequence) {
                  err = new Error('getTable(): cannot extract specific entries from sequenced data');
                  return cb(err);
                }
                value = transformInteger.recover(value, lastVal, head.transform);
              }
              result[col] = value;
            }
          });
        }
        return cb(null, result);
      });
    });
  });
};
var addTable = function addTable(buff, data, cb) {
  decodeHeader(buff, function (err, headObj) {
    if (err) return cb(err);
    protocolFromHeader(headObj, function (err, protocol) {
      if (err) return cb(err);
      var writer = new Writer();
      data.forEach(function (rowData, row) {
        var dataObj = [{}];
        rowData.forEach(function (value, ind, obj) {
          dataObj[0][headObj.header[ind].name] = value;
        });
        encodeData(protocol, dataObj, writer, function (err, writer) {
          if (err) return cb(err);
        });
      });
      var addBuff = writer.finish();
      var totalLength = buff.length + addBuff.length;
      var newBuffer = new Uint8Array(totalLength);
      newBuffer.set(buff, 0);
      newBuffer.set(addBuff, buff.length);
      cb(null, newBuffer);
    });
  });
};

// Indexing and lookup
var getIndex = function getIndex(buff, cb) {
  var reader = new Reader(buff);
  var headLen = reader.uint32();
  var err = null;
  if (reader.pos + headLen < reader.len) {
    reader.skip(headLen);
    indexData(reader, function (err, index) {
      if (err) return err;
      return cb(null, index);
    });
  } else {
    err = new Error('getIndex(): invalid buffer');
    return cb(err);
  }
};

module.exports = {
  encodeVerbose: encodeVerbose,
  decodeVerbose: decodeVerbose,
  getVerbose: getVerbose,
  addVerbose: addVerbose,
  encodeTable: encodeTable,
  decodeTable: decodeTable,
  getTable: getTable,
  addTable: addTable,
  encode: encodeTable,
  decode: decodeTable,
  get: getTable,
  add: addTable,
  getIndex: getIndex
};
