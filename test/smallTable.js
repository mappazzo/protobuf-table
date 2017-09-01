// Example - structure of JS Table object
//
// 'header' is an array of (fields) that have 'name' and 'type'
// 'data' must be an array of arrays (points), each point having an equal length to header

module.exports = {
  'header': [
    { 'name': 'location', 'type': 'string' },
    { 'name': 'total', 'type': 'uint' },
    { 'name': 'latitude', 'type': 'float' },
    { 'name': 'longitude', 'type': 'float' },
    { 'name': 'reading', 'type': 'int' }
  ],
  'meta': {
    'filename': '',
    'owner': '',
    'link': '',
    'comment': ''
  },
  'data': [
    ['east street', 34324, -42.559355, 172.60347, -889],
    ['work', 7344, -41.546799, 172.50742, 4],
    ['big tree', 9327924, -41.79346, 173.04213, 32]
  ]
}
