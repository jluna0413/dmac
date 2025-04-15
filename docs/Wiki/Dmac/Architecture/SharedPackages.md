# DMac Shared Packages Architecture

## Overview

The DMac Platform uses a shared packages architecture to promote code reuse and maintainability. This approach allows us to extract common functionality into reusable packages while keeping the existing VS Code extension structure intact.

### Terminology Clarification

- **DMac Platform**: Refers to our entire ecosystem of tools, services, and components.
- **DMac-agent**: Refers to the main agent that users interface with, which also orchestrates agent management via OpenManus-RL or passes information to the model that operates OpenManus-RL.

## Architecture

```
dmac/
├── packages/               # Shared packages
│   ├── core/               # Core business logic
│   ├── ui/                 # UI components
│   ├── api/                # API layer
│   └── state/              # State management
├── vscode-macoder/         # VS Code extension (existing)
├── workspace.code-workspace # VS Code workspace configuration
└── root-package.json       # Root package.json for workspace management
```

## Shared Packages

### Core Package (`@dmac/core`)

The core package contains the domain models, business logic, and utilities that are shared across all applications. It is platform-agnostic and does not depend on any UI framework.

**Key components:**
- Domain models
- Business logic services
- Utility functions

### UI Package (`@dmac/ui`)

The UI package contains reusable UI components built with React and Material UI. These components are used by the web and desktop applications, as well as the VS Code extension's webviews.

**Key components:**
- Button components
- Chat components
- Code components
- Layout components
- Hooks
- Themes

### API Package (`@dmac/api`)

The API package provides a consistent interface for interacting with backend services. It includes API clients, models, and middleware.

**Key components:**
- API clients
- Request/response models
- API middleware

### State Package (`@dmac/state`)

The state package manages application state using Redux Toolkit. It provides a centralized store, actions, reducers, and selectors.

**Key components:**
- Redux store
- Slices (reducers + actions)
- Selectors
- Middleware

## Integration with VS Code Extension

The VS Code extension (`vscode-macoder`) remains in its current location but gradually adopts the shared packages for common functionality. This allows for an incremental migration without disrupting the existing codebase.

### Integration Steps

1. **Add package dependencies**: Update the VS Code extension's `package.json` to include the shared packages as dependencies.

2. **Import shared functionality**: Replace existing code with imports from the shared packages.

3. **Adapt platform-specific code**: Create adapters or wrappers for VS Code-specific functionality.

## Development Workflow

### Setting Up the Development Environment

1. Open the workspace in VS Code:
   ```
   code workspace.code-workspace
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Build the shared packages:
   ```
   npm run build --workspace=@dmac/core
   npm run build --workspace=@dmac/ui
   npm run build --workspace=@dmac/api
   npm run build --workspace=@dmac/state
   ```

### Making Changes

1. **Shared packages**: Make changes to the shared packages when implementing functionality that should be reused across different applications.

2. **VS Code extension**: Make changes to the VS Code extension when implementing VS Code-specific functionality.

## Benefits of This Approach

- **Incremental adoption**: The existing VS Code extension continues to work while we gradually migrate to the shared packages.
- **Code reuse**: Common functionality is extracted into reusable packages.
- **Maintainability**: Changes to shared functionality only need to be made in one place.
- **Future-proofing**: The architecture supports future applications (web, desktop) while maintaining the existing VS Code extension.

## Future Considerations

As the project evolves, we may consider:

1. **Additional shared packages**: Creating more specialized packages for specific domains.
2. **Web and desktop applications**: Building new applications that use the shared packages.
3. **Platform-specific optimizations**: Implementing performance-critical components with platform-specific code.

## Conclusion

The shared packages architecture provides a pragmatic approach to code sharing and maintainability while respecting the existing VS Code extension structure. It allows for incremental adoption and provides a clear path for future development.
