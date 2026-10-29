import json
from pathlib import Path

import pytest

from extraction_tool import serve


def _field(section, name):
    return next(field for field in serve.SCHEMA[section]["fields"] if field["name"] == name)


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


@pytest.fixture
def client(tmp_path):
    root = tmp_path / "LocalResearch" / "level3_extraction"
    data = root / "production" / "reviewer_workspace" / "reviews" / "blind"
    template = {
        "key": "rayyan-1",
        "_phase": "blind",
        "metadata": {
            "title": "Fixture paper",
            "authors": "A. Author",
            "year": 2026,
            "source": "Journal",
            "rayyan_decision": "Included",
        },
        "eligibility": dict(serve.DEFAULTS["eligibility"]),
        "level_a": dict(serve.DEFAULTS["level_a"]),
        "level_b": dict(serve.DEFAULTS["level_b"]),
        "reviewer_notes": "",
        "reviewer_evidence": {},
        "_review_fields": ["eligibility.methodological_eligibility"],
        "_done": False,
    }
    _write_json(data / "rayyan-1.json", template)
    _write_json(
        data / "rayyan-1.ai.json",
        {"models": {"chatgpt": {"eligibility": {"methodological_eligibility": True}}}},
    )
    serve.configure(data_root=data, canonical_root=root)
    serve.app.config.update(TESTING=True)
    return serve.app.test_client(), data


def _payload(eligibility=True, done=False, notes=""):
    return {
        "eligibility": {
            **serve.DEFAULTS["eligibility"],
            "methodological_eligibility": eligibility,
            "level_3b": False,
        },
        "level_a": dict(serve.DEFAULTS["level_a"]),
        "level_b": dict(serve.DEFAULTS["level_b"]),
        "reviewer_notes": notes,
        "reviewer_evidence": {
            "eligibility.methodological_eligibility": {
                "quote": "eligible study",
                "page": 1,
                "rule": "registered eligibility threshold",
            }
        },
        "_done": done,
    }


def test_blind_ai_access_is_refused_until_atomic_commit(client):
    app, data = client
    assert app.get("/api/ai/rayyan-1").status_code == 403
    assert app.post("/api/save/rayyan-1", json=_payload()).status_code == 200
    assert app.post("/api/commit/rayyan-1").status_code == 200
    paper = app.get("/api/paper/rayyan-1").get_json()
    assert paper["_state"] == "revealed"
    assert "chatgpt" in paper["_ai"]
    assert (data / "rayyan-1.blind.json").is_file()


def test_absence_evidence_commits_false_value_without_fabricated_quote(client):
    app, data = client
    payload = _payload(eligibility=False)
    payload["reviewer_evidence"]["eligibility.methodological_eligibility"] = {
        "mode": "not_reported_after_full_text_review",
        "quote": None,
        "page": None,
        "rule": "No qualifying EnPI/EnB model was found after full-text review.",
    }
    assert app.post("/api/save/rayyan-1", json=payload).status_code == 200
    assert app.post("/api/commit/rayyan-1").status_code == 200
    blind = json.loads((data / "rayyan-1.blind.json").read_text())
    evidence = blind["reviewer_evidence"]["eligibility.methodological_eligibility"]
    assert evidence["mode"] == "not_reported_after_full_text_review"
    assert evidence["quote"] is None
    assert evidence["page"] is None


def test_absence_evidence_is_rejected_for_positive_value(client):
    app, _ = client
    payload = _payload(eligibility=True)
    payload["reviewer_evidence"]["eligibility.methodological_eligibility"] = {
        "mode": "not_reported_after_full_text_review",
        "quote": None,
        "page": None,
        "rule": "Attempted bypass.",
    }
    response = app.post("/api/save/rayyan-1", json=payload)
    assert response.status_code == 400
    assert "only valid for an absence-like value" in response.get_json()["error"]


def test_save_returns_and_persists_receipt_timestamp(client):
    app, data = client
    response = app.post("/api/save/rayyan-1", json=_payload())
    assert response.status_code == 200
    saved_at = response.get_json()["saved_at"]
    stored = json.loads((data / "rayyan-1.json").read_text())
    assert stored["saved_at"] == saved_at
    paper = app.get("/api/paper/rayyan-1").get_json()
    assert paper["_saved_at"] == saved_at


def test_finalise_requires_latest_saved_done_state_and_locks_edits(client):
    app, data = client
    app.post("/api/save/rayyan-1", json=_payload())
    app.post("/api/commit/rayyan-1")
    app.get("/api/paper/rayyan-1")
    assert app.post("/api/finalise/rayyan-1").status_code == 409
    assert app.post(
        "/api/save/rayyan-1", json=_payload(done=True, notes="final answer")
    ).status_code == 200
    assert app.post("/api/finalise/rayyan-1").status_code == 200
    assert app.post("/api/save/rayyan-1", json=_payload(done=True)).status_code == 409
    stored = json.loads((data / "rayyan-1.json").read_text())
    assert stored["reviewer_notes"] == "final answer"
    blind = json.loads((data / "rayyan-1.blind.json").read_text())
    assert blind["reviewer_evidence"]["eligibility.methodological_eligibility"]["page"] == 1


