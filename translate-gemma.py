from transformers import pipeline
import torch

pipe = pipeline(
    "image-text-to-text",
    model="google/translategemma-4b-it",
    device="cuda",
    dtype=torch.bfloat16
)

# ---- Text Translation ----
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "source_lang_code": "en",
                "target_lang_code": "ko-KR",
                "text": """# LocAI - Local AI Code Assistant

> 🚀 Autonomous AI coding assistant powered by local LLMs

LocAI is a powerful command-line AI assistant that runs entirely on your machine. No API keys, no cloud dependencies - just you and your local models working together to write better code.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

### 🤖 Autonomous Agent
- **ReAct-style reasoning**: Think, act, and observe in a loop
- **Tool use**: Automatically search, read, and edit files
- **Safety limits**: Max 10 iterations, command blacklist protection

### 🎯 Multi-Model Intelligence
- **Parallel inference**: Run multiple models simultaneously
- **Smart synthesis**: Combine answers using judge, voting, or other strategies
- **VRAM management**: Automatic fallback from concurrent to sequential execution

### 💬 Interactive Chat
- **Project-aware**: Understands your codebase context
- **Streaming output**: See responses as they're generated
- **Rich UI**: Beautiful terminal interface with progress indicators
- **Session management**: Save and restore conversations

### 🛠️ Code Operations
- **Explain**: Understand complex code with AI-powered explanations
- **Generate**: Create new code from natural language descriptions
- **Edit**: Modify existing code with atomic, safe operations
- **Review**: Get AI feedback on code quality and potential issues

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd code-assistants

# Install in development mode
pip install -e .

# Or with optional dependencies
pip install -e ".[dev,code-analysis]"
```

### First Run

```bash
# Start LocAI
loc

# First time? The setup wizard will guide you:
# 1. Search for models (e.g., "qwen coder", "codellama")
# 2. Download your chosen model
# 3. Start chatting!
```

### Basic Usage

```bash
# Interactive chat
loc chat

# Chat with project context
loc chat --project .

# Use specific model
loc chat --model qwen2.5-coder-7b

# Explain code
loc explain src/auth.py

# Generate code
loc create utils.py --prompt "Create a JWT validation function"
```

---

## 📚 Commands

### Chat Mode

```bash
loc chat                              # Start interactive session
loc chat --model <name>               # Use specific model
loc chat --project <path>             # Include project context
loc chat --files <file1> <file2>      # Include specific files
loc chat --temperature 0.7            # Set temperature
loc chat --max-tokens 2048            # Set max tokens
```

**In-chat commands:**
```
/help                  # Show help
/clear                 # Clear conversation
/model <name>          # Switch model
/project <path>        # Set project directory
/files <paths>         # Add context files
/best <question>       # Multi-model synthesis
/compare <question>    # Compare model responses
/save <name>           # Save session
/load <name>           # Load session
/exit                  # Exit
```

### Model Management

```bash
loc model search <query>              # Search Hugging Face
loc model download <repo_id>          # Download model
loc model list                        # List local models
loc model set <name>                  # Set default model
loc model info <name>                 # Show model info
loc model remove <name>               # Remove model
```

### Code Operations

```bash
loc explain <file>                    # Explain code
loc explain <file> --line 10-20       # Explain specific lines
loc explain <file> --function main    # Explain function

loc create <file> --prompt "..."      # Generate new code
loc edit <file> --prompt "..."        # Edit existing code
```

---

## 🎯 Advanced Features

### Multi-Model Synthesis

Get the best answer by running multiple models and synthesizing their responses:

```bash
loc chat

You> /best What's the most efficient way to sort a list in Python?
```

LocAI will:
1. Run inference on multiple models in parallel
2. Collect all responses
3. Use a judge model to synthesize the best answer
4. Show you the combined result

### Model Comparison

Compare responses side-by-side:

```bash
You> /compare FastAPI vs Flask - which is better for microservices?
```

See each model's perspective in beautiful panels.

### Autonomous Agent

Use LocAI programmatically for autonomous tasks:

```python
from codepilot.core.agent import Agent

agent = Agent()
result = agent.run("Find and fix the bug in tests/test_auth.py")
print(result)
```

The agent will:
- Search for relevant files
- Read the code
- Identify the bug
- Edit the file with a fix
- Create a backup automatically

---

## ⚙️ Configuration

### Config File

Location: `~/.locai/config.yaml`

```yaml
# Default model
default_model: "codellama-7b-instruct"

# Hardware settings
hardware:
  gpu_layers: 35      # Number of layers on GPU (0 = CPU only)
  threads: 8          # CPU threads

# Inference settings
inference:
  n_ctx: 4096         # Context window size
  max_tokens: 256     # Max tokens to generate
  temperature: 0.7    # Sampling temperature
  chat_format: null   # Or "qwen", "gemma", "chatml"
```

### Directory Structure

```
~/.locai/
├── models/          # Downloaded GGUF models
├── cache/           # Inference cache
├── sessions/        # Saved chat sessions
├── prompts/         # Custom prompts
└── config.yaml      # Configuration file
```

---

## 🔧 Architecture

### Components

```
┌─────────────────────────────────────────┐
│         CLI Interface Layer             │
│  (Typer, Rich, prompt_toolkit)          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       Application Core Layer            │
│  • Agent (ReAct loop)                   │
│  • Conversation Manager                 │
│  • Session Manager                      │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Service Layer                   │
│  • Model Orchestrator                   │
│  • Synthesis Engine                     │
│  • Context Builder                      │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Infrastructure Layer               │
│  • InferenceEngine (llama.cpp)          │
│  • Tools (list, read, grep, edit, bash) │
│  • Hugging Face Client                  │
└─────────────────────────────────────────┘
```

### Key Features

- **Autonomous Agent**: ReAct-style loop with tool use
- **Multi-Model Orchestration**: Concurrent/sequential execution with VRAM management
- **Synthesis Engine**: 4 strategies (judge, voting, longest, concatenation)
- **Rich UI**: Live panels, progress indicators, syntax highlighting
- **Safety**: Max iterations, command blacklist, user confirmation

---

## 📋 Requirements

### Minimum (CPU only)
- Python 3.10+
- 8GB RAM
- 10GB disk space

### Recommended (with GPU)
- Python 3.10+
- 16GB RAM
- NVIDIA GPU with 8GB+ VRAM (or Apple Silicon)
- 50GB disk space

### Dependencies

**Core:**
- `llama-cpp-python>=0.2.20` - LLM inference engine
- `typer>=0.9.0` - CLI framework
- `rich>=13.0.0` - Terminal UI
- `prompt-toolkit>=3.0.0` - Interactive REPL
- `huggingface-hub>=0.19.0` - Model downloads
- `pyyaml>=6.0` - Configuration
- `gitignore-parser>=0.1.0` - Project scanning
- `tiktoken>=0.5.0` - Token counting

**Optional:**
- `tree-sitter>=0.20.0` - Code parsing
- `pygments>=2.14.0` - Syntax highlighting

---

## 🎓 Examples

### Example 1: Project Analysis

```bash
loc chat --project ~/my-app

You> Explain the authentication flow in this project
Assistant: [Analyzes your codebase and explains the auth flow]

You> Are there any security issues?
Assistant: [Reviews code and identifies potential vulnerabilities]
```

### Example 2: Code Generation

```bash
loc create src/validators.py --prompt "Create email and phone validators with regex"
```

### Example 3: Bug Fixing

```bash
loc chat

You> /project .
You> Find and fix the bug in tests/test_api.py where the mock isn't working
```

The agent will:
1. Read the test file
2. Identify the mock issue
3. Edit the file with the fix
4. Create a backup

### Example 4: Multi-Model Comparison

```bash
You> /compare Should I use TypeScript or JavaScript for a new React project?
```

See different perspectives from multiple models side-by-side.

---

## 🛡️ Safety Features

- **Max iterations**: Agent stops after 10 reasoning loops
- **Command blacklist**: Dangerous commands blocked by default
- **User confirmation**: Bash commands require approval
- **Atomic edits**: File changes create backups automatically
- **No auto-execution**: Destructive operations need explicit permission

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black codepilot/
ruff check --fix codepilot/

# Type checking
mypy codepilot/
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [llama.cpp](https://github.com/ggerganov/llama.cpp) for efficient local inference
- Uses [Hugging Face](https://huggingface.co) for model distribution
- Inspired by [Claude Code](https://docs.anthropic.com/claude/docs) and [Aider](https://github.com/paul-gauthier/aider)

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/locai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/locai/discussions)

---

**Made with ❤️ for developers who value privacy and local control**
""",
            }
        ],
    }
]

output = pipe(text=messages)
print(output[0]["generated_text"][-1]["content"])
