# Extrair

Aplicativo desktop que extrai células e fórmulas de arquivos XLSX, XLSM, XLS e ODS para TXT. O processamento é local e a planilha original não é alterada.

## Executar no Linux

```bash
sudo apt install python3-venv libxcb-cursor0 libxkbcommon-x11-0
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m main
```

## Executar no Windows

No PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m main
```

## Gerar o executável do Windows

No PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe scripts\build.py
```

O arquivo será criado em `dist\Extrair.exe`. Ele pode ser aberto em outro computador Windows sem instalar Python.

## Uso

Abra ou arraste uma planilha, escolha a aba e clique em **Extrair conteúdo**. Depois, copie o texto ou exporte um arquivo TXT.
