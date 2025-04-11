# Code Organization and Best Practices

This document outlines the code organization, style guidelines, and best practices for the DMac project.

## Directory Structure

```
dmac/
├── agents/                  # Agent definitions and orchestration
│   ├── cody/                # Coding agent
│   ├── perry/               # Manufacturing agent
│   ├── shelly/              # Design agent
│   └── flora/               # UI agent
├── benchmarking/            # Benchmarking tools and results
├── config/                  # Configuration files
├── dashboard/               # Web interface
│   ├── static/              # Static assets (CSS, JS, images)
│   │   ├── css/             # CSS files
│   │   ├── js/              # JavaScript files
│   │   └── images/          # Image assets
│   └── templates/           # HTML templates
├── data/                    # Data storage
│   ├── agents/              # Agent-specific data
│   ├── benchmarks/          # Benchmark definitions
│   ├── benchmark_results/   # Benchmark results
│   ├── leaderboards/        # Model leaderboards
│   └── tasks/               # Task definitions and results
├── documentation/           # Project documentation
│   ├── change_logs/         # Detailed change logs
│   ├── development/         # Development guidelines
│   ├── issues/              # Issue tracking and solutions
│   └── user_guides/         # User documentation
├── integrations/            # External service integrations
│   ├── ollama_client.py     # Ollama integration
│   └── web_search.py        # Web search functionality
├── models/                  # Model management
├── scripts/                 # Utility scripts
└── task_system/             # Task management system
```

## Coding Style Guidelines

### Python

1. **PEP 8**: Follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
2. **Docstrings**: Use Google-style docstrings
   ```python
   def function_name(param1, param2):
       """Short description of the function.
       
       Longer description explaining the function in detail.
       
       Args:
           param1: Description of param1
           param2: Description of param2
           
       Returns:
           Description of return value
           
       Raises:
           ExceptionType: When and why this exception is raised
       """
       # Function implementation
   ```
3. **Type Hints**: Use type hints for function parameters and return values
   ```python
   def function_name(param1: str, param2: int) -> bool:
       # Function implementation
   ```
4. **Imports**: Organize imports in the following order:
   - Standard library imports
   - Related third-party imports
   - Local application/library specific imports
5. **Line Length**: Maximum line length of 100 characters
6. **Naming Conventions**:
   - Classes: `CamelCase`
   - Functions and variables: `snake_case`
   - Constants: `UPPER_CASE`
   - Private methods/variables: `_leading_underscore`

### JavaScript

1. **ESLint**: Follow the ESLint configuration
2. **Semicolons**: Use semicolons at the end of statements
3. **Quotes**: Use single quotes for strings
4. **Indentation**: Use 4 spaces for indentation
5. **Comments**: Use JSDoc style comments for functions
   ```javascript
   /**
    * Short description of the function
    * 
    * @param {string} param1 - Description of param1
    * @param {number} param2 - Description of param2
    * @returns {boolean} Description of return value
    */
   function functionName(param1, param2) {
       // Function implementation
   }
   ```
6. **Variable Declarations**: Use `const` for variables that don't change, `let` for variables that do
7. **Naming Conventions**:
   - Classes: `CamelCase`
   - Functions and variables: `camelCase`
   - Constants: `UPPER_CASE`
   - Private methods/variables: `_leadingUnderscore`

### HTML/CSS

1. **Indentation**: Use 4 spaces for indentation
2. **Class Names**: Use kebab-case for class names (e.g., `class-name`)
3. **ID Names**: Use camelCase for ID names (e.g., `idName`)
4. **CSS Organization**: Organize CSS properties in the following order:
   - Positioning
   - Box model
   - Typography
   - Visual
   - Misc
5. **CSS Variables**: Use CSS variables for colors, fonts, and other repeated values
6. **Responsive Design**: Use media queries for responsive design

## Documentation Guidelines

### Code Documentation

1. **Function/Method Documentation**: Document all functions and methods with:
   - Short description
   - Parameter descriptions
   - Return value description
   - Exception descriptions (if applicable)
2. **Class Documentation**: Document all classes with:
   - Class purpose
   - Constructor parameters
   - Public methods
   - Properties
3. **Module Documentation**: Document all modules with:
   - Module purpose
   - Dependencies
   - Usage examples

### Change Documentation

1. **Change Logs**: For significant changes, create a detailed change log in `documentation/change_logs/` with:
   - Overview of changes
   - Previous implementation
   - New implementation
   - Files changed
   - Issues and workarounds
   - Performance considerations
   - Future improvements
2. **Issue Tracking**: For issues, create a document in `documentation/issues/` with:
   - Issue description
   - Current implementation
   - Debugging information
   - Possible causes
   - Workarounds
   - Potential solutions
   - Next steps

## Git Workflow

1. **Branches**:
   - `main`: Production-ready code
   - `develop`: Development branch
   - `feature/feature-name`: Feature branches
   - `bugfix/bug-name`: Bug fix branches
2. **Commits**:
   - Use descriptive commit messages
   - Start with a verb in the present tense (e.g., "Add", "Fix", "Update")
   - Reference issue numbers if applicable
3. **Pull Requests**:
   - Create a pull request for each feature or bug fix
   - Include a description of the changes
   - Reference issue numbers if applicable
4. **Code Reviews**:
   - All code should be reviewed before merging
   - Address all review comments
5. **Merging**:
   - Merge only after code review and approval
   - Use squash merging to keep the history clean

## Testing Guidelines

1. **Unit Tests**:
   - Write unit tests for all new functionality
   - Use pytest for Python tests
   - Use Jest for JavaScript tests
2. **Integration Tests**:
   - Write integration tests for key workflows
   - Test API endpoints
   - Test UI components
3. **Test Coverage**:
   - Aim for at least 80% test coverage
   - Focus on testing complex logic and edge cases
4. **Test Organization**:
   - Organize tests to mirror the structure of the code
   - Use descriptive test names
5. **Test Data**:
   - Use fixtures for test data
   - Avoid hardcoding test data

## Performance Guidelines

1. **Database Queries**:
   - Minimize the number of database queries
   - Use indexes for frequently queried fields
   - Use batch operations when possible
2. **API Calls**:
   - Cache API responses when appropriate
   - Use pagination for large result sets
   - Implement rate limiting
3. **Frontend Performance**:
   - Minimize DOM manipulations
   - Use efficient CSS selectors
   - Optimize images and assets
   - Use lazy loading for non-critical resources
4. **Memory Management**:
   - Avoid memory leaks
   - Clean up resources when they're no longer needed
   - Monitor memory usage

## Security Guidelines

1. **Input Validation**:
   - Validate all user input
   - Use parameterized queries for database operations
   - Sanitize HTML output
2. **Authentication and Authorization**:
   - Use secure authentication methods
   - Implement proper authorization checks
   - Use HTTPS for all communications
3. **Sensitive Data**:
   - Don't hardcode sensitive data
   - Use environment variables for configuration
   - Encrypt sensitive data at rest
4. **Error Handling**:
   - Don't expose sensitive information in error messages
   - Log errors appropriately
   - Handle exceptions gracefully

## Accessibility Guidelines

1. **Semantic HTML**:
   - Use semantic HTML elements
   - Use ARIA attributes when necessary
2. **Keyboard Navigation**:
   - Ensure all functionality is accessible via keyboard
   - Use proper focus management
3. **Screen Readers**:
   - Provide alternative text for images
   - Use proper heading structure
   - Test with screen readers
4. **Color Contrast**:
   - Ensure sufficient color contrast
   - Don't rely solely on color to convey information
