import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { generateId } from './utils';

/**
 * Code edit interface
 */
export interface CodeEdit {
    id: string;
    filePath: string;
    oldText: string;
    newText: string;
    startLine: number;
    endLine: number;
    timestamp: number;
    source: 'user' | 'macoder' | 'other';
    description?: string;
}

/**
 * Code edit session interface
 */
export interface CodeEditSession {
    id: string;
    edits: CodeEdit[];
    startTime: number;
    endTime?: number;
    description?: string;
}

/**
 * Code edit logger interface
 */
export interface CodeEditLogger {
    /**
     * Start a new edit session
     *
     * @param description Optional description of the session
     */
    startSession(description?: string): string;

    /**
     * End an edit session
     *
     * @param sessionId The session ID
     */
    endSession(sessionId: string): void;

    /**
     * Get the current session ID
     */
    getCurrentSessionId(): string | null;

    /**
     * Log a code edit
     *
     * @param edit The code edit to log
     */
    logEdit(edit: CodeEdit): void;

    /**
     * Get all edits for a file
     *
     * @param filePath The file path
     */
    getEditsForFile(filePath: string): CodeEdit[];

    /**
     * Get all edits in a session
     *
     * @param sessionId The session ID
     */
    getEditsInSession(sessionId: string): CodeEdit[];

    /**
     * Get all sessions
     */
    getAllSessions(): CodeEditSession[];

    /**
     * Get a session by ID
     *
     * @param sessionId The session ID
     */
    getSession(sessionId: string): CodeEditSession | null;

    /**
     * Get all edits
     */
    getAllEdits(): CodeEdit[];

    /**
     * Clear all edits
     */
    clearEdits(): void;
}

/**
 * File-based code edit logger
 */
export class FileCodeEditLogger implements CodeEditLogger {
    private static instance: FileCodeEditLogger;
    private edits: CodeEdit[] = [];
    private sessions: Map<string, CodeEditSession> = new Map();
    private currentSessionId: string | null = null;
    private outputChannel: vscode.OutputChannel;
    private storagePath: string;
    private _onEditLogged: vscode.EventEmitter<CodeEdit> = new vscode.EventEmitter<CodeEdit>();
    private _onSessionStarted: vscode.EventEmitter<CodeEditSession> = new vscode.EventEmitter<CodeEditSession>();
    private _onSessionEnded: vscode.EventEmitter<CodeEditSession> = new vscode.EventEmitter<CodeEditSession>();

    /**
     * Event that fires when an edit is logged
     */
    public readonly onEditLogged: vscode.Event<CodeEdit> = this._onEditLogged.event;

    /**
     * Event that fires when a session is started
     */
    public readonly onSessionStarted: vscode.Event<CodeEditSession> = this._onSessionStarted.event;

    /**
     * Event that fires when a session is ended
     */
    public readonly onSessionEnded: vscode.Event<CodeEditSession> = this._onSessionEnded.event;

    /**
     * Create a new FileCodeEditLogger
     *
     * @param storagePath The path to store edit logs
     */
    private constructor(storagePath: string) {
        this.storagePath = storagePath;
        this.outputChannel = vscode.window.createOutputChannel('MaCoder Code Edit Logger');

        // Create storage directory if it doesn't exist
        if (!fs.existsSync(this.storagePath)) {
            fs.mkdirSync(this.storagePath, { recursive: true });
        }

        // Load existing edits and sessions
        this.loadEdits();
        this.loadSessions();

        this.log('Code edit logger initialized');
    }

    /**
     * Get the singleton instance
     *
     * @param context The extension context
     */
    public static getInstance(context: vscode.ExtensionContext): FileCodeEditLogger {
        if (!FileCodeEditLogger.instance) {
            const storagePath = path.join(context.globalStoragePath, 'code-edits');
            FileCodeEditLogger.instance = new FileCodeEditLogger(storagePath);
        }
        return FileCodeEditLogger.instance;
    }

    /**
     * Start a new edit session
     *
     * @param description Optional description of the session
     */
    public startSession(description?: string): string {
        // End current session if one exists
        if (this.currentSessionId) {
            this.endSession(this.currentSessionId);
        }

        // Create new session
        const sessionId = generateId();
        const session: CodeEditSession = {
            id: sessionId,
            edits: [],
            startTime: Date.now(),
            description
        };

        this.sessions.set(sessionId, session);
        this.currentSessionId = sessionId;

        // Save session
        this.saveSessions();

        // Emit event
        this._onSessionStarted.fire(session);

        this.log(`Started edit session: ${sessionId}${description ? ` (${description})` : ''}`);

        return sessionId;
    }

