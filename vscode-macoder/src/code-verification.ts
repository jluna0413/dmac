import * as vscode from 'vscode';
import { HybridApiClient } from './hybrid-api-client';
import { generateId } from './utils';

/**
 * Verification result interface
 */
export interface VerificationResult {
    isValid: boolean;
    issues: VerificationIssue[];
}

/**
 * Verification issue interface
 */
export interface VerificationIssue {
    type: 'error' | 'warning' | 'info';
    message: string;
    line?: number;
    column?: number;
    code?: string;
}

/**
 * Code verification interface
 */
export interface CodeVerifier {
    /**
     * Get the name of the verifier
     */
    getName(): string;

    /**
     * Verify code
     *
     * @param code The code to verify
     * @param language The language of the code
     */
    verify(code: string, language: string): Promise<VerificationResult>;
}

/**
 * Syntax verifier
 */
export class SyntaxVerifier implements CodeVerifier {
    private apiClient: HybridApiClient;

    /**
     * Create a new SyntaxVerifier
     *
     * @param apiClient The API client
     */
    constructor(apiClient: HybridApiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Get the name of the verifier
     */
    public getName(): string {
        return 'Syntax Verifier';
    }

    /**
     * Verify code syntax
     *
     * @param code The code to verify
     * @param language The language of the code
     */
    public async verify(code: string, language: string): Promise<VerificationResult> {
        try {
            // Use the API client to verify syntax
            const response = await this.apiClient.generateCode(
                `Verify the syntax of the following ${language} code. Do not explain the code, just check for syntax errors.

\`\`\`${language}
${code}
\`\`\`

Respond with a JSON object with the following structure:
{
  "isValid": boolean,
  "issues": [
    {
      "type": "error" | "warning" | "info",
      "message": string,
      "line": number (optional),
      "column": number (optional),
      "code": string (optional)
    }
  ]
}

If there are no issues, return an empty array for "issues". Return only the JSON object without any explanation or markdown formatting.`,
                'json'
            );

            if (!response.success) {
                return {
                    isValid: false,
                    issues: [{
                        type: 'error',
                        message: 'Failed to verify syntax'
                    }]
                };
            }

            try {
                // Extract JSON from the response
                const jsonMatch = response.code.match(/\{[\s\S]*\}/);
                if (!jsonMatch) {
                    return {
                        isValid: false,
                        issues: [{
                            type: 'error',
                            message: 'Failed to parse verification result'
                        }]
                    };
                }

                const result = JSON.parse(jsonMatch[0]) as VerificationResult;
                return result;
            } catch (error) {
                return {
                    isValid: false,
                    issues: [{
                        type: 'error',
                        message: `Failed to parse verification result: ${error instanceof Error ? error.message : String(error)}`
                    }]
                };
            }
        } catch (error) {
            return {
                isValid: false,
                issues: [{
                    type: 'error',
                    message: `Verification failed: ${error instanceof Error ? error.message : String(error)}`
                }]
            };
        }
    }
}

/**
 * Style verifier
 */
export class StyleVerifier implements CodeVerifier {
    private apiClient: HybridApiClient;

    /**
     * Create a new StyleVerifier
     *
     * @param apiClient The API client
     */
    constructor(apiClient: HybridApiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Get the name of the verifier
     */
    public getName(): string {
        return 'Style Verifier';
    }

    /**
     * Verify code style
     *
     * @param code The code to verify
     * @param language The language of the code
     */
    public async verify(code: string, language: string): Promise<VerificationResult> {
        try {
            // Use the API client to verify style
            const response = await this.apiClient.generateCode(
                `Verify the style of the following ${language} code. Check for style issues like inconsistent naming, indentation, etc.

\`\`\`${language}
${code}
\`\`\`

Respond with a JSON object with the following structure:
{
  "isValid": boolean,
  "issues": [
    {
      "type": "error" | "warning" | "info",
      "message": string,
      "line": number (optional),
      "column": number (optional),
      "code": string (optional)
    }
  ]
}

If there are no issues, return an empty array for "issues". Return only the JSON object without any explanation or markdown formatting.`,
                'json'
            );

            if (!response.success) {
                return {
                    isValid: false,
                    issues: [{
                        type: 'error',
                        message: 'Failed to verify style'
                    }]
                };
            }

            try {
                // Extract JSON from the response
                const jsonMatch = response.code.match(/\{[\s\S]*\}/);
                if (!jsonMatch) {
                    return {
                        isValid: false,
                        issues: [{
                            type: 'error',
                            message: 'Failed to parse verification result'
                        }]
                    };
                }

                const result = JSON.parse(jsonMatch[0]) as VerificationResult;
                return result;
            } catch (error) {
                return {
                    isValid: false,
                    issues: [{
                        type: 'error',
                        message: `Failed to parse verification result: ${error instanceof Error ? error.message : String(error)}`
                    }]
                };
            }
        } catch (error) {
            return {
                isValid: false,
                issues: [{
                    type: 'error',
                    message: `Verification failed: ${error instanceof Error ? error.message : String(error)}`
                }]
            };
        }
    }
}

/**
 * Verification session interface
 */
export interface VerificationSession {
    id: string;
    code: string;
    language: string;
    results: Map<string, VerificationResult>;
    createdAt: number;
}

/**
 * Code verification manager
 */
export class CodeVerificationManager {
    private static instance: CodeVerificationManager;
    private apiClient: HybridApiClient;
    private verifiers: Map<string, CodeVerifier> = new Map();
    private sessions: Map<string, VerificationSession> = new Map();
    private outputChannel: vscode.OutputChannel;
    private _onSessionUpdated: vscode.EventEmitter<VerificationSession> = new vscode.EventEmitter<VerificationSession>();

