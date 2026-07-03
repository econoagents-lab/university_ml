from pathlib import Path
import nbformat

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = [
    ROOT / "notebooks" / "UNI_Final_RAG_Asistente_Economico_Inmobiliario.ipynb",
]


def test_final_uni_notebook_code_cells_compile():
    """Yo valido que las celdas de código del notebook final no tengan errores de sintaxis."""
    for notebook_path in NOTEBOOKS:
        assert notebook_path.exists(), f"No encuentro el notebook esperado: {notebook_path}"
        notebook = nbformat.read(notebook_path, as_version=4)
        for index, cell in enumerate(notebook.cells):
            if cell.cell_type != "code":
                continue
            compile(cell.source, f"{notebook_path.name}:cell_{index}", "exec")
