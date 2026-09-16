from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_msi_is_per_user_and_uses_per_user_program_files():
    product = (ROOT / 'installer' / 'Product.wxs').read_text(encoding='utf-8')
    assert 'Scope="perUser"' in product
    assert 'StandardDirectory Id="PerUserProgramFilesFolder"' in product
    assert 'ProgramFiles64Folder' not in product


def test_wix7_eula_is_explicitly_accepted_in_ci_build_command():
    script = (ROOT / 'scripts' / 'build-installer.ps1').read_text(encoding='utf-8')
    assert '-acceptEula' in script
    assert 'wix7' in script
