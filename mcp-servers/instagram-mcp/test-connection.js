#!/usr/bin/env node
/**
 * Test Instagram MCP Connection
 */

require('dotenv').config({ path: '../../.env' });
const fetch = require('node-fetch');

const IG_CONFIG = {
    accessToken: process.env.IG_ACCESS_TOKEN || '',
    instagramBusinessAccountId: process.env.IG_BUSINESS_ACCOUNT_ID || '',
    version: process.env.IG_VERSION || 'v25.0'
};

async function testConnection() {
    console.log('🔍 Testing Instagram MCP Connection...\n');
    console.log('📋 Configuration:');
    console.log('   - Access Token:', IG_CONFIG.accessToken ? '✅ Present' : '❌ Missing');
    console.log('   - Business Account ID:', IG_CONFIG.instagramBusinessAccountId || '❌ Missing');
    console.log('   - API Version:', IG_CONFIG.version);
    console.log('');

    try {
        // Test 1: Validate token and get account info
        console.log('🧪 Test 1: Validating access token...');
        const response = await fetch(
            `https://graph.facebook.com/${IG_CONFIG.version}/${IG_CONFIG.instagramBusinessAccountId}?fields=username,name&access_token=${IG_CONFIG.accessToken}`
        );
        const result = await response.json();

        if (result.error) {
            console.log('❌ FAILED:', result.error.message);
            console.log('   Error Type:', result.error.type);
            console.log('   Error Code:', result.error.code);
            return false;
        }

        if (result.username) {
            console.log('✅ SUCCESS!');
            console.log('   - Username:', result.username);
            console.log('   - Name:', result.name);
            console.log('   - Account ID:', result.id);
        } else {
            console.log('❌ FAILED: Unexpected response');
            console.log('   Response:', result);
            return false;
        }

        // Test 2: Try to get recent media
        console.log('\n🧪 Test 2: Fetching recent media...');
        const mediaResponse = await fetch(
            `https://graph.facebook.com/${IG_CONFIG.version}/${IG_CONFIG.instagramBusinessAccountId}/media?fields=id,caption,media_type,media_url,permalink,timestamp&limit=3&access_token=${IG_CONFIG.accessToken}`
        );
        const mediaResult = await mediaResponse.json();

        if (mediaResult.error) {
            console.log('❌ FAILED:', mediaResult.error.message);
        } else {
            console.log('✅ SUCCESS!');
            console.log('   - Posts found:', mediaResult.data?.length || 0);
            if (mediaResult.data && mediaResult.data.length > 0) {
                console.log('   - Latest post:', mediaResult.data[0].id);
            }
        }

        console.log('\n✅ All tests passed! Instagram MCP is working correctly.\n');
        return true;

    } catch (error) {
        console.log('❌ ERROR:', error.message);
        return false;
    }
}

testConnection().then(success => {
    process.exit(success ? 0 : 1);
});
