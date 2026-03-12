#!/usr/bin/env node
/**
 * Post Image to Instagram - Test Script
 */

const fs = require('fs');
const path = require('path');
const fetch = require('node-fetch');

// Read .env directly to avoid caching issues
const envPath = path.join(__dirname, '../../.env');
const envContent = fs.readFileSync(envPath, 'utf8');

const IG_ACCESS_TOKEN = envContent.match(/IG_ACCESS_TOKEN="([^"]+)"/)?.[1] || '';
const IG_BUSINESS_ACCOUNT_ID = envContent.match(/IG_BUSINESS_ACCOUNT_ID=(\d+)/)?.[1] || '';
const IG_VERSION = envContent.match(/IG_VERSION=(.+)/)?.[1].trim() || 'v25.0';

// Sample image URL (must be a direct .jpg/.png URL, not a redirect)
// Using a sample image from Unsplash (direct link)
const SAMPLE_IMAGE_URL = 'https://images.unsplash.com/photo-1555421689-491a97ff2040?w=1080&h=1080&fit=crop';
const SAMPLE_CAPTION = '🚀 Test post from Gold Tier AI Employee! #AI #Automation #GoldTier';

async function postImage(imageUrl, caption) {
    console.log('📸 Posting image to Instagram...\n');
    console.log('   Image URL:', imageUrl);
    console.log('   Caption:', caption);
    console.log('');

    try {
        // Step 1: Create media container
        console.log('📦 Step 1: Creating media container...');
        const containerParams = new URLSearchParams({
            image_url: imageUrl,
            caption: SAMPLE_CAPTION,
            access_token: IG_ACCESS_TOKEN
        });

        const containerResponse = await fetch(
            `https://graph.facebook.com/${IG_VERSION}/${IG_BUSINESS_ACCOUNT_ID}/media?${containerParams}`,
            { method: 'POST' }
        );
        const containerResult = await containerResponse.json();

        if (containerResult.error) {
            console.log('❌ Failed to create container:', containerResult.error.message);
            return null;
        }

        console.log('✅ Container created:', containerResult.id);
        const creationId = containerResult.id;

        // Step 2: Publish the media
        console.log('\n📤 Step 2: Publishing media...');
        const publishParams = new URLSearchParams({
            creation_id: creationId,
            access_token: IG_ACCESS_TOKEN
        });

        const publishResponse = await fetch(
            `https://graph.facebook.com/${IG_VERSION}/${IG_BUSINESS_ACCOUNT_ID}/media_publish?${publishParams}`,
            { method: 'POST' }
        );
        const publishResult = await publishResponse.json();

        if (publishResult.error) {
            console.log('❌ Failed to publish:', publishResult.error.message);
            return null;
        }

        console.log('✅ Media published:', publishResult.id);
        
        // Step 3: Get the post permalink
        console.log('\n🔗 Step 3: Getting post permalink...');
        const permalinkResponse = await fetch(
            `https://graph.facebook.com/${IG_VERSION}/${publishResult.id}?fields=permalink&access_token=${IG_ACCESS_TOKEN}`
        );
        const permalinkResult = await permalinkResponse.json();

        console.log('✅ Post URL:', permalinkResult.permalink || 'Available in Instagram app');
        
        return {
            post_id: publishResult.id,
            permalink: permalinkResult.permalink,
            status: 'published'
        };

    } catch (error) {
        console.log('❌ Error:', error.message);
        return null;
    }
}

async function main() {
    console.log('🟡 Instagram Post Test\n');
    console.log('='.repeat(50) + '\n');
    
    const result = await postImage(SAMPLE_IMAGE_URL, SAMPLE_CAPTION);
    
    console.log('\n' + '='.repeat(50));
    if (result) {
        console.log('✅ SUCCESS! Post published to @ismaildevai');
        console.log('   Post ID:', result.post_id);
        if (result.permalink) {
            console.log('   View at:', result.permalink);
        }
    } else {
        console.log('❌ Failed to post image');
    }
    console.log('='.repeat(50) + '\n');
}

main();
