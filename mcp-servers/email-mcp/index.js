#!/usr/bin/env node
/**
 * Email MCP Server
 * Allows sending emails via Gmail API using gmail_watcher.py
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

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = join(__dirname, '..', '..');
const WATCHERS_DIR = join(PROJECT_ROOT, 'watchers');
const GMAIL_WATCHER = join(WATCHERS_DIR, 'gmail_watcher.py');

/**
 * Execute Python script and get result
 */
async function runPythonScript(code) {
  return new Promise((resolve, reject) => {
    const python = spawn('python', ['-c', code], {
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
 * Send email using gmail_watcher directly
 */
async function sendEmail(to, subject, body) {
  const pythonCode = `
from gmail_watcher import GmailWatcher
import json
watcher = GmailWatcher('.')
result = watcher.send_email('${to}', '${subject}', '${body}')
print(json.dumps(result))
`;
  return await runPythonScript(pythonCode);
}

// MCP Server instance
const server = new Server(
  {
    name: 'email-mcp-server',
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
        name: 'send_email',
        description: 'Send an email via Gmail. Requires prior authentication.',
        inputSchema: {
          type: 'object',
          properties: {
            to: {
              type: 'string',
              description: 'Recipient email address',
            },
            subject: {
              type: 'string',
              description: 'Email subject',
            },
            body: {
              type: 'string',
              description: 'Email body text',
            },
          },
          required: ['to', 'subject', 'body'],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === 'send_email') {
      const result = await sendEmail(args.to, args.subject, args.body);

      if (result.success) {
        return {
          content: [
            {
              type: 'text',
              text: `Email sent successfully! Message ID: ${result.message_id}`,
            },
          ],
        };
      } else {
        throw new Error(result.error || 'Failed to send email');
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
  console.error('Email MCP Server starting...');

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('Email MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
