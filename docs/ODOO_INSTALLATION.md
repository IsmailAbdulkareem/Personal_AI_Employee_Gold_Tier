# Odoo Community Installation Guide

**Gold Tier AI Employee - Accounting Integration**

---

## Overview

This guide walks you through installing Odoo Community Edition for integration with your Gold Tier AI Employee. Odoo provides:
- Invoicing and billing
- Payment tracking
- Financial reporting
- Bank reconciliation
- Customer/vendor management

---

## Prerequisites

### System Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk**: 10GB free space
- **Python**: 3.8 or higher
- **PostgreSQL**: 12 or higher

### Skills Required
- Basic command line knowledge
- Familiarity with database concepts
- Understanding of accounting basics

---

## Installation Options

### Option 1: Local Installation (Recommended for Development)

Install Odoo on your local machine for testing and development.

### Option 2: Cloud VM (Recommended for Production)

Deploy Odoo on a cloud VM for 24/7 availability.

---

## Option 1: Local Installation (Windows)

### Step 1: Download Odoo

1. Go to [Odoo Community Downloads](https://www.odoo.com/page/download)
2. Download the **Windows installer** for Odoo 18 Community Edition
3. Save to `Downloads/odoo_18.latest.exe`

### Step 2: Install Odoo

```bash
# Run the installer
# Double-click odoo_18.latest.exe

# Installation options:
# - Install directory: C:\Program Files\Odoo 18
# - PostgreSQL: Check "Install PostgreSQL" (recommended)
# - Port: 8069 (default)
```

### Step 3: Start Odoo

```bash
# Odoo should start automatically after installation
# Or start manually:
"C:\Program Files\Odoo 18\server\odoo-bin.exe"
```

### Step 4: Access Odoo

Open browser and navigate to:
```
http://localhost:8069
```

### Step 5: Create Database

1. Click **"Create Database"**
2. Fill in:
   - **Master Password**: `admin` (change this!)
   - **Database Name**: `gold_tier_accounting`
   - **Email**: your-email@example.com
   - **Password**: your-admin-password
   - **Language**: English (US)
   - **Country**: Your country
3. Click **"Create Database"**

### Step 6: Install Accounting Apps

1. After database creation, you'll see the Apps menu
2. Search and install:
   - **Invoicing** (account)
   - **Expenses** (hr_expense)
   - **Bank Synchronization** (if available for your country)

---

## Option 1: Local Installation (Linux/Ubuntu)

### Step 1: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Step 3: Create PostgreSQL User

```bash
sudo -u postgres createuser -s odoo18
sudo -u postgres psql -c "ALTER USER odoo18 WITH PASSWORD 'odoo18_password';"
```

### Step 4: Install Dependencies

```bash
sudo apt install git python3-pip build-essential wget nodejs libxslt1-dev \
libzip-dev libldap2-dev libsasl2-dev libjpeg-dev libpng-dev libfreetype6-dev \
libxml2-dev libyaml-dev -y
```

### Step 5: Create Odoo User

```bash
sudo useradd -m -d /opt/odoo18 -U -r -s /bin/bash odoo18
```

### Step 6: Download Odoo

```bash
sudo su - odoo18
git clone https://github.com/odoo/odoo.git --depth 1 --branch 18.0 /opt/odoo18/odoo
exit
```

### Step 7: Create Python Virtual Environment

```bash
sudo python3 -m venv /opt/odoo18/venv
sudo chown -R odoo18:odoo18 /opt/odoo18/venv
```

### Step 8: Install Python Dependencies

```bash
sudo su - odoo18
source /opt/odoo18/venv/bin/activate
pip install -r /opt/odoo18/odoo/requirements.txt
pip install psycopg2-binary pillow reportlab passlib python-stdnum pydot
deactivate
exit
```

### Step 9: Create Odoo Configuration File

```bash
sudo nano /etc/odoo18.conf
```

Add the following:
```ini
[options]
admin_passwd = admin
db_host = localhost
db_port = 5432
db_user = odoo18
db_password = odoo18_password
db_name = gold_tier_accounting
addons_path = /opt/odoo18/odoo/addons
logfile = /var/log/odoo18/odoo.log
log_level = info
xmlrpc_port = 8069
```

### Step 10: Create Log Directory

```bash
sudo mkdir -p /var/log/odoo18
sudo chown odoo18:odoo18 /var/log/odoo18
```

### Step 11: Create Systemd Service

```bash
sudo nano /etc/systemd/system/odoo18.service
```

Add the following:
```ini
[Unit]
Description=Odoo 18
After=network.target postgresql.service

[Service]
Type=simple
User=odoo18
Group=odoo18
ExecStart=/opt/odoo18/venv/bin/python3 /opt/odoo18/odoo/odoo-bin --config=/etc/odoo18.conf
Restart=always

[Install]
WantedBy=multi-user.target
```

### Step 12: Start Odoo Service

```bash
sudo systemctl daemon-reload
sudo systemctl start odoo18
sudo systemctl enable odoo18
sudo systemctl status odoo18
```

### Step 13: Access Odoo

Open browser and navigate to:
```
http://localhost:8069
```

---

## Option 2: Cloud VM Installation

### Step 1: Create Cloud VM

**Oracle Cloud Free Tier** (Recommended):
1. Go to [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
2. Sign up for free account
3. Create VM instance:
   - **Shape**: VM.Standard.A1.Flex (2 OCPU, 12GB RAM - always free)
   - **OS**: Ubuntu 22.04
   - **Storage**: 50GB

**AWS Free Tier**:
1. Go to [AWS Free Tier](https://aws.amazon.com/free/)
2. Launch EC2 instance:
   - **Type**: t2.micro or t3.micro (free tier eligible)
   - **OS**: Ubuntu 22.04
   - **Storage**: 30GB

### Step 2: Configure Firewall

```bash
# Allow HTTP, HTTPS, and Odoo port
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8069/tcp  # Odoo
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Step 3: Install Odoo

Follow the **Linux/Ubuntu installation steps** above.

### Step 4: Configure External Access

Edit Odoo config:
```bash
sudo nano /etc/odoo18.conf
```

Add:
```ini
[options]
; ... existing config ...
proxy_mode = True
```

### Step 5: Access Odoo from Internet

```
http://<your-vm-public-ip>:8069
```

---

## Post-Installation Configuration

### Step 1: Create Company

1. Go to **Settings → Users & Companies → Companies**
2. Click **Create**
3. Fill in:
   - **Company Name**: Your Company Name
   - **Currency**: Your local currency
   - **Address**: Your business address
4. Save

### Step 2: Configure Chart of Accounts

1. Go to **Invoicing → Configuration → Accounting → Chart of Accounts**
2. Odoo pre-configures accounts based on your country
3. Review and customize as needed

### Step 3: Set Up Taxes

1. Go to **Invoicing → Configuration → Accounting → Taxes**
2. Verify tax rates for your country
3. Add any additional taxes required

### Step 4: Configure Bank Accounts

1. Go to **Invoicing → Configuration → Accounting → Bank Accounts**
2. Click **Create**
3. Fill in:
   - **Account Name**: Main Business Account
   - **Account Number**: Your account number
   - **Bank Name**: Your bank name
4. Save

### Step 5: Create Invoice Templates

1. Go to **Invoicing → Configuration → Settings**
2. Under **Invoice Layout**, choose your preferred template
3. Upload your company logo
4. Configure invoice terms and conditions

---

## Generate API Key for MCP Integration

### Step 1: Enable Developer Mode

1. Go to **Settings**
2. Scroll to bottom
3. Click **"Activate the developer mode"**

### Step 2: Generate API Key

1. Go to **Settings → Users & Companies → Users**
2. Click on **Admin** user
3. Go to **API Keys** tab
4. Click **Add**
5. Enter description: `Gold Tier AI Employee MCP`
6. Copy the generated API key
7. **Save this key securely** - you'll need it for MCP configuration

### Step 3: Configure Odoo MCP Server

Create config file:
```bash
nano D:\Documents\GitHub\Personal_AI_Employee_Gold_Tier\config\odoo_config.json
```

Add:
```json
{
  "url": "http://localhost:8069",
  "db": "gold_tier_accounting",
  "username": "admin",
  "password": "your-admin-password",
  "api_key": "your-generated-api-key"
}
```

---

## Testing Odoo Integration

### Step 1: Test Connection

```bash
cd D:\Documents\GitHub\Personal_AI_Employee_Gold_Tier\mcp-servers\odoo-mcp
npm install
node index.js
```

### Step 2: Create Test Invoice

1. Go to **Invoicing → Customers → Invoices**
2. Click **Create**
3. Add a test customer
4. Add invoice line
5. Confirm invoice
6. Verify in Odoo MCP logs

### Step 3: Test MCP Integration

```bash
# Test authentication
node -e "require('./index.js').authenticate()"

# Test invoice creation (via MCP protocol)
```

---

## Troubleshooting

### Odoo Won't Start

```bash
# Check logs
sudo journalctl -u odoo18 -f

# Check PostgreSQL status
sudo systemctl status postgresql

# Check port availability
netstat -tlnp | grep 8069
```

### Can't Access from Browser

```bash
# Check firewall
sudo ufw status

# Check Odoo is listening
sudo netstat -tlnp | grep 8069

# Check config file
sudo nano /etc/odoo18.conf
```

### Database Connection Failed

```bash
# Test PostgreSQL connection
sudo -u postgres psql -d gold_tier_accounting

# Check Odoo user permissions
sudo -u postgres psql -c "\du odoo18"
```

### MCP Server Can't Connect

1. Verify Odoo URL in config
2. Check API key is correct
3. Verify database name
4. Check firewall allows port 8069

---

## Next Steps

After Odoo is installed and configured:

1. ✅ **Configure Odoo MCP Server** - Update `mcp-servers/odoo-mcp/index.js` with credentials
2. ✅ **Test Invoice Creation** - Use MCP server to create test invoice
3. ✅ **Test Payment Recording** - Record a test payment
4. ✅ **Integrate with AI Employee** - Add Odoo actions to approval workflow
5. ✅ **Set Up Bank Feeds** - Connect your bank account for automatic transactions
6. ✅ **Configure Auto-Categorization** - Set up rules for transaction categorization

---

## Security Best Practices

1. **Change default passwords** immediately
2. **Use HTTPS** for production (set up reverse proxy with Nginx)
3. **Regular backups** of PostgreSQL database
4. **Keep Odoo updated** with latest security patches
5. **Limit API key permissions** to minimum required
6. **Don't commit credentials** to git (use .gitignore)

---

## Resources

- [Odoo Documentation](https://www.odoo.com/documentation/18.0/)
- [Odoo Community Forum](https://www.odoo.com/forum/help-1)
- [Odoo GitHub](https://github.com/odoo/odoo)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

*Odoo Installation Guide - Gold Tier AI Employee*
*For support: Check logs and Odoo community forums*
