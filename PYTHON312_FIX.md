# Python 3.12 Compatibility Fix

If you're encountering this error with Python 3.12:

```
TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'
```

This is a known compatibility issue between Python 3.12 and older versions of pydantic/langsmith.

## Quick Fix

### Option 1: Update Dependencies (Recommended)

```bash
# Activate your virtual environment
source venv/bin/activate  # On Mac/Linux
# or
venv\Scripts\activate  # On Windows

# Upgrade pip first
pip install --upgrade pip

# Uninstall problematic packages
pip uninstall langchain langchain-openai langchain-community langsmith -y

# Reinstall with updated versions
pip install --upgrade langchain langchain-openai langchain-community

# Reinstall all requirements
pip install -r requirements.txt
```

### Option 2: Use Python 3.11 (Alternative)

If the above doesn't work, you can downgrade to Python 3.11:

```bash
# Using pyenv (recommended)
pyenv install 3.11.7
pyenv local 3.11.7

# Recreate virtual environment
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Option 3: Pin Specific Versions

If you need exact versions for Python 3.12, use this requirements file:

```bash
pip install --upgrade \
  "langchain>=0.1.0" \
  "langchain-openai>=0.1.0" \
  "langchain-community>=0.0.20" \
  "pydantic>=2.5.3" \
  "langsmith>=0.1.0"
```

## Verify the Fix

After applying the fix, test that it works:

```bash
python manage.py check
python manage.py migrate
```

## Why This Happens

- Python 3.12 changed the internal API for `ForwardRef._evaluate()`
- Older versions of `langsmith` (used by `langchain`) use `pydantic.v1` compatibility layer
- The compatibility layer doesn't work with Python 3.12's new API

## Recommended Python Version

For best compatibility with all dependencies:
- **Python 3.11.x** (most stable)
- **Python 3.12.x** (works with updated packages)

Avoid Python 3.13+ for now as some ML libraries may not be compatible yet.
