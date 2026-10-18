"""Gera um único executável para Windows."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    if sys.platform != "win32":
        raise SystemExit("O executável deve ser gerado no Windows.")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--onefile",
            "--windowed",
            "--name",
            "Extrair",
            "--distpath",
            str(ROOT / "dist"),
            "--workpath",
            str(ROOT / "build"),
            "--specpath",
            str(ROOT / "build"),
            str(ROOT / "main.py"),
        ],
        cwd=ROOT,
        check=True,
    )

    print(f"Executável criado em {ROOT / 'dist' / 'Extrair.exe'}")


if __name__ == '__main__':
    main()