    /**
     * Event that fires when a session is updated
     */
    public readonly onSessionUpdated: vscode.Event<VerificationSession> = this._onSessionUpdated.event;

    /**
     * Create a new CodeVerificationManager
     *
     * @param apiClient The API client
     */
    private constructor(apiClient: HybridApiClient) {
        this.apiClient = apiClient;
        this.outputChannel = vscode.window.createOutputChannel('MaCoder Code Verification');

        // Register default verifiers
        this.registerVerifier(new SyntaxVerifier(apiClient));
        this.registerVerifier(new StyleVerifier(apiClient));
    }

    /**
     * Get the singleton instance
     *
     * @param apiClient The API client
     */
    public static getInstance(apiClient: HybridApiClient): CodeVerificationManager {
        if (!CodeVerificationManager.instance) {
            CodeVerificationManager.instance = new CodeVerificationManager(apiClient);
        }
        return CodeVerificationManager.instance;
    }

    /**
     * Register a verifier
     *
     * @param verifier The verifier to register
     */
    public registerVerifier(verifier: CodeVerifier): void {
        this.verifiers.set(verifier.getName(), verifier);
        this.log(`Registered verifier: ${verifier.getName()}`);
    }

    /**
     * Get all registered verifiers
     */
    public getVerifiers(): CodeVerifier[] {
        return Array.from(this.verifiers.values());
    }

    /**
     * Create a verification session
     *
     * @param code The code to verify
     * @param language The language of the code
     */
    public createSession(code: string, language: string): VerificationSession {
        const sessionId = generateId();
        const session: VerificationSession = {
            id: sessionId,
            code,
            language,
            results: new Map(),
            createdAt: Date.now()
        };

        this.sessions.set(sessionId, session);
        this.log(`Created verification session: ${sessionId}`);

        return session;
    }

    /**
     * Get a session by ID
     *
     * @param sessionId The session ID
     */
    public getSession(sessionId: string): VerificationSession | undefined {
        return this.sessions.get(sessionId);
    }

    /**
     * Get all sessions
     */
    public getAllSessions(): VerificationSession[] {
        return Array.from(this.sessions.values());
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
        this.log(`Deleted verification session: ${sessionId}`);

        return true;
    }

    /**
     * Verify code using all registered verifiers
     *
     * @param sessionId The session ID
     */
    public async verifyCode(sessionId: string): Promise<Map<string, VerificationResult>> {
        const session = this.sessions.get(sessionId);
        if (!session) {
            throw new Error('Session not found');
        }

        this.log(`Verifying code for session: ${sessionId}`);

        // Clear previous results
        session.results.clear();

        // Run all verifiers
        for (const verifier of this.verifiers.values()) {
            try {
                this.log(`Running verifier: ${verifier.getName()}`);
                const result = await verifier.verify(session.code, session.language);
                session.results.set(verifier.getName(), result);
                this.log(`Verification result: ${result.isValid ? 'Valid' : 'Invalid'} (${result.issues.length} issues)`);
            } catch (error) {
                this.log(`Verifier failed: ${error instanceof Error ? error.message : String(error)}`);
                session.results.set(verifier.getName(), {
                    isValid: false,
                    issues: [{
                        type: 'error',
                        message: `Verifier failed: ${error instanceof Error ? error.message : String(error)}`
                    }]
                });
            }
        }

        // Notify listeners
        this._onSessionUpdated.fire(session);

        return session.results;
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
     * Dispose the code verification manager
     */
    public dispose(): void {
        this.outputChannel.dispose();
        this._onSessionUpdated.dispose();
    }
}