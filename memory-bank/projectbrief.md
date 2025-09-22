# Project Brief: protobuf-table

## Core Identity
**protobuf-table** is a JavaScript library that provides dynamic Protocol Buffer implementation specifically designed for structured table data compression and serialization.

## Primary Purpose
Enable efficient binary serialization of tabular data using Google's Protocol Buffers, with built-in compression optimizations for numeric data through transforms and delta encoding.

## Key Requirements
1. **Dynamic Schema Generation**: Create protobuf schemas at runtime based on table headers
2. **Multiple Data Formats**: Support both array-based and object-based data representations
3. **Compression Features**: Implement data transforms (offset, multiplication, decimals, sequencing) for optimal storage
4. **Random Access**: Allow extraction of specific rows without full deserialization
5. **Extensibility**: Support metadata and custom key-value pairs
6. **Node.js Compatibility**: Callback-based API following Node.js conventions

## Core Functionality
- **Encoding**: Convert JavaScript table objects to compressed binary buffers
- **Decoding**: Restore original table data from binary buffers
- **Data Retrieval**: Extract specific rows by index without full decode
- **Data Addition**: Append new rows to existing encoded buffers
- **Indexing**: Generate byte-position maps for efficient random access

## Success Criteria
- Significant size reduction compared to JSON serialization
- Fast encoding/decoding performance
- Reliable data integrity (encode → decode → verify)
- Support for large datasets with minimal memory overhead
- Clean, intuitive API for JavaScript developers

## Technical Constraints
- Must use protobufjs as the underlying Protocol Buffer implementation
- Maintain backward compatibility with existing encoded buffers
- Support Node.js callback patterns (error-first callbacks)
- Handle various JavaScript data types (string, number, boolean)

## Project Scope
**In Scope:**
- Table data serialization/deserialization
- Numeric data compression transforms
- Random row access
- Buffer concatenation for data addition
- Comprehensive test coverage

**Out of Scope:**
- Real-time streaming protocols
- Database integration
- Web browser optimization (Node.js focused)
- Complex nested object structures (flat table data only)

## License & Ownership
- **License**: Beerware License (Revision 42)
- **Author**: Kelly Norris (Mappazzo)
- **Repository**: https://github.com/mappazzo/protobuf-table
- **Version**: 1.2.3
