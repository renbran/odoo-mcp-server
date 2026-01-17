#!/usr/bin/env node
/**
 * Commission_AX Backend Inspector - Node.js version
 * Direct Odoo backend access for module management via MCP
 */

import * as fs from 'fs';
import * as path from 'path';
import { OdooClient } from './dist/odoo-client.js';

const ODOO_URL = process.env.ODOO_URL || 'https://erp.sgctech.ai';
const ODOO_DB = process.env.ODOO_DB || 'commission_ax';
const ODOO_USERNAME = process.env.ODOO_USERNAME || 'info@scholarixglobal.com';
const ODOO_PASSWORD = process.env.ODOO_PASSWORD || '123456';

interface ModuleInfo {
  id: number;
  name: string;
  shortdesc: string;
  state: string;
  installed_version?: string;
  latest_version?: string;
  description?: string;
  author?: string;
  category_id?: [number, string];
  dependencies_id?: [number, string][];
  installable?: boolean;
  auto_install?: boolean;
  license?: string;
}

interface ModuleSummary {
  name: string;
  state: string;
  version: string;
  description: string;
  dependencies: string;
  category: string;
  installable: boolean;
}

class CommissionAXInspector {
  private client: OdooClient;
  private connected: boolean = false;

  constructor() {
    this.client = new OdooClient({
      url: ODOO_URL,
      database: ODOO_DB,
      username: ODOO_USERNAME,
      password: ODOO_PASSWORD,
    });
  }

  async connect(): Promise<void> {
    try {
      await this.client.authenticate();
      this.connected = true;
      console.log('✅ Connected to commission_ax database');
    } catch (error) {
      console.error('❌ Connection failed:', error);
      throw error;
    }
  }

  async listModules(state?: string): Promise<ModuleSummary[]> {
    if (!this.connected) await this.connect();

    console.log('\n🔍 Fetching modules from commission_ax database...\n');

    const domain = state ? [['state', '=', state]] : [];

    try {
      const modules = await this.client.searchRead<ModuleInfo>(
        'ir.module.module',
        domain,
        {
          fields: [
            'id',
            'name',
            'shortdesc',
            'state',
            'installed_version',
            'latest_version',
            'description',
            'author',
            'category_id',
            'dependencies_id',
            'installable',
            'auto_install',
            'license',
          ],
          limit: 0,
        }
      );

      return modules.map((m) => ({
        name: m.name,
        state: m.state,
        version: m.installed_version || m.latest_version || 'unknown',
        description: m.description || '',
        dependencies: m.dependencies_id ? m.dependencies_id.length.toString() : '0',
        category: typeof m.category_id === 'object' ? m.category_id[1] : 'Uncategorized',
        installable: m.installable !== false,
      }));
    } catch (error) {
      console.error('Error fetching modules:', error);
      throw error;
    }
  }

  async getModuleInfo(moduleName: string): Promise<ModuleInfo | null> {
    if (!this.connected) await this.connect();

    console.log(`\n📋 Getting details for module: ${moduleName}\n`);

    try {
      const modules = await this.client.searchRead<ModuleInfo>(
        'ir.module.module',
        [['name', '=', moduleName]],
        {
          fields: [
            'id',
            'name',
            'shortdesc',
            'state',
            'installed_version',
            'latest_version',
            'description',
            'author',
            'category_id',
            'dependencies_id',
            'installable',
            'auto_install',
            'license',
          ],
          limit: 1,
        }
      );

      return modules.length > 0 ? modules[0] : null;
    } catch (error) {
      console.error('Error fetching module info:', error);
      throw error;
    }
  }

  async checkDependencies(moduleName: string): Promise<void> {
    if (!this.connected) await this.connect();

    console.log(`\n🔗 Checking dependencies for: ${moduleName}\n`);

    try {
      const module = await this.getModuleInfo(moduleName);
      if (!module) {
        console.log('❌ Module not found');
        return;
      }

      if (!module.dependencies_id || module.dependencies_id.length === 0) {
        console.log('✅ No dependencies required');
        return;
      }

      console.log(`Dependencies (${module.dependencies_id.length}):\n`);

      const depIds = module.dependencies_id.map((d) => (typeof d === 'object' ? d[0] : d));
      const dependencies = await this.client.read<ModuleInfo>(
        'ir.module.module',
        depIds,
        { fields: ['name', 'state'] }
      );

      let allInstalled = true;
      for (const dep of dependencies) {
        const status = dep.state === 'installed' ? '✅' : '❌';
        console.log(`   ${status} ${dep.name.padEnd(30)} [${dep.state}]`);
        if (dep.state !== 'installed') allInstalled = false;
      }

      console.log(`\n   All dependencies installed: ${allInstalled ? 'YES' : 'NO'}`);
    } catch (error) {
      console.error('Error checking dependencies:', error);
      throw error;
    }
  }

