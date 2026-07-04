# Yo preparo el entorno del notebook para ejecutar desde Colab o local.
# Yo necesito que Python vea la carpeta raíz del proyecto, donde existe rag/pipeline.py.
from pathlib import Path
import os
import sys
import zipfile

PROJECT_PREFIX = "machine_learning_university"


def _has_rag_package(path: Path) -> bool:
    """
    Yo valido si una carpeta parece ser la raíz del proyecto porque contiene
    el paquete rag y el archivo pipeline.py que voy a importar después.
    """
    return (path / "rag" / "pipeline.py").exists()


def _candidate_roots() -> list[Path]:
    """
    Yo genero candidatos rápidos para evitar búsquedas lentas en Colab.
    Primero miro la carpeta actual, luego /content y finalmente MyDrive si existe.
    """
    bases = [Path.cwd(), Path("/content"), Path("/content/drive/MyDrive")]
    candidates: list[Path] = []

    for base in bases:
        if not base.exists():
            continue
        candidates.append(base)
        candidates.extend(base.glob(f"{PROJECT_PREFIX}*"))
        candidates.extend(base.glob(f"*/{PROJECT_PREFIX}*"))

    return candidates


def _unzip_project_if_needed() -> None:
    """
    Yo descomprimo automáticamente el ZIP del proyecto si lo encuentro en Colab.
    Esto evita el error ModuleNotFoundError: No module named 'rag'.
    """
    search_dirs = [Path.cwd(), Path("/content"), Path("/content/drive/MyDrive")]
    zip_candidates: list[Path] = []

    for directory in search_dirs:
        if directory.exists():
            zip_candidates.extend(directory.glob(f"{PROJECT_PREFIX}*.zip"))

    if not zip_candidates:
        return

    zip_path = sorted(zip_candidates, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    extract_dir = Path("/content/mlu_project") if Path("/content").exists() else Path.cwd()
    extract_dir.mkdir(parents=True, exist_ok=True)

    print(f"Yo encontré el ZIP del proyecto: {zip_path}")
    print(f"Yo lo descomprimo en: {extract_dir}")
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        zip_file.extractall(extract_dir)


def find_project_root() -> Path:
    """
    Yo encuentro la raíz real del proyecto y la agrego a sys.path.
    Si no la encuentro, explico exactamente qué falta subir a Colab.
    """
    for candidate in _candidate_roots():
        if _has_rag_package(candidate):
            return candidate.resolve()

    _unzip_project_if_needed()

    for candidate in _candidate_roots():
        if _has_rag_package(candidate):
            return candidate.resolve()

    raise FileNotFoundError(
        "No encontré rag/pipeline.py. "
        "En Colab, sube el ZIP completo del proyecto o descomprímelo en /content. "
        "No basta con subir solo el notebook."
    )


PROJECT_ROOT = find_project_root()
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print("Proyecto detectado:", PROJECT_ROOT)
print("Import path listo:", str(PROJECT_ROOT) in sys.path)
print("Paquete RAG:", PROJECT_ROOT / "rag" / "pipeline.py")
