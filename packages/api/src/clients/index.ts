/**
 * API Clients
 */
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

/**
 * Base API client
 */
export class BaseApiClient {
  protected client: AxiosInstance;
  
  /**
   * Creates a new BaseApiClient
   * @param baseURL The base URL for the API
   * @param config Additional Axios configuration
   */
  constructor(baseURL: string, config: AxiosRequestConfig = {}) {
    this.client = axios.create({
      baseURL,
      ...config,
    });
  }
  
  /**
   * Sets the authorization token
   * @param token The authorization token
   */
  setAuthToken(token: string): void {
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }
  
  /**
   * Clears the authorization token
   */
  clearAuthToken(): void {
    delete this.client.defaults.headers.common['Authorization'];
  }
}

/**
 * Model API client
 */
export class ModelApiClient extends BaseApiClient {
  /**
   * Gets all available models
   * @returns A promise that resolves to an array of models
   */
  async getModels() {
    const response = await this.client.get('/models');
    return response.data;
  }
  
  /**
   * Gets a model by ID
   * @param id The model ID
   * @returns A promise that resolves to the model
   */
  async getModel(id: string) {
    const response = await this.client.get(`/models/${id}`);
    return response.data;
  }
  
  /**
   * Generates text using a model
   * @param modelId The model ID
   * @param prompt The prompt
   * @param options Additional options
   * @returns A promise that resolves to the generated text
   */
  async generateText(modelId: string, prompt: string, options = {}) {
    const response = await this.client.post('/generate', {
      model_id: modelId,
      prompt,
      ...options,
    });
    return response.data;
  }
}

/**
 * Ollama API client
 */
export class OllamaApiClient extends BaseApiClient {
  /**
   * Creates a new OllamaApiClient
   * @param baseURL The base URL for the Ollama API
   */
  constructor(baseURL = 'http://localhost:11434') {
    super(baseURL);
  }
  
  /**
   * Gets all available models
   * @returns A promise that resolves to an array of models
   */
  async getModels() {
    const response = await this.client.get('/api/tags');
    return response.data.models;
  }
  
  /**
   * Generates text using a model
   * @param model The model name
   * @param prompt The prompt
   * @param options Additional options
   * @returns A promise that resolves to the generated text
   */
  async generateText(model: string, prompt: string, options = {}) {
    const response = await this.client.post('/api/generate', {
      model,
      prompt,
      ...options,
    });
    return response.data;
  }
}
