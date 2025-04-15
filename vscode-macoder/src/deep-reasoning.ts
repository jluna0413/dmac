import * as vscode from 'vscode';
import { HybridApiClient } from './hybrid-api-client';
import { generateId } from './utils';

/**
 * Reasoning step interface
 */
export interface ReasoningStep {
    id: string;
    content: string;
    type: 'observation' | 'thought' | 'action' | 'conclusion';
    createdAt: number;
}

/**
 * Reasoning chain interface
 */
export interface ReasoningChain {
    id: string;
    topic: string;
    description: string;
    steps: ReasoningStep[];
    conclusion: string;
    createdAt: number;
    updatedAt: number;
}

/**
 * Deep reasoning manager
 */
export class DeepReasoningManager {
    private static instance: DeepReasoningManager;
    private apiClient: HybridApiClient;
    private chains: Map<string, ReasoningChain> = new Map();
    private outputChannel: vscode.OutputChannel;
    private _onChainUpdated: vscode.EventEmitter<ReasoningChain> = new vscode.EventEmitter<ReasoningChain>();
    
    /**
     * Event that fires when a chain is updated
     */
    public readonly onChainUpdated: vscode.Event<ReasoningChain> = this._onChainUpdated.event;

    /**
     * Create a new DeepReasoningManager
     * 
     * @param apiClient The API client
     */
    private constructor(apiClient: HybridApiClient) {
        this.apiClient = apiClient;
        this.outputChannel = vscode.window.createOutputChannel('MaCoder Deep Reasoning');
        
        // Load chains from storage
        this.loadFromStorage();
    }

    /**
     * Get the singleton instance
     * 
     * @param apiClient The API client
     */
    public static getInstance(apiClient: HybridApiClient): DeepReasoningManager {
        if (!DeepReasoningManager.instance) {
            DeepReasoningManager.instance = new DeepReasoningManager(apiClient);
        }
        return DeepReasoningManager.instance;
    }

