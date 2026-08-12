import pytest

from backend.projects import (
    collection_name,
    create_project,
    delete_project,
    get_project,
    list_projects,
)


def test_create_project_generates_slug_from_name():
    result = create_project("My Cool Project!")
    assert result == {"slug": "my-cool-project", "name": "My Cool Project!"}


def test_create_project_is_idempotent_for_same_slug():
    create_project("Same Name")
    create_project("Same Name")
    assert len(list_projects()) == 1


def test_create_project_rejects_name_with_no_alphanumerics():
    with pytest.raises(ValueError):
        create_project("!!!")


def test_list_projects_reflects_all_created_projects():
    create_project("Alpha")
    create_project("Beta")
    assert {p["slug"] for p in list_projects()} == {"alpha", "beta"}


def test_get_project_returns_none_for_unknown_slug():
    assert get_project("does-not-exist") is None


def test_get_project_returns_matching_project():
    create_project("Findable")
    assert get_project("findable") == {"slug": "findable", "name": "Findable"}


def test_delete_project_removes_existing_project():
    create_project("Temp")
    assert delete_project("temp") is True
    assert get_project("temp") is None


def test_delete_project_returns_false_when_not_found():
    assert delete_project("nope") is False


def test_collection_name_prefixes_slug():
    assert collection_name("abc") == "kb_abc"
