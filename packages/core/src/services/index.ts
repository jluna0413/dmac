/**
 * Core services
 */

// Service interfaces
export interface ModelService {
  getModels(): Promise<any[]>;
  getModel(id: string): Promise<any>;
}

export interface AuthService {
  login(username: string, password: string): Promise<string>;
  logout(): Promise<void>;
  getCurrentUser(): Promise<any>;
}

export interface ConfigService {
  get(key: string): any;
  set(key: string, value: any): void;
}

// Base service implementation
export abstract class BaseService {
  protected config: ConfigService;

  constructor(config: ConfigService) {
    this.config = config;
  }
}