    /**
     * Load chains from storage
     */
    private loadFromStorage(): void {
        try {
            // Get global state
            const globalState = this.getGlobalState();
            
            // Load chains
            const chains = globalState.chains || [];
            for (const chain of chains) {
                this.chains.set(chain.id, chain);
            }
            
            this.log(`Loaded ${this.chains.size} reasoning chains from storage`);
        } catch (error) {
            this.log(`Error loading from storage: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Save chains to storage
     */
    private saveToStorage(): void {
        try {
            // Create global state
            const globalState = {
                chains: Array.from(this.chains.values())
            };
            
            // Save to global state
            this.setGlobalState(globalState);
            
            this.log(`Saved ${this.chains.size} reasoning chains to storage`);
        } catch (error) {
            this.log(`Error saving to storage: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Get global state
     */
    private getGlobalState(): any {
        try {
            // Get global state from VS Code
            const state = vscode.workspace.getConfiguration('macoder').get('deepReasoning');
            
            return state || { chains: [] };
        } catch (error) {
            this.log(`Error getting global state: ${error instanceof Error ? error.message : String(error)}`);
            return { chains: [] };
        }
    }

    /**
     * Set global state
     * 
     * @param state The state to set
     */
    private setGlobalState(state: any): void {
        try {
            // Set global state in VS Code
            vscode.workspace.getConfiguration('macoder').update('deepReasoning', state, vscode.ConfigurationTarget.Global);
        } catch (error) {
            this.log(`Error setting global state: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Create a new reasoning chain
     * 
     * @param topic The chain topic
     * @param description The chain description
     */
    public createChain(topic: string, description: string): ReasoningChain {
        const chainId = generateId();
        const chain: ReasoningChain = {
            id: chainId,
            topic,
            description,
            steps: [],
            conclusion: '',
            createdAt: Date.now(),
            updatedAt: Date.now()
        };
        
        this.chains.set(chainId, chain);
        this.saveToStorage();
        
        this._onChainUpdated.fire(chain);
        this.log(`Created reasoning chain: ${topic} (${chainId})`);
        
        return chain;
    }

    /**
     * Get a chain by ID
     * 
     * @param chainId The chain ID
     */
    public getChain(chainId: string): ReasoningChain | undefined {
        return this.chains.get(chainId);
    }

    /**
     * Get all chains
     */
    public getAllChains(): ReasoningChain[] {
        return Array.from(this.chains.values());
    }

    /**
     * Update a chain
     * 
     * @param chainId The chain ID
     * @param updates The updates to apply
     */
    public updateChain(chainId: string, updates: Partial<ReasoningChain>): boolean {
        const chain = this.chains.get(chainId);
        if (!chain) {
            return false;
        }
        
        // Apply updates
        Object.assign(chain, updates);
        
        // Update timestamp
        chain.updatedAt = Date.now();
        
        this.saveToStorage();
        this._onChainUpdated.fire(chain);
        
        return true;
    }

    /**
     * Delete a chain
     * 
     * @param chainId The chain ID
     */
    public deleteChain(chainId: string): boolean {
        const chain = this.chains.get(chainId);
        if (!chain) {
            return false;
        }
        
        this.chains.delete(chainId);
        this.saveToStorage();
        
        return true;
    }

    /**
     * Add a step to a chain
     * 
     * @param chainId The chain ID
     * @param content The step content
     * @param type The step type
     */
    public addStep(
        chainId: string,
        content: string,
        type: 'observation' | 'thought' | 'action' | 'conclusion'
    ): ReasoningStep | undefined {
        const chain = this.chains.get(chainId);
        if (!chain) {
            return undefined;
        }
        
        const stepId = generateId();
        const step: ReasoningStep = {
            id: stepId,
            content,
            type,
            createdAt: Date.now()
        };
        
        // Add step to chain
        chain.steps.push(step);
        
        // If it's a conclusion, update the chain conclusion
        if (type === 'conclusion') {
            chain.conclusion = content;
        }
        
        // Update chain
        chain.updatedAt = Date.now();
        
        this.saveToStorage();
        this._onChainUpdated.fire(chain);
        
        return step;
    }

    /**
     * Perform deep reasoning on a problem
     * 
     * @param problem The problem to reason about
     * @param context Additional context
     */
    public async performReasoning(problem: string, context: string = ''): Promise<ReasoningChain> {
        // Create a new chain
        const chain = this.createChain(problem, context);
        
        try {
            // Add the initial observation
            this.addStep(chain.id, `Problem: ${problem}`, 'observation');
            if (context) {
                this.addStep(chain.id, `Context: ${context}`, 'observation');
            }
            
            // Generate initial thoughts
            await this.generateThoughts(chain.id);
            
            // Generate actions
            await this.generateActions(chain.id);
            
            // Generate conclusion
            await this.generateConclusion(chain.id);
            
            return chain;
        } catch (error) {
            this.log(`Error performing reasoning: ${error instanceof Error ? error.message : String(error)}`);
            this.addStep(chain.id, `Error: ${error instanceof Error ? error.message : String(error)}`, 'observation');
            return chain;
        }
    }

    /**
     * Generate thoughts for a chain
     * 
     * @param chainId The chain ID
     */
    private async generateThoughts(chainId: string): Promise<void> {
        const chain = this.chains.get(chainId);
        if (!chain) {
            throw new Error('Chain not found');
        }
        
        // Get the problem and context
        const problem = chain.topic;
        const context = chain.description;
        
        // Generate thoughts using the API client
        const response = await this.apiClient.generateCode(
            `I need to think deeply about the following problem:
            
            ${problem}
            
            ${context ? `Additional context: ${context}` : ''}
            
            Generate a series of thoughts that analyze this problem from multiple angles. Consider:
            1. What are the key aspects of this problem?
            2. What are potential approaches to solving it?
            3. What are the constraints and requirements?
            4. What are potential challenges or edge cases?
            5. What are the trade-offs between different approaches?
            
            Format your response as a JSON array of thought objects, each with a "content" field.
            Return only the JSON array without any explanation or markdown formatting.`,
            'json'
        );
        
        if (!response.success) {
            throw new Error('Failed to generate thoughts');
        }
        
        try {
            // Extract JSON from the response
            const jsonMatch = response.code.match(/\[[\s\S]*\]/);
            if (!jsonMatch) {
                throw new Error('No JSON found in response');
            }
            
            const thoughts = JSON.parse(jsonMatch[0]);
            
            // Add thoughts to the chain
            for (const thought of thoughts) {
                this.addStep(chain.id, thought.content, 'thought');
            }
        } catch (error) {
            throw new Error(`Failed to parse generated thoughts: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Generate actions for a chain
     * 
     * @param chainId The chain ID
     */
    private async generateActions(chainId: string): Promise<void> {
        const chain = this.chains.get(chainId);
        if (!chain) {
            throw new Error('Chain not found');
        }
        
        // Get the thoughts
        const thoughts = chain.steps.filter(step => step.type === 'thought').map(step => step.content);
        
        if (thoughts.length === 0) {
            throw new Error('No thoughts to generate actions from');
        }
        
        // Generate actions using the API client
        const response = await this.apiClient.generateCode(
            `Based on the following thoughts about the problem "${chain.topic}":
            
            ${thoughts.map((thought, index) => `${index + 1}. ${thought}`).join('\n')}
            
            Generate a series of concrete actions that could be taken to solve this problem. These should be specific, actionable steps.
            
            Format your response as a JSON array of action objects, each with a "content" field.
            Return only the JSON array without any explanation or markdown formatting.`,
            'json'
        );
        
        if (!response.success) {
            throw new Error('Failed to generate actions');
        }
        
        try {
            // Extract JSON from the response
            const jsonMatch = response.code.match(/\[[\s\S]*\]/);
            if (!jsonMatch) {
                throw new Error('No JSON found in response');
            }
            
            const actions = JSON.parse(jsonMatch[0]);
            
            // Add actions to the chain
            for (const action of actions) {
                this.addStep(chain.id, action.content, 'action');
            }
        } catch (error) {
            throw new Error(`Failed to parse generated actions: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Generate a conclusion for a chain
     * 
     * @param chainId The chain ID
     */
    private async generateConclusion(chainId: string): Promise<void> {
        const chain = this.chains.get(chainId);
        if (!chain) {
            throw new Error('Chain not found');
        }
        
        // Get the thoughts and actions
        const thoughts = chain.steps.filter(step => step.type === 'thought').map(step => step.content);
        const actions = chain.steps.filter(step => step.type === 'action').map(step => step.content);
        
        if (thoughts.length === 0 || actions.length === 0) {
            throw new Error('Not enough steps to generate a conclusion');
        }
        
        // Generate conclusion using the API client
        const response = await this.apiClient.generateCode(
            `Based on the following analysis of the problem "${chain.topic}":
            
            Thoughts:
            ${thoughts.map((thought, index) => `${index + 1}. ${thought}`).join('\n')}
            
            Actions:
            ${actions.map((action, index) => `${index + 1}. ${action}`).join('\n')}
            
            Generate a comprehensive conclusion that summarizes the key insights, recommended approach, and next steps.
            
            Return only the conclusion text without any explanation or markdown formatting.`,
            'text'
        );
        
        if (!response.success) {
            throw new Error('Failed to generate conclusion');
        }
        
        // Add conclusion to the chain
        this.addStep(chain.id, response.code, 'conclusion');
    }

    /**
     * Log a message to the output channel
     * 
     * @param message The message to log
     */
    private log(message: string): void {
        const timestamp = new Date().toISOString();
        this.outputChannel.appendLine(`[${timestamp}] ${message}`);
    }

    /**
     * Dispose the deep reasoning manager
     */
    public dispose(): void {
        this.outputChannel.dispose();
        this._onChainUpdated.dispose();
    }
}
