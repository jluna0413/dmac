# MaCoder Developer Documentation

This document provides information for developers who want to understand or contribute to the MaCoder VS Code extension.

## Architecture

MaCoder is designed with a hybrid architecture that allows it to work both with the DMac server (integrated mode) and completely independently (standalone mode).

### Core Components

#### 1. API Clients

- **HybridApiClient**: The main client that dynamically switches between DMac and standalone modes
- **MaCoderApiClient**: Client for communicating with the DMac server
- **StandaloneApiClient**: Client for standalone operation without external dependencies

#### 2. Model Providers

- **LocalModelInterface**: Interface for local model providers
- **OllamaProvider**: Provider for Ollama models
- **LMStudioProvider**: Provider for LM Studio models

#### 3. Project Indexing

- **ProjectIndexer**: Indexes the workspace for better context awareness in standalone mode
- Includes file watching, symbol extraction, and search functionality

#### 4. Autonomous Mode

- **AutonomousMode**: Manages autonomous coding tasks
- **AutonomousPanel**: UI for interacting with autonomous mode
- Includes task parsing, execution, and tracking

#### 5. Brainstorming

- **BrainstormingManager**: Manages brainstorming sessions and roadmaps
- **BrainstormingPanel**: UI for brainstorming and roadmap generation
- Includes idea generation, organization, and roadmap creation

#### 6. Deep Reasoning

- **DeepReasoningManager**: Manages deep reasoning chains
- **DeepReasoningPanel**: UI for deep reasoning
- Includes problem analysis, thought generation, and conclusion formation

#### 7. Code Verification

- **CodeVerificationManager**: Manages code verification
- **SyntaxVerifier**: Verifies code syntax
- **StyleVerifier**: Verifies code style
- Integration with VS Code's Problems panel

#### 8. Enhanced Context Awareness

- **FileCodeEditLogger**: Logs code edits to file
- **CodeEditTracker**: Tracks code changes in real-time
- **CodeEdit**: Represents a single code edit
- **CodeEditSession**: Groups related edits together

#### 9. Sandbox Testing and Debugging

- **LocalCodeSandbox**: Executes code in a local sandbox environment
- **SandboxPanel**: UI for the sandbox
- **SandboxTest**: Represents a test case
- **SandboxResult**: Represents the result of code execution

#### 10. UI Components

- **ChatPanel**: UI for chat interactions
- **NextEditPanel**: UI for next edit guidance
- Various webview panels for different features

#### 11. Integration

- **LaminarService**: Integration with Laminar for tracing and evaluation
- **CompletionsProvider**: Integration with VS Code's completion system

## Code Organization

