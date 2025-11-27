#!/usr/bin/env node
// Build script to convert head.proto to head.json for runtime use

const { execSync } = require('child_process')
const path = require('path')

const protoFile = path.join(__dirname, '../src/head.proto')
const jsonFile = path.join(__dirname, '../src/head.json')

console.log('Converting head.proto to head.json...')

try {
  // Use protobuf.js CLI to convert .proto to JSON
  execSync(`npx pbjs -t json "${protoFile}" > "${jsonFile}"`, { 
    stdio: 'inherit',
    cwd: path.join(__dirname, '..')
  })
  
  console.log('✓ Successfully generated head.json from head.proto')
  console.log('  Input:', protoFile)
  console.log('  Output:', jsonFile)
} catch (error) {
  console.error('✗ Failed to generate head.json:', error.message)
  process.exit(1)
}
