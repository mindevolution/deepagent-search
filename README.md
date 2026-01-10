# How to Run Skill Agent UI

Complete step-by-step guide for running the Skill Agent UI with Qianwen models.

## Prerequisites

### 1. Python Environment

Ensure you have Python 3.11+ installed:

```bash
python --version
# Should show Python 3.11 or higher
```

### 2. Install Required Dependencies

Install all required packages:

```bash
# Install Streamlit (for UI)
pip install streamlit

# Install LangChain dependencies
pip install langchain langchain-core langchain-community

# Install other dependencies
pip install python-dotenv

# Or install from requirements if available
pip install -r requirements_agentskill.txt
```

### 3. Get DashScope API Key

1. Go to [阿里云 DashScope Console](https://dashscope.console.aliyun.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the API key

## Setup Steps

### Step 1: Create Environment File

Create a `.env` file in the project root directory:

```bash
# In the project root
touch .env
```

Add your API key to the `.env` file:

```env
DASHSCOPE_API_KEY=your_api_key_here
DASHSCOPE_MODEL=qwen-turbo
```

**Important**: Replace `your_api_key_here` with your actual API key.

### Step 2: Verify Skills Directory

Ensure the `skills/` directory exists and contains skill files:

```bash
# Check if skills directory exists
ls skills/

# Should show files like:
# skill_calculator.py
# skill_text_processor.py
# skill_time.py
# skill_example.py
```

If the directory doesn't exist, create it:

```bash
mkdir -p skills
```

### Step 3: Verify Project Structure

Your project should have this structure:

```
deepagent/
├── skill_agent_ui.py          # Main UI file
├── AgentSkill.py              # Skill agent module
├── config.py                  # Configuration module
├── core/                      # Core modules
│   ├── __init__.py
│   └── state.py
├── middleware.py              # Middleware module
├── utils.py                   # Utility functions
├── skills/                     # Skills directory
│   ├── skill_calculator.py
│   ├── skill_text_processor.py
│   ├── skill_time.py
│   └── skill_example.py
├── .env                       # Environment variables (create this)
└── README files
```

## Running the UI

### Method 1: Direct Streamlit Command

```bash
# From project root directory
streamlit run skill_agent_ui.py
```

### Method 2: With Custom Port

If port 8501 is already in use:

```bash
streamlit run skill_agent_ui.py --server.port 8502
```

### Method 3: With Custom Address

To access from other devices on your network:

```bash
streamlit run skill_agent_ui.py --server.address 0.0.0.0
```

### Method 4: Headless Mode (No Browser)

```bash
streamlit run skill_agent_ui.py --server.headless true
```

## First-Time Setup Checklist

- [ ] Python 3.11+ installed
- [ ] All dependencies installed (`pip install streamlit langchain langchain-community python-dotenv`)
- [ ] `.env` file created with `DASHSCOPE_API_KEY`
- [ ] `skills/` directory exists with at least one skill file
- [ ] Running from project root directory
- [ ] No port conflicts (8501 available)

## Accessing the UI

After running the command, you should see:

```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

1. Open your web browser
2. Navigate to `http://localhost:8501`
3. You should see the Skill Agent UI

## Initial Configuration

### 1. Configure Model Settings (Sidebar)

- **Qianwen Model**: Select from dropdown (qwen-turbo recommended for first run)
- **Temperature**: Adjust slider (0.7 is a good starting point)
- **Top P**: Adjust slider (0.8 is a good starting point)

### 2. Configure Skill System (Sidebar)

- **Skills Directory**: Should be `./skills` (default)
- **State Mode**: Select `fifo` (recommended)
- **Auto Discover Skills**: Check this box
- **Enable Middleware**: Check this box
- **Verbose Logging**: Optional (uncheck for cleaner output)

### 3. Initialize Agent

1. Click the **"🚀 Initialize Agent"** button
2. Wait for initialization (may take a few seconds)
3. You should see: "✅ Agent initialized with X skills!"
4. Skills list will appear in the sidebar

### 4. Start Chatting

1. Type your question in the chat input at the bottom
2. Press Enter or click send
3. Agent will respond using available skills

## Common Issues and Solutions

### Issue 1: "DASHSCOPE_API_KEY not found"

**Solution**:
```bash
# Check if .env file exists
ls -la .env

# If not, create it
echo "DASHSCOPE_API_KEY=your_key_here" > .env

# Verify contents
cat .env
```

### Issue 2: "No skills loaded"

**Solution**:
```bash
# Check skills directory
ls skills/

# If empty, ensure you have skill files with pattern skill_*.py
# Example skill files should be present:
# - skill_calculator.py
# - skill_example.py
```

### Issue 3: "Port 8501 is already in use"

**Solution**:
```bash
# Use a different port
streamlit run skill_agent_ui.py --server.port 8502

# Or find and kill the process using port 8501
# On macOS/Linux:
lsof -ti:8501 | xargs kill -9
```

### Issue 4: "ModuleNotFoundError"

**Solution**:
```bash
# Ensure you're in the project root directory
pwd
# Should show: /path/to/deepagent

# Install missing dependencies
pip install -r requirements_agentskill.txt

# Or install individually
pip install streamlit langchain langchain-core langchain-community python-dotenv
```

### Issue 5: "ImportError: attempted relative import"

**Solution**:
```bash
# Make sure you're running from project root
cd /path/to/deepagent

# Verify project structure
ls -la AgentSkill.py config.py core/ middleware.py utils.py

# Run from project root
streamlit run skill_agent_ui.py
```

### Issue 6: "Agent initialization fails"

**Possible causes**:
1. Invalid API key - Check `.env` file
2. Network issues - Check internet connection
3. API quota exceeded - Check DashScope console
4. Model name incorrect - Use valid model name (qwen-turbo, qwen-plus, etc.)

**Solution**:
```bash
# Test API key manually
python -c "
from langchain_community.chat_models import ChatTongyi
import os
from dotenv import load_dotenv
load_dotenv()
model = ChatTongyi(model='qwen-turbo', api_key=os.getenv('DASHSCOPE_API_KEY'))
print('API key test:', 'OK' if model else 'FAILED')
"
```

## Quick Start Script

Create a helper script `run_ui.sh`:

```bash
#!/bin/bash
# run_ui.sh

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create .env file with DASHSCOPE_API_KEY"
    exit 1
fi

# Check if skills directory exists
if [ ! -d "skills" ]; then
    echo "Warning: skills directory not found. Creating it..."
    mkdir -p skills
fi

# Run the UI
echo "Starting Skill Agent UI..."
streamlit run skill_agent_ui.py
```

Make it executable and run:

```bash
chmod +x run_ui.sh
./run_ui.sh
```

## Testing the Setup

### Test 1: Verify Dependencies

```bash
python -c "import streamlit; import langchain; print('✓ All dependencies OK')"
```

### Test 2: Verify Environment

```bash
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
key = os.getenv('DASHSCOPE_API_KEY')
print('✓ API Key:', 'Found' if key else 'NOT FOUND')
"
```

### Test 3: Verify Skills

```bash
python -c "
from pathlib import Path
skills = list(Path('skills').glob('skill_*.py'))
print(f'✓ Found {len(skills)} skill files')
for s in skills:
    print(f'  - {s.name}')
"
```

### Test 4: Verify Imports

```bash
python -c "
import sys
from pathlib import Path
sys.path.insert(0, '.')
from AgentSkill import create_skill_agent
from config import SkillSystemConfig
print('✓ All modules import successfully')
"
```

## Usage Examples

### Example 1: Basic Calculation

1. Initialize agent (if not done)
2. Type: `Calculate 25 * 4`
3. Agent will use calculator skill
4. Response: `Result: 100`

### Example 2: Text Processing

1. Type: `Convert "hello world" to uppercase`
2. Agent will use text processor skill
3. Response: `HELLO WORLD`

### Example 3: Time Query

1. Type: `What time is it?`
2. Agent will use time skill
3. Response: `Current time: 2024-01-15 14:30:25`

### Example 4: List Skills

1. Click "📋 List Skills" button
2. Or type: `What skills do you have?`
3. Agent will list all available skills

## Advanced Configuration

### Custom Port

```bash
streamlit run skill_agent_ui.py --server.port 8502
```

### Custom Address

```bash
streamlit run skill_agent_ui.py --server.address 0.0.0.0 --server.port 8501
```

### Enable Browser Auto-open

```bash
streamlit run skill_agent_ui.py --server.headless false
```

### Disable Browser Auto-open

```bash
streamlit run skill_agent_ui.py --server.headless true
```

## Troubleshooting Checklist

If the UI doesn't work, check:

1. ✅ Python version is 3.11+
2. ✅ All dependencies installed
3. ✅ `.env` file exists with valid API key
4. ✅ Running from project root directory
5. ✅ `skills/` directory exists with skill files
6. ✅ No port conflicts
7. ✅ Internet connection active
8. ✅ API key is valid and has quota
9. ✅ Model name is correct (qwen-turbo, qwen-plus, etc.)

## Getting Help

If you encounter issues:

1. Check the error message in the terminal
2. Check the error message in the browser (if any)
3. Review the troubleshooting section above
4. Check Streamlit logs in terminal
5. Verify all prerequisites are met

## Next Steps

After successfully running the UI:

1. Try different Qianwen models (qwen-plus, qwen-max)
2. Create your own custom skills
3. Adjust temperature and top_p for different response styles
4. Experiment with different state modes
5. Add more skills to the skills directory

## Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [DashScope Console](https://dashscope.console.aliyun.com/)
- [Qianwen Model Documentation](https://help.aliyun.com/zh/model-studio/)
- [Skill Agent Guide](./QIANWEN_SKILL_AGENT_GUIDE.md)
