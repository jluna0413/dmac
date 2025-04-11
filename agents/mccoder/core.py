"""
McCoder - Code Intelligence Agent for DMac

This module provides code understanding, generation, and refactoring capabilities
similar to Augment Code but running natively within the DMac ecosystem.
"""

import os
import re
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

# Set up logging
logger = logging.getLogger('dmac.mccoder')

class McCoder:
    """
    McCoder is a code intelligence agent that can understand, generate, and refactor code.
    It provides similar functionality to Augment Code but runs natively within DMac.
    """
    
    def __init__(self, project_root: Optional[str] = None, model_provider=None):
        """
        Initialize the McCoder agent.
        
        Args:
            project_root: Root directory of the project to analyze
            model_provider: Provider for LLM capabilities (if None, will use default from DMac)
        """
        self.project_root = project_root or os.getcwd()
        self.model_provider = model_provider
        self.file_index = {}
        self.symbol_index = {}
        self.dependency_graph = {}
        
        # Initialize the code index
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize the code index by scanning the project files."""
        logger.info(f"Initializing code index for {self.project_root}")
        
        # Get all code files in the project
        code_files = self._get_code_files()
        
        # Index each file
        for file_path in code_files:
            self._index_file(file_path)
        
        # Build dependency graph
        self._build_dependency_graph()
        
        logger.info(f"Indexed {len(self.file_index)} files and {len(self.symbol_index)} symbols")
    
    def _get_code_files(self) -> List[str]:
        """
        Get all code files in the project.
        
        Returns:
            List of file paths
        """
        code_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.scss',
            '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.go', '.rb', '.php',
            '.swift', '.kt', '.rs', '.dart', '.vue', '.sh', '.bash', '.sql'
        }
        
        ignore_dirs = {
            'node_modules', 'venv', '.git', '.idea', '.vscode', '__pycache__',
            'build', 'dist', 'target', 'bin', 'obj', '.dart_tool', '.pub'
        }
        
        code_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in code_extensions:
                    file_path = os.path.join(root, file)
                    code_files.append(file_path)
        
        return code_files
    
    def _index_file(self, file_path: str):
        """
        Index a single file.
        
        Args:
            file_path: Path to the file to index
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            relative_path = os.path.relpath(file_path, self.project_root)
            
            # Store file content in the index
            self.file_index[relative_path] = {
                'content': content,
                'size': len(content),
                'language': self._detect_language(file_path),
                'symbols': [],
                'last_modified': os.path.getmtime(file_path)
            }
            
            # Extract symbols from the file
            symbols = self._extract_symbols(relative_path, content)
            
            # Add symbols to the file index
            self.file_index[relative_path]['symbols'] = [s['name'] for s in symbols]
            
            # Add symbols to the symbol index
            for symbol in symbols:
                self.symbol_index[symbol['name']] = {
                    'file': relative_path,
                    'type': symbol['type'],
                    'line': symbol['line'],
                    'column': symbol['column'],
                    'end_line': symbol.get('end_line'),
                    'end_column': symbol.get('end_column'),
                    'signature': symbol.get('signature'),
                    'docstring': symbol.get('docstring')
                }
        
        except Exception as e:
            logger.error(f"Error indexing file {file_path}: {str(e)}")
    
    def _detect_language(self, file_path: str) -> str:
        """
        Detect the programming language of a file based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Language name
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.rs': 'rust',
            '.dart': 'dart',
            '.vue': 'vue',
            '.sh': 'shell',
            '.bash': 'shell',
            '.sql': 'sql'
        }
        
        return language_map.get(ext, 'unknown')
    
    def _extract_symbols(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """
        Extract symbols (functions, classes, variables) from a file.
        
        Args:
            file_path: Path to the file
            content: Content of the file
            
        Returns:
            List of symbols
        """
        language = self.file_index[file_path]['language']
        symbols = []
        
        if language == 'python':
            symbols = self._extract_python_symbols(content)
        elif language in ('javascript', 'typescript'):
            symbols = self._extract_js_ts_symbols(content)
        # Add more language extractors as needed
        
        return symbols
    
    def _extract_python_symbols(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract symbols from Python code.
        
        Args:
            content: Python code content
            
        Returns:
            List of symbols
        """
        symbols = []
        
        # Regular expressions for Python symbols
        class_pattern = r'class\s+(\w+)\s*(?:\(([^)]*)\))?:'
        function_pattern = r'def\s+(\w+)\s*\(([^)]*)\):'
        variable_pattern = r'(\w+)\s*=\s*([^#\n]*)'
        
        # Extract classes
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            line_start = content[:match.start()].count('\n') + 1
            column_start = match.start() - content.rfind('\n', 0, match.start())
            
            # Find class docstring
            docstring = self._extract_docstring(content[match.end():])
            
            symbols.append({
                'name': class_name,
                'type': 'class',
                'line': line_start,
                'column': column_start,
                'signature': match.group(0),
                'docstring': docstring
            })
        
        # Extract functions
        for match in re.finditer(function_pattern, content):
            function_name = match.group(1)
            line_start = content[:match.start()].count('\n') + 1
            column_start = match.start() - content.rfind('\n', 0, match.start())
            
            # Find function docstring
            docstring = self._extract_docstring(content[match.end():])
            
            symbols.append({
                'name': function_name,
                'type': 'function',
                'line': line_start,
                'column': column_start,
                'signature': match.group(0),
                'docstring': docstring
            })
        
        # Extract top-level variables
        for match in re.finditer(variable_pattern, content):
            # Skip variables inside functions or classes
            line_start = content[:match.start()].count('\n') + 1
            prev_lines = content.split('\n')[:line_start]
            if any(line.strip().startswith(('def ', 'class ')) for line in prev_lines[-2:]):
                continue
                
            variable_name = match.group(1)
            column_start = match.start() - content.rfind('\n', 0, match.start())
            
            symbols.append({
                'name': variable_name,
                'type': 'variable',
                'line': line_start,
                'column': column_start,
                'signature': match.group(0).strip()
            })
        
        return symbols
    
    def _extract_js_ts_symbols(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract symbols from JavaScript/TypeScript code.
        
        Args:
            content: JavaScript/TypeScript code content
            
        Returns:
            List of symbols
        """
        symbols = []
        
        # Regular expressions for JS/TS symbols
        class_pattern = r'class\s+(\w+)'
        function_pattern = r'function\s+(\w+)\s*\(([^)]*)\)'
        arrow_function_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)|\w+)\s*=>'
        variable_pattern = r'(?:const|let|var)\s+(\w+)\s*='
        
        # Extract classes
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            line_start = content[:match.start()].count('\n') + 1
            column_start = match.start() - content.rfind('\n', 0, match.start())
            
            symbols.append({
                'name': class_name,
                'type': 'class',
                'line': line_start,
                'column': column_start,
                'signature': match.group(0)
            })
        
        # Extract functions
        for match in re.finditer(function_pattern, content):
            function_name = match.group(1)
            line_start = content[:match.start()].count('\n') + 1
            column_start = match.start() - content.rfind('\n', 0, match.start())
            
            symbols.append({
                'name': function_name,
                'type': 'function',
                'line': line_start,
                'column': column_start,
                'signature': match.group(0)
            })
        
        # Extract arrow functions
        for match in re.finditer(arrow_function_pattern, content):
            function_name = match.group(1)
            line_start = content[:match.start()].count('\n') + 1
            column_start = match.start() - content.rfind('\n', 0, match.start())
            
            symbols.append({
                'name': function_name,
                'type': 'function',
                'line': line_start,
                'column': column_start,
                'signature': match.group(0)
            })
        
        # Extract variables
        for match in re.finditer(variable_pattern, content):
            variable_name = match.group(1)
            line_start = content[:match.start()].count('\n') + 1
            column_start = match.start() - content.rfind('\n', 0, match.start())
            
            # Skip if this is an arrow function (already captured)
            if re.search(r'=\s*(?:\([^)]*\)|\w+)\s*=>', match.group(0)):
                continue
                
            symbols.append({
                'name': variable_name,
                'type': 'variable',
                'line': line_start,
                'column': column_start,
                'signature': match.group(0)
            })
        
        return symbols
    
    def _extract_docstring(self, content: str) -> Optional[str]:
        """
        Extract docstring from code.
        
        Args:
            content: Code content after the symbol definition
            
        Returns:
            Docstring if found, None otherwise
        """
        # Look for triple-quoted strings
        triple_quote_pattern = r'"""(.*?)"""'
        match = re.search(triple_quote_pattern, content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        return None
    
    def _build_dependency_graph(self):
        """Build a dependency graph of the project files."""
        for file_path, file_info in self.file_index.items():
            self.dependency_graph[file_path] = []
            
            language = file_info['language']
            content = file_info['content']
            
            if language == 'python':
                # Find Python imports
                import_pattern = r'(?:from|import)\s+([\w.]+)'
                for match in re.finditer(import_pattern, content):
                    module_name = match.group(1).split('.')[0]
                    
                    # Find the corresponding file
                    for other_path in self.file_index:
                        if other_path.endswith(f'/{module_name}.py') or other_path == f'{module_name}.py':
                            self.dependency_graph[file_path].append(other_path)
            
            elif language in ('javascript', 'typescript'):
                # Find JS/TS imports
                import_pattern = r'(?:import|require)\s*\(?[\'"]([^\'"]*)[\'"]\)?'
                for match in re.finditer(import_pattern, content):
                    module_path = match.group(1)
                    
                    # Handle relative imports
                    if module_path.startswith('.'):
                        dir_name = os.path.dirname(file_path)
                        module_path = os.path.normpath(os.path.join(dir_name, module_path))
                        
                        # Try different extensions
                        for ext in ['.js', '.jsx', '.ts', '.tsx']:
                            full_path = f'{module_path}{ext}'
                            if full_path in self.file_index:
                                self.dependency_graph[file_path].append(full_path)
                                break
    
    def search_code(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for code based on a natural language query.
        
        Args:
            query: Natural language query
            
        Returns:
            List of search results
        """
        results = []
        
        # Convert query to lowercase for case-insensitive search
        query_lower = query.lower()
        
        # Search in file content
        for file_path, file_info in self.file_index.items():
            content = file_info['content'].lower()
            if query_lower in content:
                # Find the line numbers where the query appears
                lines = file_info['content'].split('\n')
                matches = []
                
                for i, line in enumerate(lines):
                    if query_lower in line.lower():
                        matches.append({
                            'line': i + 1,
                            'content': line.strip()
                        })
                
                if matches:
                    results.append({
                        'file': file_path,
                        'language': file_info['language'],
                        'matches': matches
                    })
        
        # Search in symbols
        for symbol_name, symbol_info in self.symbol_index.items():
            if query_lower in symbol_name.lower():
                file_path = symbol_info['file']
                file_info = self.file_index[file_path]
                
                results.append({
                    'file': file_path,
                    'language': file_info['language'],
                    'symbol': symbol_name,
                    'type': symbol_info['type'],
                    'line': symbol_info['line'],
                    'signature': symbol_info.get('signature', '')
                })
        
        return results
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        """
        Get the content of a file.
        
        Args:
            file_path: Path to the file (relative to project root)
            
        Returns:
            File content if found, None otherwise
        """
        if file_path in self.file_index:
            return self.file_index[file_path]['content']
        
        # Try to read the file if it's not in the index
        full_path = os.path.join(self.project_root, file_path)
        if os.path.isfile(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {str(e)}")
        
        return None
    
    def get_symbol_info(self, symbol_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a symbol.
        
        Args:
            symbol_name: Name of the symbol
            
        Returns:
            Symbol information if found, None otherwise
        """
        if symbol_name in self.symbol_index:
            symbol_info = self.symbol_index[symbol_name]
            file_path = symbol_info['file']
            file_content = self.get_file_content(file_path)
            
            if file_content:
                lines = file_content.split('\n')
                line_index = symbol_info['line'] - 1
                
                # Get the symbol definition and context
                start_line = max(0, line_index - 2)
                end_line = min(len(lines), line_index + 3)
                context = '\n'.join(lines[start_line:end_line])
                
                return {
                    **symbol_info,
                    'context': context
                }
        
        return None
    
    def generate_code(self, prompt: str, language: str = None, context: str = None) -> str:
        """
        Generate code based on a natural language prompt.
        
        Args:
            prompt: Natural language prompt
            language: Target programming language
            context: Additional context for code generation
            
        Returns:
            Generated code
        """
        if self.model_provider is None:
            raise ValueError("Model provider is required for code generation")
        
        # Prepare the prompt for the model
        full_prompt = f"Generate {language or 'code'} for the following task:\n\n{prompt}"
        
        if context:
            full_prompt += f"\n\nContext:\n{context}"
        
        # Generate code using the model provider
        response = self.model_provider.generate(full_prompt)
        
        # Extract code from the response
        code = self._extract_code_from_response(response, language)
        
        return code
    
    def _extract_code_from_response(self, response: str, language: str = None) -> str:
        """
        Extract code blocks from a model response.
        
        Args:
            response: Model response
            language: Expected programming language
            
        Returns:
            Extracted code
        """
        # Look for code blocks with backticks
        code_block_pattern = r'```(?:\w+)?\n(.*?)```'
        matches = re.findall(code_block_pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # If no code blocks found, return the entire response
        return response.strip()
    
    def explain_code(self, code: str, language: str = None) -> str:
        """
        Explain code in natural language.
        
        Args:
            code: Code to explain
            language: Programming language of the code
            
        Returns:
            Natural language explanation
        """
        if self.model_provider is None:
            raise ValueError("Model provider is required for code explanation")
        
        # Prepare the prompt for the model
        prompt = f"Explain the following {language or 'code'} in detail:\n\n```\n{code}\n```"
        
        # Generate explanation using the model provider
        response = self.model_provider.generate(prompt)
        
        return response
    
    def refactor_code(self, code: str, instructions: str, language: str = None) -> str:
        """
        Refactor code based on instructions.
        
        Args:
            code: Code to refactor
            instructions: Refactoring instructions
            language: Programming language of the code
            
        Returns:
            Refactored code
        """
        if self.model_provider is None:
            raise ValueError("Model provider is required for code refactoring")
        
        # Prepare the prompt for the model
        prompt = f"Refactor the following {language or 'code'} according to these instructions:\n\n"
        prompt += f"Instructions: {instructions}\n\n"
        prompt += f"Code:\n```\n{code}\n```\n\n"
        prompt += "Please provide only the refactored code without explanations."
        
        # Generate refactored code using the model provider
        response = self.model_provider.generate(prompt)
        
        # Extract code from the response
        refactored_code = self._extract_code_from_response(response, language)
        
        return refactored_code
    
    def find_bugs(self, code: str, language: str = None) -> List[Dict[str, Any]]:
        """
        Find potential bugs in code.
        
        Args:
            code: Code to analyze
            language: Programming language of the code
            
        Returns:
            List of potential bugs
        """
        if self.model_provider is None:
            raise ValueError("Model provider is required for bug finding")
        
        # Prepare the prompt for the model
        prompt = f"Find potential bugs in the following {language or 'code'}:\n\n```\n{code}\n```\n\n"
        prompt += "Format your response as a JSON array of objects with 'line', 'description', and 'severity' fields."
        
        # Generate bug report using the model provider
        response = self.model_provider.generate(prompt)
        
        # Try to parse JSON from the response
        try:
            # Extract JSON array from the response
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                bugs = json.loads(json_match.group(0))
                return bugs
        except Exception as e:
            logger.error(f"Error parsing bug report: {str(e)}")
        
        # If JSON parsing fails, return an empty list
        return []
    
    def generate_tests(self, code: str, language: str = None) -> str:
        """
        Generate unit tests for code.
        
        Args:
            code: Code to test
            language: Programming language of the code
            
        Returns:
            Generated test code
        """
        if self.model_provider is None:
            raise ValueError("Model provider is required for test generation")
        
        # Prepare the prompt for the model
        prompt = f"Generate unit tests for the following {language or 'code'}:\n\n```\n{code}\n```\n\n"
        prompt += "Please provide comprehensive tests that cover all functionality."
        
        # Generate tests using the model provider
        response = self.model_provider.generate(prompt)
        
        # Extract code from the response
        test_code = self._extract_code_from_response(response, language)
        
        return test_code
    
    def document_code(self, code: str, language: str = None) -> str:
        """
        Add documentation to code.
        
        Args:
            code: Code to document
            language: Programming language of the code
            
        Returns:
            Documented code
        """
        if self.model_provider is None:
            raise ValueError("Model provider is required for code documentation")
        
        # Prepare the prompt for the model
        prompt = f"Add comprehensive documentation to the following {language or 'code'}:\n\n```\n{code}\n```\n\n"
        prompt += "Please include docstrings, comments, and type hints where appropriate."
        
        # Generate documented code using the model provider
        response = self.model_provider.generate(prompt)
        
        # Extract code from the response
        documented_code = self._extract_code_from_response(response, language)
        
        return documented_code
    
    def refresh_index(self):
        """Refresh the code index."""
        self.file_index = {}
        self.symbol_index = {}
        self.dependency_graph = {}
        self._initialize_index()
    
    def get_project_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the project.
        
        Returns:
            Project summary
        """
        languages = {}
        for file_info in self.file_index.values():
            language = file_info['language']
            if language in languages:
                languages[language] += 1
            else:
                languages[language] = 1
        
        symbol_types = {}
        for symbol_info in self.symbol_index.values():
            symbol_type = symbol_info['type']
            if symbol_type in symbol_types:
                symbol_types[symbol_type] += 1
            else:
                symbol_types[symbol_type] = 1
        
        return {
            'project_root': self.project_root,
            'file_count': len(self.file_index),
            'symbol_count': len(self.symbol_index),
            'languages': languages,
            'symbol_types': symbol_types
        }
