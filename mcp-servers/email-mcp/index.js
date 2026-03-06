#!/usr/bin/env node
/**
 * Email MCP Server
 * Allows Claude Code to send emails via Gmail API
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { google } from 'googleapis';
import { promises as fs } from 'fs';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Token path - same as Gmail Watcher for shared authentication
const TOKEN_PATH = join(__dirname, '..', '..', 'token.json');
const CREDENTIALS_PATH = join(__dirname, '..', '..', 'credentials.json');

let oauth2Client;

/**
 * Load OAuth2 credentials
 */
async function loadCredentials() {
  try {
    const content = await readFile(CREDENTIALS_PATH, 'utf8');
    const credentials = JSON.parse(content);

    oauth2Client = new google.auth.OAuth2(
      credentials.installed.client_id,
      credentials.installed.client_secret,
      credentials.installed.redirect_uris[0]
    );

    return true;
  } catch (error) {
    console.error('Failed to load credentials:', error.message);
    console.error(`Expected credentials at: ${CREDENTIALS_PATH}`);
    return false;
  }
}

/**
 * Get authorized OAuth2 client
 */
async function getAuthorizedClient() {
  try {
    const tokenContent = await readFile(TOKEN_PATH, 'utf8');
    const token = JSON.parse(tokenContent);
    oauth2Client.setCredentials(token);
    return oauth2Client;
  } catch (error) {
    console.error('Token not found or invalid. Please run: python watchers/gmail_watcher.py auth');
    throw error;
  }
}

/**
 * Send email via Gmail API
 */
async function sendEmail(to, subject, body, cc = null, attachments = []) {
  const auth = await getAuthorizedClient();
  const gmail = google.gmail({ version: 'v1', auth });

  // Create email message
  let message = [
    `To: ${to}\r\n`,
    `Subject: ${subject}\r\n`,
    'Content-Type: text/plain; charset="UTF-8"\r\n\r\n',
    body,
  ].join('');

  if (cc) {
    message = message.replace(`To: ${to}\r\n`, `To: ${to}\r\nCc: ${cc}\r\n`);
  }

  const encodedMessage = Buffer.from(message).toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');

  try {
    const result = await gmail.users.messages.send({
      userId: 'me',
      requestBody: {
        raw: encodedMessage,
      },
    });

    return {
      success: true,
      messageId: result.data.id,
      threadId: result.data.threadId,
    };
  } catch (error) {
    console.error('Error sending email:', error.message);
    throw error;
  }
}

/**
 * Create draft email
 */
async function createDraft(to, subject, body, cc = null) {
  const auth = await getAuthorizedClient();
  const gmail = google.gmail({ version: 'v1', auth });
  
  const message = [
    `To: ${to}\r\n`,
    `Subject: ${subject}\r\n`,
    'Content-Type: text/plain; charset="UTF-8"\r\n\r\n',
    body,
  ].join('');
  
  if (cc) {
    message.replace(`To: ${to}\r\n`, `To: ${to}\r\nCc: ${cc}\r\n`);
  }
  
  const encodedMessage = Buffer.from(message).toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
  
  try {
    const result = await gmail.users.drafts.create({
      userId: 'me',
      requestBody: {
        message: {
          raw: encodedMessage,
        },
      },
    });
    
    return {
      success: true,
      draftId: result.data.id,
    };
  } catch (error) {
    console.error('Error creating draft:', error.message);
    throw error;
  }
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
        description: 'Send an email via Gmail. Requires prior human approval.',
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
            cc: {
              type: 'string',
              description: 'CC recipient (optional)',
            },
          },
          required: ['to', 'subject', 'body'],
        },
      },
      {
        name: 'create_draft_email',
        description: 'Create a draft email (safer alternative to direct send)',
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
            cc: {
              type: 'string',
              description: 'CC recipient (optional)',
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
      const result = await sendEmail(
        args.to,
        args.subject,
        args.body,
        args.cc
      );
      
      return {
        content: [
          {
            type: 'text',
            text: `Email sent successfully! Message ID: ${result.messageId}`,
          },
        ],
      };
    } else if (name === 'create_draft_email') {
      const result = await createDraft(
        args.to,
        args.subject,
        args.body,
        args.cc
      );
      
      return {
        content: [
          {
            type: 'text',
            text: `Draft email created successfully! Draft ID: ${result.draftId}`,
          },
        ],
      };
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
  
  const credentialsLoaded = await loadCredentials();
  if (!credentialsLoaded) {
    console.error('Failed to load credentials. Please ensure credentials.json is in the watchers/ folder.');
    process.exit(1);
  }
  
  console.error('Credentials loaded successfully');
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  console.error('Email MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
