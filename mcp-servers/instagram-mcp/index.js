#!/usr/bin/env node
/**
 * Instagram MCP Server - Gold Tier
 * 
 * Model Context Protocol server for Instagram Graph API integration.
 * Provides media posting, stories, and analytics capabilities.
 * 
 * Status: PLANNED (Gold Tier - Phase 3)
 * Requires: Instagram Business Account connected to Facebook Page
 */

// Load environment variables
require('dotenv').config();

const fetch = require('node-fetch');

// Configuration from environment variables
const IG_CONFIG = {
    appId: process.env.IG_APP_ID || '',
    appSecret: process.env.IG_APP_SECRET || '',
    accessToken: process.env.IG_ACCESS_TOKEN || '',
    instagramBusinessAccountId: process.env.IG_BUSINESS_ACCOUNT_ID || '',
    version: process.env.IG_VERSION || 'v18.0'
};

// State
let authenticated = false;

/**
 * Validate access token and get Instagram account info
 */
async function validateToken() {
    try {
        const response = await fetch(
            `https://graph.facebook.com/${IG_CONFIG.version}/${IG_CONFIG.instagramBusinessAccountId}?fields=username,name&access_token=${IG_CONFIG.accessToken}`
        );
        const result = await response.json();

        if (result.username) {
            authenticated = true;
            console.log(`✅ Instagram authenticated as ${result.username}`);
            return true;
        }

        console.error('❌ Instagram token validation failed');
        return false;
    } catch (error) {
        console.error('❌ Instagram validation error:', error.message);
        return false;
    }
}

/**
 * Create media container (required before publishing)
 */
async function createMediaContainer(mediaType, mediaUrl, caption = '') {
    const params = new URLSearchParams({
        image_url: mediaType === 'IMAGE' ? mediaUrl : undefined,
        video_url: mediaType === 'VIDEO' ? mediaUrl : undefined,
        media_type: mediaType,
        caption: caption,
        access_token: IG_CONFIG.accessToken
    });

    const response = await fetch(
        `https://graph.facebook.com/${IG_CONFIG.version}/${IG_CONFIG.instagramBusinessAccountId}/media?${params}`,
        { method: 'POST' }
    );

    const result = await response.json();
    
    if (result.id) {
        console.log(`✅ Instagram media container created: ${result.id}`);
        return result.id;
    }
    
    throw new Error(result.error?.message || 'Failed to create media container');
}

/**
 * Publish media container
 */
async function publishMedia(creationId) {
    const params = new URLSearchParams({
        creation_id: creationId,
        access_token: IG_CONFIG.accessToken
    });

    const response = await fetch(
        `https://graph.facebook.com/${IG_CONFIG.version}/${IG_CONFIG.instagramBusinessAccountId}/media_publish?${params}`,
        { method: 'POST' }
    );

    const result = await response.json();
    
    if (result.id) {
        console.log(`✅ Instagram post published: ${result.id}`);
        return { post_id: result.id, status: 'published' };
    }
    
    throw new Error(result.error?.message || 'Failed to publish media');
}

/**
 * Post image to Instagram
 */
async function postImage(imageUrl, caption = '') {
    const creationId = await createMediaContainer('IMAGE', imageUrl, caption);
    return await publishMedia(creationId);
}

/**
 * Post carousel (multiple images)
 */
async function postCarousel(imageUrls, caption = '') {
    const children = [];
    
    for (const imageUrl of imageUrls) {
        const creationId = await createMediaContainer('IMAGE', imageUrl, '');
        children.push(creationId);
    }
    
    // Create carousel container
    const params = new URLSearchParams({
        media_type: 'CAROUSEL',
        children: children.join(','),
        caption: caption,
        access_token: IG_CONFIG.accessToken
    });

    const response = await fetch(
        `https://graph.facebook.com/${IG_CONFIG.version}/${IG_CONFIG.instagramBusinessAccountId}/media?${params}`,
        { method: 'POST' }
    );

    const result = await response.json();
    
    if (result.id) {
        return await publishMedia(result.id);
    }
    
    throw new Error(result.error?.message || 'Failed to create carousel');
}

