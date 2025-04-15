import * as vscode from 'vscode';
import { MaCoderApiClient } from './api-client';

/**
 * Completion item provider for MaCoder.
 */
export class MaCoderCompletionItemProvider implements vscode.CompletionItemProvider {
    private apiClient: MaCoderApiClient;
    private cache: Map<string, vscode.CompletionItem[]> = new Map();
    private cacheTimeout: number = 60000; // 1 minute
    private lastCacheCleanup: number = Date.now();

    /**
     * Create a new MaCoderCompletionItemProvider.
     * 
     * @param apiClient The API client
     */
    constructor(apiClient: MaCoderApiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Provide completion items for the given position.
     * 
     * @param document The document in which the completion was requested
     * @param position The position at which the completion was requested
     * @param token A cancellation token
     * @param context The completion context
     * @returns A list of completion items or a thenable that resolves to such
     */
    async provideCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken,
        context: vscode.CompletionContext
    ): Promise<vscode.CompletionItem[] | vscode.CompletionList> {
        // Clean up cache if needed
        this.cleanupCache();

        // Get the current line and prefix
        const linePrefix = document.lineAt(position).text.substring(0, position.character);
        
        // Skip if the line is empty or only whitespace
        if (!linePrefix.trim()) {
            return [];
        }

        // Skip if the user is typing a comment
        if (this.isComment(document, position)) {
            return [];
        }

        // Check cache
        const cacheKey = `${document.uri.fsPath}:${position.line}:${position.character}:${linePrefix}`;
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey) || [];
        }

        try {
            // Get the text up to the cursor position
            const text = document.getText(new vscode.Range(new vscode.Position(0, 0), position));
            const cursorPosition = text.length;
            
            // Get completions from the API
            const response = await this.apiClient.completeCode(
                text,
                cursorPosition,
                document.languageId
            );

            if (response.success && response.completion) {
                // Create completion items
                const completionItems = this.createCompletionItems(response.completion, position, document);
                
                // Cache the results
                this.cache.set(cacheKey, completionItems);
                
                return completionItems;
            }
        } catch (error) {
            console.error('Error providing completions:', error);
        }

        return [];
    }

    /**
     * Resolve additional information for a completion item.
     * 
     * @param item The completion item to resolve
     * @param token A cancellation token
     * @returns The resolved completion item or a thenable that resolves to such
     */
    resolveCompletionItem(
        item: vscode.CompletionItem,
        token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.CompletionItem> {
        // Add documentation if not already present
        if (!item.documentation && item.detail) {
            item.documentation = new vscode.MarkdownString(item.detail);
        }
        
        return item;
    }

    /**
     * Create completion items from the completion text.
     * 
     * @param completion The completion text
     * @param position The position at which the completion was requested
     * @param document The document in which the completion was requested
     * @returns A list of completion items
     */
    private createCompletionItems(
        completion: string,
        position: vscode.Position,
        document: vscode.TextDocument
    ): vscode.CompletionItem[] {
        // Split the completion into lines
        const lines = completion.split('\n');
        
        if (lines.length === 0) {
            return [];
        }
        
        // Create a completion item for the entire completion
        const fullCompletion = new vscode.CompletionItem(completion);
        fullCompletion.insertText = new vscode.SnippetString(this.escapeSnippetText(completion));
        fullCompletion.detail = 'MaCoder completion';
        fullCompletion.documentation = new vscode.MarkdownString('```' + document.languageId + '\n' + completion + '\n```');
        fullCompletion.kind = vscode.CompletionItemKind.Snippet;
        fullCompletion.sortText = '0000';
        
        // For single-line completions, also offer word-based completions
        if (lines.length === 1) {
            const words = this.splitIntoWords(completion);
            const items: vscode.CompletionItem[] = [fullCompletion];
            
            words.forEach((word, index) => {
                if (word.length > 1) {
                    const item = new vscode.CompletionItem(word);
                    item.insertText = word;
                    item.kind = vscode.CompletionItemKind.Text;
                    item.sortText = `0001${index.toString().padStart(4, '0')}`;
                    items.push(item);
                }
            });
            
            return items;
        }
        
        return [fullCompletion];
    }

    /**
     * Split a string into words.
     * 
     * @param text The text to split
     * @returns An array of words
     */
    private splitIntoWords(text: string): string[] {
        // Split on common delimiters
        return text.split(/[\s\(\)\[\]\{\}\.\,\;\:\+\-\*\/\=\<\>\!\?\&\|\^\%\#\@\~]+/)
            .filter(word => word.length > 0);
    }

    /**
     * Escape special characters in snippet text.
     * 
     * @param text The text to escape
     * @returns The escaped text
     */
    private escapeSnippetText(text: string): string {
        return text
            .replace(/\$/g, '\\$')
            .replace(/\}/g, '\\}')
            .replace(/\{/g, '\\{');
    }

    /**
     * Check if the position is inside a comment.
     * 
     * @param document The document
     * @param position The position
     * @returns True if the position is inside a comment
     */
    private isComment(document: vscode.TextDocument, position: vscode.Position): boolean {
        // This is a simplified implementation
        // In a real implementation, you would use the language's tokenizer
        
        const line = document.lineAt(position).text;
        
        // Check for single-line comments
        if (document.languageId === 'javascript' || document.languageId === 'typescript' ||
            document.languageId === 'java' || document.languageId === 'c' || document.languageId === 'cpp' ||
            document.languageId === 'csharp' || document.languageId === 'go' || document.languageId === 'rust' ||
            document.languageId === 'swift' || document.languageId === 'php') {
            // Check for // comments
            const commentIndex = line.indexOf('//');
            if (commentIndex >= 0 && position.character > commentIndex) {
                return true;
            }
        }
        
        if (document.languageId === 'python' || document.languageId === 'yaml' ||
            document.languageId === 'shellscript' || document.languageId === 'perl' ||
            document.languageId === 'ruby') {
            // Check for # comments
            const commentIndex = line.indexOf('#');
            if (commentIndex >= 0 && position.character > commentIndex) {
                return true;
            }
        }
        
        // For multi-line comments, a more sophisticated approach would be needed
        
        return false;
    }

    /**
     * Clean up the cache.
     */
    private cleanupCache(): void {
        const now = Date.now();
        
        // Only clean up once per minute
        if (now - this.lastCacheCleanup < 60000) {
            return;
        }
        
        this.lastCacheCleanup = now;
        
        // Remove entries older than the cache timeout
        for (const [key, value] of this.cache.entries()) {
            const timestamp = parseInt(key.split(':')[0]);
            if (now - timestamp > this.cacheTimeout) {
                this.cache.delete(key);
            }
        }
    }
}
