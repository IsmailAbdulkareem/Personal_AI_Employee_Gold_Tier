#!/usr/bin/env node
/**
 * Post to Facebook - Test Script
 */

const fs = require('fs');
const path = require('path');
const fetch = require('node-fetch');

// Read .env directly to avoid caching issues
const envPath = path.join(__dirname, '../../.env');
const envContent = fs.readFileSync(envPath, 'utf8');

const FB_ACCESS_TOKEN = envContent.match(/FB_ACCESS_TOKEN="([^"]+)"/)?.[1] || '';
const FB_PAGE_ID = envContent.match(/FB_PAGE_ID="([^"]+)"/)?.[1] || '';
const FB_VERSION = envContent.match(/FB_VERSION=(.+)/)?.[1].trim() || 'v25.0';

const SAMPLE_MESSAGE = '🚀 Test post from Gold Tier AI Employee! #AI #Automation #GoldTier';
const SAMPLE_IMAGE = 'https://images.unsplash.com/photo-1555421689-491a97ff2040?w=1080&h=1080&fit=crop';

async function postToFacebook(message, imageUrl) {
    console.log('📘 Posting to Facebook...\n');
    console.log('   Message:', message);
    console.log('   Image:', imageUrl);
    console.log('   Page ID:', FB_PAGE_ID);
    console.log('');

    try {
        // Create link post with image preview
        const params = new URLSearchParams({
            message: message,
            link: imageUrl,
            access_token: FB_ACCESS_TOKEN
        });

        const response = await fetch(
            `https://graph.facebook.com/${FB_VERSION}/${FB_PAGE_ID}/feed`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: params
            }
        );

        const result = await response.json();

        if (result.error) {
            console.log('❌ Failed:', result.error.message);
            return null;
        }

        if (result.id) {
            console.log('✅ Post created:', result.id);
            
            // Get permalink
            const permalinkResponse = await fetch(
                `https://graph.facebook.com/${FB_VERSION}/${result.id}?fields=permalink&access_token=${FB_ACCESS_TOKEN}`
            );
            const permalinkResult = await permalinkResponse.json();
            
            console.log('🔗 Post URL:', permalinkResult.permalink || 'Available on Facebook');
            
            return {
                post_id: result.id,
                permalink: permalinkResult.permalink,
                status: 'published'
            };
        }

        return null;

    } catch (error) {
        console.log('❌ Error:', error.message);
        return null;
    }
}

async function main() {
    console.log('🟡 Facebook Post Test\n');
    console.log('='.repeat(50) + '\n');
    
    const result = await postToFacebook(SAMPLE_MESSAGE, SAMPLE_IMAGE);
    
    console.log('\n' + '='.repeat(50));
    if (result) {
        console.log('✅ SUCCESS! Post published to Facebook');
        console.log('   Post ID:', result.post_id);
        if (result.permalink) {
            console.log('   View at:', result.permalink);
        }
    } else {
        console.log('❌ Failed to post to Facebook');
    }
    console.log('='.repeat(50) + '\n');
}

main();
