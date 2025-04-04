# DMac Installation Guide

This guide will help you install and set up DMac and its dependencies.

## Prerequisites

DMac requires the following prerequisites:

1. **Python 3.8+**: DMac is built with Python and requires version 3.8 or higher.
2. **Ollama**: DMac uses Ollama to run local LLMs, which is a core requirement.
3. **Required Python packages**: Listed in `requirements.txt`.

## Step 1: Install Python

If you don't have Python 3.8+ installed, download and install it from the [official Python website](https://www.python.org/downloads/).

Verify your Python installation:

```bash
python --version
```

## Step 2: Install Ollama

Ollama is a critical dependency for DMac as it manages our local LLM ecosystem. DMac prioritizes using local models through Ollama and only uses external services like Gemini strategically when needed.

### Windows

1. Download the Ollama installer from [https://ollama.com/download](https://ollama.com/download)
2. Run the installer and follow the instructions
3. After installation, Ollama will start automatically

### macOS

1. Download the Ollama app from [https://ollama.com/download](https://ollama.com/download)
2. Open the downloaded file and drag Ollama to the Applications folder
3. Launch Ollama from the Applications folder

### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

After installation, start the Ollama service:

```bash
ollama serve
```

## Step 3: Verify Ollama Installation

Verify that Ollama is installed and running:

```bash
ollama list
```

You should see a list of available models (which might be empty if you haven't pulled any models yet).

## Step 4: Install DMac

1. Clone the DMac repository:

```bash
git clone https://github.com/yourusername/dmac.git
cd dmac
```

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Step 5: Configure DMac

1. Copy the example configuration file:

```bash
cp config/config.example.yaml config/config.yaml
```

2. Edit the configuration file to set your API keys and preferences:

```bash
# Use your favorite text editor
nano config/config.yaml
```

### API Keys and Credentials (Optional)

DMac prioritizes local models through Ollama, but can also use external services like Gemini as a fallback or for specific tasks. For security reasons, API keys are stored separately from the main configuration:

1. Create a credentials file by copying the example:

```bash
cp config/credentials.example.json config/credentials.json
```

2. Edit the credentials file to add your API keys:

```bash
# Use your favorite text editor
nano config/credentials.json
```

3. Alternatively, you can set environment variables:

```bash
# For Gemini API key
export DMAC_MODELS_GEMINI_API_KEY=your_gemini_api_key_here

# For other services
export DMAC_INTEGRATIONS_GITHUB_TOKEN=your_github_token_here
```

**IMPORTANT**: Never commit your credentials.json file to version control! It's already added to .gitignore for your protection.

## Step 6: Pull Required Models

DMac requires certain models to function properly. Pull them using Ollama:

```bash
# Pull the local model
ollama pull gemma3:12b

# Pull the DeepSeek model
ollama pull GandalfBaum/deepseek_r1-claude3.7
```

## Step 7: Run DMac

Start DMac:

```bash
python main.py
```

## Troubleshooting

### Ollama Issues

If you encounter issues with Ollama:

1. Make sure Ollama is running:
   ```bash
   ollama serve
   ```

2. Check if the required models are available:
   ```bash
   ollama list
   ```

3. If models are missing, pull them:
   ```bash
   ollama pull gemma3:12b
   ollama pull GandalfBaum/deepseek_r1-claude3.7
   ```

### Python Package Issues

If you encounter issues with Python packages:

```bash
pip install --upgrade -r requirements.txt
```

## Learning System

DMac features an enhanced learning system that allows the AI models to improve over time:

- **Continuous Learning**: The system learns from all interactions with all models
- **Feedback Mechanism**: Users can provide feedback on responses
- **Training Process**: DeepSeek-RL is periodically trained on the collected learning data
- **Model Evaluation**: The system regularly evaluates model performance to track improvements

The learning system prioritizes improving our local models to reduce dependency on external services over time.
