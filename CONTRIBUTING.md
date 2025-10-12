# Contributing to Claude Vision & Hands

First off, thank you for considering contributing! 🎉

## How to Contribute

### Reporting Bugs

1. Check if the bug is already reported in [Issues](https://github.com/yourusername/claude-vision-hands/issues)
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Logs if available

### Suggesting Features

1. Check [existing feature requests](https://github.com/yourusername/claude-vision-hands/issues?q=is%3Aissue+label%3Aenhancement)
2. Create a new issue with:
   - Clear use case
   - Expected behavior
   - Why it would be useful

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Commit: `git commit -m 'Add amazing feature'`
7. Push: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

### Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=mcp-servers tests/
```

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/claude-vision-hands
cd claude-vision-hands

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r mcp-servers/vision-mcp/requirements.txt
pip install -r mcp-servers/hands-mcp/requirements.txt
pip install -r mcp-servers/integration-mcp/requirements.txt

# Install dev dependencies
pip install pytest pytest-cov black flake8
```

## Community

- Be respectful and inclusive
- Help others when you can
- Share your use cases and workflows

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
