# DMac Learning System

The DMac learning system is a sophisticated component that enables continuous improvement of AI models through learning from interactions and feedback.

## Overview

The learning system is designed to:

1. **Learn from all model interactions**: The system captures and learns from interactions with all models, not just Gemini 2.5 Pro.
2. **Collect and apply feedback**: Users can provide feedback on responses, which is used to improve future responses.
3. **Train models periodically**: DeepSeek-RL is trained on the collected learning data to improve its capabilities.
4. **Evaluate model performance**: The system regularly evaluates model performance to track improvements.
5. **Adapt to changing conditions**: The system intelligently switches between models based on usage caps and performance metrics.

## Architecture

The learning system consists of the following components:

### Learning Data Collection

- **Interaction Capture**: All interactions with AI models are captured and stored.
- **Feedback Collection**: User feedback on responses is collected and stored.
- **Data Storage**: Learning data is stored in JSONL files organized by month.

### Training Process

- **Batch Training**: The system trains DeepSeek-RL in batches to improve efficiency.
- **Epoch-based Learning**: Multiple epochs are used to ensure thorough learning.
- **Validation**: The system validates the model's performance during training.

### Evaluation

- **Metrics Tracking**: The system tracks various metrics including:
  - Training loss
  - Validation loss
  - Accuracy
  - ROUGE score
  - BLEU score
- **Performance Comparison**: The system compares the performance of different models.

### Feedback Application

- **Rating System**: Users can rate responses on a scale of 1-5.
- **Textual Feedback**: Users can provide textual feedback on responses.
- **Feedback Integration**: Feedback is integrated into the training process.

## Usage

### Providing Feedback

To provide feedback on a response:

```python
await model_manager.provide_feedback(
    prompt="What is the future of AI?",
    response="The future of AI is...",
    feedback="The response was informative but could include more specific examples.",
    rating=4
)
```

### Training the Model

To manually trigger training:

```python
await model_manager.train_deepseek()
```

### Evaluating the Model

To evaluate the model:

```python
test_prompts = [
    "What is the role of attention in transformer models?",
    "How can reinforcement learning be applied to robotics?",
    "Explain the concept of few-shot learning."
]
evaluation_results = await learning_system.evaluate_model(test_prompts)
```

## Configuration

The learning system can be configured in the `config/config.yaml` file:

```yaml
models:
  deepseek:
    learning_enabled: true
    learning_rate: 0.001
    batch_size: 16
    epochs: 5
    evaluation_interval: 100
```

## Testing

The learning system can be tested using the `test_learning_system.py` script:

```bash
python test_learning_system.py
```

This script tests:
- Learning from all models
- The feedback system
- The training process
- Model evaluation

## Future Improvements

Planned improvements for the learning system include:

1. **Active Learning**: Proactively identify areas where the model needs improvement.
2. **Multi-modal Learning**: Learn from images, audio, and other modalities.
3. **Distributed Training**: Distribute training across multiple machines.
4. **Transfer Learning**: Apply knowledge from one domain to another.
5. **Explainable AI**: Provide explanations for why the model made certain decisions.
