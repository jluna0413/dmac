import * as https from 'https';
import * as http from 'http';
import { ModelProvider, ModelInfo } from './provider-interface';
import { logger } from '../core/logger';

/**
 * Ollama model information
 */
interface OllamaModelInfo {
  name: string;
  modified_at: string;
  size: number;
  digest: string;
  details: {
    format: string;
    family: string;
    families: string[];
    parameter_size: string;
    quantization_level: string;
  };
}

/**
 * Ollama provider
 */
export class OllamaProvider implements ModelProvider {
  public id = 'ollama';
  public name = 'Ollama';
  public description = 'Run large language models locally';
  public supportsLocalModels = true;
  public supportsRemoteModels = false;

  private baseUrl: string;

  constructor(options: { baseUrl?: string } = {}) {
    this.baseUrl = options.baseUrl || 'http://localhost:11434';

    logger.info(`Ollama provider initialized with base URL: ${this.baseUrl}`);
  }

  /**
   * Initializes the provider
   */
  public async initialize(): Promise<void> {
    try {
      // Check if Ollama is running
      await this.makeRequest('/api/tags');

      logger.info('Ollama provider initialized successfully');
    } catch (error: any) {
      logger.error('Error initializing Ollama provider:', error);
      throw new Error(`Failed to initialize Ollama provider: ${error.message}`);
    }
  }

  /**
   * Lists available models
   */
  public async listModels(): Promise<ModelInfo[]> {
    try {
      // Get models from Ollama
      const response = await this.makeRequest('/api/tags');
      const data = JSON.parse(response);

      // Convert to ModelInfo
      return data.models.map((model: OllamaModelInfo) => ({
        id: model.name,
        name: this.formatModelName(model.name),
        provider: this.name,
        size: model.details.parameter_size || 'Unknown',
        description: `${model.details.family} model (${model.details.quantization_level})`,
        tags: [
          model.details.family,
          model.details.quantization_level,
          ...model.details.families
        ],
        localPath: this.baseUrl
      }));
    } catch (error: any) {
      logger.error('Error listing Ollama models:', error);
      throw new Error(`Failed to list Ollama models: ${error.message}`);
    }
  }

  /**
   * Generates code using Ollama
   */
  public async generateCode(prompt: string, options: any = {}): Promise<string> {
    try {
      const model = options.model || 'codellama';

      // Generate code using Ollama
      const response = await this.makeRequest('/api/generate', 'POST', {
        model,
        prompt,
        stream: false,
        options: {
          temperature: options.temperature || 0.2,
          top_p: options.top_p || 0.95,
          top_k: options.top_k || 40,
          max_tokens: options.max_tokens || 2048
        }
      });

      const data = JSON.parse(response);

      return data.response;
    } catch (error: any) {
      logger.error('Error generating code with Ollama:', error);
      throw new Error(`Failed to generate code with Ollama: ${error.message}`);
    }
  }

  /**
   * Disposes the provider
   */
  public async dispose(): Promise<void> {
    // Nothing to dispose
  }

  /**
   * Makes an HTTP request to Ollama
   */
  private makeRequest(
    path: string,
    method: string = 'GET',
    body: any = null
  ): Promise<string> {
    return new Promise((resolve, reject) => {
      const url = new URL(path, this.baseUrl);
      const isHttps = url.protocol === 'https:';
      const requestModule = isHttps ? https : http;

      const options: http.RequestOptions = {
        method,
        headers: {
          'Content-Type': 'application/json'
        }
      };

      const req = requestModule.request(url, options, res => {
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
   * Formats a model name
   */
  private formatModelName(name: string): string {
    // Convert "codellama:7b" to "CodeLlama 7B"
    const parts = name.split(':');
    const baseName = parts[0];
    const size = parts[1] || '';

    // Convert camelCase or kebab-case to Title Case
    const formattedName = baseName
      .replace(/([a-z])([A-Z])/g, '$1 $2') // camelCase to space-separated
      .replace(/-/g, ' ') // kebab-case to space-separated
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');

    return size ? `${formattedName} ${size.toUpperCase()}` : formattedName;
  }
}
