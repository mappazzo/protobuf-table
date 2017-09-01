
# protobuf-table
## A dynamic protobuf implementation for structured table data

Tests and documentation under development. Stay tuned

## Purpose

## License
 ----------------------------------------------------------------------------
 "THE BEER-WARE LICENSE" (Revision 42):
 [Mappazzo](mailto:info@mappazzo.com) wrote this file. As long as you retain this notice you
 can do whatever you want with this stuff. If we meet some day, and you think
 this stuff is worth it, you can buy me a beer in return. Cheers, Kelly Norris
 ----------------------------------------------------------------------------

## Usage

Structure your table data as object with an array of headers 'header' and an array of 'data'. Each 'data' entry array can be an object with keys corresponding to each name in the header or an array.
You can also include metadata information in a 'meta' object.

Example 'Table' structure (with data as an Array):

    var table = {
      'header': [
        { 'name': 'location', 'type': 'string' },
        { 'name': 'total', 'type': 'uint' },
        { 'name': 'latitude', 'type': 'float' },
        { 'name': 'longitude', 'type': 'float' },
        { 'name': 'reading', 'type': 'int' }
      ],
      'meta': {
        'filename': 'exampleTable',
        'owner': 'mappazzo',
        'link': 'www.mappazzo.com',
        'comment': 'basic table example'
      },
      'data': [
        ['east street', 34324, -42.559355, 172.60347, -889],
        ['work', 7344, -41.546799, 172.50742, 4],
        ['big tree', 9327924, -41.79346, 173.04213, 32]
      ]
    }

You can encode this data as follows:

    pbTable.encodeTable(table, function (err, buffer) {
        if(err) return console.log(err)
        console.log('success, buffer is:' + buffer.length + 'bytes')
    })

### Installation

For packaging with NPM and ES6

    npm install --save protobuf-table

    and then:

    include pbTable from 'protobuf-table'

Stand alone

    var pbTable = require('./dist/pbTable-min.js')

### Testing

    npm run test

### Build

[software by mappazzo](https://www.mappazzo.com)
