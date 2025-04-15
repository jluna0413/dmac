/**
 * Core domain models
 */

// Model interfaces
export interface Model {
  id: string;
  name: string;
  provider: string;
  contextLength: number;
  capabilities: string[];
}

export interface User {
  id: string;
  username: string;
  email: string;
  roles: string[];
}

export interface Project {
  id: string;
  name: string;
  description: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  modelId: string;
  capabilities: string[];
}

// Enums
export enum ModelProvider {
  OLLAMA = 'ollama',
  HUGGINGFACE = 'huggingface',
  OPENAI = 'openai',
  ANTHROPIC = 'anthropic',
}

export enum AgentCapability {
  CODE_GENERATION = 'code_generation',
  CODE_COMPLETION = 'code_completion',
  CODE_EXPLANATION = 'code_explanation',
  CODE_REFACTORING = 'code_refactoring',
  BUG_FINDING = 'bug_finding',
  TEST_GENERATION = 'test_generation',
  DOCUMENTATION = 'documentation',
}

// Type definitions
export type ModelConfig = {
  temperature: number;
  maxTokens: number;
  topP: number;
  frequencyPenalty: number;
  presencePenalty: number;
};
