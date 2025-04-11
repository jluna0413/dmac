import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import * as crypto from 'crypto';
import { debounce } from './utils';

/**
 * Interface for a file index entry
 */
export interface FileIndexEntry {
    uri: vscode.Uri;
    relativePath: string;
    language: string;
    lastModified: number;
    size: number;
    hash: string;
    symbols?: SymbolInfo[];
}

/**
 * Interface for symbol information
 */
export interface SymbolInfo {
    name: string;
    kind: vscode.SymbolKind;
    range: {
        start: { line: number; character: number };
        end: { line: number; character: number };
    };
    containerName?: string;
    detail?: string;
    children?: SymbolInfo[];
}

/**
 * Interface for project index
 */
export interface ProjectIndex {
    workspaceFolder: string;
    files: Map<string, FileIndexEntry>;
    lastUpdated: number;
    fileCount: number;
    totalSize: number;
}

/**
 * Project indexer for standalone mode
 */
export class ProjectIndexer {
    private static instance: ProjectIndexer;
    private indexes: Map<string, ProjectIndex> = new Map();
    private indexing: boolean = false;
    private pendingIndexes: Set<string> = new Set();
    private fileWatcher: vscode.FileSystemWatcher | undefined;
    private statusBarItem: vscode.StatusBarItem;
    private _onIndexUpdated: vscode.EventEmitter<string> = new vscode.EventEmitter<string>();
    
    /**
     * Event that fires when an index is updated
     */
    public readonly onIndexUpdated: vscode.Event<string> = this._onIndexUpdated.event;

    /**
     * Create a new ProjectIndexer
     */
    private constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
        this.statusBarItem.text = '$(sync) MaCoder: Indexing...';
        this.statusBarItem.tooltip = 'MaCoder is indexing your project';
        this.statusBarItem.command = 'macoder.refreshIndex';
        