- **src/**: Source code for the extension
  - **api-client.ts**: DMac API client
  - **standalone-api-client.ts**: Standalone API client
  - **hybrid-api-client.ts**: Hybrid API client
  - **local-model-interface.ts**: Interface for local models
  - **project-indexer.ts**: Project indexing system
  - **autonomous-mode.ts**: Autonomous mode implementation
  - **autonomous-panel.ts**: UI for autonomous mode
  - **brainstorming.ts**: Brainstorming and roadmap implementation
  - **brainstorming-panel.ts**: UI for brainstorming
  - **deep-reasoning.ts**: Deep reasoning implementation
  - **deep-reasoning-panel.ts**: UI for deep reasoning
  - **code-verification.ts**: Code verification implementation
  - **code-edit-logger.ts**: Code edit logging implementation
  - **code-edit-tracker.ts**: Code edit tracking implementation
  - **code-sandbox.ts**: Sandbox implementation
  - **sandbox-panel.ts**: UI for sandbox
  - **chat-panel.ts**: UI for chat
  - **next-edit-panel.ts**: UI for next edit
  - **completions-provider.ts**: Code completions provider
  - **laminar-service.ts**: Laminar integration
  - **utils.ts**: Utility functions
  - **extension.ts**: Main extension entry point
- **media/**: UI resources
  - **autonomous-panel.js**: JavaScript for autonomous panel
  - **autonomous-panel.css**: CSS for autonomous panel
  - **brainstorming-panel.js**: JavaScript for brainstorming panel
  - **brainstorming-panel.css**: CSS for brainstorming panel
  - **deep-reasoning-panel.js**: JavaScript for deep reasoning panel
  - **deep-reasoning-panel.css**: CSS for deep reasoning panel
  - Other UI resources

## Development Workflow

### Setting Up the Development Environment

1. Clone the repository
2. Run `npm install` to install dependencies
3. Open the project in VS Code
4. Press F5 to launch the extension in debug mode

### Adding a New Feature

1. Identify the component that needs to be modified
2. Make changes to the relevant files
3. Update the UI if necessary
4. Add any new commands to package.json
5. Register commands in extension.ts
6. Update documentation and CHANGELOG.md
7. Test the changes

### Testing

- Manual testing in VS Code
- Unit tests (to be implemented)
- Integration tests (to be implemented)

## Extension Settings

See README.md for a complete list of settings.

## API Reference

### HybridApiClient

The main client that dynamically switches between DMac and standalone modes.

```typescript
class HybridApiClient {
    constructor(serverUrl: string, modelName: string, preferStandalone: boolean);

    // Mode management
    getCurrentMode(): 'dmac' | 'standalone';
    setPreferredMode(preferStandalone: boolean): void;
    onModeChange(listener: () => void): void;

    // API methods
    async generateCode(prompt: string, language?: string): Promise<any>;
    async explainCode(code: string, language?: string): Promise<any>;
    async refactorCode(code: string, instructions: string, language?: string): Promise<any>;
    async findBugs(code: string, language?: string): Promise<any>;
    async generateTests(code: string, language?: string): Promise<any>;
    async documentCode(code: string, language?: string): Promise<any>;
    async searchCode(query: string, maxResults?: number): Promise<any>;
    async refreshIndex(): Promise<any>;
    async getProjectSummary(): Promise<any>;
    async benchmarkModels(task: string, models: string[]): Promise<any>;
}
```

### ProjectIndexer

Indexes the workspace for better context awareness in standalone mode.

```typescript
class ProjectIndexer {
    static getInstance(): ProjectIndexer;

    async indexAllWorkspaces(): Promise<void>;
    async refreshIndex(workspacePath?: string): Promise<void>;
    getIndex(workspacePath: string): ProjectIndex | undefined;
    async searchFiles(query: string, options?: SearchOptions): Promise<FileIndexEntry[]>;
    async searchSymbols(query: string, options?: SearchOptions): Promise<SymbolSearchResult[]>;
}
```

### AutonomousMode

Manages autonomous coding tasks.

```typescript
class AutonomousMode {
    static getInstance(apiClient: HybridApiClient): AutonomousMode;

    start(): void;
    stop(): void;
    toggle(): void;
    isActive(): boolean;

    createTask(description: string, parentId?: string): Task;
    startTask(taskId: string): boolean;
    completeTask(taskId: string, result?: any): boolean;
    failTask(taskId: string, error: string): boolean;
    cancelTask(taskId: string): boolean;

    async executeTask(description: string): Promise<any>;
}
```

### BrainstormingManager

Manages brainstorming sessions and roadmaps.

```typescript
class BrainstormingManager {
    static getInstance(apiClient: HybridApiClient): BrainstormingManager;

    createSession(topic: string, description: string): BrainstormingSession;
    getSession(sessionId: string): BrainstormingSession | undefined;
    getAllSessions(): BrainstormingSession[];
    updateSession(sessionId: string, updates: Partial<BrainstormingSession>): boolean;
    deleteSession(sessionId: string): boolean;

    addIdea(sessionId: string, content: string, category?: string, tags?: string[], parentId?: string): Idea | undefined;
    connectIdeas(sessionId: string, ideaId1: string, ideaId2: string): boolean;
    async generateIdeas(sessionId: string, count?: number): Promise<Idea[]>;

    async createRoadmapFromSession(sessionId: string, title: string, description: string): Promise<Roadmap>;
    getRoadmap(roadmapId: string): Roadmap | undefined;
    getAllRoadmaps(): Roadmap[];
    updateRoadmap(roadmapId: string, updates: Partial<Roadmap>): boolean;
    deleteRoadmap(roadmapId: string): boolean;
    updateRoadmapItem(roadmapId: string, itemId: string, updates: Partial<RoadmapItem>): boolean;
}
```

### DeepReasoningManager

Manages deep reasoning chains for complex problem analysis.

```typescript
class DeepReasoningManager {
    static getInstance(apiClient: HybridApiClient): DeepReasoningManager;

    createChain(topic: string, description: string): ReasoningChain;
    getChain(chainId: string): ReasoningChain | undefined;
    getAllChains(): ReasoningChain[];
    updateChain(chainId: string, updates: Partial<ReasoningChain>): boolean;
    deleteChain(chainId: string): boolean;

    addStep(chainId: string, content: string, type: 'observation' | 'thought' | 'action' | 'conclusion'): ReasoningStep | undefined;

    async performReasoning(problem: string, context?: string): Promise<ReasoningChain>;
}
```

### CodeVerificationManager

Manages code verification for syntax and style.

```typescript
class CodeVerificationManager {
    static getInstance(apiClient: HybridApiClient): CodeVerificationManager;

    registerVerifier(verifier: CodeVerifier): void;
    getVerifiers(): CodeVerifier[];

    createSession(code: string, language: string): VerificationSession;
    getSession(sessionId: string): VerificationSession | undefined;
    getAllSessions(): VerificationSession[];
    deleteSession(sessionId: string): boolean;

    async verifyCode(sessionId: string): Promise<Map<string, VerificationResult>>;
}
```

### FileCodeEditLogger

Logs code edits for enhanced context awareness.

```typescript
class FileCodeEditLogger implements CodeEditLogger {
    static getInstance(context: vscode.ExtensionContext): FileCodeEditLogger;

    startSession(description?: string): string;
    endSession(sessionId: string): void;
    getCurrentSessionId(): string | null;

    logEdit(edit: CodeEdit): void;
    getEditsForFile(filePath: string): CodeEdit[];
    getEditsInSession(sessionId: string): CodeEdit[];
    getAllSessions(): CodeEditSession[];
    getSession(sessionId: string): CodeEditSession | null;
    getAllEdits(): CodeEdit[];
    clearEdits(): void;
}
```

### LocalCodeSandbox

Executes code in a local sandbox environment.

```typescript
class LocalCodeSandbox implements CodeSandbox {
    static getInstance(context: vscode.ExtensionContext): LocalCodeSandbox;

    executeCode(code: string, language: string): Promise<SandboxResult>;
    createTest(name: string, code: string, language: string): SandboxTest;
    runTest(testId: string): Promise<SandboxResult>;
    getTest(testId: string): SandboxTest | undefined;
    getAllTests(): SandboxTest[];
    deleteTest(testId: string): boolean;

    dispose(): void;
}
```

## Future Development

See the roadmap in README.md for planned features.

## Known Issues and Limitations

See the known issues section in README.md.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
