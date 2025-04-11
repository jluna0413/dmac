import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { Plugin, PluginMetadata } from './plugin-interface';
import { logger } from '../core/logger';

/**
 * Plugin Manager
 */
export class PluginManager implements vscode.Disposable {
  private plugins: Map<string, Plugin> = new Map();
  private context: vscode.ExtensionContext;
  
  constructor(context: vscode.ExtensionContext) {
    this.context = context;
    logger.info('Plugin Manager initialized');
  }
  
  /**
   * Discovers plugins in a directory
   */
  public async discoverPlugins(pluginsPath: string): Promise<void> {
    try {
      logger.info(`Discovering plugins in ${pluginsPath}`);
      
      // Check if directory exists
      if (!fs.existsSync(pluginsPath)) {
        logger.info(`Plugins directory ${pluginsPath} does not exist`);
        return;
      }
      
      // Get plugin directories
      const entries = await fs.promises.readdir(pluginsPath, { withFileTypes: true });
      const pluginDirs = entries.filter(entry => entry.isDirectory());
      
      logger.info(`Found ${pluginDirs.length} potential plugin directories`);
      
      // Load each plugin
      for (const dir of pluginDirs) {
        const pluginDir = path.join(pluginsPath, dir.name);
        await this.loadPlugin(pluginDir);
      }
      
      logger.info(`Loaded ${this.plugins.size} plugins`);
    } catch (error) {
      logger.error(`Error discovering plugins in ${pluginsPath}:`, error);
      throw error;
    }
  }
  
  /**
   * Loads a plugin from a directory
   */
  private async loadPlugin(pluginDir: string): Promise<void> {
    try {
      logger.info(`Loading plugin from ${pluginDir}`);
      
      // Check for package.json
      const packageJsonPath = path.join(pluginDir, 'package.json');
      
      if (!fs.existsSync(packageJsonPath)) {
        logger.warn(`No package.json found in ${pluginDir}`);
        return;
      }
      
      // Read package.json
      const packageJson = JSON.parse(await fs.promises.readFile(packageJsonPath, 'utf8'));
      
      // Check if it's a valid plugin
      if (!this.isValidPluginPackage(packageJson)) {
        logger.warn(`Invalid plugin package in ${pluginDir}`);
        return;
      }
      
      // Create plugin metadata
      const metadata: PluginMetadata = {
        id: packageJson.name,
        name: packageJson.displayName || packageJson.name,
        description: packageJson.description || '',
        version: packageJson.version,
        author: packageJson.author,
        repository: typeof packageJson.repository === 'object' ? packageJson.repository.url : packageJson.repository,
        dependencies: packageJson.dependencies ? Object.keys(packageJson.dependencies) : [],
        main: packageJson.main
      };
      
      // Load plugin module
      const mainPath = path.join(pluginDir, metadata.main);
      
      if (!fs.existsSync(mainPath)) {
        logger.warn(`Main file ${mainPath} not found for plugin ${metadata.id}`);
        return;
      }
      
      // Import plugin module
      const pluginModule = require(mainPath);
      
      // Check if plugin exports a Plugin class
      if (!pluginModule.default && !pluginModule.Plugin) {
        logger.warn(`No Plugin class exported from ${mainPath}`);
        return;
      }
      
      // Create plugin instance
      const PluginClass = pluginModule.default || pluginModule.Plugin;
      const plugin: Plugin = new PluginClass();
      
      // Validate plugin
      if (!this.isValidPlugin(plugin)) {
        logger.warn(`Invalid plugin instance for ${metadata.id}`);
        return;
      }
      
      // Check if plugin is already registered
      if (this.plugins.has(plugin.id)) {
        logger.warn(`Plugin ${plugin.id} is already registered`);
        return;
      }
      
      // Activate plugin
      plugin.activate(this.context);
      
      // Register plugin
      this.plugins.set(plugin.id, plugin);
      
      logger.info(`Loaded plugin: ${plugin.name} (${plugin.id}) v${plugin.version}`);
    } catch (error) {
      logger.error(`Error loading plugin from ${pluginDir}:`, error);
    }
  }
  
  /**
   * Checks if a package.json is a valid plugin package
   */
  private isValidPluginPackage(packageJson: any): boolean {
    return (
      packageJson &&
      typeof packageJson.name === 'string' &&
      typeof packageJson.version === 'string' &&
      typeof packageJson.main === 'string' &&
      packageJson.name.startsWith('macoder-plugin-')
    );
  }
  
  /**
   * Checks if a plugin is valid
   */
  private isValidPlugin(plugin: any): boolean {
    return (
      plugin &&
      typeof plugin.id === 'string' &&
      typeof plugin.name === 'string' &&
      typeof plugin.description === 'string' &&
      typeof plugin.version === 'string' &&
      typeof plugin.activate === 'function' &&
      typeof plugin.deactivate === 'function'
    );
  }
  
  /**
   * Gets all registered plugins
   */
  public getPlugins(): Plugin[] {
    return Array.from(this.plugins.values());
  }
  
  /**
   * Gets a plugin by ID
   */
  public getPlugin(pluginId: string): Plugin | undefined {
    return this.plugins.get(pluginId);
  }
  
  /**
   * Disposes all plugins
   */
  public dispose(): void {
    try {
      // Deactivate all plugins
      for (const plugin of this.plugins.values()) {
        try {
          plugin.deactivate();
        } catch (error) {
          logger.error(`Error deactivating plugin ${plugin.id}:`, error);
        }
      }
      
      // Clear plugins
      this.plugins.clear();
      
      logger.info('Plugin Manager disposed');
    } catch (error) {
      logger.error('Error disposing Plugin Manager:', error);
    }
  }
}
