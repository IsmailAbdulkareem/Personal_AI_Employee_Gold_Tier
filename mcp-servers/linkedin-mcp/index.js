#!/usr/bin/env node
/**
 * LinkedIn MCP Server
 * Allows sending messages, creating posts, and replying via LinkedIn
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { promises as fs } from 'fs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = join(__dirname, '..', '..');
const WATCHERS_DIR = join(PROJECT_ROOT, 'watchers');
const SESSION_DIR = join(WATCHERS_DIR, '.linkedin_session');
const HELPER_SCRIPT = join(WATCHERS_DIR, 'linkedin_mcp_helper.py');

/**
 * Execute Python helper script and get result
 */
async function runPythonHelper(args) {
  return new Promise((resolve, reject) => {
    const python = spawn('python', [HELPER_SCRIPT, ...args], {
      cwd: WATCHERS_DIR,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, PYTHONPATH: WATCHERS_DIR },
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
          resolve(JSON.parse(stdout.trim()));
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

/**
 * Send LinkedIn message
 */
async function sendLinkedinMessage(recipientName, messageText) {
  return await runPythonHelper(['send_message', recipientName, messageText]);
}

/**
 * Create LinkedIn post
 */
async function createLinkedinPost(postText, imagePath = null) {
  const args = ['create_post', postText];
  if (imagePath) args.push(imagePath);
  return await runPythonHelper(args);
}

/**
 * Reply to LinkedIn message
 */
async function replyToLinkedinMessage(messageText) {
  return await runPythonHelper(['reply_to_message', messageText]);
}

// MCP Server instance
const server = new Server(
  {
    name: 'linkedin-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'send_linkedin_message',
        description: 'Send a direct message to a LinkedIn connection. Requires prior login session.',
        inputSchema: {
          type: 'object',
          properties: {
            recipient_name: {
              type: 'string',
              description: 'Name of the LinkedIn connection to message',
            },
            message: {
              type: 'string',
              description: 'Message content to send',
            },
          },
          required: ['recipient_name', 'message'],
        },
      },
      {
        name: 'create_linkedin_post',
        description: 'Create a LinkedIn post. Opens browser with saved session.',
        inputSchema: {
          type: 'object',
          properties: {
            content: {
              type: 'string',
              description: 'Post content text',
            },
            image_path: {
              type: 'string',
              description: 'Optional path to image to attach',
            },
          },
          required: ['content'],
        },
      },
      {
        name: 'reply_to_linkedin_message',
        description: 'Reply to the currently open LinkedIn conversation.',
        inputSchema: {
          type: 'object',
          properties: {
            message: {
              type: 'string',
              description: 'Reply message content',
            },
          },
          required: ['message'],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === 'send_linkedin_message') {
      const result = await sendLinkedinMessage(args.recipient_name, args.message);

      if (result.success) {
        return {
          content: [
            {
              type: 'text',
              text: `LinkedIn message sent successfully to ${args.recipient_name}!`,
            },
          ],
        };
      } else {
        throw new Error(result.error || 'Failed to send message');
      }
    } else if (name === 'create_linkedin_post') {
      const result = await createLinkedinPost(args.content, args.image_path);

      if (result.success) {
        return {
          content: [
            {
              type: 'text',
              text: `LinkedIn post created successfully! Preview: ${result.post_text}`,
            },
          ],
        };
      } else {
        throw new Error(result.error || 'Failed to create post');
      }
    } else if (name === 'reply_to_linkedin_message') {
      const result = await replyToLinkedinMessage(args.message);

      if (result.success) {
        return {
          content: [
            {
              type: 'text',
              text: 'LinkedIn reply sent successfully!',
            },
          ],
        };
      } else {
        throw new Error(result.error || 'Failed to send reply');
      }
    } else {
      throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  console.error('LinkedIn MCP Server starting...');

  // Check if session exists
  try {
    await fs.access(SESSION_DIR);
    console.error(`Session directory found: ${SESSION_DIR}`);
  } catch (error) {
    console.error('Warning: LinkedIn session not found. First run will require login.');
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('LinkedIn MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
