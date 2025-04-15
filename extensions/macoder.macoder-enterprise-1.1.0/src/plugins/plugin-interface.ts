import * as vscode from 'vscode';

/**
 * Plugin interface
 */
export interface Plugin {
  id: string;
  name: string;
  description: string;
  version: string;
  
  activate(context: vscode.ExtensionContext): void;
  deactivate(): void;
}

/**
 * Plugin metadata
 */
export interface PluginMetadata {
  id: string;
  name: string;
  description: string;
  version: string;
  author?: string;
  repository?: string;
  dependencies?: string[];
  main: string;
}
