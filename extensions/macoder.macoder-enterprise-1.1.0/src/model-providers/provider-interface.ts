/**
 * Model provider interface
 */
export interface ModelProvider {
  id: string;
  name: string;
  description: string;
  supportsLocalModels: boolean;
  supportsRemoteModels: boolean;
  
  initialize(): Promise<void>;
  listModels(): Promise<ModelInfo[]>;
  generateCode(prompt: string, options?: any): Promise<string>;
  dispose(): Promise<void>;
}

/**
 * Model information
 */
export interface ModelInfo {
  id: string;
  name: string;
  provider: string;
  size: string;
  description: string;
  tags: string[];
  localPath?: string;
}
