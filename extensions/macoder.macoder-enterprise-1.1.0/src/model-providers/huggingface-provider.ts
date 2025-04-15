import * as https from 'https';
import { ModelProvider, ModelInfo } from './provider-interface';
import { logger } from '../core/logger';

/**
 * HuggingFace provider
 */
export class HuggingFaceProvider implements ModelProvider {
  public id = 'huggingface';
  public name = 'HuggingFace';
  public description = 'Access models from HuggingFace Hub';
  public supportsLocalModels = false;
  public supportsRemoteModels = true;

  private apiKey: string | null = null;
  private apiUrl = 'https://huggingface.co/api';

  constructor(options: { apiKey?: string } = {}) {
    this.apiKey = options.apiKey || null;

    logger.info('HuggingFace provider initialized');
  }

  /**
   * Initializes the provider
   */
  public async initialize(): Promise<void> {
    // No initialization needed
    logger.info('HuggingFace provider initialized successfully');
  }

  /**
   * Lists available models
   */
  public async listModels(): Promise<ModelInfo[]> {
    try {
      // Get code models from HuggingFace
      const response = await this.makeRequest('/models?filter=text-generation&sort=downloads&direction=-1&limit=20');
      const data = JSON.parse(response);

      // Convert to ModelInfo
      return data.map((model: any) => ({
        id: model.id,
        name: model.id.split('/').pop(),
        provider: this.name,
        size: this.extractModelSize(model.tags),
        description: model.description || 'No description available',
        tags: model.tags || []
      }));
    } catch (error: any) {
      logger.error('Error listing HuggingFace models:', error);
      throw new Error(`Failed to list HuggingFace models: ${error.message}`);
    }
  }

  /**
   * Generates code using HuggingFace
   */
  public async generateCode(prompt: string, options: any = {}): Promise<string> {
    try {
      if (!this.apiKey) {
        throw new Error('API key is required for HuggingFace code generation');
      }

      const model = options.model || 'bigcode/starcoder';

      // Generate code using HuggingFace Inference API
      const response = await this.makeRequest(`/models/${model}`, 'POST', {
        inputs: prompt,
        parameters: {
          max_new_tokens: options.max_tokens || 512,
          temperature: options.temperature || 0.2,
          top_p: options.top_p || 0.95,
          top_k: options.top_k || 40,
          return_full_text: false
        }
      });

      const data = JSON.parse(response);

      return data[0].generated_text;
    } catch (error: any) {
      logger.error('Error generating code with HuggingFace:', error);
      throw new Error(`Failed to generate code with HuggingFace: ${error.message}`);
    }
  }

  /**
   * Disposes the provider
   */
  public async dispose(): Promise<void> {
    // Nothing to dispose
  }

  /**
   * Makes an HTTP request to HuggingFace
   */
  private makeRequest(
    path: string,
    method: string = 'GET',
    body: any = null
  ): Promise<string> {
    return new Promise((resolve, reject) => {
      const url = new URL(path, this.apiUrl);

      const options: https.RequestOptions = {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...(this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {})
        }
      };

      const req = https.request(url, options, res => {
        let data = '';

        res.on('data', chunk => {
          data += chunk;
        });

        res.on('end', () => {
          if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) {
            resolve(data);
          } else {
            reject(new Error(`HTTP error ${res.statusCode}: ${data}`));
          }
        });
      });

      req.on('error', error => {
        reject(error);
      });

      if (body) {
        req.write(JSON.stringify(body));
      }

      req.end();
    });
  }

  /**
   * Extracts model size from tags
   */
  private extractModelSize(tags: string[]): string {
    if (!tags || tags.length === 0) {
      return 'Unknown';
    }

    // Look for size tags like "1b", "7b", "13b", etc.
    const sizeTag = tags.find(tag => /^\d+b$/i.test(tag));

    if (sizeTag) {
      return sizeTag.toUpperCase();
    }

    return 'Unknown';
  }
}
