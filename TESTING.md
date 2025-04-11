# Testing the DMac WebArena Integration

This document provides instructions for testing the DMac WebArena integration.

## Prerequisites

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Install Ollama from [https://ollama.ai/](https://ollama.ai/)

3. Start Ollama:
   ```
   ollama serve
   ```

## Testing Steps

### 1. Pull Ollama Models

Run the following command to pull the necessary Ollama models:

```
python pull_models.py
```

This will pull the following models:
- llama2
- mistral
- gemma:2b

### 2. Test Ollama Integration

Run the following command to test the Ollama integration:

```
python test_app.py
```

This will check if Ollama is running and list the available models.

### 3. Test Dashboard

Run the following command to test the dashboard:

```
python test_dashboard.py
```

This will start a test dashboard server on http://localhost:8080.

You can access the following pages:
- Home: http://localhost:8080/
- Login: http://localhost:8080/login
- Dashboard: http://localhost:8080/dashboard
- WebArena: http://localhost:8080/webarena
- WebArena Dashboard: http://localhost:8080/webarena/dashboard

### 4. Test WebArena Integration

Run the following command to test the WebArena integration:

```
python tests/test_webarena_integration.py
```

This will test the WebArena integration by creating a WebArena agent, running an experiment, and checking the results.

## Troubleshooting

### Ollama Not Running

If you see an error like "Ollama is not running", make sure Ollama is installed and running:

```
ollama serve
```

### Missing Models

If you see an error about missing models, run the pull_models.py script:

```
python pull_models.py
```

### Import Errors

If you see import errors, make sure you have installed all the required packages:

```
pip install -r requirements.txt
```

### Configuration Errors

If you see configuration errors, check the config/config.py file and make sure it has the correct settings.

## Next Steps

After testing the WebArena integration, you can:

1. Implement the full DMac application with WebArena integration
2. Create a WebArena agent that can interact with the WebArena environment
3. Develop visualizations for WebArena results
4. Integrate WebArena with the DMac learning system
