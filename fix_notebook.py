import json

# Load the notebook
with open('OpenManus-RL/openmanus_rl/agentgym/agentenv-webarena/webarena/scripts/webarena-zeno.ipynb', 'r') as f:
    notebook = json.load(f)

# Find the cell with the ZenoClient initialization
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        if 'client = zeno_client.ZenoClient' in source:
            print(f"Found cell with ZenoClient: {source}")
            # Create a new source with the fixed code
            new_source = [
                "# read ZENO_API_KEY from .env file\n",
                "load_dotenv(override=True)\n",
                "\n",
                "client = zeno_client.ZenoClient(os.environ.get(\"ZENO_API_KEY\"))\n"
            ]
            cell['source'] = new_source
            print(f"Fixed cell: {cell['source']}")
            break

# Save the notebook
with open('OpenManus-RL/openmanus_rl/agentgym/agentenv-webarena/webarena/scripts/webarena-zeno.ipynb', 'w') as f:
    json.dump(notebook, f, indent=1)

print("Notebook fixed successfully!")
