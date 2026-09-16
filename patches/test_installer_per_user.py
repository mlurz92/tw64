from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_msi_is_fixed_scope_per_user_under_local_appdata_programs():
    product = (ROOT / 'installer' / 'Product.wxs').read_text(encoding='utf-8')
    assert 'Scope="perUser"' in product
    assert 'StandardDirectory Id="LocalAppDataFolder"' in product
    assert 'Name="Programs"' in product
    assert 'ProgramFiles64Folder' not in product


def test_installer_uses_wix_5_without_wix7_eula_acceptance():
    script = (ROOT / 'scripts' / 'build-installer.ps1').read_text(encoding='utf-8')
    assert 'dotnet tool install wix --version 5.0.2' in script
    assert '7.0.0' not in script
    assert '-acceptEula' not in script
    assert 'wix7' not in script


def test_app_is_self_contained_and_does_not_request_elevation():
    build_app = (ROOT / 'scripts' / 'build-app.ps1').read_text(encoding='utf-8')
    manifest = (ROOT / 'src' / 'AssemblyNetStudio.App' / 'app.manifest').read_text(encoding='utf-8')
    assert '--self-contained true' in build_app
    assert 'requestedExecutionLevel level="asInvoker"' in manifest