/**
 * Get Instagram insights
 */
async function getInsights(metrics = ['impressions', 'reach', 'profile_views'], days = 7) {
    const since = new Date();
    since.setDate(since.getDate() - days);
    
    const until = new Date();
    
    const params = new URLSearchParams({
        metric: metrics.join(','),
        since: since.toISOString().split('T')[0],
        until: until.toISOString().split('T')[0],
        access_token: IG_CONFIG.accessToken
    });

    const response = await fetch(
        `https://graph.facebook.com/${IG_CONFIG.version}/${IG_CONFIG.instagramBusinessAccountId}/insights?${params}`
    );

    const result = await response.json();
    return result.data || [];
}

/**
 * Get recent media posts
 */
async function getMedia(limit = 10) {
    const params = new URLSearchParams({
        fields: 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count',
        limit: limit.toString(),
        access_token: IG_CONFIG.accessToken
    });

    const response = await fetch(
        `https://graph.facebook.com/${IG_CONFIG.version}/${IG_CONFIG.instagramBusinessAccountId}/media?${params}`
    );

    const result = await response.json();
    return result.data || [];
}

/**
 * Generate weekly summary
 */
async function generateSummary() {
    const insights = await getInsights();
    const media = await getMedia(20);
    
    const summary = {
        period: 'last_7_days',
        total_posts: media.length,
        metrics: {}
    };

    // Process insights
    for (const metric of insights) {
        const values = metric.values || [];
        const total = values.reduce((sum, v) => sum + (v.value || 0), 0);
        summary.metrics[metric.name] = total;
    }

    // Calculate engagement
    let totalLikes = 0;
    let totalComments = 0;

    for (const post of media) {
        totalLikes += post.like_count || 0;
        totalComments += post.comments_count || 0;
    }

    summary.engagement = {
        likes: totalLikes,
        comments: totalComments,
        total: totalLikes + totalComments
    };

    return summary;
}

// MCP Server Protocol Handlers
const handlers = {
    'instagram/authenticate': async () => {
        const success = await validateToken();
        return { authenticated: success };
    },

    'instagram/post_image': async (params) => {
        const result = await postImage(params.image_url, params.caption);
        return result;
    },

    'instagram/post_carousel': async (params) => {
        const result = await postCarousel(params.image_urls, params.caption);
        return result;
    },

    'instagram/get_insights': async (params) => {
        const insights = await getInsights(params.metrics, params.days);
        return { insights };
    },

    'instagram/get_media': async (params) => {
        const media = await getMedia(params.limit);
        return { media };
    },

    'instagram/generate_summary': async () => {
        const summary = await generateSummary();
        return { summary };
    }
};

// Main MCP Server Loop
async function main() {
    console.error('🟡 Instagram MCP Server starting...');
    console.error('🟡 Status: PLANNED (Gold Tier - Phase 3)');
    console.error('🟡 Requires: Instagram Business Account + Facebook Page Connection');
    
    // Read from stdin for MCP protocol
    process.stdin.on('data', async (data) => {
        try {
            const message = JSON.parse(data.toString());
            const { method, params, id } = message;

            if (handlers[method]) {
                const result = await handlers[method](params || {});
                const response = {
                    jsonrpc: '2.0',
                    result,
                    id
                };
                process.stdout.write(JSON.stringify(response) + '\n');
            } else {
                const response = {
                    jsonrpc: '2.0',
                    error: { code: -32601, message: `Method not found: ${method}` },
                    id
                };
                process.stdout.write(JSON.stringify(response) + '\n');
            }
        } catch (error) {
            console.error('❌ Error processing message:', error.message);
        }
    });

    console.error('✅ Instagram MCP Server ready (PLANNED)');
}

main().catch(console.error);
