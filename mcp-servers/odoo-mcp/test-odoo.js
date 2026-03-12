#!/usr/bin/env node
/**
 * Odoo MCP Server Test Script
 * Tests Odoo connection and API
 */

require('dotenv').config({ path: require('path').join(__dirname, '../../.env') });
const fetch = require('node-fetch');

const ODOO_CONFIG = {
    url: process.env.ODOO_URL || 'http://localhost:8069',
    db: process.env.ODOO_DB || 'odoo',
    username: process.env.ODOO_USERNAME || 'admin',
    password: process.env.ODOO_PASSWORD || 'admin',
    apiKey: process.env.ODOO_API_KEY || null
};

async function testConnection() {
    console.log('='.repeat(60));
    console.log('ODOO MCP SERVER - CONNECTION TEST');
    console.log('='.repeat(60));
    console.log();
    
    console.log('Configuration:');
    console.log(`  URL: ${ODOO_CONFIG.url}`);
    console.log(`  Database: ${ODOO_CONFIG.db}`);
    console.log(`  Username: ${ODOO_CONFIG.username}`);
    console.log(`  API Key: ${ODOO_CONFIG.apiKey ? 'Set ✅' : 'Missing ❌'}`);
    console.log();
    
    // Test 1: Check Odoo is running
    console.log('1. Testing Odoo server connection...');
    try {
        const response = await fetch(`${ODOO_CONFIG.url}/web/webclient/version_info`);
        if (response.ok) {
            console.log('   ✅ Odoo server is running!');
        } else {
            console.log('   ⚠️  Odoo server responded but not standard endpoint');
        }
    } catch (error) {
        console.log('   ❌ Cannot connect to Odoo server');
        console.log('   Make sure Odoo is running at:', ODOO_CONFIG.url);
        return false;
    }
    console.log();
    
    // Test 2: Test JSON-RPC authentication
    console.log('2. Testing authentication...');
    try {
        const authResponse = await fetch(`${ODOO_CONFIG.url}/jsonrpc`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    service: 'common',
                    method: 'authenticate',
                    args: [
                        ODOO_CONFIG.db,
                        ODOO_CONFIG.username,
                        ODOO_CONFIG.password,
                        {}
                    ]
                },
                id: 1
            })
        });
        
        const result = await authResponse.json();
        
        if (result.result) {
            console.log('   ✅ Authentication successful!');
            console.log(`   User ID: ${result.result}`);
        } else {
            console.log('   ❌ Authentication failed');
            console.log('   Check username, password, and database name');
            return false;
        }
    } catch (error) {
        console.log('   ❌ Authentication error:', error.message);
        return false;
    }
    console.log();
    
    // Test 3: Get company info
    console.log('3. Getting company information...');
    try {
        const response = await fetch(`${ODOO_CONFIG.url}/jsonrpc`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    service: 'object',
                    method: 'execute_kwargs',
                    args: [
                        ODOO_CONFIG.db,
                        1, // Will be replaced after auth
                        ODOO_CONFIG.password,
                        'res.company',
                        'search_read',
                        [],
                        { fields: ['name', 'currency_id'], limit: 1 }
                    ]
                },
                id: 2
            })
        });
        
        const result = await response.json();
        console.log('   Company data:', JSON.stringify(result, null, 2));
        
        if (result.result) {
            console.log('   ✅ Can read company data!');
        }
    } catch (error) {
        console.log('   ⚠️  Company data read skipped (normal for first test)');
    }
    console.log();
    
    return true;
}

async function main() {
    const success = await testConnection();
    
    console.log('='.repeat(60));
    if (success) {
        console.log('✅ ODOO MCP SERVER - READY');
        console.log();
        console.log('Odoo is connected and ready for:');
        console.log('  - Creating invoices');
        console.log('  - Recording payments');
        console.log('  - Financial reporting');
        console.log('  - Transaction categorization');
    } else {
        console.log('❌ ODOO MCP SERVER - NEEDS CONFIGURATION');
        console.log();
        console.log('Check:');
        console.log('  1. Odoo is installed and running');
        console.log('  2. Database name is correct');
        console.log('  3. Username and password are correct');
        console.log('  4. See docs/ODOO_INSTALLATION.md for setup guide');
    }
    console.log('='.repeat(60));
    
    process.exit(success ? 0 : 1);
}

main().catch(console.error);
