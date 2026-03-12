#!/usr/bin/env node
/**
 * Post to LinkedIn - Test Script
 * Uses browser automation via Python helper
 */

import { spawn } from 'cross-spawn';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.join(__dirname, '../../.env') });

const WATCHERS_DIR = path.join(__dirname, '..', '..', 'watchers');
const HELPER_SCRIPT = path.join(WATCHERS_DIR, 'linkedin_mcp_helper.py');

// Use python from PATH
const PYTHON_CMD = 'python';

const SAMPLE_POST = '🚀 Excited to share an update from Gold Tier AI Employee!\n\nBuilding autonomous AI agents for social media management. This post was created automatically via MCP integration!\n\n#AI #Automation #LinkedIn #GoldTier #Innovation';

async function postToLinkedIn(text) {
    console.log('💼 Posting to LinkedIn...\n');
    console.log('   Content:', text.substring(0, 100) + '...');
    console.log('');

    return new Promise((resolve, reject) => {
        const python = spawn(PYTHON_CMD, [HELPER_SCRIPT, 'create_post', text], {
            cwd: WATCHERS_DIR,
            stdio: ['pipe', 'pipe', 'pipe'],
            env: { ...process.env, PYTHONPATH: WATCHERS_DIR }
        });

        let stdout = '';
        let stderr = '';

        python.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        python.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        python.on('close', (code) => {
            if (code === 0) {
                try {
                    const result = JSON.parse(stdout.trim());
                    resolve(result);
                } catch (e) {
                    resolve({ success: true, output: stdout.trim() });
                }
            } else {
                reject(new Error(`Python exited with code ${code}: ${stderr}`));
            }
        });

        python.on('error', (err) => {
            reject(err);
        });
    });
}

async function main() {
    console.log('🟡 LinkedIn Post Test\n');
    console.log('='.repeat(50) + '\n');
    
    try {
        const result = await postToLinkedIn(SAMPLE_POST);
        
        console.log('\n' + '='.repeat(50));
        if (result.success) {
            console.log('✅ SUCCESS! Post published to LinkedIn');
            console.log('   Result:', JSON.stringify(result, null, 2));
        } else {
            console.log('❌ Failed:', result.error || 'Unknown error');
        }
    } catch (error) {
        console.log('❌ Error:', error.message);
        console.log('   Note: LinkedIn posting requires browser automation and an active session.');
        console.log('   Make sure you have selenium and webdriver installed.');
    }
    console.log('='.repeat(50) + '\n');
}

main();
