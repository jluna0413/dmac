import { DMacConfigManager } from './config';
import { logger } from '../core/logger';
import fetch from 'node-fetch';

/**
 * ChromaDB collection
 */
export interface ChromaCollection {
  id: string;
  name: string;
  metadata: Record<string, any>;
}

/**
 * ChromaDB embedding
 */
export interface ChromaEmbedding {
  id: string;
  embedding: number[];
  metadata: Record<string, any>;
  document: string;
}

/**
 * ChromaDB client
 */
export class ChromaClient {
  private configManager: DMacConfigManager;
  private baseUrl: string;

  constructor(configManager: DMacConfigManager) {
    this.configManager = configManager;
    const config = configManager.getConfig();
    this.baseUrl = config.chromaDbUrl;

    logger.info(`ChromaDB client initialized with base URL: ${this.baseUrl}`);
  }

  /**
   * Lists all collections
   */
  public async listCollections(): Promise<ChromaCollection[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/collections`);

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}: ${await response.text()}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      logger.error('Error listing ChromaDB collections:', error);
      throw error;
    }
  }

  /**
   * Creates a collection
   */
  public async createCollection(name: string, metadata: Record<string, any> = {}): Promise<ChromaCollection> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/collections`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name,
          metadata
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}: ${await response.text()}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      logger.error(`Error creating ChromaDB collection ${name}:`, error);
      throw error;
    }
  }

  /**
   * Gets a collection
   */
  public async getCollection(name: string): Promise<ChromaCollection> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/collections/${name}`);

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}: ${await response.text()}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      logger.error(`Error getting ChromaDB collection ${name}:`, error);
      throw error;
    }
  }

  /**
   * Adds embeddings to a collection
   */
  public async addEmbeddings(
    collectionName: string,
    embeddings: {
      id: string;
      embedding: number[];
      metadata: Record<string, any>;
      document: string;
    }[]
  ): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/collections/${collectionName}/embeddings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          embeddings: embeddings.map(e => e.embedding),
          metadatas: embeddings.map(e => e.metadata),
          documents: embeddings.map(e => e.document),
          ids: embeddings.map(e => e.id)
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}: ${await response.text()}`);
      }
    } catch (error) {
      logger.error(`Error adding embeddings to ChromaDB collection ${collectionName}:`, error);
      throw error;
    }
  }

  /**
   * Queries a collection
   */
  public async queryCollection(
    collectionName: string,
    queryEmbedding: number[],
    nResults: number = 10,
    filter: Record<string, any> = {}
  ): Promise<ChromaEmbedding[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/collections/${collectionName}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          queryEmbedding,
          nResults,
          filter
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}: ${await response.text()}`);
      }

      const data = await response.json();

      // Convert to ChromaEmbedding format
      return data.ids.map((id: string, index: number) => ({
        id,
        embedding: data.embeddings[index],
        metadata: data.metadatas[index],
        document: data.documents[index]
      }));
    } catch (error) {
      logger.error(`Error querying ChromaDB collection ${collectionName}:`, error);
      throw error;
    }
  }
}
