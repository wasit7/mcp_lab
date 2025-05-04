#!/bin/bash

# Create project directory
mkdir -p ./lab

# Download Northwind database
wget -O ./lab/northwind.db https://raw.githubusercontent.com/jpwhite3/northwind-SQLite3/master/dist/northwind.db

# Create placeholder files
touch ./lab/app.py
touch ./lab/test.py
touch ./lab/requirements.txt
touch ./lab/README.md

# Populate requirements.txt
echo -e "fastapi\nuvicorn\nrequests\nollama\npytest" > ./lab/requirements.txt

# Populate README.md
echo -e "# MCP LLM Evaluation Project\n\nEvaluates LLM accuracy with MCP queries using the Northwind database.\n\n## Setup\n1. Install dependencies: \`pip install -r requirements.txt\`\n2. Start Ollama: \`ollama run llama3.2\`\n3. Run: \`python app.py\`\n4. Test: \`python test.py\`" > ./lab/README.md

echo "Project setup complete."