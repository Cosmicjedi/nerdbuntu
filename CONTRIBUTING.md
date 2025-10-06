# Contributing to Nerdbuntu

Thank you for your interest in contributing to Nerdbuntu! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check if the issue already exists in [GitHub Issues](https://github.com/Cosmicjedi/nerdbuntu/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (Ubuntu version, Python version, etc.)

### Submitting Changes

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then:
   git clone https://github.com/YOUR_USERNAME/nerdbuntu.git
   cd nerdbuntu
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test your changes**
   ```bash
   # Activate environment
   source ~/nerdbuntu/venv/bin/activate
   
   # Run the app
   python app.py
   
   # Test with sample PDFs
   python examples.py batch ./test_input ./test_output
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Describe your changes
   - Link any related issues

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose

### Example:
```python
def process_pdf(file_path: str, output_dir: str) -> str:
    """
    Process a PDF file and convert to markdown.
    
    Args:
        file_path: Path to the PDF file
        output_dir: Directory to save output
        
    Returns:
        Path to the generated markdown file
    """
    # Implementation
```

## Areas for Contribution

### High Priority
- [ ] Add more file format support (DOCX, PPTX, etc.)
- [ ] Improve error handling and user feedback
- [ ] Add unit tests
- [ ] Performance optimizations

### Features
- [ ] Web interface (Flask/FastAPI)
- [ ] Batch processing UI
- [ ] Custom embedding model selection
- [ ] Export/import vector database
- [ ] Docker containerization

### Documentation
- [ ] Video tutorials
- [ ] More usage examples
- [ ] Troubleshooting guide expansion
- [ ] Architecture diagrams

### Testing
- [ ] Unit tests for core functions
- [ ] Integration tests
- [ ] Test with various PDF types
- [ ] Performance benchmarks

## Development Setup

1. **Install dependencies**
   ```bash
   ./setup.sh
   ```

2. **Activate virtual environment**
   ```bash
   source ~/nerdbuntu/venv/bin/activate
   ```

3. **Install development tools** (optional)
   ```bash
   pip install pytest black flake8 mypy
   ```

## Testing Guidelines

When adding new features, please include tests:

```python
# tests/test_semantic_linker.py
import pytest
from app import SemanticLinker

def test_chunk_markdown():
    linker = SemanticLinker(endpoint, api_key)
    text = "# Heading\n\nParagraph 1\n\nParagraph 2"
    chunks = linker.chunk_markdown(text, chunk_size=50)
    assert len(chunks) > 0
    assert all(len(chunk) <= 50 for chunk in chunks)
```

## Documentation

- Update README.md for new features
- Add examples to examples.py
- Update QUICKSTART.md if setup changes
- Comment complex code sections

## Pull Request Checklist

Before submitting, ensure:

- [ ] Code follows project style
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] Changes are focused and minimal

## Questions?

- Open a [Discussion](https://github.com/Cosmicjedi/nerdbuntu/discussions)
- Comment on related issues
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Nerdbuntu! 🚀**
