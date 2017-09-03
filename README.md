
# protobuf-table
## A dynamic protobuf implementation for structured table data

[software by mappazzo](https://www.mappazzo.com)

Basic tests and compression protocol tested and working. Detailed documentation under development... Stay tuned

## Purpose

## License

This software is 'Beerware'

"THE BEER-WARE LICENSE" (Revision 42):
[Mappazzo](mailto:info@mappazzo.com) wrote this file. As long as you retain this notice you
can do whatever you want with this stuff. If we meet some day, and you think
this stuff is worth it, you can buy me a beer in return. Cheers, Kelly Norris

## Basic Usage

Structure your table data as object with an array of headers 'header' and an array of 'data'. Each 'data' entry array can be an object with keys corresponding to each name in the header or an array.
You can also include metadata information in a 'meta' object.

Example 'Table' structure (with data as an Array):

    var table = {
      meta: {
        filename: 'exampleTable',
        owner: 'mappazzo',
        link: 'www.mappazzo.com',
        comment: 'basic table example'
      },
      header: [
        { name: 'location', type: 'string' },
        { name: 'total', type: 'uint' },
        { name: 'latitude', type: 'float' },
        { name: 'longitude', type: 'float' },
        { name: 'reading', type: 'int' }
      ],
      data: [
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

    or..  pbTable.encode((table, function (err, buffer) { } )

And decode the resulting buffer as follows:

    pbTable.decodeTable(buffer, function (err, table) {
        if(err) return console.log(err)
        console.log('success, restored data:', table)
    })

    or...  pbTable.decode((table, function (err, buffer) { } )

Each 'row' of data can also be a verbose object

    data: [
      { location: 'east street', total: 34324, latitude: -42.559355, .... },
      { location: 'work', .... },
      ...
    ]

If data is stored as verbose objects then we use:

    pbTable.encodeVerbose(buffer, callback (err, buffer) { } )

    and...   pbTable.decodeVerbose(buffer, callback (err, buffer) { } )

We can also add additional data to an existing buffer

    pbTable.add(buffer, data, callback (err, buffer) { } )
    ...
    pbTable.addTable(buffer, data, callback(err, buffer) { } )
    pbTable.addVerbose(buffer, data, callback (err, buffer) { } )

## Data extraction

We can get an individual row of our data directly from the buffer. We provide the buffer and a 'request'. The request represents the 'table row numbers' that you want returned and can be a single an integer or an Array of integers.

    pbTable.get(buffer, request, callback(err, data) { } )
    ...
    pbTable.getTable(buffer, request, callback(err, data) { } )
    pbTable.getVerbose(buffer, request, callback(err, data) { } )

## Compressing data

We can making use of Proto Buffers integer compression by transforming structured data via offset, multiplication and sequencing.

Transform your 'float' and 'int' data using inbuilt data transformation

    header: [
      {
        name: 'latitude',
        type: 'int',
        transform: {
          offset: -42.2454,
          decimals: 4,
          sequence: true
        }  
      },
      {
        name: 'longitude',
        type: 'int',
        transform: {
          offset: 173.9302,
          multip: 10000,
        }  
      },
      ...
    ]

more examples and documentation coming......

# Installation

## For packaging with NPM and ES6

    npm install --save protobuf-table

and then:

    include pbTable from 'protobuf-table'

## Stand alone

    var pbTable = require('./dist/pbTable-min.js')

# Building and Testing

Build

    npm run build

Build and test

    npm run test
