#!/usr/bin/env node
/**
 * Direct Facebook Token Test
 */

require('dotenv').config({ path: '../../.env' });
const fetch = require('node-fetch');

const FB_CONFIG = {
    accessToken: process.env.FB_ACCESS_TOKEN || '',
    pageId: process.env.FB_PAGE_ID || '',
    version: process.env.FB_VERSION || 'v25.0'
};

async function test() {
    console.log('Token starts with:', FB_CONFIG.accessToken.substring(0, 20) + '...');
    console.log('Token ends with:', FB_CONFIG.accessToken.substring(FB_CONFIG.accessToken.length - 10) + '...');
    console.log('Token length:', FB_CONFIG.accessToken.length);
    console.log('');
    
    const response = await fetch(
        `https://graph.facebook.com/${FB_CONFIG.version}/${FB_CONFIG.pageId}?fields=id,name,username&access_token=${FB_CONFIG.accessToken}`
    );
    const result = await response.json();
    
    if (result.error) {
        console.log('❌ Error:', result.error.message);
        console.log('Error type:', result.error.type);
        console.log('Error subcode:', result.error.error_subcode);
    } else {
        console.log('✅ SUCCESS!');
        console.log('Page ID:', result.id);
        console.log('Page Name:', result.name);
        console.log('Username:', result.username || 'N/A');
    }
}

test();
