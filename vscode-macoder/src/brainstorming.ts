import * as vscode from 'vscode';
import { HybridApiClient } from './hybrid-api-client';
import { generateId } from './utils';

/**
 * Idea interface
 */
export interface Idea {
    id: string;
    content: string;
    category: string;
    tags: string[];
    createdAt: number;
    parentId?: string;
    children?: Idea[];
    connections?: string[];
}

/**
 * Brainstorming session interface
 */
export interface BrainstormingSession {
    id: string;
    topic: string;
    description: string;
    createdAt: number;
    updatedAt: number;
    ideas: Idea[];
}

/**
 * Roadmap item interface
 */
export interface RoadmapItem {
    id: string;
    title: string;
    description: string;
    priority: 'high' | 'medium' | 'low';
    status: 'pending' | 'in_progress' | 'completed';
    dependencies: string[];
    estimatedTime?: string;
    assignee?: string;
    tags: string[];
    children?: RoadmapItem[];
}

/**
 * Roadmap interface
 */
export interface Roadmap {
    id: string;
    title: string;
    description: string;
    createdAt: number;
    updatedAt: number;
    items: RoadmapItem[];
}

/**
 * Brainstorming manager
 */
export class BrainstormingManager {
    private static instance: BrainstormingManager;
    private apiClient: HybridApiClient;
    private sessions: Map<string, BrainstormingSession> = new Map();
    private roadmaps: Map<string, Roadmap> = new Map();
    private outputChannel: vscode.OutputChannel;
    private _onSessionUpdated: vscode.EventEmitter<BrainstormingSession> = new vscode.EventEmitter<BrainstormingSession>();
    private _onRoadmapUpdated: vscode.EventEmitter<Roadmap> = new vscode.EventEmitter<Roadmap>();
    
    /**
     * Event that fires when a session is updated
     */
    public readonly onSessionUpdated: vscode.Event<BrainstormingSession> = this._onSessionUpdated.event;
    
    /**
     * Event that fires when a roadmap is updated
     */
    public readonly onRoadmapUpdated: vscode.Event<Roadmap> = this._onRoadmapUpdated.event;

    /**
     * Create a new BrainstormingManager
     * 
     * @param apiClient The API client
     */
    private constructor(apiClient: HybridApiClient) {
        this.apiClient = apiClient;
        this.outputChannel = vscode.window.createOutputChannel('MaCoder Brainstorming');
        
        // Load sessions and roadmaps from storage
        this.loadFromStorage();
    }

    /**
     * Get the singleton instance
     * 
     * @param apiClient The API client
     */
    public static getInstance(apiClient: HybridApiClient): BrainstormingManager {
        if (!BrainstormingManager.instance) {
            BrainstormingManager.instance = new BrainstormingManager(apiClient);
        }
        return BrainstormingManager.instance;
    }

