import pytest
from app.services.predefined_templates import get_predefined_projects

def test_predefined_templates_count():
    templates = get_predefined_projects()
    assert len(templates) == 12

def test_template_required_fields():
    templates = get_predefined_projects()
    template_ids = [t["id"] for t in templates]
    
    # Check innovation suite templates
    assert "template_climate_agri" in template_ids
    assert "template_smart_grid" in template_ids
    assert "template_supply_chain_fragility" in template_ids
    assert "template_hospital_response" in template_ids

    for t in templates:
        assert "id" in t
        assert "name" in t
        assert "domain" in t
        assert "global_variables" in t
        assert "system_dynamics" in t

def test_system_dynamics_structure():
    templates = get_predefined_projects()
    for t in templates:
        sd = t["system_dynamics"]
        assert "stocks" in sd
        assert "flows" in sd
