#!/usr/bin/env node
/**
 * Twitter/X MCP Server - Gold Tier
 * 
 * Model Context Protocol server for Twitter API v2 integration.
 * Provides tweet posting, thread creation, and analytics capabilities.
 * 
 * Status: PLANNED (Gold Tier - Phase 3)
 * Requires: Twitter Developer Account + API Keys
 */

// Load environment variables
require('dotenv').config();

const fetch = require('node-fetch');

// Configuration from environment variables
const TWITTER_CONFIG = {
    apiKey: process.env.TWITTER_API_KEY || '',
    apiSecret: process.env.TWITTER_API_SECRET || '',
    accessToken: process.env.TWITTER_ACCESS_TOKEN || '',
    accessSecret: process.env.TWITTER_ACCESS_SECRET || '',
    bearerToken: process.env.TWITTER_BEARER_TOKEN || ''
};

// State
let authenticated = false;

/**
 * Validate credentials by getting user info
 */
async function validateCredentials() {
    try {
        const response = await fetch(
            'https://api.twitter.com/2/users/me',
            {
                headers: {
                    'Authorization': `Bearer ${TWITTER_CONFIG.bearerToken}`
                }
            }
        );
        const result = await response.json();
        
        if (result.data && result.data.id) {
            authenticated = true;
            console.log(`✅ Twitter authenticated as ${result.data.username}`);
            return true;
        }
        
        console.error('❌ Twitter credential validation failed');
        return false;
    } catch (error) {
        console.error('❌ Twitter validation error:', error.message);
        return false;
    }
}

/**
 * Post a tweet
 */
async function postTweet(text, options = {}) {
    const body = { text };
    
    if (options.media_ids && options.media_ids.length > 0) {
        body.media = { media_ids: options.media_ids };
    }
    
    if (options.reply_settings) {
        body.reply = options.reply_settings;
    }

    const response = await fetch('https://api.twitter.com/2/tweets', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${TWITTER_CONFIG.bearerToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
    });

    const result = await response.json();
    
    if (result.data && result.data.id) {
        console.log(`✅ Tweet posted: ${result.data.id}`);
        return { tweet_id: result.data.id, status: 'posted' };
    }
    
    throw new Error(result.errors?.[0]?.message || 'Failed to post tweet');
}

/**
 * Post a thread (multiple tweets)
 */
async function postThread(tweets) {
    const results = [];
    let previousTweetId = null;
    
    for (let i = 0; i < tweets.length; i++) {
        const text = tweets[i];
        const options = {};
        
        if (previousTweetId) {
            options.reply_settings = { in_reply_to_tweet_id: previousTweetId };
        }
        
        const result = await postTweet(text, options);
        results.push(result);
        previousTweetId = result.tweet_id;
    }
    
    return {
        thread_id: results[0].tweet_id,
        tweet_count: results.length,
        tweets: results,
        status: 'posted'
    };
}

/**
 * Upload media (for tweets with images/videos)
 */
async function uploadMedia(mediaUrl, mediaType = 'image') {
    // Note: Full media upload requires multipart/form-data
    // This is a simplified version
    console.log(`🟡 Media upload requested: ${mediaUrl} (${mediaType})`);
    console.log('🟡 Full media upload requires additional implementation');
    return { media_id: 'placeholder', status: 'not_implemented' };
}

/**
 * Get tweet analytics
 */
async function getTweetAnalytics(tweetId) {
    const response = await fetch(
        `https://api.twitter.com/2/tweets/${tweetId}?metrics=public_metrics`,
        {
            headers: {
                'Authorization': `Bearer ${TWITTER_CONFIG.bearerToken}`
            }
        }
    );

    const result = await response.json();
    return result.data?.public_metrics || {};
}

/**
 * Get user's recent tweets
 */
async function getRecentTweets(userId = 'me', limit = 10) {
    // Get user ID if 'me'
    let actualUserId = userId;
    if (userId === 'me') {
        const userResponse = await fetch(
            'https://api.twitter.com/2/users/me',
            {
                headers: {
                    'Authorization': `Bearer ${TWITTER_CONFIG.bearerToken}`
                }
            }
        );
        const userResult = await userResponse.json();
        actualUserId = userResult.data.id;
    }

    const params = new URLSearchParams({
        max_results: limit.toString(),
        'tweet.fields': 'created_at,public_metrics,text'
    });

    const response = await fetch(
        `https://api.twitter.com/2/users/${actualUserId}/tweets?${params}`,
        {
            headers: {
                'Authorization': `Bearer ${TWITTER_CONFIG.bearerToken}`
            }
        }
    );

    const result = await response.json();
    return result.data || [];
}

/**
 * Generate weekly summary
 */
async function generateSummary() {
    const tweets = await getRecentTweets('me', 20);
    
    const summary = {
        period: 'last_7_days',
        total_tweets: tweets.length,
        engagement: {
            impressions: 0,
            likes: 0,
            retweets: 0,
            replies: 0,
            url_clicks: 0
        }
    };

    // Aggregate metrics
    for (const tweet of tweets) {
        const metrics = tweet.public_metrics || {};
        summary.engagement.impressions += metrics.impression_count || 0;
        summary.engagement.likes += metrics.like_count || 0;
        summary.engagement.retweets += metrics.retweet_count || 0;
        summary.engagement.replies += metrics.reply_count || 0;
        summary.engagement.url_clicks += metrics.url_link_clicks || 0;
    }

    summary.engagement.total = 
        summary.engagement.likes + 
        summary.engagement.retweets + 
        summary.engagement.replies;

    return summary;
}

// MCP Server Protocol Handlers
const handlers = {
    'twitter/authenticate': async () => {
        const success = await validateCredentials();
        return { authenticated: success };
    },

    'twitter/post_tweet': async (params) => {
        const result = await postTweet(params.text, params.options);
        return result;
    },

    'twitter/post_thread': async (params) => {
        const result = await postThread(params.tweets);
        return result;
    },

    'twitter/upload_media': async (params) => {
        const result = await uploadMedia(params.media_url, params.media_type);
        return result;
    },

    'twitter/get_tweet_analytics': async (params) => {
        const metrics = await getTweetAnalytics(params.tweet_id);
        return { metrics };
    },

    'twitter/get_recent_tweets': async (params) => {
        const tweets = await getRecentTweets(params.user_id, params.limit);
        return { tweets };
    },

    'twitter/generate_summary': async () => {
        const summary = await generateSummary();
        return { summary };
    }
};

// Main MCP Server Loop
async function main() {
    console.error('🟡 Twitter/X MCP Server starting...');
    console.error('🟡 Status: PLANNED (Gold Tier - Phase 3)');
    console.error('🟡 Requires: Twitter Developer Account + API Keys');
    
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

    console.error('✅ Twitter/X MCP Server ready (PLANNED)');
}

main().catch(console.error);
