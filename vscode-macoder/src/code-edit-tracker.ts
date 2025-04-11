import * as vscode from 'vscode';
import { CodeEdit, CodeEditLogger } from './code-edit-logger';
import { generateId } from './utils';

/**
 * Code edit tracker
 */
export class CodeEditTracker {
    private static instance: CodeEditTracker;
    private logger: CodeEditLogger;
    private disposables: vscode.Disposable[] = [];
    private lastEditTime: number = 0;
    private editTimeout: NodeJS.Timeout | null = null;
    private pendingEdits: Map<string, { oldText: string, newText: string }> = new Map();
    
    /**
     * Create a new CodeEditTracker
     * 
     * @param logger The code edit logger
     */
    private constructor(logger: CodeEditLogger) {
        this.logger = logger;
        
        // Listen for text document changes
        this.disposables.push(
            vscode.workspace.onDidChangeTextDocument(this.onDocumentChanged.bind(this))
        );
        
        // Listen for active editor changes
        this.disposables.push(
            vscode.window.onDidChangeActiveTextEditor(this.onActiveEditorChanged.bind(this))
        );
    }
    
    /**
     * Get the singleton instance
     * 
     * @param logger The code edit logger
     */
    public static getInstance(logger: CodeEditLogger): CodeEditTracker {
        if (!CodeEditTracker.instance) {
            CodeEditTracker.instance = new CodeEditTracker(logger);
        }
        return CodeEditTracker.instance;
    }
    
    /**
     * Handle document changes
     * 
     * @param event The document change event
     */
    private onDocumentChanged(event: vscode.TextDocumentChangeEvent): void {
        // Skip if no changes
        if (event.contentChanges.length === 0) {
            return;
        }
        
        // Skip non-file documents
        if (event.document.uri.scheme !== 'file') {
            return;
        }
        
        // Process each change
        for (const change of event.contentChanges) {
            // Get the file path
            const filePath = event.document.uri.fsPath;
            
            // Get the start and end lines
            const startLine = change.range.start.line;
            const endLine = change.range.end.line;
            
            // Get the old and new text
            const oldText = change.rangeLength > 0 ? event.document.getText(change.range) : '';
            const newText = change.text;
            
            // Create a key for this change
            const changeKey = `${filePath}:${startLine}:${endLine}`;
            
            // Store the change
            this.pendingEdits.set(changeKey, { oldText, newText });
            
            // Reset the timeout
            if (this.editTimeout) {
                clearTimeout(this.editTimeout);
            }
            
            // Set a timeout to log the edit after a delay
            this.editTimeout = setTimeout(() => {
                this.logPendingEdits();
            }, 1000); // 1 second delay
        }
    }
    
    /**
     * Handle active editor changes
     * 
     * @param editor The new active editor
     */
    private onActiveEditorChanged(editor: vscode.TextEditor | undefined): void {
        // Log any pending edits
        if (this.pendingEdits.size > 0) {
            this.logPendingEdits();
        }
    }
    
    /**
     * Log pending edits
     */
    private logPendingEdits(): void {
        // Skip if no pending edits
        if (this.pendingEdits.size === 0) {
            return;
        }
        
        // Process each pending edit
        for (const [changeKey, { oldText, newText }] of this.pendingEdits.entries()) {
            // Parse the change key
            const [filePath, startLineStr, endLineStr] = changeKey.split(':');
            const startLine = parseInt(startLineStr);
            const endLine = parseInt(endLineStr);
            
            // Create the edit
            const edit: CodeEdit = {
                id: generateId(),
                filePath,
                oldText,
                newText,
                startLine,
                endLine,
                timestamp: Date.now(),
                source: 'user' // Assume user edits for now
            };
            
            // Log the edit
            this.logger.logEdit(edit);
        }
        
        // Clear pending edits
        this.pendingEdits.clear();
        
        // Clear the timeout
        if (this.editTimeout) {
            clearTimeout(this.editTimeout);
            this.editTimeout = null;
        }
    }
    
    /**
     * Log an edit from MaCoder
     * 
     * @param filePath The file path
     * @param oldText The old text
     * @param newText The new text
     * @param startLine The start line
     * @param endLine The end line
     * @param description Optional description
     */
    public logMaCoderEdit(
        filePath: string,
        oldText: string,
        newText: string,
        startLine: number,
        endLine: number,
        description?: string
    ): void {
        // Create the edit
        const edit: CodeEdit = {
            id: generateId(),
            filePath,
            oldText,
            newText,
            startLine,
            endLine,
            timestamp: Date.now(),
            source: 'macoder',
            description
        };
        
        // Log the edit
        this.logger.logEdit(edit);
    }
    
    /**
     * Start a new edit session
     * 
     * @param description Optional description
     */
    public startSession(description?: string): string {
        return this.logger.startSession(description);
    }
    
    /**
     * End the current edit session
     */
    public endCurrentSession(): void {
        const currentSessionId = this.logger.getCurrentSessionId();
        if (currentSessionId) {
            this.logger.endSession(currentSessionId);
        }
    }
    
    /**
     * Dispose the tracker
     */
    public dispose(): void {
        // Dispose all disposables
        for (const disposable of this.disposables) {
            disposable.dispose();
        }
        this.disposables = [];
        
        // Clear the timeout
        if (this.editTimeout) {
            clearTimeout(this.editTimeout);
            this.editTimeout = null;
        }
    }
}
