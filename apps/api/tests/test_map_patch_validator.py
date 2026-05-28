from atlas_api.models.patches import ClaimCandidate, MapPatch, Provenance
from atlas_api.services.map_patch_validator import MapPatchValidator


def test_validator_rejects_fake_user_belief():
    patch = MapPatch(
        action="create_new",
        create_maps=[{"title": "Bad Memory"}],
        add_claims=[ClaimCandidate(text="User now believes X", epistemic_status="user_asserted")],
        provenance=[Provenance(turn_id="turn_1", session_id="ses_1")],
    )
    result = MapPatchValidator().validate(patch)
    assert not result.valid
    assert any("Forbidden user belief" in issue for issue in result.issues)


def test_validator_rejects_source_backed_without_source():
    patch = MapPatch(
        action="create_new",
        create_maps=[{"title": "Sources"}],
        add_claims=[ClaimCandidate(text="A paper says X", epistemic_status="source_backed")],
        provenance=[Provenance(turn_id="turn_1", session_id="ses_1")],
    )
    result = MapPatchValidator().validate(patch)
    assert not result.valid
    assert any("Source-backed" in issue for issue in result.issues)

