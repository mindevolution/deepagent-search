# Quick Start Guide - DeepAgent Chat UI

## 🚀 Quick Start

### Option 1: Web UI (Streamlit) - Recommended

```bash
streamlit run chat_ui.py
```

Then open your browser to `http://localhost:8501`

### Option 2: Command Line Interface

```bash
python chat_cli.py
```

## 📋 Prerequisites

Make sure you have:
- ✅ Python 3.8+
- ✅ All dependencies installed (from `long-term-memory.py`)
- ✅ `.env` file with API keys:
  - `DASHSCOPE_API_KEY`
  - `TAVILY_API_KEY`

## 🎯 Features

### Web UI Features
- 💬 Real-time chat interface
- 🧵 Thread management (new conversations)
- 🔍 Memory inspection sidebar
- 📱 Responsive design
- 💾 Persistent memory

### CLI Features
- 💻 Terminal-based interface
- 🧵 Thread management
- 🔍 Memory commands
- 📝 Simple command interface

## 💡 Example Usage

### Web UI
1. Start: `streamlit run chat_ui.py`
2. Type question in chat input
3. View response
4. Use sidebar to inspect memories

### CLI
```bash
python chat_cli.py

You: What is React?
🤖 Agent: React is a JavaScript library...

You: memories
📚 Found 2 memory item(s):
  1. /memories/project_notes.txt
  2. /memories/preferences.txt

You: quit
```

## 🔧 Troubleshooting

**Streamlit not found:**
```bash
pip install streamlit
```

**Import errors:**
- Check that `long-term-memory.py` is in the same directory
- Verify all dependencies are installed

**API errors:**
- Check `.env` file has correct API keys
- Verify network connection

## 📚 More Information

See `README_CHAT_UI.md` for detailed documentation.

