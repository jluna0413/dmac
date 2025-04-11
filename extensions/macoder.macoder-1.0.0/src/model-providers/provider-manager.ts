import * as vscode from 'vscode';
import { ModelProvider, ModelInfo } from './provider-interface';
import { logger } from '../core/logger';

/**
 * Provider Manager
 */
export class ProviderManager implements vscode.Disposable {
  private providers: Map<string, ModelProvider> = new Map();
  private activeProvider: ModelProvider | null = null;
  private activeModel: ModelInfo | null = null;
  
  constructor() {
    logger.info('Provider Manager initialized');
  }
  
  /**
   * Registers a provider
   */
  public registerProvider(provider: ModelProvider): void {
    if (this.providers.has(provider.id)) {
      throw new Error(`Provider ${provider.id} is already registered`);
    }
    
    this.providers.set(provider.id, provider);
    logger.info(`Provider ${provider.name} (${provider.id}) registered`);
  }
  
  /**
   * Unregisters a provider
   */
  public unregisterProvider(providerId: string): boolean {
    const provider = this.providers.get(providerId);
    
    if (!provider) {
      return false;
    }
    
    // If this is the active provider, clear it
    if (this.activeProvider === provider) {
      this.activeProvider = null;
      this.activeModel = null;
    }
    
    // Remove from providers map
    this.providers.delete(providerId);
    
    logger.info(`Provider ${provider.name} (${providerId}) unregistered`);
    
    return true;
  }
  
  /**
   * Gets all registered providers
   */
  public getProviders(): ModelProvider[] {
    return Array.from(this.providers.values());
  }
  
  /**
   * Gets a provider by ID
   */
  public getProvider(providerId: string): ModelProvider | undefined {
    return this.providers.get(providerId);
  }
  
  /**
   * Sets the active provider and model
   */
  public async setActiveProvider(
    providerId: string,
    modelId: string
  ): Promise<void> {
    const provider = this.providers.get(providerId);
    
    if (!provider) {
      throw new Error(`Provider ${providerId} not found`);
    }
    
    // Get models from provider
    const models = await provider.listModels();
    
    // Find the model
    const model = models.find(m => m.id === modelId);
    
    if (!model) {
      throw new Error(`Model ${modelId} not found in provider ${providerId}`);
    }
    
    // Set active provider and model
    this.activeProvider = provider;
    this.activeModel = model;
    
    logger.info(`Active provider set to ${provider.name} (${providerId}) with model ${model.name} (${modelId})`);
  }
  
  /**
   * Gets the active provider and model
   */
  public getActiveProvider(): { provider: ModelProvider; model: ModelInfo } | null {
    if (!this.activeProvider || !this.activeModel) {
      return null;
    }
    
    return {
      provider: this.activeProvider,
      model: this.activeModel
    };
  }
  
  /**
   * Generates code using the active provider
   */
  public async generateCode(prompt: string, options?: any): Promise<string> {
    if (!this.activeProvider) {
      throw new Error('No active provider set');
    }
    
    return this.activeProvider.generateCode(prompt, options);
  }
  
  /**
   * Lists all available models from all providers
   */
  public async listAllModels(): Promise<ModelInfo[]> {
    const allModels: ModelInfo[] = [];
    
    for (const provider of this.providers.values()) {
      try {
        const models = await provider.listModels();
        allModels.push(...models);
      } catch (error) {
        logger.error(`Error listing models from provider ${provider.name}:`, error);
      }
    }
    
    return allModels;
  }
  
  /**
   * Disposes all providers
   */
  public async dispose(): Promise<void> {
    for (const provider of this.providers.values()) {
      try {
        await provider.dispose();
      } catch (error) {
        logger.error(`Error disposing provider ${provider.name}:`, error);
      }
    }
    
    this.providers.clear();
    this.activeProvider = null;
    this.activeModel = null;
  }
}
