"""
Tool Agent for DMac.

This module provides the tool agent class for handling tool operations.
"""

import asyncio
import logging
import time
import json
import os
import subprocess
from typing import Dict, List, Optional, Any, Callable, Awaitable

from config.config import config
from utils.secure_logging import get_logger
from agents.base_agent import BaseAgent
from models.model_manager import ModelManager

logger = get_logger('dmac.agents.tool_agent')


class ToolAgent(BaseAgent):
    """Agent for handling tool operations."""
    
    def __init__(self, name: str, tool_type: str, model_name: Optional[str] = None):
        """Initialize the tool agent.
        
        Args:
            name: The name of the agent.
            tool_type: The type of tool this agent handles.
            model_name: The name of the model to use for the agent.
        """
        super().__init__(name, agent_type="tool", model_name=model_name)
        
        # Initialize the model manager
        self.model_manager = ModelManager()
        
        # Set the default model if none is provided
        if not self.model_name:
            self.model_name = config.get('models.default_model', 'gemma3:12b')
        
        # Tool-specific attributes
        self.tool_type = tool_type
        self.tool_operations = {}
        self.tool_results = {}
        self.tool_status = {}
        
        # Register message handlers
        asyncio.create_task(self.register_message_handler('tool_request', self._handle_tool_request))
        asyncio.create_task(self.register_message_handler('tool_status_request', self._handle_tool_status_request))
        asyncio.create_task(self.register_message_handler('tool_result_request', self._handle_tool_result_request))
        
        # Register tool operations based on tool type
        self._register_tool_operations()
        
        logger.info(f"Initialized tool agent '{name}' of type '{tool_type}' with model '{self.model_name}'")
    
    def _register_tool_operations(self) -> None:
        """Register tool operations based on the tool type."""
        if self.tool_type == 'search':
            self.tool_operations['web_search'] = self._handle_web_search
            self.tool_operations['document_search'] = self._handle_document_search
        elif self.tool_type == 'code':
            self.tool_operations['code_generation'] = self._handle_code_generation
            self.tool_operations['code_explanation'] = self._handle_code_explanation
            self.tool_operations['code_review'] = self._handle_code_review
        elif self.tool_type == 'data':
            self.tool_operations['data_analysis'] = self._handle_data_analysis
            self.tool_operations['data_visualization'] = self._handle_data_visualization
        elif self.tool_type == 'system':
            self.tool_operations['file_operation'] = self._handle_file_operation
            self.tool_operations['process_operation'] = self._handle_process_operation
        else:
            logger.warning(f"Unknown tool type '{self.tool_type}' for agent {self.id}")
    
    async def _handle_task(self, task: Dict[str, Any]) -> None:
        """Handle a task.
        
        Args:
            task: The task to handle.
        """
        task_id = task.get('id')
        operation = task.get('operation')
        params = task.get('params', {})
        
        if not task_id:
            logger.warning(f"Agent {self.id} received task with no ID")
            return
        
        if not operation:
            logger.warning(f"Agent {self.id} received task with no operation: {task}")
            return
        
        logger.info(f"Agent {self.id} handling task {task_id} with operation '{operation}'")
        
        # Update task status
        self.tool_status[task_id] = 'processing'
        
        try:
            # Check if the operation is supported
            if operation not in self.tool_operations:
                logger.warning(f"Agent {self.id} received unsupported operation '{operation}'")
                result = {'error': f"Unsupported operation '{operation}'"}
                self.tool_status[task_id] = 'failed'
                self.tool_results[task_id] = result
                return
            
            # Execute the operation
            result = await self.tool_operations[operation](params)
            
            # Store the task result
            self.tool_results[task_id] = result
            
            # Update task status
            self.tool_status[task_id] = 'completed'
            
            logger.info(f"Agent {self.id} completed task {task_id}")
            
            # Notify the task requester if specified
            if 'requester_id' in task:
                await self.send_message(
                    task['requester_id'],
                    'tool_completed',
                    {
                        'task_id': task_id,
                        'result': result,
                    }
                )
        except Exception as e:
            logger.error(f"Error handling task {task_id} for agent {self.id}: {e}")
            
            # Update task status
            self.tool_status[task_id] = 'failed'
            
            # Store the error as the task result
            self.tool_results[task_id] = {'error': str(e)}
            
            # Notify the task requester if specified
            if 'requester_id' in task:
                await self.send_message(
                    task['requester_id'],
                    'tool_failed',
                    {
                        'task_id': task_id,
                        'error': str(e),
                    }
                )
    
    async def _handle_web_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a web search operation.
        
        Args:
            params: Parameters for the web search.
            
        Returns:
            The search results.
        """
        query = params.get('query')
        
        if not query:
            raise ValueError("No query provided for web search")
        
        # This is a placeholder for a real web search implementation
        # In a real implementation, this would use a search engine API
        
        # Generate a search response using the model manager
        system_prompt = "You are a search engine. Provide relevant information for the following query."
        
        response = await self.model_manager.generate(
            prompt=query,
            model=self.model_name,
            system_prompt=system_prompt
        )
        
        return {
            'query': query,
            'results': [
                {
                    'title': 'Search Result 1',
                    'url': 'https://example.com/result1',
                    'snippet': response[:100] + '...',
                    'content': response,
                }
            ],
            'timestamp': time.time(),
        }
    
    async def _handle_document_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a document search operation.
        
        Args:
            params: Parameters for the document search.
            
        Returns:
            The search results.
        """
        query = params.get('query')
        document_ids = params.get('document_ids', [])
        
        if not query:
            raise ValueError("No query provided for document search")
        
        # This is a placeholder for a real document search implementation
        # In a real implementation, this would search through documents
        
        return {
            'query': query,
            'document_ids': document_ids,
            'results': [
                {
                    'document_id': 'doc1',
                    'title': 'Document 1',
                    'snippet': 'This is a snippet from document 1...',
                    'relevance': 0.95,
                }
            ],
            'timestamp': time.time(),
        }
    
    async def _handle_code_generation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a code generation operation.
        
        Args:
            params: Parameters for the code generation.
            
        Returns:
            The generated code.
        """
        prompt = params.get('prompt')
        language = params.get('language', 'python')
        
        if not prompt:
            raise ValueError("No prompt provided for code generation")
        
        # Generate code using the model manager
        system_prompt = f"You are an expert programmer. Generate {language} code for the following task. Only provide the code, no explanations."
        
        code = await self.model_manager.generate(
            prompt=prompt,
            model=self.model_name,
            system_prompt=system_prompt
        )
        
        return {
            'prompt': prompt,
            'language': language,
            'code': code,
            'timestamp': time.time(),
        }
    
    async def _handle_code_explanation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a code explanation operation.
        
        Args:
            params: Parameters for the code explanation.
            
        Returns:
            The code explanation.
        """
        code = params.get('code')
        language = params.get('language', 'python')
        
        if not code:
            raise ValueError("No code provided for code explanation")
        
        # Generate an explanation using the model manager
        system_prompt = f"You are an expert programmer. Explain the following {language} code in detail."
        
        explanation = await self.model_manager.generate(
            prompt=code,
            model=self.model_name,
            system_prompt=system_prompt
        )
        
        return {
            'code': code,
            'language': language,
            'explanation': explanation,
            'timestamp': time.time(),
        }
    
    async def _handle_code_review(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a code review operation.
        
        Args:
            params: Parameters for the code review.
            
        Returns:
            The code review.
        """
        code = params.get('code')
        language = params.get('language', 'python')
        
        if not code:
            raise ValueError("No code provided for code review")
        
        # Generate a review using the model manager
        system_prompt = f"You are an expert code reviewer. Review the following {language} code and provide feedback on improvements, bugs, and best practices."
        
        review = await self.model_manager.generate(
            prompt=code,
            model=self.model_name,
            system_prompt=system_prompt
        )
        
        return {
            'code': code,
            'language': language,
            'review': review,
            'timestamp': time.time(),
        }
    
    async def _handle_data_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a data analysis operation.
        
        Args:
            params: Parameters for the data analysis.
            
        Returns:
            The data analysis results.
        """
        data = params.get('data')
        analysis_type = params.get('analysis_type', 'summary')
        
        if not data:
            raise ValueError("No data provided for data analysis")
        
        # This is a placeholder for a real data analysis implementation
        # In a real implementation, this would use data analysis libraries
        
        # Generate an analysis using the model manager
        system_prompt = f"You are a data analyst. Analyze the following data and provide a {analysis_type}."
        
        analysis = await self.model_manager.generate(
            prompt=str(data),
            model=self.model_name,
            system_prompt=system_prompt
        )
        
        return {
            'analysis_type': analysis_type,
            'analysis': analysis,
            'timestamp': time.time(),
        }
    
    async def _handle_data_visualization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a data visualization operation.
        
        Args:
            params: Parameters for the data visualization.
            
        Returns:
            The data visualization results.
        """
        data = params.get('data')
        visualization_type = params.get('visualization_type', 'bar_chart')
        
        if not data:
            raise ValueError("No data provided for data visualization")
        
        # This is a placeholder for a real data visualization implementation
        # In a real implementation, this would use data visualization libraries
        
        return {
            'visualization_type': visualization_type,
            'visualization_data': {
                'type': visualization_type,
                'data': data,
            },
            'timestamp': time.time(),
        }
    
    async def _handle_file_operation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a file operation.
        
        Args:
            params: Parameters for the file operation.
            
        Returns:
            The file operation results.
        """
        operation_type = params.get('operation_type')
        file_path = params.get('file_path')
        
        if not operation_type:
            raise ValueError("No operation type provided for file operation")
        
        if not file_path:
            raise ValueError("No file path provided for file operation")
        
        # Validate the file path for security
        if '..' in file_path or file_path.startswith('/'):
            raise ValueError(f"Invalid file path: {file_path}")
        
        # Perform the file operation
        if operation_type == 'read':
            content = await self._read_file(file_path)
            return {
                'operation_type': operation_type,
                'file_path': file_path,
                'content': content,
                'timestamp': time.time(),
            }
        elif operation_type == 'write':
            content = params.get('content')
            if not content:
                raise ValueError("No content provided for write operation")
            await self._write_file(file_path, content)
            return {
                'operation_type': operation_type,
                'file_path': file_path,
                'success': True,
                'timestamp': time.time(),
            }
        elif operation_type == 'delete':
            await self._delete_file(file_path)
            return {
                'operation_type': operation_type,
                'file_path': file_path,
                'success': True,
                'timestamp': time.time(),
            }
        else:
            raise ValueError(f"Unsupported file operation type: {operation_type}")
    
    async def _handle_process_operation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a process operation.
        
        Args:
            params: Parameters for the process operation.
            
        Returns:
            The process operation results.
        """
        operation_type = params.get('operation_type')
        command = params.get('command')
        
        if not operation_type:
            raise ValueError("No operation type provided for process operation")
        
        if not command:
            raise ValueError("No command provided for process operation")
        
        # Validate the command for security
        if ';' in command or '&' in command or '|' in command:
            raise ValueError(f"Invalid command: {command}")
        
        # Perform the process operation
        if operation_type == 'execute':
            output = await self._execute_command(command)
            return {
                'operation_type': operation_type,
                'command': command,
                'output': output,
                'timestamp': time.time(),
            }
        else:
            raise ValueError(f"Unsupported process operation type: {operation_type}")
    
    async def _read_file(self, file_path: str) -> str:
        """Read a file.
        
        Args:
            file_path: The path to the file to read.
            
        Returns:
            The content of the file.
        """
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise
    
    async def _write_file(self, file_path: str, content: str) -> None:
        """Write to a file.
        
        Args:
            file_path: The path to the file to write to.
            content: The content to write to the file.
        """
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Error writing to file {file_path}: {e}")
            raise
    
    async def _delete_file(self, file_path: str) -> None:
        """Delete a file.
        
        Args:
            file_path: The path to the file to delete.
        """
        try:
            os.remove(file_path)
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            raise
    
    async def _execute_command(self, command: str) -> str:
        """Execute a command.
        
        Args:
            command: The command to execute.
            
        Returns:
            The output of the command.
        """
        try:
            # Execute the command and capture the output
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.warning(f"Command '{command}' exited with code {process.returncode}: {stderr.decode()}")
            
            return stdout.decode()
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            raise
    
    async def _handle_tool_request(self, message: Dict[str, Any]) -> None:
        """Handle a tool request message.
        
        Args:
            message: The message containing the tool request.
        """
        content = message.get('content', {})
        operation = content.get('operation')
        params = content.get('params', {})
        
        if not operation:
            logger.warning(f"Agent {self.id} received tool request with no operation: {message}")
            
            # Send an error response
            await self.send_message(
                message['sender_id'],
                'tool_request_error',
                {
                    'error': 'No operation provided',
                    'original_message': message,
                }
            )
            return
        
        # Create a task for the tool operation
        task = {
            'id': f"task_{time.time()}_{operation}",
            'operation': operation,
            'params': params,
            'requester_id': message['sender_id'],
        }
        
        # Add the task to the queue
        await self.add_task(task)
        
        # Send an acknowledgement
        await self.send_message(
            message['sender_id'],
            'tool_request_ack',
            {
                'task_id': task['id'],
                'message': f"Tool request received and queued for processing",
            }
        )
    
    async def _handle_tool_status_request(self, message: Dict[str, Any]) -> None:
        """Handle a tool status request message.
        
        Args:
            message: The message containing the tool status request.
        """
        content = message.get('content', {})
        task_id = content.get('task_id')
        
        if not task_id:
            logger.warning(f"Agent {self.id} received tool status request with no task ID: {message}")
            
            # Send an error response
            await self.send_message(
                message['sender_id'],
                'tool_status_error',
                {
                    'error': 'No task ID provided',
                    'original_message': message,
                }
            )
            return
        
        # Get the task status
        status = self.tool_status.get(task_id, 'unknown')
        
        # Send the status response
        await self.send_message(
            message['sender_id'],
            'tool_status_response',
            {
                'task_id': task_id,
                'status': status,
            }
        )
    
    async def _handle_tool_result_request(self, message: Dict[str, Any]) -> None:
        """Handle a tool result request message.
        
        Args:
            message: The message containing the tool result request.
        """
        content = message.get('content', {})
        task_id = content.get('task_id')
        
        if not task_id:
            logger.warning(f"Agent {self.id} received tool result request with no task ID: {message}")
            
            # Send an error response
            await self.send_message(
                message['sender_id'],
                'tool_result_error',
                {
                    'error': 'No task ID provided',
                    'original_message': message,
                }
            )
            return
        
        # Get the task result
        result = self.tool_results.get(task_id)
        
        if result is None:
            # Send an error response
            await self.send_message(
                message['sender_id'],
                'tool_result_error',
                {
                    'error': f"No result found for task ID '{task_id}'",
                    'task_id': task_id,
                }
            )
            return
        
        # Send the result response
        await self.send_message(
            message['sender_id'],
            'tool_result_response',
            {
                'task_id': task_id,
                'result': result,
            }
        )
    
    async def get_info(self) -> Dict[str, Any]:
        """Get information about the agent.
        
        Returns:
            A dictionary containing information about the agent.
        """
        info = await super().get_info()
        
        # Add tool agent specific information
        info.update({
            'tool_type': self.tool_type,
            'supported_operations': list(self.tool_operations.keys()),
            'task_count': len(self.tool_results),
            'completed_tasks': sum(1 for status in self.tool_status.values() if status == 'completed'),
            'failed_tasks': sum(1 for status in self.tool_status.values() if status == 'failed'),
            'processing_tasks': sum(1 for status in self.tool_status.values() if status == 'processing'),
        })
        
        return info
