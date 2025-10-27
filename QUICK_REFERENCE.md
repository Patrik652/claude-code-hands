# Claude Vision & Hands - Quick Reference

**Version**: 2.0.0 | **Status**: Production-Ready

---

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Clone & Install
git clone https://github.com/Patrik652/claude-vision-hands.git
cd claude-vision-hands
pip install -r requirements.txt

# 2. Configure
export GEMINI_API_KEY="your-key-here"

# 3. Run Demo
python3 examples/autonomous_agent_demo.py
```

---

## 📦 Docker Quick Start

```bash
# Setup
cp .env.example .env
nano .env  # Add GEMINI_API_KEY

# Deploy
docker-compose up -d

# Check
docker-compose ps
curl http://localhost:8080/health
```

---

## 🧪 Run Tests

```bash
# All tests
cd tests && python3 run_all_tests.py

# Specific suite
python3 test_security.py      # Security (18 tests)
python3 test_recorder.py      # Recorder (15 tests)
python3 test_integration.py   # Integration (20 tests)
```

---

## 💻 Quick Code Examples

### 1. Autonomous Agent
```python
from integration.autonomous_agent import AutonomousAgent

agent = AutonomousAgent()
result = await agent.execute_goal_autonomously(
    goal="Complete login process",
    max_iterations=10
)
```

### 2. Memory Search
```python
from memory.manager import MemoryManager

memory = MemoryManager()
memory.start_session("my_session")
results = memory.search_memories("login", limit=10)
```

### 3. Security Validation
```python
from security.validator import SecurityValidator

validator = SecurityValidator()
is_valid, reason = validator.validate_input(user_input, "command")
```

### 4. Workflow Recording
```python
from recorder.capture import WorkflowCapture

recorder = WorkflowCapture()
session_id = recorder.start_recording("my_workflow")
# ... perform actions ...
recorder.stop_recording()
```

---

## 🔧 Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your-key              # Required
CLAUDE_VISION_MODE=production        # production/development
SECURITY_STRICT_MODE=true            # Enable strict security
```

### Files
- `config/master_config.yaml` - Main configuration
- `.env` - Environment variables
- `config/security_config.yaml` - Security settings

---

## 📊 System Components

| Component | Purpose | Status |
|-----------|---------|--------|
| Vision AI | Screen analysis (Gemini 2.0 Flash) | ✅ |
| Memory | Persistent learning (ChromaDB) | ✅ |
| Security | Multi-layer protection | ✅ |
| Recorder | Workflow capture/replay | ✅ |
| Orchestrator | Unified coordination | ✅ |
| Agent | Autonomous decisions | ✅ |
| MCP Tools | Standard interface (8 tools) | ✅ |

---

## 🛠️ MCP Tools

```python
# 8 Production Tools Available:
start_recording(workflow_name, metadata)
stop_recording()
replay_workflow(workflow_name, variables)
security_scan(target, scan_type)
validate_input(input_text, input_type)
autonomous_task(task_description, screenshot_path, max_iterations)
get_agent_status()
search_memory(query, limit, min_score)
```

---

## 📚 Documentation

| Document | Lines | Purpose |
|----------|-------|---------|
| README.md | 965 | Main overview |
| docs/SECURITY.md | 800 | Security guide |
| docs/WORKFLOWS.md | 700 | Workflow guide |
| docs/DEPLOYMENT.md | 900 | Deployment guide |
| docs/COMPLETE_SYSTEM_OVERVIEW.md | 665 | System details |

**Total**: 5,000+ lines of documentation

---

## 🔐 Security Quick Check

```python
# Test security validation
from security.validator import SecurityValidator
from security.prompt_guard import PromptGuard

validator = SecurityValidator()
guard = PromptGuard()

# Command injection check
is_valid, reason = validator.validate_input("rm -rf /", "command")
# Returns: (False, "Dangerous command pattern detected")

# Prompt injection check
is_safe, reason = guard.validate_prompt("Ignore previous instructions")
# Returns: (False, "Prompt injection detected")

# Risk scoring
risk = guard.get_risk_score("Write a Python function")
# Returns: 0.1 (low risk)
```

---

## 📈 Performance Benchmarks

| Metric | Performance |
|--------|-------------|
| Memory Search | < 100ms @ 10K memories |
| Vision Analysis | 2-5 seconds |
| Agent Decision | < 1 second |
| Storage | ~1MB / 1K memories |
| Scalability | 100K+ memories |

---

## 🐞 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Add to path
export PYTHONPATH="${PYTHONPATH}:/path/to/claude-vision-hands"
```

**2. API Key Not Found**
```bash
# Set environment variable
export GEMINI_API_KEY="your-key"

# Or in .env file
echo "GEMINI_API_KEY=your-key" > .env
```

**3. ChromaDB Errors**
```bash
# Install dependencies
pip install chromadb sentence-transformers
```

**4. Docker Issues**
```bash
# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Patrik652/claude-vision-hands/issues)
- **Docs**: `docs/` directory
- **Examples**: `examples/` directory
- **Tests**: `tests/` directory

---

## ✅ Quick Checklist

### Pre-Deployment
- [ ] Set GEMINI_API_KEY
- [ ] Review master_config.yaml
- [ ] Run test suite
- [ ] Check security settings

### Deployment
- [ ] Choose deployment method (Docker/K8s/Bare Metal)
- [ ] Configure environment
- [ ] Deploy services
- [ ] Verify health endpoints
- [ ] Check logs

### Post-Deployment
- [ ] Monitor metrics
- [ ] Review audit logs
- [ ] Test workflows
- [ ] Backup data

---

## 🎯 Key Files

```
claude-vision-hands/
├── README.md                    ← Start here
├── QUICK_REFERENCE.md          ← This file
├── requirements.txt            ← Dependencies
├── docker-compose.yml          ← Docker setup
├── config/master_config.yaml   ← Configuration
├── examples/                   ← Usage examples
│   └── autonomous_agent_demo.py
├── tests/                      ← Test suite
│   └── run_all_tests.py
└── docs/                       ← Full documentation
    ├── SECURITY.md
    ├── WORKFLOWS.md
    └── DEPLOYMENT.md
```

---

## 💡 Pro Tips

1. **Start Simple**: Run `autonomous_agent_demo.py` first
2. **Read Security**: Check `docs/SECURITY.md` before production
3. **Use Docker**: Easiest deployment method
4. **Monitor Logs**: Enable verbose logging for debugging
5. **Test First**: Run test suite before deploying

---

**Version**: 2.0.0 | **Status**: ✅ Production-Ready | **Date**: 2025-10-27

*For complete documentation, see README.md and docs/ directory*
