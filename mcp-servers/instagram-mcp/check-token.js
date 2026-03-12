const fs = require('fs');
const path = require('path');
const fetch = require('node-fetch');

const envPath = path.join(__dirname, '../../.env');
const envContent = fs.readFileSync(envPath, 'utf8');

const IG_ACCESS_TOKEN = envContent.match(/IG_ACCESS_TOKEN="([^"]+)"/)?.[1] || '';
const IG_BUSINESS_ACCOUNT_ID = envContent.match(/IG_BUSINESS_ACCOUNT_ID=(\d+)/)?.[1] || '';

console.log('🔍 Testing Instagram Token...\n');
console.log('Token starts with:', IG_ACCESS_TOKEN.substring(0, 30) + '...');
console.log('Token length:', IG_ACCESS_TOKEN.length);
console.log('Account ID:', IG_BUSINESS_ACCOUNT_ID);
console.log('');

async function testToken() {
    const url = `https://graph.facebook.com/v25.0/${IG_BUSINESS_ACCOUNT_ID}?fields=username,name&access_token=${IG_ACCESS_TOKEN}`;
    
    const response = await fetch(url);
    const result = await response.json();
    
    if (result.error) {
        console.log('❌ TOKEN INVALID/EXPIRED');
        console.log('Error:', result.error.message);
        console.log('');
        console.log('📋 To get a new token:');
        console.log('1. Go to: https://developers.facebook.com/tools/explorer/');
        console.log('2. Select app: 1048321038357104');
        console.log('3. Click "Get Token" → "Generate Page Access Token"');
        console.log('4. Select Instagram account: ismaildevai');
        console.log('5. Copy the new token');
        console.log('6. Update .env file with new IG_ACCESS_TOKEN');
    } else {
        console.log('✅ TOKEN VALID!');
        console.log('Username:', result.username);
        console.log('Name:', result.name);
    }
}

testToken();
