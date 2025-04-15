import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { logger } from '../core/logger';

/**
 * Context level
 */
export enum ContextLevel {
  FILE,
  DIRECTORY,
  PROJECT,
  WORKSPACE
}

/**
 * Context information
 */
export interface ContextInfo {
  level: ContextLevel;
  content: string;
  path?: string;
  language?: string;
  symbols?: vscode.DocumentSymbol[];
  dependencies?: string[];
  imports?: string[];
}

/**
 * Context Engine for code understanding
 */
export class ContextEngine implements vscode.Disposable {
  private disposables: vscode.Disposable[] = [];
  private fileWatcher: vscode.FileSystemWatcher | undefined;
  private cachedContexts: Map<string, ContextInfo> = new Map();
  
  constructor() {
    logger.info('Context Engine initialized');
  }
  
  /**
   * Initializes the context engine
   */
  public async initialize(): Promise<void> {
    try {
      // Create file watcher
      this.fileWatcher = vscode.workspace.createFileSystemWatcher('**/*.{js,ts,jsx,tsx,py,java,c,cpp,cs,go,rb,php,html,css,json,md}');
      
      // Listen for file changes
      this.disposables.push(
        this.fileWatcher.onDidChange(uri => this.invalidateContext(uri.fsPath)),
        this.fileWatcher.onDidCreate(uri => this.invalidateContext(uri.fsPath)),
        this.fileWatcher.onDidDelete(uri => this.invalidateContext(uri.fsPath))
      );
      
      // Listen for editor changes
      this.disposables.push(
        vscode.window.onDidChangeActiveTextEditor(() => this.onActiveEditorChanged()),
        vscode.workspace.onDidChangeTextDocument(e => this.onDocumentChanged(e))
      );
      
      logger.info('Context Engine initialized successfully');
    } catch (error) {
      logger.error('Error initializing Context Engine:', error);
      throw error;
    }
  }
  
  /**
   * Gets context for the current file
   */
  public async getFileContext(uri?: vscode.Uri): Promise<ContextInfo | undefined> {
    try {
      // Get the URI of the current file
      const currentUri = uri || (vscode.window.activeTextEditor?.document.uri);
      
      if (!currentUri) {
        logger.warn('No active editor or URI provided');
        return undefined;
      }
      
      const filePath = currentUri.fsPath;
      
      // Check if context is cached
      if (this.cachedContexts.has(filePath)) {
        return this.cachedContexts.get(filePath);
      }
      
      // Get document
      let document: vscode.TextDocument;
      
      try {
        document = await vscode.workspace.openTextDocument(currentUri);
      } catch (error) {
        logger.error(`Error opening document ${filePath}:`, error);
        return undefined;
      }
      
      // Get document content
      const content = document.getText();
      
      // Get document language
      const language = document.languageId;
      
      // Get document symbols
      let symbols: vscode.DocumentSymbol[] = [];
      
      try {
        symbols = await vscode.commands.executeCommand<vscode.DocumentSymbol[]>(
          'vscode.executeDocumentSymbolProvider',
          currentUri
        ) || [];
      } catch (error) {
        logger.warn(`Error getting symbols for ${filePath}:`, error);
      }
      
      // Create context info
      const contextInfo: ContextInfo = {
        level: ContextLevel.FILE,
        content,
        path: filePath,
        language,
        symbols
      };
      
      // Cache context
      this.cachedContexts.set(filePath, contextInfo);
      
      return contextInfo;
    } catch (error) {
      logger.error('Error getting file context:', error);
      return undefined;
    }
  }
  
  /**
   * Gets context for the current directory
   */
  public async getDirectoryContext(uri?: vscode.Uri): Promise<ContextInfo | undefined> {
    try {
      // Get the URI of the current file
      const currentUri = uri || (vscode.window.activeTextEditor?.document.uri);
      
      if (!currentUri) {
        logger.warn('No active editor or URI provided');
        return undefined;
      }
      
      const filePath = currentUri.fsPath;
      const dirPath = path.dirname(filePath);
      
      // Check if context is cached
      if (this.cachedContexts.has(dirPath)) {
        return this.cachedContexts.get(dirPath);
      }
      
      // Get directory files
      const files = await this.getDirectoryFiles(dirPath);
      
      // Create context info
      const contextInfo: ContextInfo = {
        level: ContextLevel.DIRECTORY,
        content: files.join('\n'),
        path: dirPath
      };
      
      // Cache context
      this.cachedContexts.set(dirPath, contextInfo);
      
      return contextInfo;
    } catch (error) {
      logger.error('Error getting directory context:', error);
      return undefined;
    }
  }
  
