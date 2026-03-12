#!/usr/bin/env node
/**
 * Test Facebook Token and Connection
 */

require('dotenv').config({ path: '../../.env' });
const fetch = require('node-fetch');

const FB_CONFIG = {
    accessToken: process.env.FB_ACCESS_TOKEN || '',
    pageId: process.env.FB_PAGE_ID || '',
    version: process.env.FB_VERSION || 'v25.0'
};

async function testFacebookToken() {
    console.log('📘 Testing Facebook Token\n');
    console.log('='.repeat(50) + '\n');
    
    console.log('📋 Configuration:');
    console.log('   - Access Token:', FB_CONFIG.accessToken ? '✅ Present (' + FB_CONFIG.accessToken.substring(0, 30) + '...)' : '❌ Missing');
    console.log('   - Page ID:', FB_CONFIG.pageId || '❌ Missing');
    console.log('   - API Version:', FB_CONFIG.version);
    console.log('');

    try {
        // Test 1: Validate token and get page info
        console.log('🧪 Test 1: Validating access token...');
        const response = await fetch(
            `https://graph.facebook.com/${FB_CONFIG.version}/${FB_CONFIG.pageId}?fields=id,name,username&access_token=${FB_CONFIG.accessToken}`
        );
        const result = await response.json();

        if (result.error) {
            console.log('❌ FAILED:', result.error.message);
            console.log('   Error Type:', result.error.type);
            console.log('   Error Code:', result.error.code);
            console.log('   Error Subcode:', result.error.error_subcode);
            
            if (result.error.message.includes('expired')) {
                console.log('\n⚠️  TOKEN EXPIRED - Please generate a new one!');
                console.log('   Go to: https://developers.facebook.com/tools/explorer/');
                console.log('   Select your app > Get Token > Generate Page Access Token');
                console.log('   Permissions needed: pages_manage_posts, pages_read_engagement');
            }
            return false;
        }

        if (result.id) {
            console.log('✅ SUCCESS!');
            console.log('   - Page ID:', result.id);
            console.log('   - Page Name:', result.name);
            console.log('   - Username:', result.username || 'N/A');
        } else {
            console.log('❌ FAILED: Unexpected response');
            console.log('   Response:', result);
            return false;
        }

        // Test 2: Check token permissions
        console.log('\n🧪 Test 2: Checking token permissions...');
        const permissionsResponse = await fetch(
            `https://graph.facebook.com/${FB_CONFIG.version}/${FB_CONFIG.pageId}?fields=permissions&access_token=${FB_CONFIG.accessToken}`
        );
        const permissionsResult = await permissionsResponse.json();

        if (permissionsResult.permissions) {
            console.log('✅ Permissions found:');
            for (const perm of permissionsResult.permissions.data || []) {
                const status = perm.status === 'granted' ? '✅' : '❌';
                console.log(`   ${status} ${perm.permission}`);
            }
        }

        // Test 3: Try to get recent posts
        console.log('\n🧪 Test 3: Fetching recent posts...');
        const postsResponse = await fetch(
            `https://graph.facebook.com/${FB_CONFIG.version}/${FB_CONFIG.pageId}/posts?limit=3&access_token=${FB_CONFIG.accessToken}`
        );
        const postsResult = await postsResponse.json();

        if (postsResult.error) {
            console.log('❌ Failed to get posts:', postsResult.error.message);
        } else {
            console.log('✅ SUCCESS!');
            console.log('   - Posts found:', postsResult.data?.length || 0);
            if (postsResult.data && postsResult.data.length > 0) {
                console.log('   - Latest post:', postsResult.data[0].id);
            }
        }

        console.log('\n' + '='.repeat(50));
        console.log('✅ All tests passed! Facebook MCP is ready.\n');
        return true;

    } catch (error) {
        console.log('❌ ERROR:', error.message);
        return false;
    }
}

async function main() {
    const success = await testFacebookToken();
    process.exit(success ? 0 : 1);
}

main();
