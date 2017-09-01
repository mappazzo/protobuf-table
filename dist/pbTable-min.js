var pbuf=require('protobufjs'),Root=pbuf.Root,Reader=pbuf.Reader,Writer=pbuf.Writer,types={string:'string',uint:'int32',int:'sint32',float:'float'},headProto={TableHeader:{nested:{Transform:{fields:{offset:{id:1,rule:'optional',type:'int32'},multip:{id:2,rule:'optional',type:'int32'},decimals:{id:3,rule:'optional',type:'int32'},sequence:{id:4,rule:'optional',type:'bool'}}},Field:{fields:{name:{id:1,rule:'required',type:'string'},type:{id:2,rule:'required',type:'string'},transform:{id:3,rule:'optional',type:'Transform'}}},Meta:{fields:{name:{id:1,rule:'optional',type:'string'},owner:{id:2,rule:'optional',type:'string'},link:{id:3,rule:'optional',type:'string'},comment:{id:4,rule:'optional',type:'string'}}},Header:{fields:{header:{id:1,rule:'repeated',type:'Field'},meta:{id:2,rule:'optional',type:'Meta'}}}}}},protocolFromHeader=function(a,b){var c={DataArray:{nested:{Row:{fields:{}},Data:{fields:{data:{id:1,rule:'repeated',type:'Row'}}}}}},d={};a.header.forEach(function(a,b){var c=types[a.type];d[a.name]={id:b+1,type:c,rule:a.rule||'optional'}}),c.DataArray.nested.Row.fields=d;var e=new Root;e.addJSON(c),b(null,e)},decodeData=function(a,b,c){var d=a.lookupType('DataArray.Data'),e=d.decode(b);c(null,e)},encodeData=function(a,b,c,d){var e=a.lookupType('DataArray.Data'),f=e.verify(b);if(f){var g=new Error(f);d(g)}else c||(c=new Writer),e.encode(b,c),d(null,c)},decodeHeader=function(a,b){var c=new Root;c.addJSON(headProto);var d=c.lookupType('TableHeader.Header'),e=d.decodeDelimited(a);b(null,e)},encodeHeader=function(a,b,c){var d=new Root;d.addJSON(headProto);var e=d.lookupType('TableHeader.Header'),f=e.verify(a);if(f){var g=new Error(f);c(g)}else b||(b=new Writer),e.encodeDelimited(a,b),c(null,b)},transformInteger={parse:function(a,b,c){c.offset||(c.offset=0),c.multip||(c.multip=1),c.decimals||(c.decimals=0),a-=c.sequence&&b?b:c.offset;var d=a*c.multip;return d*=Math.pow(10,c.decimals),parseInt(d)},recover:function(a,b,c){c.offset||(c.offset=0),c.multip||(c.multip=1),c.decimals||(c.decimals=0);var d=a*Math.pow(10,-c.decimals);return d/=c.multip,d+=c.sequence&&b?b:c.offset,d}},encodeVerbose=function(a,b){if(!a.header||!a.data){var c=new Error('object is not a valid format');return b(c)}encodeHeader(a,null,function(c,d){return c?b(c):void protocolFromHeader(a,function(c,e){return c?b(c):void encodeData(e,a,d,function(a,c){if(a)return b(a);var d=c.finish();b(null,d)})})})},decodeVerbose=function(a,b){var c=new Reader(a);decodeHeader(c,function(a,d){return a?b(a):void protocolFromHeader(d,function(a,e){return a?b(a):void decodeData(e,c,function(a,c){if(a)return b(a);var e={header:d.header,data:c.data};b(null,JSON.parse(JSON.stringify(e)))})})})},addVerbose=function(a,b,c){decodeHeader(a,function(d,e){return d?c(d):void protocolFromHeader(e,function(d,e){return d?c(d):void encodeData(e,{data:b},null,function(b,d){if(b)return c(b);var e=d.finish(),f=a.length+e.length,g=new Uint8Array(f);g.set(a,0),g.set(e,a.length),c(null,g)})})})},encodeTable=function(a,b){var c;return a.header&&a.data?Array.isArray(a.data)?void encodeHeader(a,null,function(c,d){return c?b(c):void protocolFromHeader(a,function(c,e){if(c)return b(c);a.data.forEach(function(c,f){var g={data:[{}]};a.header.forEach(function(b,d){var e=c[d];if(b.transform&&('int'===b.type||'uint'===b.type)){var h=null;1<=f&&(h=a.data[f-1][d]),e=transformInteger.parse(e,h,b.transform)}g.data[0][b.name]=e}),encodeData(e,g,d,function(a){if(a)return b(a)})});var f=d.finish();b(null,f)})}):(c=new Error('object is not an array'),b(c)):(c=new Error('object is not a valid format'),b(c))},decodeTable=function(a,b){var c=new Reader(a);decodeHeader(c,function(a,d){return a?b(a):void protocolFromHeader(d,function(a,e){return a?b(a):void decodeData(e,c,function(a,c){if(a)return b(a);var e={header:JSON.parse(JSON.stringify(d.header)),data:[]};c.data.forEach(function(a,b){e.data[b]=[],d.header.forEach(function(c,d){if(a[c.name]){var f=a[c.name];if(c.transform&&('int'===c.type||'uint'===c.type)){var g=null;1<=b&&(g=e.data[b-1][d]),f=transformInteger.recover(f,g,c.transform)}e.data[b][d]=f}})}),b(null,e)})})})},addTable=function(a,b,c){decodeHeader(a,function(d,e){return d?c(d):void protocolFromHeader(e,function(d,f){if(d)return c(d);var g=new Writer;b.forEach(function(a){var b=[{}];a.forEach(function(a,c){b[0][e.header[c].name]=a}),encodeData(f,b,g,function(a){if(a)return c(a)})});var h=g.finish(),i=a.length+h.length,j=new Uint8Array(i);j.set(a,0),j.set(h,a.length),c(null,j)})})};module.exports={encodeVerbose,decodeVerbose,addVerbose,encodeTable,decodeTable,addTable,types};