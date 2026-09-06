Write-Host ""
Write-Host "====================================="
Write-Host "Setting up Privacy-Preserving CDSS"
Write-Host "====================================="
Write-Host ""

python -m venv backend\.venv

.\backend\.venv\Scripts\Activate.ps1

pip install --upgrade pip

pip install -r requirements.txt

Write-Host ""
Write-Host "====================================="
Write-Host "Python dependencies installed."
Write-Host "====================================="
Write-Host ""

Write-Host "Installing Ollama models..."

ollama pull llama3
ollama pull nomic-embed-text

Write-Host ""
Write-Host "====================================="
Write-Host "Setup Complete!"
Write-Host "====================================="
Write-Host ""
Write-Host "Next steps:"
Write-Host ""
Write-Host "1) Start Ollama:"
Write-Host "   ollama serve"
Write-Host ""
Write-Host "2) Start backend:"
Write-Host "   .\start.ps1"
Write-Host ""
Write-Host "3) Open another terminal:"
Write-Host "   python doctor_console.py"
Write-Host ""