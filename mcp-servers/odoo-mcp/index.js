#!/usr/bin/env node
/**
 * Odoo MCP Server - Gold Tier
 * 
 * Model Context Protocol server for Odoo Community Edition integration.
 * Provides accounting, invoicing, and financial management capabilities.
 * 
 * Status: PLANNED (Gold Tier - Phase 2)
 */

// Load environment variables
require('dotenv').config();

const fetch = require('node-fetch');

// Configuration from environment variables
const ODOO_CONFIG = {
    url: process.env.ODOO_URL || 'http://localhost:8069',
    db: process.env.ODOO_DB || 'odoo',
    username: process.env.ODOO_USERNAME || 'admin',
    password: process.env.ODOO_PASSWORD || 'admin',
    apiKey: process.env.ODOO_API_KEY || null
};

// State
let authenticated = false;
let uid = null;

/**
 * Authenticate with Odoo
 */
async function authenticate() {
    try {
        const response = await fetch(`${ODOO_CONFIG.url}/jsonrpc`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    service: 'common',
                    method: 'authenticate',
                    args: [
                        ODOO_CONFIG.db,
                        ODOO_CONFIG.username,
                        ODOO_CONFIG.password,
                        {}
                    ]
                },
                id: Math.floor(Math.random() * 1000000)
            })
        });

        const result = await response.json();
        
        if (result.result) {
            authenticated = true;
            uid = result.result;
            console.log(`✅ Odoo authenticated as ${ODOO_CONFIG.username}`);
            return true;
        }
        
        console.error('❌ Odoo authentication failed');
        return false;
    } catch (error) {
        console.error('❌ Odoo authentication error:', error.message);
        return false;
    }
}

/**
 * Execute Odoo JSON-RPC call
 */
async function execute(model, method, args = [], kwargs = {}) {
    if (!authenticated) {
        await authenticate();
    }

    try {
        const response = await fetch(`${ODOO_CONFIG.url}/jsonrpc`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    service: 'object',
                    method: 'execute_kwargs',
                    args: [
                        ODOO_CONFIG.db,
                        uid,
                        ODOO_CONFIG.password,
                        model,
                        method,
                        args,
                        kwargs
                    ]
                },
                id: Math.floor(Math.random() * 1000000)
            })
        });

        const result = await response.json();
        return result.result;
    } catch (error) {
        console.error(`❌ Odoo execute error (${model}.${method}):`, error.message);
        throw error;
    }
}

/**
 * Create invoice in Odoo
 */
async function createInvoice(invoiceData) {
    const invoice = {
        move_type: invoiceData.type || 'out_invoice',
        partner_id: invoiceData.partner_id,
        invoice_date: invoiceData.date || new Date().toISOString().split('T')[0],
        invoice_line_ids: []
    };

    // Add invoice lines
    if (invoiceData.lines) {
        for (const line of invoiceData.lines) {
            invoice.invoice_line_ids.push([0, 0, {
                product_id: line.product_id,
                name: line.name,
                quantity: line.quantity || 1,
                price_unit: line.price_unit,
                tax_ids: line.tax_ids || []
            }]);
        }
    }

    const invoiceId = await execute('account.move', 'create', [invoice]);
    console.log(`✅ Invoice created: ${invoiceId}`);
    return invoiceId;
}

/**
 * Record payment in Odoo
 */
async function recordPayment(paymentData) {
    const payment = {
        partner_id: paymentData.partner_id,
        payment_type: paymentData.type || 'inbound',
        amount: paymentData.amount,
        currency_id: paymentData.currency_id || 1,
        payment_date: paymentData.date || new Date().toISOString().split('T')[0],
        journal_id: paymentData.journal_id
    };

    const paymentId = await execute('account.payment', 'create', [payment]);
    console.log(`✅ Payment recorded: ${paymentId}`);
    return paymentId;
}

/**
 * Generate financial report
 */
async function generateReport(reportType, dateFrom, dateTo) {
    const reportData = await execute('account.report', 'get_report', [
        reportType,
        {
            date_from: dateFrom,
            date_to: dateTo,
            company_id: 1
        }
    ]);
    
    return reportData;
}

/**
 * Search and read records
 */
async function searchRecords(model, domain = [], limit = 80) {
    const ids = await execute(model, 'search', [domain], { limit });
    if (ids && ids.length > 0) {
        return await execute(model, 'read', [ids]);
    }
    return [];
}

// MCP Server Protocol Handlers
const handlers = {
    'odoo/authenticate': async () => {
        const success = await authenticate();
        return { authenticated: success };
    },

    'odoo/create_invoice': async (params) => {
        const invoiceId = await createInvoice(params);
        return { invoice_id: invoiceId, status: 'created' };
    },

    'odoo/record_payment': async (params) => {
        const paymentId = await recordPayment(params);
        return { payment_id: paymentId, status: 'recorded' };
    },

    'odoo/generate_report': async (params) => {
        const report = await generateReport(params.type, params.date_from, params.date_to);
        return { report };
    },

    'odoo/search_invoices': async (params) => {
        const domain = params.domain || [];
        const invoices = await searchRecords('account.move', domain);
        return { invoices };
    },

    'odoo/search_partners': async (params) => {
        const domain = params.domain || [];
        const partners = await searchRecords('res.partner', domain);
        return { partners };
    },

    'odoo/categorize_transaction': async (params) => {
        // Auto-categorization logic based on description patterns
        const patterns = {
            'income': ['payment received', 'invoice paid', 'transfer in'],
            'expense': ['payment sent', 'bill', 'subscription', 'service fee'],
            'transfer': ['transfer', 'internal']
        };

        const description = (params.description || '').toLowerCase();
        
        for (const [category, keywords] of Object.entries(patterns)) {
            if (keywords.some(kw => description.includes(kw))) {
                return { category, confidence: 'high' };
            }
        }

        return { category: 'uncategorized', confidence: 'low' };
    }
};

// Main MCP Server Loop
async function main() {
    console.error('🟡 Odoo MCP Server starting...');
    console.error(`🟡 Odoo URL: ${ODOO_CONFIG.url}`);
    console.error(`🟡 Status: PLANNED (Gold Tier - Phase 2)`);
    
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

    console.error('✅ Odoo MCP Server ready (PLANNED)');
}

main().catch(console.error);