  async installModule(moduleName: string): Promise<void> {
    if (!this.connected) await this.connect();

    console.log(`\n🚀 Installing module: ${moduleName}\n`);

    try {
      const module = await this.getModuleInfo(moduleName);
      if (!module) {
        console.log('❌ Module not found');
        return;
      }

      if (module.state === 'installed') {
        console.log('ℹ️  Module already installed');
        return;
      }

      if (!module.installable) {
        console.log('❌ Module is not installable');
        return;
      }

      console.log('⏳ Installing... (this may take a moment)');

      // Execute the button_install action
      await this.client.executeKw('ir.module.module', 'button_install', [module.id]);

      console.log(`✅ SUCCESS: ${moduleName} installed successfully`);
    } catch (error) {
      console.error(`❌ Installation failed:`, error);
      throw error;
    }
  }

  async uninstallModule(moduleName: string): Promise<void> {
    if (!this.connected) await this.connect();

    console.log(`\n🗑️  Uninstalling module: ${moduleName}\n`);

    try {
      const module = await this.getModuleInfo(moduleName);
      if (!module) {
        console.log('❌ Module not found');
        return;
      }

      if (module.state !== 'installed') {
        console.log(`ℹ️  Module is not installed (state: ${module.state})`);
        return;
      }

      console.log('⏳ Uninstalling...');

      // Execute the button_uninstall action
      await this.client.executeKw('ir.module.module', 'button_uninstall', [module.id]);

      console.log(`✅ SUCCESS: ${moduleName} uninstalled successfully`);
    } catch (error) {
      console.error(`❌ Uninstallation failed:`, error);
      throw error;
    }
  }

  async suggestInstallations(): Promise<void> {
    if (!this.connected) await this.connect();

    console.log('\n🧠 Analyzing available modules for safe installation...\n');

    try {
      const uninstalled = await this.listModules('uninstalled');
      const installed = await this.listModules('installed');

      const installedNames = new Set(installed.map((m) => m.name));

      // Filter for installable modules with all deps available
      const candidates: ModuleSummary[] = [];

      for (const module of uninstalled) {
        if (!module.installable) continue;

        // Get full info to check dependencies
        const fullInfo = await this.getModuleInfo(module.name);
        if (!fullInfo || !fullInfo.dependencies_id || fullInfo.dependencies_id.length === 0) {
          candidates.push(module);
        } else {
          // Check if all dependencies are available (installed or in candidates)
          const allDepsAvailable = fullInfo.dependencies_id.every((dep) => {
            const depName = typeof dep === 'object' ? dep[1] : dep;
            return installedNames.has(depName) || candidates.some((c) => c.name === depName);
          });

          if (allDepsAvailable) {
            candidates.push(module);
          }
        }
      }

      if (candidates.length === 0) {
        console.log('❌ No suitable modules found for installation');
        return;
      }

      console.log(`✅ Found ${candidates.length} modules ready for installation:\n`);

      for (const module of candidates.slice(0, 10)) {
        console.log(`   • ${module.name:30} - ${module.description.substring(0, 40)}`);
      }

      if (candidates.length > 10) {
        console.log(`\n   ... and ${candidates.length - 10} more`);
      }

      console.log(
        '\nRun "node inspect-backend.ts install <module_name>" to install any of these modules'
      );
    } catch (error) {
      console.error('Error analyzing modules:', error);
      throw error;
    }
  }

  async displayStats(): Promise<void> {
    if (!this.connected) await this.connect();

    console.log('\n📊 Module Statistics\n');

    try {
      const installed = await this.listModules('installed');
      const uninstalled = await this.listModules('uninstalled');
      const broken = await this.listModules('broken');

      console.log(`   ✅ Installed:   ${installed.length}`);
      console.log(`   ⭕ Uninstalled: ${uninstalled.length}`);
      console.log(`   ❌ Broken:      ${broken.length}`);
      console.log(`   📦 Total:       ${installed.length + uninstalled.length + broken.length}\n`);
    } catch (error) {
      console.error('Error getting stats:', error);
      throw error;
    }
  }
}

