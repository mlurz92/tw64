from __future__ import annotations

import runpy
import sys
import types
from pathlib import Path


def _execute_spec(monkeypatch, spec_path: Path) -> Path:
    captured: dict[str, object] = {}

    hooks = types.ModuleType("PyInstaller.utils.hooks")
    hooks.collect_all = lambda _package: ([], [], [])
    monkeypatch.setitem(sys.modules, "PyInstaller", types.ModuleType("PyInstaller"))
    monkeypatch.setitem(sys.modules, "PyInstaller.utils", types.ModuleType("PyInstaller.utils"))
    monkeypatch.setitem(sys.modules, "PyInstaller.utils.hooks", hooks)

    def analysis(scripts, **_kwargs):
        captured["entry"] = Path(scripts[0]).resolve()
        return types.SimpleNamespace(pure=[], scripts=[], binaries=[], datas=[])

    globals_for_spec = {
        "SPECPATH": str(spec_path.parent),
        "Analysis": analysis,
        "PYZ": lambda _pure: object(),
        "EXE": lambda *_args, **_kwargs: object(),
        "COLLECT": lambda *_args, **_kwargs: object(),
    }
    code = compile(spec_path.read_text(encoding="utf-8"), str(spec_path), "exec")
    exec(code, globals_for_spec)
    return captured["entry"]


def test_pyinstaller_spec_uses_package_aware_entrypoint(monkeypatch):
    """Regression: the frozen executable must not execute backend_host/__main__.py as a top-level script."""
    repo_root = Path(__file__).resolve().parents[2]
    spec_path = repo_root / "engine" / "packaging" / "AssemblyNetEngine.spec"
    expected_entry = (repo_root / "engine" / "packaging" / "engine_entry.py").resolve()

    actual_entry = _execute_spec(monkeypatch, spec_path)

    assert actual_entry == expected_entry
    assert expected_entry.is_file()


def test_package_entrypoint_imports_backend_host_as_package(monkeypatch):
    """The wrapper must import backend_host.__main__, preserving its package context for relative imports."""
    repo_root = Path(__file__).resolve().parents[2]
    entry_path = repo_root / "engine" / "packaging" / "engine_entry.py"
    calls: list[list[str] | None] = []

    package = types.ModuleType("backend_host")
    package.__path__ = []
    backend_main = types.ModuleType("backend_host.__main__")

    def fake_main(argv=None):
        calls.append(argv)
        return 0

    backend_main.main = fake_main
    monkeypatch.setitem(sys.modules, "backend_host", package)
    monkeypatch.setitem(sys.modules, "backend_host.__main__", backend_main)

    try:
        runpy.run_path(str(entry_path), run_name="__main__")
    except SystemExit as exc:
        assert exc.code == 0

    assert calls == [None]
