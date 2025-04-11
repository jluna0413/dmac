import * as vscode from 'vscode';
import { BrainstormingManager, BrainstormingSession, Idea, Roadmap, RoadmapItem } from './brainstorming';
import { formatDate } from './utils';

/**
 * Brainstorming panel
 */
export class BrainstormingPanel {
    public static readonly viewType = 'macoder.brainstormingPanel';
    
    private panel: vscode.WebviewPanel;
    private brainstormingManager: BrainstormingManager;
    private disposables: vscode.Disposable[] = [];
    private activeSessionId: string | null = null;
    private activeRoadmapId: string | null = null;
    private mode: 'sessions' | 'session' | 'roadmaps' | 'roadmap' = 'sessions';
    
    /**
     * Create a new BrainstormingPanel
     * 
     * @param extensionUri The extension URI
     * @param brainstormingManager The brainstorming manager
     */
    private constructor(
        private readonly extensionUri: vscode.Uri,
        brainstormingManager: BrainstormingManager
    ) {
        this.brainstormingManager = brainstormingManager;
        
        // Create the webview panel
        this.panel = vscode.window.createWebviewPanel(
            BrainstormingPanel.viewType,
            'MaCoder Brainstorming',
            vscode.ViewColumn.Beside,
            {
                enableScripts: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, 'media')
                ]
            }
        );
        
        // Set the webview's initial html content
        this.panel.webview.html = this.getHtmlForWebview();
        
        // Listen for messages from the webview
        this.panel.webview.onDidReceiveMessage(
            message => {
                switch (message.command) {
                    case 'createSession':
                        this.createSession(message.topic, message.description);
                        return;
                    case 'openSession':
                        this.openSession(message.sessionId);
                        return;
                    case 'updateSession':
                        this.updateSession(message.sessionId, message.updates);
                        return;
                    case 'deleteSession':
                        this.deleteSession(message.sessionId);
                        return;
                    case 'addIdea':
                        this.addIdea(message.sessionId, message.content, message.category, message.tags, message.parentId);
                        return;
                    case 'generateIdeas':
                        this.generateIdeas(message.sessionId, message.count);
                        return;
                    case 'createRoadmap':
                        this.createRoadmap(message.sessionId, message.title, message.description);
                        return;
                    case 'openRoadmap':
                        this.openRoadmap(message.roadmapId);
                        return;
                    case 'updateRoadmap':
                        this.updateRoadmap(message.roadmapId, message.updates);
                        return;
                    case 'deleteRoadmap':
                        this.deleteRoadmap(message.roadmapId);
                        return;
                    case 'updateRoadmapItem':
                        this.updateRoadmapItem(message.roadmapId, message.itemId, message.updates);
                        return;
                    case 'showSessions':
                        this.showSessions();
                        return;
                    case 'showRoadmaps':
                        this.showRoadmaps();
                        return;
                }
            },
            null,
            this.disposables
        );
        
        // Listen for session updates
        this.brainstormingManager.onSessionUpdated(session => {
            if (this.mode === 'sessions') {
                this.updateSessionsList();
            } else if (this.mode === 'session' && this.activeSessionId === session.id) {
                this.updateSessionView(session);
            }
        });
        
        // Listen for roadmap updates
        this.brainstormingManager.onRoadmapUpdated(roadmap => {
            if (this.mode === 'roadmaps') {
                this.updateRoadmapsList();
            } else if (this.mode === 'roadmap' && this.activeRoadmapId === roadmap.id) {
                this.updateRoadmapView(roadmap);
            }
        });
        
        // Update the webview when the panel becomes visible
        this.panel.onDidChangeViewState(
            e => {
                if (this.panel.visible) {
                    this.updateWebview();
                }
            },
            null,
            this.disposables
        );
        
        // Clean up resources when the panel is closed
        this.panel.onDidDispose(
            () => this.dispose(),
            null,
            this.disposables
        );
        
        // Initial update
        this.updateWebview();
    }
    
    /**
     * Create or show the brainstorming panel
     * 
     * @param extensionUri The extension URI
     * @param brainstormingManager The brainstorming manager
     */
    public static createOrShow(extensionUri: vscode.Uri, brainstormingManager: BrainstormingManager): BrainstormingPanel {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;
            
        // If we already have a panel, show it
        if (BrainstormingPanel.currentPanel) {
            BrainstormingPanel.currentPanel.panel.reveal(column);
            return BrainstormingPanel.currentPanel;
        }
        
        // Otherwise, create a new panel
        BrainstormingPanel.currentPanel = new BrainstormingPanel(extensionUri, brainstormingManager);
        return BrainstormingPanel.currentPanel;
    }
    
    /**
     * Current panel instance
     */
    private static currentPanel: BrainstormingPanel | undefined;
    
    /**
     * Create a new session
     * 
     * @param topic The session topic
     * @param description The session description
     */
    private createSession(topic: string, description: string): void {
        try {
            const session = this.brainstormingManager.createSession(topic, description);
            this.openSession(session.id);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create session: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Open a session
     * 
     * @param sessionId The session ID
     */
    private openSession(sessionId: string): void {
        try {
            const session = this.brainstormingManager.getSession(sessionId);
            if (!session) {
                throw new Error('Session not found');
            }
            
            this.activeSessionId = sessionId;
            this.mode = 'session';
            this.updateSessionView(session);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to open session: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Update a session
     * 
     * @param sessionId The session ID
     * @param updates The updates to apply
     */
    private updateSession(sessionId: string, updates: Partial<BrainstormingSession>): void {
        try {
            const success = this.brainstormingManager.updateSession(sessionId, updates);
            if (!success) {
                throw new Error('Failed to update session');
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to update session: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Delete a session
     * 
     * @param sessionId The session ID
     */
    private deleteSession(sessionId: string): void {
        try {
            const success = this.brainstormingManager.deleteSession(sessionId);
            if (!success) {
                throw new Error('Failed to delete session');
            }
            
            // If this is the active session, go back to sessions list
            if (this.activeSessionId === sessionId) {
                this.showSessions();
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to delete session: ${error instanceof Error ? error.message : String(error)}`);
        }
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
    private addIdea(
        sessionId: string,
        content: string,
        category: string,
        tags: string[],
        parentId?: string
    ): void {
        try {
            const idea = this.brainstormingManager.addIdea(sessionId, content, category, tags, parentId);
            if (!idea) {
                throw new Error('Failed to add idea');
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to add idea: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Generate ideas for a session
     * 
     * @param sessionId The session ID
     * @param count The number of ideas to generate
     */
    private async generateIdeas(sessionId: string, count: number): Promise<void> {
        try {
            await vscode.window.withProgress(
                {
                    location: vscode.ProgressLocation.Notification,
                    title: 'Generating ideas...',
                    cancellable: false
                },
                async () => {
                    const ideas = await this.brainstormingManager.generateIdeas(sessionId, count);
                    vscode.window.showInformationMessage(`Generated ${ideas.length} ideas`);
                }
            );
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to generate ideas: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Create a roadmap from a session
     * 
     * @param sessionId The session ID
     * @param title The roadmap title
     * @param description The roadmap description
     */
    private async createRoadmap(sessionId: string, title: string, description: string): Promise<void> {
        try {
            await vscode.window.withProgress(
                {
                    location: vscode.ProgressLocation.Notification,
                    title: 'Creating roadmap...',
                    cancellable: false
                },
                async () => {
                    const roadmap = await this.brainstormingManager.createRoadmapFromSession(sessionId, title, description);
                    this.openRoadmap(roadmap.id);
                }
            );
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create roadmap: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Open a roadmap
     * 
     * @param roadmapId The roadmap ID
     */
    private openRoadmap(roadmapId: string): void {
        try {
            const roadmap = this.brainstormingManager.getRoadmap(roadmapId);
            if (!roadmap) {
                throw new Error('Roadmap not found');
            }
            
            this.activeRoadmapId = roadmapId;
            this.mode = 'roadmap';
            this.updateRoadmapView(roadmap);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to open roadmap: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Update a roadmap
     * 
     * @param roadmapId The roadmap ID
     * @param updates The updates to apply
     */
    private updateRoadmap(roadmapId: string, updates: Partial<Roadmap>): void {
        try {
            const success = this.brainstormingManager.updateRoadmap(roadmapId, updates);
            if (!success) {
                throw new Error('Failed to update roadmap');
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to update roadmap: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Delete a roadmap
     * 
     * @param roadmapId The roadmap ID
     */
    private deleteRoadmap(roadmapId: string): void {
        try {
            const success = this.brainstormingManager.deleteRoadmap(roadmapId);
            if (!success) {
                throw new Error('Failed to delete roadmap');
            }
            
            // If this is the active roadmap, go back to roadmaps list
            if (this.activeRoadmapId === roadmapId) {
                this.showRoadmaps();
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to delete roadmap: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Update a roadmap item
     * 
     * @param roadmapId The roadmap ID
     * @param itemId The item ID
     * @param updates The updates to apply
     */
    private updateRoadmapItem(roadmapId: string, itemId: string, updates: Partial<RoadmapItem>): void {
        try {
            const success = this.brainstormingManager.updateRoadmapItem(roadmapId, itemId, updates);
            if (!success) {
                throw new Error('Failed to update roadmap item');
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to update roadmap item: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Show the sessions list
     */
    private showSessions(): void {
        this.activeSessionId = null;
        this.mode = 'sessions';
        this.updateSessionsList();
    }
    
    /**
     * Show the roadmaps list
     */
    private showRoadmaps(): void {
        this.activeRoadmapId = null;
        this.mode = 'roadmaps';
        this.updateRoadmapsList();
    }
    
    /**
     * Update the webview content
     */
    private updateWebview(): void {
        switch (this.mode) {
            case 'sessions':
                this.updateSessionsList();
                break;
            case 'session':
                if (this.activeSessionId) {
                    const session = this.brainstormingManager.getSession(this.activeSessionId);
                    if (session) {
                        this.updateSessionView(session);
                    } else {
                        this.showSessions();
                    }
                } else {
                    this.showSessions();
                }
                break;
            case 'roadmaps':
                this.updateRoadmapsList();
                break;
            case 'roadmap':
                if (this.activeRoadmapId) {
                    const roadmap = this.brainstormingManager.getRoadmap(this.activeRoadmapId);
                    if (roadmap) {
                        this.updateRoadmapView(roadmap);
                    } else {
                        this.showRoadmaps();
                    }
                } else {
                    this.showRoadmaps();
                }
                break;
        }
    }
    
    /**
     * Update the sessions list
     */
    private updateSessionsList(): void {
        const sessions = this.brainstormingManager.getAllSessions();
        
        this.panel.webview.postMessage({
            command: 'updateSessionsList',
            sessions
        });
    }
    
    /**
     * Update the session view
     * 
     * @param session The session to view
     */
    private updateSessionView(session: BrainstormingSession): void {
        this.panel.webview.postMessage({
            command: 'updateSessionView',
            session
        });
    }
    
    /**
     * Update the roadmaps list
     */
    private updateRoadmapsList(): void {
        const roadmaps = this.brainstormingManager.getAllRoadmaps();
        
        this.panel.webview.postMessage({
            command: 'updateRoadmapsList',
            roadmaps
        });
    }
    
    /**
     * Update the roadmap view
     * 
     * @param roadmap The roadmap to view
     */
    private updateRoadmapView(roadmap: Roadmap): void {
        this.panel.webview.postMessage({
            command: 'updateRoadmapView',
            roadmap
        });
    }
    
    /**
     * Get the HTML for the webview
     */
    private getHtmlForWebview(): string {
        // Get the local path to main script and stylesheet
        const scriptUri = this.panel.webview.asWebviewUri(
            vscode.Uri.joinPath(this.extensionUri, 'media', 'brainstorming-panel.js')
        );
        
        const styleUri = this.panel.webview.asWebviewUri(
            vscode.Uri.joinPath(this.extensionUri, 'media', 'brainstorming-panel.css')
        );
        
        // Use a nonce to only allow specific scripts to be run
        const nonce = getNonce();
        
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${this.panel.webview.cspSource}; script-src 'nonce-${nonce}';">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="${styleUri}" rel="stylesheet">
            <title>MaCoder Brainstorming</title>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>MaCoder Brainstorming</h1>
                    <div class="tabs">
                        <button id="sessionsTab" class="tab active">Sessions</button>
                        <button id="roadmapsTab" class="tab">Roadmaps</button>
                    </div>
                </div>
                
                <div id="sessionsView" class="view">
                    <div class="sessions-header">
                        <h2>Brainstorming Sessions</h2>
                        <button id="newSessionButton" class="primary-button">New Session</button>
                    </div>
                    
                    <div id="sessionsList" class="sessions-list">
                        <div class="empty-state">No sessions yet</div>
                    </div>
                </div>
                
                <div id="sessionView" class="view hidden">
                    <div class="session-header">
                        <button id="backToSessionsButton" class="back-button">← Back to Sessions</button>
                        <h2 id="sessionTitle">Session Title</h2>
                        <div class="session-actions">
                            <button id="generateIdeasButton" class="action-button">Generate Ideas</button>
                            <button id="createRoadmapButton" class="action-button">Create Roadmap</button>
                        </div>
                    </div>
                    
                    <div id="sessionDescription" class="session-description"></div>
                    
                    <div class="ideas-header">
                        <h3>Ideas</h3>
                        <button id="addIdeaButton" class="secondary-button">Add Idea</button>
                    </div>
                    
                    <div id="ideasList" class="ideas-list">
                        <div class="empty-state">No ideas yet</div>
                    </div>
                </div>
                
                <div id="roadmapsView" class="view hidden">
                    <div class="roadmaps-header">
                        <h2>Roadmaps</h2>
                    </div>
                    
                    <div id="roadmapsList" class="roadmaps-list">
                        <div class="empty-state">No roadmaps yet</div>
                    </div>
                </div>
                
                <div id="roadmapView" class="view hidden">
                    <div class="roadmap-header">
                        <button id="backToRoadmapsButton" class="back-button">← Back to Roadmaps</button>
                        <h2 id="roadmapTitle">Roadmap Title</h2>
                    </div>
                    
                    <div id="roadmapDescription" class="roadmap-description"></div>
                    
                    <div class="items-header">
                        <h3>Items</h3>
                    </div>
                    
                    <div id="itemsList" class="items-list">
                        <div class="empty-state">No items yet</div>
                    </div>
                </div>
            </div>
            
            <script nonce="${nonce}" src="${scriptUri}"></script>
        </body>
        </html>`;
    }
    
    /**
     * Dispose the panel
     */
    public dispose(): void {
        BrainstormingPanel.currentPanel = undefined;
        
        // Clean up resources
        this.panel.dispose();
        
        while (this.disposables.length) {
            const disposable = this.disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}

/**
 * Get a nonce
 */
function getNonce(): string {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