        // Set up file watcher
        this.setupFileWatcher();
    }

    /**
     * Get the singleton instance
     */
    public static getInstance(): ProjectIndexer {
        if (!ProjectIndexer.instance) {
            ProjectIndexer.instance = new ProjectIndexer();
        }
        return ProjectIndexer.instance;
    }

    /**
     * Set up file watcher
     */
    private setupFileWatcher(): void {
        // Dispose existing watcher
        if (this.fileWatcher) {
            this.fileWatcher.dispose();
        }
        
        // Create new watcher for all files
        this.fileWatcher = vscode.workspace.createFileSystemWatcher('**/*');
        
        // Handle file creation
        this.fileWatcher.onDidCreate(debounce((uri: vscode.Uri) => {
            this.handleFileChange(uri);
        }, 1000));
        
        // Handle file changes
        this.fileWatcher.onDidChange(debounce((uri: vscode.Uri) => {
            this.handleFileChange(uri);
        }, 1000));
        
        // Handle file deletion
        this.fileWatcher.onDidDelete(debounce((uri: vscode.Uri) => {
            this.handleFileDelete(uri);
        }, 1000));
    }

    /**
     * Handle file change
     * 
     * @param uri The URI of the changed file
     */
    private handleFileChange(uri: vscode.Uri): void {
        // Get workspace folder for the file
        const workspaceFolder = vscode.workspace.getWorkspaceFolder(uri);
        if (!workspaceFolder) {
            return;
        }
        
        // Queue the workspace folder for indexing
        this.queueWorkspaceForIndexing(workspaceFolder.uri.fsPath);
    }

    /**
     * Handle file deletion
     * 
     * @param uri The URI of the deleted file
     */
    private handleFileDelete(uri: vscode.Uri): void {
        // Get workspace folder for the file
        const workspaceFolder = vscode.workspace.getWorkspaceFolder(uri);
        if (!workspaceFolder) {
            return;
        }
        
        // Get the index for the workspace folder
        const index = this.indexes.get(workspaceFolder.uri.fsPath);
        if (!index) {
            return;
        }
        
        // Get the relative path of the file
        const relativePath = path.relative(workspaceFolder.uri.fsPath, uri.fsPath);
        
        // Remove the file from the index
        if (index.files.has(relativePath)) {
            const fileEntry = index.files.get(relativePath)!;
            index.totalSize -= fileEntry.size;
            index.fileCount--;
            index.files.delete(relativePath);
            index.lastUpdated = Date.now();
            
            // Notify listeners
            this._onIndexUpdated.fire(workspaceFolder.uri.fsPath);
        }
    }

    /**
     * Queue a workspace folder for indexing
     * 
     * @param workspacePath The path of the workspace folder
     */
    private queueWorkspaceForIndexing(workspacePath: string): void {
        this.pendingIndexes.add(workspacePath);
        this.processQueue();
    }

    /**
     * Process the queue of pending indexes
     */
    private async processQueue(): Promise<void> {
        if (this.indexing || this.pendingIndexes.size === 0) {
            return;
        }
        
        this.indexing = true;
        
        // Get the next workspace to index
        const workspacePath = this.pendingIndexes.values().next().value;
        this.pendingIndexes.delete(workspacePath);
        
        try {
            // Show status bar item
            this.statusBarItem.show();
            
            // Index the workspace
            await this.indexWorkspace(workspacePath);
            
            // Hide status bar item if no more pending indexes
            if (this.pendingIndexes.size === 0) {
                this.statusBarItem.hide();
            }
        } catch (error) {
            console.error('Error indexing workspace:', error);
        } finally {
            this.indexing = false;
            
            // Process next item in queue
            this.processQueue();
        }
    }

    /**
     * Index a workspace folder
     * 
     * @param workspacePath The path of the workspace folder
     */
    private async indexWorkspace(workspacePath: string): Promise<void> {
        console.log(`Indexing workspace: ${workspacePath}`);
        
        // Create or get existing index
        let index = this.indexes.get(workspacePath);
        if (!index) {
            index = {
                workspaceFolder: workspacePath,
                files: new Map<string, FileIndexEntry>(),
                lastUpdated: Date.now(),
                fileCount: 0,
                totalSize: 0
            };
            this.indexes.set(workspacePath, index);
        }
        
        // Get all files in the workspace
        const pattern = new vscode.RelativePattern(workspacePath, '**/*');
        const excludePattern = this.getExcludePattern();
        
        const files = await vscode.workspace.findFiles(pattern, excludePattern);
        
        // Update progress in status bar
        this.statusBarItem.text = `$(sync) MaCoder: Indexing (0/${files.length})`;
        
        // Process files in batches to avoid blocking the UI
        const batchSize = 100;
        for (let i = 0; i < files.length; i += batchSize) {
            const batch = files.slice(i, i + batchSize);
            
            // Process batch
            await Promise.all(batch.map(async (uri) => {
                await this.indexFile(uri, index!);
            }));
            
            // Update progress
            this.statusBarItem.text = `$(sync) MaCoder: Indexing (${Math.min(i + batchSize, files.length)}/${files.length})`;
        }
        
        // Update index metadata
        index.lastUpdated = Date.now();
        
        // Notify listeners
        this._onIndexUpdated.fire(workspacePath);
        
        console.log(`Indexed ${index.fileCount} files (${this.formatSize(index.totalSize)}) in ${workspacePath}`);
    }

    /**
     * Index a file
     * 
     * @param uri The URI of the file
     * @param index The project index
     */
    private async indexFile(uri: vscode.Uri, index: ProjectIndex): Promise<void> {
        try {
            // Get file stats
            const stats = fs.statSync(uri.fsPath);
            
            // Skip directories
            if (stats.isDirectory()) {
                return;
            }
            
            // Get relative path
            const relativePath = path.relative(index.workspaceFolder, uri.fsPath);
            
            // Check if file is already indexed and unchanged
            const existingEntry = index.files.get(relativePath);
            if (existingEntry && existingEntry.lastModified === stats.mtimeMs) {
                return;
            }
            
            // Get file content
            const content = fs.readFileSync(uri.fsPath, 'utf8');
            
            // Calculate hash
            const hash = crypto.createHash('md5').update(content).digest('hex');
            
            // Get language ID
            const language = this.getLanguageId(uri.fsPath);
            
            // Create file entry
            const fileEntry: FileIndexEntry = {
                uri,
                relativePath,
                language,
                lastModified: stats.mtimeMs,
                size: stats.size,
                hash
            };
            
            // Extract symbols if it's a code file
            if (this.isCodeFile(uri.fsPath)) {
                try {
                    fileEntry.symbols = await this.extractSymbols(uri);
                } catch (error) {
                    console.error(`Error extracting symbols from ${uri.fsPath}:`, error);
                }
            }
            
            // Update index statistics
            if (existingEntry) {
                index.totalSize = index.totalSize - existingEntry.size + stats.size;
            } else {
                index.fileCount++;
                index.totalSize += stats.size;
            }
            
            // Add to index
            index.files.set(relativePath, fileEntry);
        } catch (error) {
            console.error(`Error indexing file ${uri.fsPath}:`, error);
        }
    }

    /**
     * Extract symbols from a file
     * 
     * @param uri The URI of the file
     * @returns The extracted symbols
     */
    private async extractSymbols(uri: vscode.Uri): Promise<SymbolInfo[]> {
        // Get document symbols
        const symbols = await vscode.commands.executeCommand<vscode.DocumentSymbol[]>(
            'vscode.executeDocumentSymbolProvider',
            uri
        );
        
        if (!symbols || symbols.length === 0) {
            return [];
        }
        
        // Convert to SymbolInfo
        return symbols.map(symbol => this.convertSymbol(symbol));
    }

    /**
     * Convert a DocumentSymbol to SymbolInfo
     * 
     * @param symbol The DocumentSymbol
     * @returns The SymbolInfo
     */
    private convertSymbol(symbol: vscode.DocumentSymbol): SymbolInfo {
        return {
            name: symbol.name,
            kind: symbol.kind,
            range: {
                start: {
                    line: symbol.range.start.line,
                    character: symbol.range.start.character
                },
                end: {
                    line: symbol.range.end.line,
                    character: symbol.range.end.character
                }
            },
            detail: symbol.detail,
            children: symbol.children.map(child => this.convertSymbol(child))
        };
    }

    /**
     * Get the language ID for a file
     * 
     * @param filePath The path of the file
     * @returns The language ID
     */
    private getLanguageId(filePath: string): string {
        const extension = path.extname(filePath).toLowerCase();
        
        // Map file extensions to language IDs
        const extensionMap: { [key: string]: string } = {
            '.js': 'javascript',
            '.jsx': 'javascriptreact',
            '.ts': 'typescript',
            '.tsx': 'typescriptreact',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.less': 'less',
            '.json': 'json',
            '.md': 'markdown',
            '.py': 'python',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.rs': 'rust',
            '.swift': 'swift',
            '.sh': 'shellscript',
            '.bat': 'bat',
            '.ps1': 'powershell',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.xml': 'xml',
            '.sql': 'sql'
        };
        
        return extensionMap[extension] || 'plaintext';
    }

    /**
     * Check if a file is a code file
     * 
     * @param filePath The path of the file
     * @returns Whether the file is a code file
     */
    private isCodeFile(filePath: string): boolean {
        const extension = path.extname(filePath).toLowerCase();
        
        // List of code file extensions
        const codeExtensions = [
            '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.scss', '.less',
            '.json', '.py', '.java', '.c', '.cpp', '.cs', '.go', '.rb',
            '.php', '.rs', '.swift', '.sh', '.bat', '.ps1', '.yaml', '.yml',
            '.xml', '.sql'
        ];
        
        return codeExtensions.includes(extension);
    }

    /**
     * Get the exclude pattern for file indexing
     * 
     * @returns The exclude pattern
     */
    private getExcludePattern(): vscode.GlobPattern {
        // Get exclude patterns from settings
        const config = vscode.workspace.getConfiguration('search');
        const excludes = config.get<{ [key: string]: boolean }>('exclude', {});
        
        // Convert to glob pattern
        const patterns = Object.keys(excludes)
            .filter(pattern => excludes[pattern])
            .map(pattern => `**/${pattern}/**`);
        
        // Add common exclude patterns
        patterns.push('**/node_modules/**');
        patterns.push('**/dist/**');
        patterns.push('**/build/**');
        patterns.push('**/.git/**');
        patterns.push('**/.vscode/**');
        
        return `{${patterns.join(',')}}`;
    }

    /**
     * Format a size in bytes to a human-readable string
     * 
     * @param bytes The size in bytes
     * @returns The formatted size
     */
    private formatSize(bytes: number): string {
        const units = ['B', 'KB', 'MB', 'GB', 'TB'];
        let size = bytes;
        let unitIndex = 0;
        
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        
        return `${size.toFixed(2)} ${units[unitIndex]}`;
    }

    /**
     * Index all workspace folders
     */
    public async indexAllWorkspaces(): Promise<void> {
        // Get all workspace folders
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            return;
        }
        
        // Queue all workspace folders for indexing
        for (const folder of workspaceFolders) {
            this.queueWorkspaceForIndexing(folder.uri.fsPath);
        }
    }

    /**
     * Refresh the index for a workspace folder
     * 
     * @param workspacePath The path of the workspace folder
     */
    public async refreshIndex(workspacePath?: string): Promise<void> {
        if (workspacePath) {
            // Refresh specific workspace
            this.queueWorkspaceForIndexing(workspacePath);
        } else {
            // Refresh all workspaces
            await this.indexAllWorkspaces();
        }
    }

    /**
     * Get the index for a workspace folder
     * 
     * @param workspacePath The path of the workspace folder
     * @returns The project index
     */
    public getIndex(workspacePath: string): ProjectIndex | undefined {
        return this.indexes.get(workspacePath);
    }

    /**
     * Get all indexes
     * 
     * @returns All project indexes
     */
    public getAllIndexes(): Map<string, ProjectIndex> {
        return this.indexes;
    }

    /**
     * Search for files in the index
     * 
     * @param query The search query
     * @param options Search options
     * @returns The search results
     */
    public async searchFiles(query: string, options: {
        workspacePath?: string;
        maxResults?: number;
        fileTypes?: string[];
    } = {}): Promise<FileIndexEntry[]> {
        const maxResults = options.maxResults || 100;
        const fileTypes = options.fileTypes || [];
        
        // Normalize query
        const normalizedQuery = query.toLowerCase();
        
        // Get indexes to search
        const indexesToSearch: ProjectIndex[] = [];
        if (options.workspacePath) {
            const index = this.indexes.get(options.workspacePath);
            if (index) {
                indexesToSearch.push(index);
            }
        } else {
            indexesToSearch.push(...this.indexes.values());
        }
        
        // Search for files
        const results: FileIndexEntry[] = [];
        
        for (const index of indexesToSearch) {
            for (const file of index.files.values()) {
                // Skip if file type doesn't match
                if (fileTypes.length > 0 && !fileTypes.includes(file.language)) {
                    continue;
                }
                
                // Check if file matches query
                const fileName = path.basename(file.relativePath).toLowerCase();
                if (fileName.includes(normalizedQuery)) {
                    results.push(file);
                    
                    // Stop if we have enough results
                    if (results.length >= maxResults) {
                        break;
                    }
                }
            }
            
            // Stop if we have enough results
            if (results.length >= maxResults) {
                break;
            }
        }
        
        return results;
    }

    /**
     * Search for symbols in the index
     * 
     * @param query The search query
     * @param options Search options
     * @returns The search results
     */
    public async searchSymbols(query: string, options: {
        workspacePath?: string;
        maxResults?: number;
        symbolKinds?: vscode.SymbolKind[];
    } = {}): Promise<{ file: FileIndexEntry; symbol: SymbolInfo }[]> {
        const maxResults = options.maxResults || 100;
        const symbolKinds = options.symbolKinds || [];
        
        // Normalize query
        const normalizedQuery = query.toLowerCase();
        
        // Get indexes to search
        const indexesToSearch: ProjectIndex[] = [];
        if (options.workspacePath) {
            const index = this.indexes.get(options.workspacePath);
            if (index) {
                indexesToSearch.push(index);
            }
        } else {
            indexesToSearch.push(...this.indexes.values());
        }
        
        // Search for symbols
        const results: { file: FileIndexEntry; symbol: SymbolInfo }[] = [];
        
        for (const index of indexesToSearch) {
            for (const file of index.files.values()) {
                // Skip files without symbols
                if (!file.symbols) {
                    continue;
                }
                
                // Search for symbols in the file
                const matchingSymbols = this.findMatchingSymbols(file.symbols, normalizedQuery, symbolKinds);
                
                // Add matching symbols to results
                for (const symbol of matchingSymbols) {
                    results.push({ file, symbol });
                    
                    // Stop if we have enough results
                    if (results.length >= maxResults) {
                        break;
                    }
                }
                
                // Stop if we have enough results
                if (results.length >= maxResults) {
                    break;
                }
            }
            
            // Stop if we have enough results
            if (results.length >= maxResults) {
                break;
            }
        }
        
        return results;
    }

    /**
     * Find symbols matching a query
     * 
     * @param symbols The symbols to search
     * @param query The search query
     * @param symbolKinds The symbol kinds to include
     * @returns The matching symbols
     */
    private findMatchingSymbols(
        symbols: SymbolInfo[],
        query: string,
        symbolKinds: vscode.SymbolKind[]
    ): SymbolInfo[] {
        const results: SymbolInfo[] = [];
        
        for (const symbol of symbols) {
            // Check if symbol kind matches
            if (symbolKinds.length > 0 && !symbolKinds.includes(symbol.kind)) {
                continue;
            }
            
            // Check if symbol name matches query
            if (symbol.name.toLowerCase().includes(query)) {
                results.push(symbol);
            }
            
            // Check children
            if (symbol.children && symbol.children.length > 0) {
                const matchingChildren = this.findMatchingSymbols(symbol.children, query, symbolKinds);
                results.push(...matchingChildren);
            }
        }
        
        return results;
    }

    /**
     * Dispose the indexer
     */
    public dispose(): void {
        if (this.fileWatcher) {
            this.fileWatcher.dispose();
        }
        
        if (this.statusBarItem) {
            this.statusBarItem.dispose();
        }
        
        this._onIndexUpdated.dispose();
    }
}