def test_second_commit_and_unsafe_key_are_rejected(client):
    app, _ = client
    app.post("/api/save/rayyan-1", json=_payload())
    assert app.post("/api/commit/rayyan-1").status_code == 200
    assert app.post("/api/commit/rayyan-1").status_code == 409
    assert app.get("/api/paper/not-a-rayyan-key").status_code == 404


def test_configure_rejects_desktop_or_icloud_root(tmp_path):
    with pytest.raises(RuntimeError, match="prohibited"):
        serve.configure(
            data_root=Path("/Users/bernardoribeiro/Desktop/Screening/reviews"),
            canonical_root=Path("/Users/bernardoribeiro/Desktop/Screening"),
        )


def test_human_schema_uses_registered_eligibility_and_model_value_domains():
    eligibility = _field("eligibility", "methodological_eligibility")
    assert "presents, proposes, evaluates, or critiques" in eligibility["help"].lower()
    multi_site = _field("level_a", "multi_site")
    assert multi_site["options"] == [True, False, "not applicable"]
    scale = _field("level_b", "scale_of_application")
    assert "sub-system / utility system" in scale["options"]


def test_human_schema_exactly_uses_the_canonical_controlled_vocabularies():
    assert _field("level_a", "ems_standard")["options"] == [
        "ISO 50001", "ISO 50002", "ISO 50006", "other-named", "none"
    ]
    assert _field("level_a", "mv_protocol")["options"][-2:] == ["other-named", "none"]
    assert _field("level_a", "regulatory_driver")["options"][-2:] == [
        "other-named", "none"
    ]
    assert _field("level_a", "enpi_enb_model_types")["options"] == [
        "linear regression",
        "multiple regression",
        "physical model",
        "ML",
        "simple intensity ratio",
        "SEC mean",
        "composite index",
        "change-point or SPC",
        "process integration",
        "other",
        "not applicable",
    ]
    assert _field("level_b", "specific_limitations")["options"][-1] == "other"
    assert _field("level_b", "adaptation_types")["options"][-1] == "other"
    for section, name in (
        ("level_a", "ems_standard"),
        ("level_a", "mv_protocol"),
        ("level_a", "regulatory_driver"),
        ("level_a", "enpi_enb_model_types"),
        ("level_b", "specific_limitations"),
        ("level_b", "adaptation_types"),
    ):
        assert "other" not in _field(section, name)


def test_human_b13b_is_value_only_and_evidence_stays_in_reviewer_evidence():
    metric = _field("level_b", "performance_metrics_reported")
    assert [item["name"] for item in metric["item_fields"]] == [
        "metric", "value", "unit", "period_or_context"
    ]
    assert all(
        item["name"] not in {"evidence_quote", "page", "non_contiguous_evidence"}
        for item in metric["item_fields"]
    )
    assert "reviewer_evidence" not in serve.DEFAULTS["level_b"]


def test_browser_contract_has_recovery_autosave_and_safe_navigation():
    app_js = (Path(__file__).parent / "extraction_tool" / "app.js").read_text()
    index_html = (Path(__file__).parent / "extraction_tool" / "index.html").read_text()
    for required in (
        "localStorage",
        "beforeunload",
        "persistLocalDraft",
        "restoreLocalDraft",
        "scheduleAutosave",
        "flushSave",
        "navigateTo",
        "Recovered local draft",
        "Saved to disk",
        "Unsaved changes",
        "Save failed",
    ):
        assert required in app_js
    assert "id=\"save-state\"" in index_html


def test_non_blind_verification_template_reveals_models_without_commit(tmp_path):
    root = tmp_path / "LocalResearch" / "level3_extraction"
    data = root / "production" / "reviewer_workspace" / "reviews" / "verification"
    template = {
        "key": "rayyan-9",
        "_phase": "verification",
        "_blind_required": False,
        "_review_fields": ["eligibility.methodological_eligibility"],
        "metadata": {
            "title": "Verification paper", "authors": "A", "year": 2026,
            "source": "J", "rayyan_decision": "Included",
        },
        "eligibility": {**serve.DEFAULTS["eligibility"], "methodological_eligibility": True},
        "level_a": dict(serve.DEFAULTS["level_a"]),
        "level_b": dict(serve.DEFAULTS["level_b"]),
        "reviewer_notes": "",
        "reviewer_evidence": {},
        "_done": False,
    }
    _write_json(data / "rayyan-9.json", template)
    _write_json(data / "rayyan-9.ai.json", {"models": {"chatgpt": {}}})
    serve.configure(data_root=data, canonical_root=root)
    serve.app.config.update(TESTING=True)
    app = serve.app.test_client()
    paper = app.get("/api/paper/rayyan-9").get_json()
    assert paper["_state"] == "revealed"
    assert "chatgpt" in paper["_ai"]
    assert app.get("/api/ai/rayyan-9").status_code == 200
