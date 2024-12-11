# ASTRA AI Setup Guide for Beginners

# Prerequisites
- A computer with at least 8GB RAM (16GB recommended)
- Internet connection
- Windows, macOS, or Linux operating system

# Step 1: Install PyCharm Community Edition
1. Visit [PyCharm download page](https://www.jetbrains.com/pycharm/download/)
2. Select "Community Edition"
3. Download and run the installer
4. During installation:
   - Accept default options
   - Select "Create Desktop Shortcut" if desired
   - Select "Update PATH variable" (Windows)
5. Launch PyCharm after installation

# Step 2: Install Ollama
1. Visit [Ollama download page](https://ollama.ai/download)
2. Download the appropriate version:
   - Windows: Click "Download for Windows"
   - macOS: Click "Download for macOS"
   - Linux: Follow Linux installation instructions
3. Install Ollama:
   - Windows: Run the installer
   - macOS: Move to Applications folder
   - Linux: Follow terminal commands
4. Pull required models:
   - Open terminal/command prompt
   - Run these commands:
   ollama pull tinyllama (Small)
   
   Optional larger models if you have more RAM:
   - ollama pull orca-mini (Medium)
   - ollama pull llama3.2 (Medium-Large)

# Step 3: Set Up GitHub and Clone Repository
1. Create GitHub account at [github.com](https://github.com) if you don't have one
2. Install Git:
   - Windows: Download from [git-scm.com](https://git-scm.com)
   - macOS: Install via Terminal: `brew install git`
3. Configure Git to your account
4. Clone the repository:
   - Open PyCharm
   - Click "Get from VCS" on welcome screen
   - Paste repository URL: `(https://github.com/kevCastillo/AstraAI.git)`
   - Choose directory for project "C:\Users\[NameHere]\PycharmProjects\AstraAI
   - Click "Clone"

# Step 4: Set Up Python Virtual Environment
1. In PyCharm:
2. Click 'astra_ai.py' and you will be prompted to create a virtual enviorment for your PyCharm Session, if not you may follow the instructions below.
   - Click "File" → "Settings" (Windows/Linux) | or "PyCharm" → "Preferences" (macOS)
   - Navigate to "Project: [ProjectName]" → "Python Interpreter"
   - Click gear icon → "Add"
   - Select "Virtualenv Environment" → "New environment"
   - Select Python 3.12 as base interpreter
   - Click "OK"
   - 
[Note: You may visit the link here to ensure Venv setup is configured properly: https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html]

3. Open PyCharm terminal:
   - View → Tool Windows → Terminal
   - Verify virtual environment is active (should see `(venv)` prefix)

# Step 5: Install Dependencies
1. Ensure `requirements.txt` in project root:
   ' streamlit==1.31.0
   PyPDF2==3.0.1
   python-docx==1.0.0
   ollama==0.1.6
   rich==13.7.0 `

2. Install requirements:
   - In PyCharm terminal:
   pip install -r requirements.txt

# Step 6: Project Structure
1. Ensure your project has this structure:
   ```
   AstraAI/
   ├── astra_ai.py
   ├── streamlit_app.py
   ├── requirements.txt
   └── temp/
   ```

2. Create `temp` directory if it doesn't exist

# Step 7: Run the Application
1. In PyCharm terminal:
   'streamlit run streamlit_app.py'
2. Web browser should open automatically
3. If not, copy URL from terminal and paste in browser

# Step 8: Using the Application
1. Upload a document:
   - Click "Browse files" in sidebar
   - Select a TXT, PDF, or DOCX file
   - Wait for confirmation

2. Chat mode:
   - Type questions about your document
   - Wait for AI responses
   - Continue conversation

3. Quiz mode:
   - Switch to "Quiz" mode in sidebar
   - Select number of questions
   - Click "Start Quiz"
   - Answer questions
   - View your score and streak

## Troubleshooting Common Issues

### Python Path Issues
If terminal says "python not found":
1. Windows:
   - Search "Environment Variables"
   - Edit Path variable
   - Add Python installation directory

2. macOS/Linux:
   'export PATH="$PATH:/usr/local/bin/python3"'

### Ollama Connection Issues
If you get "Failed to connect to Ollama":
1. Verify Ollama is running:
   - Windows: Check Task Manager
   - macOS/Linux: `ps aux | grep ollama`
2. Restart Ollama service
3. Ensure no firewall blocking

### Package Installation Issues
If `pip install` fails:
1. Upgrade pip:
   `python -m pip install --upgrade pip`
2. Try installing packages individually:
   `pip install streamlit
   pip install PyPDF2
   # etc.`

### Document Loading Issues
If documents fail to load:
1. Check file permissions
2. Ensure document isn't corrupted
3. Try a smaller document first
4. Check `temp` directory exists

## Additional Tips
1. Keep documents under 10 pages for best performance
2. Start with small documents to test functionality
3. Use TXT files initially as they're simplest
4. Monitor system resources while running
5. Save chat logs if needed for reference

## Support Resources
- Python Documentation: [docs.python.org](https://docs.python.org)
- Streamlit Documentation: [docs.streamlit.io](https://docs.streamlit.io)
- Ollama Documentation: [ollama.ai/docs](https://ollama.ai/docs)
- PyCharm Guide: [jetbrains.com/help/pycharm](https://jetbrains.com/help/pycharm)
