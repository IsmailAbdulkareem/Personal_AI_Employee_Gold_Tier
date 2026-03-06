#!/usr/bin/env node
/**
 * Direct Facebook Post Test
 * Posts directly to Facebook without MCP protocol overhead
 */

require('dotenv').config({ path: require('path').join(__dirname, '../../.env') });
const fetch = require('node-fetch');

const FB_CONFIG = {
    accessToken: process.env.FB_ACCESS_TOKEN,
    pageId: process.env.FB_PAGE_ID,
    version: process.env.FB_VERSION || 'v25.0'
};

async function postToFacebook() {
    console.log('='.repeat(60));
    console.log('DIRECT FACEBOOK POST TEST');
    console.log('='.repeat(60));
    console.log();
    console.log('Configuration:');
    console.log(`  Page ID: ${FB_CONFIG.pageId}`);
    console.log(`  API Version: ${FB_CONFIG.version}`);
    console.log(`  Token Length: ${FB_CONFIG.accessToken?.length || 0} chars`);
    console.log();
    
    const message = "🚀 Gold Tier AI Employee - Direct Post Test!\n\nThis is a test post to verify Facebook integration is working. If you see this on Facebook, the integration is successful!\n\n#AI #Automation #GoldTier #Test";
    
    console.log('Post Content:');
    console.log('-'.repeat(60));
    console.log(message);
    console.log('-'.repeat(60));
    console.log();
    
    try {
        // Try to post
        const params = new URLSearchParams({
            message: message,
            access_token: FB_CONFIG.accessToken
        });
        
        console.log('Posting to Facebook...');
        console.log(`URL: https://graph.facebook.com/${FB_CONFIG.version}/${FB_CONFIG.pageId}/feed`);
        console.log();
        
        const response = await fetch(
            `https://graph.facebook.com/${FB_CONFIG.version}/${FB_CONFIG.pageId}/feed`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: params
            }
        );
        
        const result = await response.json();
        
        console.log('Facebook Response:');
        console.log('-'.repeat(60));
        console.log(JSON.stringify(result, null, 2));
        console.log('-'.repeat(60));
        console.log();
        
        if (result.id) {
            console.log('✅ SUCCESS! Post published to Facebook!');
            console.log(`   Post ID: ${result.id}`);
            console.log(`   View at: https://facebook.com/${result.id.split('_')[0]}/posts/${result.id.split('_')[1]}`);
            console.log();
            console.log('The integration is working!');
            return true;
        } else if (result.error) {
            console.log('❌ FAILED! Facebook returned an error:');
            console.log(`   Error: ${result.error.message}`);
            console.log(`   Type: ${result.error.type}`);
            console.log(`   Code: ${result.error.code}`);
            console.log();
            console.log('This means your token needs different permissions.');
            console.log('See docs/FACEBOOK_POSTING_STATUS.md for the fix.');
            return false;
        }
        
    } catch (error) {
        console.log('❌ ERROR! Request failed:');
        console.log(`   ${error.message}`);
        console.log();
        return false;
    }
}

postToFacebook().then(success => {
    process.exit(success ? 0 : 1);
});
