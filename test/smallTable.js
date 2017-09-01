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
    ['work', 7344, -42.55931, 172.60742, 4],
    ['big tree', 9327924, -42.5553115, 173.60213, 32],
    ['big tree', 9327924, -42.555315, 173.60213, 32],
    ['big tree', 9327924, -42.555325, 173.60213, 32],
    ['big tree', 9327924, -42.55535, 173.60213, 32],
    ['big tree', 9327924, -42.555425, 173.60213, 32],
    ['big tree', 9327924, -42.5555885, 173.60213, 32],
    ['big tree', 9327924, -42.5551355, 173.60213, 32],
    ['big tree', 9327924, -42.555425, 173.60213, 32],
    ['big tree', 9327924, -42.555225, 173.60213, 32],
    ['big tree', 9327924, -42.555215, 173.60213, 32],
    ['big tree', 9327924, -42.555115, 173.60213, 32],
    ['big tree', 9327924, -42.555105, 173.60213, 32],
    ['big tree', 9327924, -42.555215, 173.60213, 32],
    ['big tree', 9327924, -42.555235, 173.60213, 32],
    ['big tree', 9327924, -42.555455, 173.60213, 32],
    ['big tree', 9327924, -42.555435, 173.60213, 32]
  ]
}