  /**
   * Gets context for the current project
   */
  public async getProjectContext(uri?: vscode.Uri): Promise<ContextInfo | undefined> {
    try {
      // Get the URI of the current file
      const currentUri = uri || (vscode.window.activeTextEditor?.document.uri);
      
      if (!currentUri) {
        logger.warn('No active editor or URI provided');
        return undefined;
      }
      
      const filePath = currentUri.fsPath;
      const workspaceFolder = vscode.workspace.getWorkspaceFolder(currentUri);
      
      if (!workspaceFolder) {
        logger.warn(`No workspace folder found for ${filePath}`);
        return undefined;
      }
      
      const projectPath = workspaceFolder.uri.fsPath;
      
      // Check if context is cached
      if (this.cachedContexts.has(projectPath)) {
        return this.cachedContexts.get(projectPath);
      }
      
      // Get project files
      const files = await this.getProjectFiles(projectPath);
      
      // Get project dependencies
      const dependencies = await this.getProjectDependencies(projectPath);
      
      // Create context info
      const contextInfo: ContextInfo = {
        level: ContextLevel.PROJECT,
        content: files.join('\n'),
        path: projectPath,
        dependencies
      };
      
      // Cache context
      this.cachedContexts.set(projectPath, contextInfo);
      
      return contextInfo;
    } catch (error) {
      logger.error('Error getting project context:', error);
      return undefined;
    }
  }
  
  /**
   * Gets context for the current workspace
   */
  public async getWorkspaceContext(): Promise<ContextInfo | undefined> {
    try {
      if (!vscode.workspace.workspaceFolders || vscode.workspace.workspaceFolders.length === 0) {
        logger.warn('No workspace folders found');
        return undefined;
      }
      
      const workspacePath = vscode.workspace.workspaceFolders[0].uri.fsPath;
      
      // Check if context is cached
      if (this.cachedContexts.has(workspacePath)) {
        return this.cachedContexts.get(workspacePath);
      }
      
      // Get workspace folders
      const folders = vscode.workspace.workspaceFolders.map(folder => folder.uri.fsPath);
      
      // Create context info
      const contextInfo: ContextInfo = {
        level: ContextLevel.WORKSPACE,
        content: folders.join('\n'),
        path: workspacePath
      };
      
      // Cache context
      this.cachedContexts.set(workspacePath, contextInfo);
      
      return contextInfo;
    } catch (error) {
      logger.error('Error getting workspace context:', error);
      return undefined;
    }
  }
  
  /**
   * Gets all context levels for the current file
   */
  public async getAllContexts(uri?: vscode.Uri): Promise<ContextInfo[]> {
    try {
      const contexts: ContextInfo[] = [];
      
      // Get file context
      const fileContext = await this.getFileContext(uri);
      if (fileContext) {
        contexts.push(fileContext);
      }
      
      // Get directory context
      const directoryContext = await this.getDirectoryContext(uri);
      if (directoryContext) {
        contexts.push(directoryContext);
      }
      
      // Get project context
      const projectContext = await this.getProjectContext(uri);
      if (projectContext) {
        contexts.push(projectContext);
      }
      
      // Get workspace context
      const workspaceContext = await this.getWorkspaceContext();
      if (workspaceContext) {
        contexts.push(workspaceContext);
      }
      
      return contexts;
    } catch (error) {
      logger.error('Error getting all contexts:', error);
      return [];
    }
  }
  
  /**
   * Gets imports for the current file
   */
  public async getImports(uri?: vscode.Uri): Promise<string[]> {
    try {
      // Get the URI of the current file
      const currentUri = uri || (vscode.window.activeTextEditor?.document.uri);
      
      if (!currentUri) {
        logger.warn('No active editor or URI provided');
        return [];
      }
      
      // Get document
      const document = await vscode.workspace.openTextDocument(currentUri);
      
      // Get document content
      const content = document.getText();
      
      // Get document language
      const language = document.languageId;
      
      // Extract imports based on language
      let imports: string[] = [];
      
      switch (language) {
        case 'javascript':
        case 'typescript':
        case 'javascriptreact':
        case 'typescriptreact':
          imports = this.extractJsImports(content);
          break;
        case 'python':
          imports = this.extractPythonImports(content);
          break;
        case 'java':
          imports = this.extractJavaImports(content);
          break;
        case 'csharp':
          imports = this.extractCSharpImports(content);
          break;
        case 'go':
          imports = this.extractGoImports(content);
          break;
        default:
          logger.warn(`Unsupported language for import extraction: ${language}`);
      }
      
      return imports;
    } catch (error) {
      logger.error('Error getting imports:', error);
      return [];
    }
  }
  
