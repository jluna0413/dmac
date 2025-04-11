# DeepClaude Integration

DMac includes integration with DeepClaude, a hybrid approach that combines DeepSeek R1 with Claude 3.7 Sonnet to create a powerful system for code generation, explanation, and refactoring. This guide explains how DeepClaude is integrated into the DMac system and how to use it effectively.

## What is DeepClaude?

DeepClaude is a hybrid approach to AI code generation and reasoning that combines the strengths of two powerful models:

1. **DeepSeek R1**: A model with strong reasoning capabilities, particularly for code-related tasks
2. **Claude 3.7 Sonnet**: A model with high-quality output generation and natural language understanding

By combining these models, DeepClaude provides superior results compared to using either model alone.

![DeepClaude Architecture](../assets/deepclaude-architecture.png)

## How DeepClaude Works

The DeepClaude approach works through a three-step process:

1. **Reasoning Generation**: DeepSeek R1 generates detailed reasoning about a problem or task, thinking through the solution step by step.

2. **Reasoning Extraction**: The system extracts this reasoning from the model's output, isolating the thought process.

3. **Final Generation**: The reasoning is passed to Claude 3.7 Sonnet, which uses it to generate the final output (code, explanation, etc.).

This approach leverages the strengths of both models:
- DeepSeek R1's strong reasoning capabilities
- Claude 3.7 Sonnet's high-quality output generation

## DeepClaude in DMac

In DMac, DeepClaude is primarily used by the Cody agent for code-related tasks, but the module is designed to be flexible and can be used by any agent in the system.

### Key Features

- **Flexible Integration**: Can be used by any agent in the system
- **Support for Different Model Combinations**: Can use different models for reasoning and generation
- **Caching**: Includes caching for improved performance
- **Specialized Methods**: Provides methods for code generation, explanation, and refactoring

## Using DeepClaude

You can access DeepClaude's capabilities through the Cody agent:

1. **Code Generation**:
   ```
   @Cody Generate a Python function to parse JSON data
   ```

2. **Code Explanation**:
   ```
   @Cody Explain how this algorithm works:
   ```python
   def quicksort(arr):
       if len(arr) <= 1:
           return arr
       pivot = arr[len(arr) // 2]
       left = [x for x in arr if x < pivot]
       middle = [x for x in arr if x == pivot]
       right = [x for x in arr if x > pivot]
       return quicksort(left) + middle + quicksort(right)
   ```
   ```

3. **Code Refactoring**:
   ```
   @Cody Refactor this code to improve performance:
   ```python
   def find_duplicates(items):
       duplicates = []
       for i in range(len(items)):
           for j in range(i+1, len(items)):
               if items[i] == items[j] and items[i] not in duplicates:
                   duplicates.append(items[i])
       return duplicates
   ```
   ```

## Configuration

DeepClaude can be configured through the agent configuration file (`config/agent_config.json`). The following options are available:

```json
{
  "reasoning_model": "GandalfBaum/deepseek_r1-claude3.7:latest",
  "generation_model": "claude-3-7-sonnet",
  "temperature": 0.2,
  "supports_native_reasoning": true,
  "enable_proxy": {
    "reasoning_model": false,
    "generation_model": true
  }
}
```

You can also configure DeepClaude through the agent dashboard:

1. Navigate to the Cody agent dashboard
2. Click on the "Settings" tab
3. Adjust the DeepClaude settings as needed

## Performance

DeepClaude generally outperforms single-model approaches for code-related tasks. Benchmarks show improvements in:

- **Code Quality**: More efficient, readable, and maintainable code
- **Execution Success Rate**: Code that works correctly the first time
- **Explanation Clarity**: More detailed and accurate explanations
- **Refactoring Effectiveness**: Better code improvements

You can view benchmark results on the Cody agent dashboard:

1. Navigate to the Cody agent dashboard
2. Click on the "Benchmarks" tab
3. View the model comparison chart and benchmark results

## Reinforcement Learning Integration

DeepClaude is integrated with OpenManus RL, allowing it to learn from experience and improve over time. The system tracks:

- Which approaches work best for different coding tasks
- How to optimize prompting strategies
- Which models perform best for different programming languages
- User preferences and feedback

This integration helps DeepClaude continuously improve its performance and adapt to user needs.

## Troubleshooting

If you encounter issues with DeepClaude:

1. **Generation Issues**:
   - Check that the models are available and properly configured
   - Try adjusting the temperature setting (lower for more deterministic results)
   - Ensure your prompt is clear and specific

2. **Performance Issues**:
   - Check the cache settings to ensure caching is enabled
   - Verify that the models are properly loaded
   - Monitor system resources to ensure sufficient memory and CPU

3. **Integration Issues**:
   - Check the agent configuration to ensure DeepClaude is properly configured
   - Verify that the API endpoints are accessible
   - Check the logs for any error messages

## Next Steps

Now that you're familiar with DMac's DeepClaude integration, you can:

- Explore the [Cody Agent](AI-Agents.md#cody) documentation
- Learn about the [Agent Dashboard](User-Interface.md#agent-dashboard)
- Check the [Troubleshooting](Troubleshooting.md) section for common issues
