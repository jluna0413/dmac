import * as vscode from 'vscode';
import { logger } from '../core/logger';
import fetch from 'node-fetch';

/**
 * DMac integration configuration
 */
export interface DMacIntegrationConfig {
  enabled: boolean;
  chromaDbUrl: string;
  useSharedChromaDb: boolean;
  agentCommunicationEnabled: boolean;
}

/**
 * DMac configuration manager
 */
export class DMacConfigManager {
  private context: vscode.ExtensionContext;

  constructor(context: vscode.ExtensionContext) {
    this.context = context;
    logger.info('DMac config manager initialized');
  }

  /**
   * Gets the DMac integration configuration
   */
  public getConfig(): DMacIntegrationConfig {
    const config = vscode.workspace.getConfiguration('macoder.dmacIntegration');

    return {
      enabled: config.get<boolean>('enabled', false),
      chromaDbUrl: config.get<string>('chromaDbUrl', 'http://localhost:8000'),
      useSharedChromaDb: config.get<boolean>('useSharedChromaDb', false),
      agentCommunicationEnabled: config.get<boolean>('agentCommunicationEnabled', false)
    };
  }

  /**
   * Updates the DMac integration configuration
   */
  public async updateConfig(config: Partial<DMacIntegrationConfig>): Promise<void> {
    const currentConfig = vscode.workspace.getConfiguration('macoder.dmacIntegration');

    for (const [key, value] of Object.entries(config)) {
      await currentConfig.update(key, value, vscode.ConfigurationTarget.Global);
    }

    logger.info('DMac integration configuration updated');
  }

  /**
   * Checks if DMac is available
   */
  public async isDMacAvailable(): Promise<boolean> {
    try {
      const config = this.getConfig();

      if (!config.enabled) {
        return false;
      }

      // Check if ChromaDB is available
      if (config.useSharedChromaDb) {
        try {
          const response = await fetch(`${config.chromaDbUrl}/api/v1/heartbeat`);
          return response.ok;
        } catch (error) {
          logger.warn('ChromaDB is not available:', error);
          return false;
        }
      }

      return true;
    } catch (error) {
      logger.error('Error checking if DMac is available:', error);
      return false;
    }
  }
}
