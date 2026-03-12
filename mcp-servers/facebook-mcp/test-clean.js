#!/usr/bin/env node
/**
 * Facebook Token Test - Clean Load
 */

const fs = require('fs');
const path = require('path');
const fetch = require('node-fetch');

// Read .env directly
const envPath = path.join(__dirname, '../../.env');
const envContent = fs.readFileSync(envPath, 'utf8');

// Parse FB_ACCESS_TOKEN
const tokenMatch = envContent.match(/FB_ACCESS_TOKEN="([^"]+)"/);
const pageIdMatch = envContent.match(/FB_PAGE_ID="([^"]+)"/);
const versionMatch = envContent.match(/FB_VERSION=(.+)/);

const FB_ACCESS_TOKEN = tokenMatch ? tokenMatch[1] : '';
const FB_PAGE_ID = pageIdMatch ? pageIdMatch[1] : '';
const FB_VERSION = versionMatch ? versionMatch[1].trim() : 'v25.0';

console.log('Loading from:', envPath);
console.log('Token starts with:', FB_ACCESS_TOKEN.substring(0, 20) + '...');
console.log('Token ends with:', FB_ACCESS_TOKEN.substring(FB_ACCESS_TOKEN.length - 10) + '...');
console.log('Page ID:', FB_PAGE_ID);
console.log('Version:', FB_VERSION);
console.log('');

async function test() {
    const url = `https://graph.facebook.com/${FB_VERSION}/${FB_PAGE_ID}?fields=id,name,username&access_token=${FB_ACCESS_TOKEN}`;
    
    console.log('Testing URL:', url.substring(0, 100) + '...');
    console.log('');
    
    const response = await fetch(url);
    const result = await response.json();
    
    if (result.error) {
        console.log('❌ Error:', result.error.message);
        console.log('Error type:', result.error.type);
        console.log('Error subcode:', result.error.error_subcode);
        console.log('');
        console.log('The token in .env file is invalid or expired.');
        console.log('Please generate a new token from: https://developers.facebook.com/tools/explorer/');
    } else {
        console.log('✅ SUCCESS!');
        console.log('Page ID:', result.id);
        console.log('Page Name:', result.name);
        console.log('Username:', result.username || 'N/A');
    }
}

test();