    /**
     * End an edit session
     *
     * @param sessionId The session ID
     */
    public endSession(sessionId: string): void {
        const session = this.sessions.get(sessionId);
        if (!session) {
            return;
        }

        // Update session
        session.endTime = Date.now();

        // Clear current session if this is the current one
        if (this.currentSessionId === sessionId) {
            this.currentSessionId = null;
        }

        // Save session
        this.saveSessions();

        // Emit event
        this._onSessionEnded.fire(session);

        this.log(`Ended edit session: ${sessionId}`);
    }

    /**
     * Get the current session ID
     */
    public getCurrentSessionId(): string | null {
        return this.currentSessionId;
    }

    /**
     * Log a code edit
     *
     * @param edit The code edit to log
     */
    public logEdit(edit: CodeEdit): void {
        // Add edit to list
        this.edits.push(edit);

        // Add edit to current session if one exists
        if (this.currentSessionId) {
            const session = this.sessions.get(this.currentSessionId);
            if (session) {
                session.edits.push(edit);
            }
        }

        // Save edits
        this.saveEdits();

        // Emit event
        this._onEditLogged.fire(edit);

        this.log(`Logged edit: ${edit.id} (${edit.filePath}, lines ${edit.startLine}-${edit.endLine})`);
    }

    /**
     * Get all edits for a file
     *
     * @param filePath The file path
     */
    public getEditsForFile(filePath: string): CodeEdit[] {
        return this.edits.filter(edit => edit.filePath === filePath);
    }

    /**
     * Get all edits in a session
     *
     * @param sessionId The session ID
     */
    public getEditsInSession(sessionId: string): CodeEdit[] {
        const session = this.sessions.get(sessionId);
        if (!session) {
            return [];
        }
        return session.edits;
    }

    /**
     * Get all sessions
     */
    public getAllSessions(): CodeEditSession[] {
        return Array.from(this.sessions.values());
    }

    /**
     * Get a session by ID
     *
     * @param sessionId The session ID
     */
    public getSession(sessionId: string): CodeEditSession | null {
        return this.sessions.get(sessionId) || null;
    }

    /**
     * Get all edits
     */
    public getAllEdits(): CodeEdit[] {
        return [...this.edits];
    }

    /**
     * Clear all edits
     */
    public clearEdits(): void {
        this.edits = [];
        this.sessions.clear();
        this.currentSessionId = null;

        // Delete edit log files
        const editsPath = path.join(this.storagePath, 'edits.json');
        const sessionsPath = path.join(this.storagePath, 'sessions.json');

        if (fs.existsSync(editsPath)) {
            fs.unlinkSync(editsPath);
        }

        if (fs.existsSync(sessionsPath)) {
            fs.unlinkSync(sessionsPath);
        }

        this.log('Cleared all edits');
    }

    /**
     * Load edits from file
     */
    private loadEdits(): void {
        const editsPath = path.join(this.storagePath, 'edits.json');

        if (fs.existsSync(editsPath)) {
            try {
                const editsJson = fs.readFileSync(editsPath, 'utf8');
                this.edits = JSON.parse(editsJson);
                this.log(`Loaded ${this.edits.length} edits from file`);
            } catch (error) {
                this.log(`Error loading edits: ${error instanceof Error ? error.message : String(error)}`);
            }
        }
    }

    /**
     * Save edits to file
     */
    private saveEdits(): void {
        const editsPath = path.join(this.storagePath, 'edits.json');

        try {
            const editsJson = JSON.stringify(this.edits, null, 2);
            fs.writeFileSync(editsPath, editsJson, 'utf8');
        } catch (error) {
            this.log(`Error saving edits: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Load sessions from file
     */
    private loadSessions(): void {
        const sessionsPath = path.join(this.storagePath, 'sessions.json');

        if (fs.existsSync(sessionsPath)) {
            try {
                const sessionsJson = fs.readFileSync(sessionsPath, 'utf8');
                const sessions = JSON.parse(sessionsJson) as CodeEditSession[];

                // Convert to map
                this.sessions = new Map(sessions.map(session => [session.id, session]));

                this.log(`Loaded ${this.sessions.size} sessions from file`);
            } catch (error) {
                this.log(`Error loading sessions: ${error instanceof Error ? error.message : String(error)}`);
            }
        }
    }

    /**
     * Save sessions to file
     */
    private saveSessions(): void {
        const sessionsPath = path.join(this.storagePath, 'sessions.json');

        try {
            const sessions = Array.from(this.sessions.values());
            const sessionsJson = JSON.stringify(sessions, null, 2);
            fs.writeFileSync(sessionsPath, sessionsJson, 'utf8');
        } catch (error) {
            this.log(`Error saving sessions: ${error instanceof Error ? error.message : String(error)}`);
        }
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
     * Dispose the logger
     */
    public dispose(): void {
        this.outputChannel.dispose();
        this._onEditLogged.dispose();
        this._onSessionStarted.dispose();
        this._onSessionEnded.dispose();
    }
}
