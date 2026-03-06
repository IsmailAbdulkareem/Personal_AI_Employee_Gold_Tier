#!/usr/bin/env node
/**
 * Facebook MCP Interactive Test
 * Send commands and see responses
 */

const { spawn } = require('child_process');
const path = require('path');

console.log('='.repeat(60));
console.log('FACEBOOK MCP - INTERACTIVE TEST');
console.log('='.repeat(60));
console.log();

// Start the MCP server
const mcp = spawn('node', ['index.js'], {
    cwd: __dirname,
    stdio: ['pipe', 'pipe', 'pipe']
});

// Test commands
const tests = [
    {
        name: 'Authenticate',
        method: 'facebook/authenticate',
        params: {}
    },
    {
        name: 'Get Page Info',
        method: 'facebook/get_posts',
        params: { limit: 3 }
    }
];

let testIndex = 0;

mcp.stdout.on('data', (data) => {
    const output = data.toString();
    console.log('Response:', output.trim());
    
    // Try to parse as JSON and pretty print
    try {
        const json = JSON.parse(output.trim());
        console.log('Parsed:', JSON.stringify(json, null, 2));
    } catch (e) {
        // Not JSON, just print
    }
    
    testIndex++;
    if (testIndex < tests.length) {
        // Send next test after a short delay
        setTimeout(sendNextTest, 1000);
    } else {
        console.log();
        console.log('='.repeat(60));
        console.log('✅ Tests complete!');
        console.log('='.repeat(60));
        mcp.kill();
    }
});

mcp.stderr.on('data', (data) => {
    const output = data.toString();
    if (output.includes('✅') || output.includes('🟡')) {
        console.log(output.trim());
    }
});

function sendNextTest() {
    const test = tests[testIndex];
    const message = {
        jsonrpc: '2.0',
        method: test.method,
        params: test.params,
        id: testIndex + 1
    };
    
    console.log(`\nSending: ${test.name}`);
    console.log('Request:', JSON.stringify(message));
    mcp.stdin.write(JSON.stringify(message) + '\n');
}

// Start first test
setTimeout(() => {
    sendNextTest();
}, 1000);