  /**
   * Extracts imports from JavaScript/TypeScript code
   */
  private extractJsImports(content: string): string[] {
    try {
      const imports: string[] = [];
      
      // Match import statements
      const importRegex = /import\s+(?:{[^}]*}|\*\s+as\s+[^;]*|[^;]*)\s+from\s+['"]([^'"]+)['"]/g;
      let match;
      
      while ((match = importRegex.exec(content)) !== null) {
        imports.push(match[1]);
      }
      
      // Match require statements
      const requireRegex = /(?:const|let|var)\s+(?:{[^}]*}|[^=]*)\s*=\s*require\s*\(\s*['"]([^'"]+)['"]\s*\)/g;
      
      while ((match = requireRegex.exec(content)) !== null) {
        imports.push(match[1]);
      }
      
      return imports;
    } catch (error) {
      logger.error('Error extracting JS imports:', error);
      return [];
    }
  }
  
  /**
   * Extracts imports from Python code
   */
  private extractPythonImports(content: string): string[] {
    try {
      const imports: string[] = [];
      
      // Match import statements
      const importRegex = /import\s+([^\s;]+)|from\s+([^\s;]+)\s+import/g;
      let match;
      
      while ((match = importRegex.exec(content)) !== null) {
        imports.push(match[1] || match[2]);
      }
      
      return imports;
    } catch (error) {
      logger.error('Error extracting Python imports:', error);
      return [];
    }
  }
  
  /**
   * Extracts imports from Java code
   */
  private extractJavaImports(content: string): string[] {
    try {
      const imports: string[] = [];
      
      // Match import statements
      const importRegex = /import\s+([^;]+);/g;
      let match;
      
      while ((match = importRegex.exec(content)) !== null) {
        imports.push(match[1]);
      }
      
      return imports;
    } catch (error) {
      logger.error('Error extracting Java imports:', error);
      return [];
    }
  }
  
  /**
   * Extracts imports from C# code
   */
  private extractCSharpImports(content: string): string[] {
    try {
      const imports: string[] = [];
      
      // Match using statements
      const importRegex = /using\s+([^;]+);/g;
      let match;
      
      while ((match = importRegex.exec(content)) !== null) {
        imports.push(match[1]);
      }
      
      return imports;
    } catch (error) {
      logger.error('Error extracting C# imports:', error);
      return [];
    }
  }
  
  /**
   * Extracts imports from Go code
   */
  private extractGoImports(content: string): string[] {
    try {
      const imports: string[] = [];
      
      // Match import statements
      const importRegex = /import\s+\(\s*((?:[^)]+\s*)+)\)/g;
      let match;
      
      while ((match = importRegex.exec(content)) !== null) {
        const importBlock = match[1];
        const importLines = importBlock.split('\n');
        
        for (const line of importLines) {
          const trimmedLine = line.trim();
          if (trimmedLine && !trimmedLine.startsWith('//')) {
            const importMatch = /["']([^"']+)["']/.exec(trimmedLine);
            if (importMatch) {
              imports.push(importMatch[1]);
            }
          }
        }
      }
      
      // Match single import statements
      const singleImportRegex = /import\s+["']([^"']+)["']/g;
      
      while ((match = singleImportRegex.exec(content)) !== null) {
        imports.push(match[1]);
      }
      
      return imports;
    } catch (error) {
      logger.error('Error extracting Go imports:', error);
      return [];
    }
  }
  
  /**
   * Gets files in a directory
   */
  private async getDirectoryFiles(dirPath: string): Promise<string[]> {
    try {
      const files: string[] = [];
      
      // Read directory
      const entries = await fs.promises.readdir(dirPath, { withFileTypes: true });
      
      for (const entry of entries) {
        const entryPath = path.join(dirPath, entry.name);
        
        if (entry.isFile()) {
          files.push(entryPath);
        }
      }
      
      return files;
    } catch (error) {
      logger.error(`Error getting directory files for ${dirPath}:`, error);
      return [];
    }
  }
  
  /**
   * Gets files in a project
   */
  private async getProjectFiles(projectPath: string): Promise<string[]> {
    try {
      const files: string[] = [];
      
      // Find files in the project
      const uris = await vscode.workspace.findFiles(
        new vscode.RelativePattern(projectPath, '**/*.{js,ts,jsx,tsx,py,java,c,cpp,cs,go,rb,php,html,css,json,md}'),
        new vscode.RelativePattern(projectPath, '**/node_modules/**')
      );
      
      for (const uri of uris) {
        files.push(uri.fsPath);
      }
      
      return files;
    } catch (error) {
      logger.error(`Error getting project files for ${projectPath}:`, error);
      return [];
    }
  }
  
  /**
   * Gets dependencies for a project
   */
  private async getProjectDependencies(projectPath: string): Promise<string[]> {
    try {
      const dependencies: string[] = [];
      
      // Check for package.json
      const packageJsonPath = path.join(projectPath, 'package.json');
      
      if (fs.existsSync(packageJsonPath)) {
        try {
          const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
          
          if (packageJson.dependencies) {
            dependencies.push(...Object.keys(packageJson.dependencies));
          }
          
          if (packageJson.devDependencies) {
            dependencies.push(...Object.keys(packageJson.devDependencies));
          }
        } catch (error) {
          logger.warn(`Error parsing package.json at ${packageJsonPath}:`, error);
        }
      }
      
      // Check for requirements.txt
      const requirementsPath = path.join(projectPath, 'requirements.txt');
      
      if (fs.existsSync(requirementsPath)) {
        try {
          const requirements = fs.readFileSync(requirementsPath, 'utf8');
          const lines = requirements.split('\n');
          
          for (const line of lines) {
            const trimmedLine = line.trim();
            if (trimmedLine && !trimmedLine.startsWith('#')) {
              const dependency = trimmedLine.split('==')[0].split('>=')[0].split('<=')[0].trim();
              dependencies.push(dependency);
            }
          }
        } catch (error) {
          logger.warn(`Error parsing requirements.txt at ${requirementsPath}:`, error);
        }
      }
      
      // Check for pom.xml
      const pomPath = path.join(projectPath, 'pom.xml');
      
      if (fs.existsSync(pomPath)) {
        try {
          const pom = fs.readFileSync(pomPath, 'utf8');
          const dependencyRegex = /<dependency>[\s\S]*?<groupId>(.*?)<\/groupId>[\s\S]*?<artifactId>(.*?)<\/artifactId>[\s\S]*?<\/dependency>/g;
          let match;
          
          while ((match = dependencyRegex.exec(pom)) !== null) {
            dependencies.push(`${match[1]}:${match[2]}`);
          }
        } catch (error) {
          logger.warn(`Error parsing pom.xml at ${pomPath}:`, error);
        }
      }
      
      return dependencies;
    } catch (error) {
      logger.error(`Error getting project dependencies for ${projectPath}:`, error);
      return [];
    }
  }
  
  /**
   * Invalidates cached context for a file
   */
  private invalidateContext(filePath: string): void {
    try {
      // Remove file context
      this.cachedContexts.delete(filePath);
      
      // Remove directory context
      const dirPath = path.dirname(filePath);
      this.cachedContexts.delete(dirPath);
      
      // Remove project context
      const workspaceFolder = vscode.workspace.workspaceFolders?.find(folder => {
        return filePath.startsWith(folder.uri.fsPath);
      });
      
      if (workspaceFolder) {
        this.cachedContexts.delete(workspaceFolder.uri.fsPath);
      }
      
      logger.debug(`Invalidated context for ${filePath}`);
    } catch (error) {
      logger.error(`Error invalidating context for ${filePath}:`, error);
    }
  }
  
  /**
   * Handles active editor changes
   */
  private onActiveEditorChanged(): void {
    try {
      const editor = vscode.window.activeTextEditor;
      
      if (editor) {
        // Preload context for the active editor
        this.getFileContext(editor.document.uri).catch(error => {
          logger.error('Error preloading file context:', error);
        });
      }
    } catch (error) {
      logger.error('Error handling active editor change:', error);
    }
  }
  
  /**
   * Handles document changes
   */
  private onDocumentChanged(e: vscode.TextDocumentChangeEvent): void {
    try {
      // Invalidate context for the changed document
      this.invalidateContext(e.document.uri.fsPath);
    } catch (error) {
      logger.error('Error handling document change:', error);
    }
  }
  
  /**
   * Disposes resources
   */
  public dispose(): void {
    try {
      // Dispose all disposables
      for (const disposable of this.disposables) {
        disposable.dispose();
      }
      
      // Dispose file watcher
      this.fileWatcher?.dispose();
      
      // Clear cached contexts
      this.cachedContexts.clear();
      
      logger.info('Context Engine disposed');
    } catch (error) {
      logger.error('Error disposing Context Engine:', error);
    }
  }
}
