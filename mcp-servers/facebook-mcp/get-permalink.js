#!/usr/bin/env node
/**
 * Get Facebook Post Permalink
 */

const fs = require('fs');
const path = require('path');
const fetch = require('node-fetch');

const envPath = path.join(__dirname, '../../.env');
const envContent = fs.readFileSync(envPath, 'utf8');

const FB_ACCESS_TOKEN = envContent.match(/FB_ACCESS_TOKEN="([^"]+)"/)?.[1] || '';
const FB_VERSION = envContent.match(/FB_VERSION=(.+)/)?.[1].trim() || 'v25.0';

const POST_ID = '101144749664954_869319339483846';

async function getPermalink() {
    const url = `https://graph.facebook.com/${FB_VERSION}/${POST_ID}?fields=permalink_url&access_token=${FB_ACCESS_TOKEN}`;
    
    const response = await fetch(url);
    const result = await response.json();
    
    if (result.error) {
        console.log('❌ Error:', result.error.message);
    } else {
        console.log('✅ Facebook Post Published!');
        console.log('   Post ID:', POST_ID);
        console.log('   Permalink:', result.permalink_url || 'N/A');
        console.log('   Full URL:', `https://www.facebook.com/${result.permalink_url}`);
    }
}

getPermalink();
