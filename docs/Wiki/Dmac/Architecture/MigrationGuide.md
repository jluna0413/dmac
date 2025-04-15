# Migration Guide: VS Code Extension to Shared Packages

This guide provides step-by-step instructions for migrating code from the VS Code extension to the shared packages architecture.

## Overview

The migration process is incremental, allowing us to gradually move code from the VS Code extension to the shared packages without disrupting the existing functionality. The goal is to extract reusable code while keeping VS Code-specific code in the extension.

### Terminology Clarification

- **DMac Platform**: Refers to our entire ecosystem of tools, services, and components.
- **DMac-agent**: Refers to the main agent that users interface with, which also orchestrates agent management via OpenManus-RL or passes information to the model that operates OpenManus-RL.

## Migration Steps

### Step 1: Identify Candidates for Migration

Before migrating any code, identify components that are good candidates for extraction:

- **Domain models**: Data structures that represent core concepts
- **Business logic**: Functions and services that implement core functionality
- **Utilities**: Helper functions that are not tied to VS Code
- **UI components**: Reusable UI components used in webviews

### Step 2: Extract Domain Models

Domain models are usually the easiest to extract since they have minimal dependencies.

1. **Identify domain models**: Look for interfaces, types, and classes that represent core concepts.

2. **Create corresponding files in the core package**:
   ```typescript
   // packages/core/src/models/model.ts
   export interface Model {
     id: string;
     name: string;
     provider: string;
     contextLength: number;
     capabilities: string[];
   }
   ```

3. **Export from the package index**:
   ```typescript
   // packages/core/src/index.ts
   export * from './models/model';
   ```

4. **Update imports in the VS Code extension**:
   ```typescript
   // Before
   import { Model } from './models/model';

   // After
   import { Model } from '@dmac/core';
   ```

### Step 3: Extract Business Logic

Business logic can be more complex to extract due to dependencies, but the process is similar:

1. **Identify business logic**: Look for services, managers, and other classes that implement core functionality.

2. **Create corresponding files in the core package**:
   ```typescript
   // packages/core/src/services/model-service.ts
   import { Model } from '../models/model';

   export interface ModelService {
     getModels(): Promise<Model[]>;
     getModel(id: string): Promise<Model>;
   }

   export class BaseModelService implements ModelService {
     async getModels(): Promise<Model[]> {
       // Implementation
       return [];
     }

     async getModel(id: string): Promise<Model> {
       // Implementation
       return {} as Model;
     }
   }
   ```

3. **Export from the package index**:
   ```typescript
   // packages/core/src/index.ts
   export * from './services/model-service';
   ```

4. **Create adapters in the VS Code extension**:
   ```typescript
   // vscode-macoder/src/services/vscode-model-service.ts
   import { BaseModelService, Model } from '@dmac/core';
   import * as vscode from 'vscode';

   export class VsCodeModelService extends BaseModelService {
     constructor(private context: vscode.ExtensionContext) {
       super();
     }

     // Override methods as needed for VS Code-specific functionality
     async getModels(): Promise<Model[]> {
       const models = await super.getModels();
       // Add VS Code-specific logic
       return models;
     }
   }
   ```

### Step 4: Extract API Clients

API clients are good candidates for extraction since they often have minimal dependencies on the VS Code API:

1. **Identify API clients**: Look for classes that communicate with external services.

2. **Create corresponding files in the API package**:
   ```typescript
   // packages/api/src/clients/model-api-client.ts
   import { Model } from '@dmac/core';

   export class ModelApiClient {
     constructor(private baseUrl: string) {}

     async getModels(): Promise<Model[]> {
       // Implementation
       return [];
     }

     async getModel(id: string): Promise<Model> {
       // Implementation
       return {} as Model;
     }
   }
   ```

3. **Export from the package index**:
   ```typescript
   // packages/api/src/index.ts
   export * from './clients/model-api-client';
   ```

4. **Update imports in the VS Code extension**:
   ```typescript
   // Before
   import { ModelApiClient } from './api/model-api-client';

   // After
   import { ModelApiClient } from '@dmac/api';
   ```

### Step 5: Extract UI Components

UI components used in webviews can be extracted to the UI package:

1. **Identify UI components**: Look for React components or HTML templates used in webviews.

2. **Create corresponding files in the UI package**:
   ```typescript
   // packages/ui/src/components/chat/chat-message.tsx
   import React from 'react';

   export interface ChatMessageProps {
     content: string;
     sender: 'user' | 'assistant';
     timestamp: Date;
   }

   export const ChatMessage: React.FC<ChatMessageProps> = ({
     content,
     sender,
     timestamp,
   }) => {
     return (
       <div className={`chat-message ${sender}`}>
         <div className="content">{content}</div>
         <div className="timestamp">{timestamp.toLocaleTimeString()}</div>
       </div>
     );
   };
   ```

