from pathlib import Path

import local_storage


def test_desktop_is_prohibited():
    assert local_storage.is_prohibited(
        Path("/Users/bernardoribeiro/Desktop/Screening")
    )


def test_documents_is_prohibited():
    assert local_storage.is_prohibited(
        Path("/Users/bernardoribeiro/Documents/Screening")
    )


def test_localresearch_is_allowed():
    assert not local_storage.is_prohibited(
        Path("/Users/bernardoribeiro/LocalResearch/Screening")
    )


def test_validator_rejects_dataless(monkeypatch, tmp_path):
    item = tmp_path / "paper.pdf"
    item.write_bytes(b"%PDF-local")
    monkeypatch.setattr(local_storage, "is_dataless", lambda path: path == item)

    try:
        local_storage.validate_required_paths(tmp_path, [item])
    except local_storage.StorageValidationError as exc:
        assert "dataless" in str(exc)
    else:
        raise AssertionError("dataless input was accepted")


def test_validator_rejects_symlink_escape(tmp_path):
    outside = tmp_path.parent / "outside.pdf"
    outside.write_bytes(b"%PDF-outside")
    link = tmp_path / "paper.pdf"
    link.symlink_to(outside)

    try:
        local_storage.validate_required_paths(tmp_path, [link])
    except local_storage.StorageValidationError as exc:
        assert "escapes root" in str(exc)
    else:
        raise AssertionError("escaping symlink was accepted")


def test_validator_returns_relative_hash_inventory(tmp_path):
    item = tmp_path / "paper.pdf"
    item.write_bytes(b"%PDF-local")

    report = local_storage.validate_required_paths(tmp_path, [item])

    assert report["root"] == str(tmp_path.resolve())
    assert report["count"] == 1
    assert report["files"] == {
        "paper.pdf": "e886634ef385beefe73352c7cb07f5f9594117e0ae689bdc9e79fcaf573aa280"
    }