    /**
     * Load sessions and roadmaps from storage
     */
    private loadFromStorage(): void {
        try {
            // Get global state
            const globalState = this.getGlobalState();
            
            // Load sessions
            const sessions = globalState.sessions || [];
            for (const session of sessions) {
                this.sessions.set(session.id, session);
            }
            
            // Load roadmaps
            const roadmaps = globalState.roadmaps || [];
            for (const roadmap of roadmaps) {
                this.roadmaps.set(roadmap.id, roadmap);
            }
            
            this.log(`Loaded ${this.sessions.size} sessions and ${this.roadmaps.size} roadmaps from storage`);
        } catch (error) {
            this.log(`Error loading from storage: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Save sessions and roadmaps to storage
     */
    private saveToStorage(): void {
        try {
            // Create global state
            const globalState = {
                sessions: Array.from(this.sessions.values()),
                roadmaps: Array.from(this.roadmaps.values())
            };
            
            // Save to global state
            this.setGlobalState(globalState);
            
            this.log(`Saved ${this.sessions.size} sessions and ${this.roadmaps.size} roadmaps to storage`);
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
            const state = vscode.workspace.getConfiguration('macoder').get('brainstorming');
            
            return state || { sessions: [], roadmaps: [] };
        } catch (error) {
            this.log(`Error getting global state: ${error instanceof Error ? error.message : String(error)}`);
            return { sessions: [], roadmaps: [] };
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
            vscode.workspace.getConfiguration('macoder').update('brainstorming', state, vscode.ConfigurationTarget.Global);
        } catch (error) {
            this.log(`Error setting global state: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Create a new brainstorming session
     * 
     * @param topic The session topic
     * @param description The session description
     */
    public createSession(topic: string, description: string): BrainstormingSession {
        const sessionId = generateId();
        const session: BrainstormingSession = {
            id: sessionId,
            topic,
            description,
            createdAt: Date.now(),
            updatedAt: Date.now(),
            ideas: []
        };
        
        this.sessions.set(sessionId, session);
        this.saveToStorage();
        
        this._onSessionUpdated.fire(session);
        this.log(`Created session: ${topic} (${sessionId})`);
        
        return session;
    }

    /**
     * Get a session by ID
     * 
     * @param sessionId The session ID
     */
    public getSession(sessionId: string): BrainstormingSession | undefined {
        return this.sessions.get(sessionId);
    }

    /**
     * Get all sessions
     */
    public getAllSessions(): BrainstormingSession[] {
        return Array.from(this.sessions.values());
    }

    /**
     * Update a session
     * 
     * @param sessionId The session ID
     * @param updates The updates to apply
     */
    public updateSession(sessionId: string, updates: Partial<BrainstormingSession>): boolean {
        const session = this.sessions.get(sessionId);
        if (!session) {
            return false;
        }
        
        // Apply updates
        Object.assign(session, updates);
        
        // Update timestamp
        session.updatedAt = Date.now();
        
        this.saveToStorage();
        this._onSessionUpdated.fire(session);
        
        return true;
    }

    /**
     * Delete a session
     * 
     * @param sessionId The session ID
     */
    public deleteSession(sessionId: string): boolean {
        const session = this.sessions.get(sessionId);
        if (!session) {
            return false;
        }
        
        this.sessions.delete(sessionId);
        this.saveToStorage();
        
        return true;
    }

    /**
     * Add an idea to a session
     * 
     * @param sessionId The session ID
     * @param content The idea content
     * @param category The idea category
     * @param tags The idea tags
     * @param parentId The parent idea ID
     */
    public addIdea(
        sessionId: string,
        content: string,
        category: string = 'general',
        tags: string[] = [],
        parentId?: string
    ): Idea | undefined {
        const session = this.sessions.get(sessionId);
        if (!session) {
            return undefined;
        }
        
        const ideaId = generateId();
        const idea: Idea = {
            id: ideaId,
            content,
            category,
            tags,
            createdAt: Date.now(),
            parentId
        };
        
        // If it's a child idea, add it to the parent
        if (parentId) {
            const parentIdea = this.findIdea(session, parentId);
            if (parentIdea) {
                if (!parentIdea.children) {
                    parentIdea.children = [];
                }
                parentIdea.children.push(idea);
            } else {
                // If parent not found, add as top-level idea
                session.ideas.push(idea);
            }
        } else {
            // Add as top-level idea
            session.ideas.push(idea);
        }
        
        // Update session
        session.updatedAt = Date.now();
        
        this.saveToStorage();
        this._onSessionUpdated.fire(session);
        
        return idea;
    }

    /**
     * Find an idea in a session
     * 
     * @param session The session
     * @param ideaId The idea ID
     */
    private findIdea(session: BrainstormingSession, ideaId: string): Idea | undefined {
        // Check top-level ideas
        for (const idea of session.ideas) {
            if (idea.id === ideaId) {
                return idea;
            }
            
            // Check children
            if (idea.children) {
                const childIdea = this.findIdeaInChildren(idea.children, ideaId);
                if (childIdea) {
                    return childIdea;
                }
            }
        }
        
        return undefined;
    }

    /**
     * Find an idea in children
     * 
     * @param children The children
     * @param ideaId The idea ID
     */
    private findIdeaInChildren(children: Idea[], ideaId: string): Idea | undefined {
        for (const child of children) {
            if (child.id === ideaId) {
                return child;
            }
            
            // Check children
            if (child.children) {
                const grandchildIdea = this.findIdeaInChildren(child.children, ideaId);
                if (grandchildIdea) {
                    return grandchildIdea;
                }
            }
        }
        
        return undefined;
    }

    /**
     * Connect two ideas
     * 
     * @param sessionId The session ID
     * @param ideaId1 The first idea ID
     * @param ideaId2 The second idea ID
     */
    public connectIdeas(sessionId: string, ideaId1: string, ideaId2: string): boolean {
        const session = this.sessions.get(sessionId);
        if (!session) {
            return false;
        }
        
        // Find the ideas
        const idea1 = this.findIdea(session, ideaId1);
        const idea2 = this.findIdea(session, ideaId2);
        
        if (!idea1 || !idea2) {
            return false;
        }
        
        // Add connections
        if (!idea1.connections) {
            idea1.connections = [];
        }
        if (!idea2.connections) {
            idea2.connections = [];
        }
        
        // Add connection if it doesn't exist
        if (!idea1.connections.includes(ideaId2)) {
            idea1.connections.push(ideaId2);
        }
        if (!idea2.connections.includes(ideaId1)) {
            idea2.connections.push(ideaId1);
        }
        
        // Update session
        session.updatedAt = Date.now();
        
        this.saveToStorage();
        this._onSessionUpdated.fire(session);
        
        return true;
    }

    /**
     * Generate ideas for a session
     * 
     * @param sessionId The session ID
     * @param count The number of ideas to generate
     */
    public async generateIdeas(sessionId: string, count: number = 5): Promise<Idea[]> {
        const session = this.sessions.get(sessionId);
        if (!session) {
            throw new Error('Session not found');
        }
        
        // Generate ideas using the API client
        const response = await this.apiClient.generateCode(
            `Generate ${count} creative ideas for a brainstorming session on the topic: "${session.topic}"
            
            ${session.description}
            
            Return a JSON array of ideas, where each idea has:
            - content: The idea text
            - category: A category for the idea (e.g., "feature", "improvement", "solution", "question")
            - tags: An array of relevant tags
            
            Return only the JSON array without any explanation or markdown formatting.`,
            'json'
        );
        
        if (!response.success) {
            throw new Error('Failed to generate ideas');
        }
        
        try {
            // Extract JSON from the response
            const jsonMatch = response.code.match(/\[[\s\S]*\]/);
            if (!jsonMatch) {
                throw new Error('No JSON found in response');
            }
            
            const generatedIdeas = JSON.parse(jsonMatch[0]);
            
            // Add ideas to the session
            const addedIdeas: Idea[] = [];
            for (const generatedIdea of generatedIdeas) {
                const idea = this.addIdea(
                    sessionId,
                    generatedIdea.content,
                    generatedIdea.category,
                    generatedIdea.tags
                );
                
                if (idea) {
                    addedIdeas.push(idea);
                }
            }
            
            return addedIdeas;
        } catch (error) {
            throw new Error(`Failed to parse generated ideas: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Create a roadmap from a brainstorming session
     * 
     * @param sessionId The session ID
     * @param title The roadmap title
     * @param description The roadmap description
     */
    public async createRoadmapFromSession(
        sessionId: string,
        title: string,
        description: string
    ): Promise<Roadmap> {
        const session = this.sessions.get(sessionId);
        if (!session) {
            throw new Error('Session not found');
        }
        
        // Get all ideas from the session
        const allIdeas = this.getAllIdeasFromSession(session);
        
        // Generate roadmap using the API client
        const response = await this.apiClient.generateCode(
            `Create a project roadmap based on the following brainstorming session:
            
            Topic: ${session.topic}
            Description: ${session.description}
            
            Ideas:
            ${allIdeas.map(idea => `- ${idea.content} [${idea.category}] ${idea.tags.map(tag => `#${tag}`).join(' ')}`).join('\n')}
            
            Create a structured roadmap with items that have:
            - title: Short title for the item
            - description: Detailed description
            - priority: "high", "medium", or "low"
            - status: "pending"
            - dependencies: Array of other item titles this depends on
            - estimatedTime: Estimated time to complete (e.g., "2 days", "1 week")
            - tags: Array of relevant tags
            
            Group related items together and organize them in a logical sequence.
            Return a JSON object with a "title", "description", and "items" array.
            
            Return only the JSON object without any explanation or markdown formatting.`,
            'json'
        );
        
        if (!response.success) {
            throw new Error('Failed to generate roadmap');
        }
        
        try {
            // Extract JSON from the response
            const jsonMatch = response.code.match(/\{[\s\S]*\}/);
            if (!jsonMatch) {
                throw new Error('No JSON found in response');
            }
            
            const generatedRoadmap = JSON.parse(jsonMatch[0]);
            
            // Create roadmap
            const roadmapId = generateId();
            const roadmap: Roadmap = {
                id: roadmapId,
                title: generatedRoadmap.title || title,
                description: generatedRoadmap.description || description,
                createdAt: Date.now(),
                updatedAt: Date.now(),
                items: []
            };
            
            // Process roadmap items
            if (generatedRoadmap.items && Array.isArray(generatedRoadmap.items)) {
                for (const item of generatedRoadmap.items) {
                    const roadmapItem: RoadmapItem = {
                        id: generateId(),
                        title: item.title || 'Untitled Item',
                        description: item.description || '',
                        priority: item.priority || 'medium',
                        status: 'pending',
                        dependencies: item.dependencies || [],
                        estimatedTime: item.estimatedTime,
                        tags: item.tags || [],
                        children: []
                    };
                    
                    // Add children if available
                    if (item.children && Array.isArray(item.children)) {
                        for (const child of item.children) {
                            const childItem: RoadmapItem = {
                                id: generateId(),
                                title: child.title || 'Untitled Item',
                                description: child.description || '',
                                priority: child.priority || 'medium',
                                status: 'pending',
                                dependencies: child.dependencies || [],
                                estimatedTime: child.estimatedTime,
                                tags: child.tags || []
                            };
                            
                            roadmapItem.children!.push(childItem);
                        }
                    }
                    
                    roadmap.items.push(roadmapItem);
                }
            }
            
            // Save roadmap
            this.roadmaps.set(roadmapId, roadmap);
            this.saveToStorage();
            
            this._onRoadmapUpdated.fire(roadmap);
            this.log(`Created roadmap: ${roadmap.title} (${roadmapId})`);
            
            return roadmap;
        } catch (error) {
            throw new Error(`Failed to parse generated roadmap: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Get all ideas from a session (flattened)
     * 
     * @param session The session
     */
    private getAllIdeasFromSession(session: BrainstormingSession): Idea[] {
        const allIdeas: Idea[] = [];
        
        // Add top-level ideas
        for (const idea of session.ideas) {
            allIdeas.push(idea);
            
            // Add children
            if (idea.children) {
                this.addChildrenToList(idea.children, allIdeas);
            }
        }
        
        return allIdeas;
    }

    /**
     * Add children to a list
     * 
     * @param children The children
     * @param list The list to add to
     */
    private addChildrenToList(children: Idea[], list: Idea[]): void {
        for (const child of children) {
            list.push(child);
            
            // Add children
            if (child.children) {
                this.addChildrenToList(child.children, list);
            }
        }
    }

    /**
     * Get a roadmap by ID
     * 
     * @param roadmapId The roadmap ID
     */
    public getRoadmap(roadmapId: string): Roadmap | undefined {
        return this.roadmaps.get(roadmapId);
    }

    /**
     * Get all roadmaps
     */
    public getAllRoadmaps(): Roadmap[] {
        return Array.from(this.roadmaps.values());
    }

    /**
     * Update a roadmap
     * 
     * @param roadmapId The roadmap ID
     * @param updates The updates to apply
     */
    public updateRoadmap(roadmapId: string, updates: Partial<Roadmap>): boolean {
        const roadmap = this.roadmaps.get(roadmapId);
        if (!roadmap) {
            return false;
        }
        
        // Apply updates
        Object.assign(roadmap, updates);
        
        // Update timestamp
        roadmap.updatedAt = Date.now();
        
        this.saveToStorage();
        this._onRoadmapUpdated.fire(roadmap);
        
        return true;
    }

    /**
     * Delete a roadmap
     * 
     * @param roadmapId The roadmap ID
     */
    public deleteRoadmap(roadmapId: string): boolean {
        const roadmap = this.roadmaps.get(roadmapId);
        if (!roadmap) {
            return false;
        }
        
        this.roadmaps.delete(roadmapId);
        this.saveToStorage();
        
        return true;
    }

    /**
     * Update a roadmap item
     * 
     * @param roadmapId The roadmap ID
     * @param itemId The item ID
     * @param updates The updates to apply
     */
    public updateRoadmapItem(roadmapId: string, itemId: string, updates: Partial<RoadmapItem>): boolean {
        const roadmap = this.roadmaps.get(roadmapId);
        if (!roadmap) {
            return false;
        }
        
        // Find the item
        const item = this.findRoadmapItem(roadmap, itemId);
        if (!item) {
            return false;
        }
        
        // Apply updates
        Object.assign(item, updates);
        
        // Update timestamp
        roadmap.updatedAt = Date.now();
        
        this.saveToStorage();
        this._onRoadmapUpdated.fire(roadmap);
        
        return true;
    }

    /**
     * Find a roadmap item
     * 
     * @param roadmap The roadmap
     * @param itemId The item ID
     */
    private findRoadmapItem(roadmap: Roadmap, itemId: string): RoadmapItem | undefined {
        // Check top-level items
        for (const item of roadmap.items) {
            if (item.id === itemId) {
                return item;
            }
            
            // Check children
            if (item.children) {
                for (const child of item.children) {
                    if (child.id === itemId) {
                        return child;
                    }
                }
            }
        }
        
        return undefined;
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
     * Dispose the brainstorming manager
     */
    public dispose(): void {
        this.outputChannel.dispose();
        this._onSessionUpdated.dispose();
        this._onRoadmapUpdated.dispose();
    }
}