3. **Export from the package index**:
   ```typescript
   // packages/ui/src/index.ts
   export * from './components/chat/chat-message';
   ```

4. **Update webview code in the VS Code extension**:
   ```typescript
   // Before
   const getWebviewContent = (messages) => {
     return `
       <html>
         <body>
           ${messages.map(m => `
             <div class="chat-message ${m.sender}">
               <div class="content">${m.content}</div>
               <div class="timestamp">${new Date(m.timestamp).toLocaleTimeString()}</div>
             </div>
           `).join('')}
         </body>
       </html>
     `;
   };

   // After (using React)
   import { ChatMessage } from '@dmac/ui';
   import * as React from 'react';
   import * as ReactDOMServer from 'react-dom/server';

   const getWebviewContent = (messages) => {
     const messagesHtml = ReactDOMServer.renderToString(
       <>
         {messages.map(m => (
           <ChatMessage
             key={m.id}
             content={m.content}
             sender={m.sender}
             timestamp={new Date(m.timestamp)}
           />
         ))}
       </>
     );

     return `
       <html>
         <body>
           ${messagesHtml}
         </body>
       </html>
     `;
   };
   ```

### Step 6: Extract State Management

State management can be extracted to the state package:

1. **Identify state management code**: Look for Redux slices, actions, reducers, and selectors.

2. **Create corresponding files in the state package**:
   ```typescript
   // packages/state/src/slices/models.ts
   import { createSlice, PayloadAction } from '@reduxjs/toolkit';
   import { Model } from '@dmac/core';

   interface ModelsState {
     items: Model[];
     selectedModel: string | null;
     loading: boolean;
     error: string | null;
   }

   const initialState: ModelsState = {
     items: [],
     selectedModel: null,
     loading: false,
     error: null,
   };

   const modelsSlice = createSlice({
     name: 'models',
     initialState,
     reducers: {
       setModels: (state, action: PayloadAction<Model[]>) => {
         state.items = action.payload;
       },
       setSelectedModel: (state, action: PayloadAction<string>) => {
         state.selectedModel = action.payload;
       },
     },
   });

   export const { setModels, setSelectedModel } = modelsSlice.actions;
   export default modelsSlice.reducer;
   ```

3. **Export from the package index**:
   ```typescript
   // packages/state/src/index.ts
   export * from './slices/models';
   ```

4. **Update imports in the VS Code extension**:
   ```typescript
   // Before
   import { setModels, setSelectedModel } from './state/models';

   // After
   import { setModels, setSelectedModel } from '@dmac/state';
   ```

## Testing the Migration

After migrating each component, test the functionality to ensure it still works as expected:

1. **Build the shared packages**:
   ```bash
   npm run build --workspace=@dmac/core
   npm run build --workspace=@dmac/ui
   npm run build --workspace=@dmac/api
   npm run build --workspace=@dmac/state
   ```

2. **Build and test the VS Code extension**:
   ```bash
   cd vscode-macoder
   npm run build
   npm test
   ```

3. **Launch the extension in the VS Code Extension Development Host**:
   - Press F5 in VS Code
   - Test the functionality manually

## Troubleshooting

### Import Resolution Issues

If you encounter issues with import resolution:

1. **Check the tsconfig.json paths**:
   ```json
   {
     "compilerOptions": {
       "paths": {
         "@dmac/core": ["packages/core/src"],
         "@dmac/core/*": ["packages/core/src/*"],
         // ...
       }
     }
   }
   ```

2. **Check the package.json dependencies**:
   ```json
   {
     "dependencies": {
       "@dmac/core": "^0.1.0",
       "@dmac/ui": "^0.1.0",
       "@dmac/api": "^0.1.0",
       "@dmac/state": "^0.1.0"
     }
   }
   ```

3. **Use relative imports if necessary**:
   ```typescript
   // If path aliases don't work
   import { Model } from '../../packages/core/src/models/model';
   ```

### Build Issues

If you encounter build issues:

1. **Check for circular dependencies**:
   - Ensure that packages don't have circular dependencies
   - Use interfaces to break circular dependencies

2. **Check for missing exports**:
   - Ensure that all required types and functions are exported from the package index

3. **Check for VS Code API dependencies**:
   - Ensure that shared packages don't depend on the VS Code API
   - Use dependency injection or adapters for VS Code-specific functionality

## Conclusion

By following this guide, you can incrementally migrate code from the VS Code extension to the shared packages architecture. This approach allows you to extract reusable code while keeping the existing functionality intact, providing a path to a more maintainable and scalable codebase.