async function main(): Promise<void> {
  const inspector = new CommissionAXInspector();
  const command = process.argv[2];
  const arg = process.argv[3];

  console.log('\n' + '='.repeat(70));
  console.log('🎓 COMMISSION_AX BACKEND MODULE INSPECTOR');
  console.log('='.repeat(70));

  if (!command) {
    console.log('\nUsage:');
    console.log('  npx tsx inspect-backend-node.ts list [state]');
    console.log('  npx tsx inspect-backend-node.ts info <module_name>');
    console.log('  npx tsx inspect-backend-node.ts deps <module_name>');
    console.log('  npx tsx inspect-backend-node.ts install <module_name>');
    console.log('  npx tsx inspect-backend-node.ts uninstall <module_name>');
    console.log('  npx tsx inspect-backend-node.ts suggest');
    console.log('  npx tsx inspect-backend-node.ts stats');
    console.log('\nExamples:');
    console.log('  npx tsx inspect-backend-node.ts list');
    console.log('  npx tsx inspect-backend-node.ts list uninstalled');
    console.log('  npx tsx inspect-backend-node.ts info sale');
    console.log('  npx tsx inspect-backend-node.ts deps sale_commission');
    console.log('  npx tsx inspect-backend-node.ts suggest\n');
    return;
  }

  try {
    switch (command) {
      case 'list': {
        const modules = await inspector.listModules(arg);
        console.log(`\n📦 Found ${modules.length} modules:\n`);
        for (const m of modules) {
          const status = m.state === 'installed' ? '✅' : m.state === 'uninstalled' ? '⭕' : '❌';
          console.log(`${status} ${m.name.padEnd(30)} v${m.version.padEnd(10)} [${m.state}]`);
          if (m.description) {
            console.log(`   ${m.description.substring(0, 60)}`);
          }
          if (m.dependencies !== '0') {
            console.log(`   Deps: ${m.dependencies}`);
          }
          console.log();
        }
        break;
      }

      case 'info': {
        if (!arg) {
          console.log('ERROR: Module name required');
          return;
        }
        const info = await inspector.getModuleInfo(arg);
        if (!info) {
          console.log('❌ Module not found');
          return;
        }
        console.log(`\n📋 Module: ${info.shortdesc}`);
        console.log(`   Name: ${info.name}`);
        console.log(`   State: ${info.state}`);
        console.log(`   Version: ${info.installed_version || info.latest_version}`);
        console.log(`   Author: ${info.author || 'Unknown'}`);
        console.log(
          `   Category: ${typeof info.category_id === 'object' ? info.category_id[1] : 'Uncategorized'}`
        );
        console.log(`   Installable: ${info.installable !== false ? 'Yes' : 'No'}`);
        console.log(`   Auto Install: ${info.auto_install ? 'Yes' : 'No'}`);
        if (info.dependencies_id && info.dependencies_id.length > 0) {
          const deps = info.dependencies_id.map((d) => (typeof d === 'object' ? d[1] : d));
          console.log(`   Dependencies: ${deps.join(', ')}`);
        }
        if (info.description) {
          console.log(`\n   Description:\n   ${info.description}`);
        }
        console.log();
        break;
      }

      case 'deps': {
        if (!arg) {
          console.log('ERROR: Module name required');
          return;
        }
        await inspector.checkDependencies(arg);
        break;
      }

      case 'install': {
        if (!arg) {
          console.log('ERROR: Module name required');
          return;
        }
        await inspector.installModule(arg);
        break;
      }

      case 'uninstall': {
        if (!arg) {
          console.log('ERROR: Module name required');
          return;
        }
        await inspector.uninstallModule(arg);
        break;
      }

      case 'suggest': {
        await inspector.suggestInstallations();
        break;
      }

      case 'stats': {
        await inspector.displayStats();
        break;
      }

      default:
        console.log(`ERROR: Unknown command: ${command}`);
    }
  } catch (error) {
    console.error('\n❌ Error:', error);
    process.exit(1);
  }
}

main();
