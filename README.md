# Python Development Environment Setup

This guide walks you through setting up a complete Python development environment on a Linux-based system. Follow these steps to prepare your system for Python development projects.

## Prerequisites

- A Linux-based operating system (Ubuntu/Debian-based instructions provided)
- User with sudo privileges
- Internet connection

## Installation Steps

### Step 1: Update Package Repository

Before installing any packages, update your package repository:

```bash
sudo apt-get update
```

### Step 2: Install Python Development Headers

Install the Python development headers:

```bash
sudo apt-get install python3-dev
```

### Step 3: Install Setuptools and Pip

Install Setuptools and pip (Python's package manager):

```bash
sudo apt-get install python3-setuptools python3-pip
```

### Step 4: Install Virtualenv

Install Virtualenv for creating isolated Python environments:

```bash
sudo apt-get install virtualenv
```

## Creating a Virtual Environment

After installation, you can create a virtual environment for your project:

1. Navigate to your project directory:
   ```bash
   mkdir my_project
   cd my_project
   ```

2. Create a virtual environment:
   ```bash
   virtualenv venv
   ```
   
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

4. Deactivate when finished:
   ```bash
   deactivate
   ```

## Next Steps

- Install project-specific dependencies using `pip install <package_name>`
- Create a `requirements.txt` file to track dependencies
- Set up version control with Git

## Additional Resources

- [Python Official Documentation](https://docs.python.org/)
- [pip Documentation](https://pip.pypa.io/en/stable/)
- [Virtualenv Documentation](https://virtualenv.pypa.io/en/latest/)

## Troubleshooting

If you encounter permission issues, try adding the `--user` flag to pip commands:

```bash
pip install --user <package_name>
```

For system-level packages that require permissions, use sudo with caution.
