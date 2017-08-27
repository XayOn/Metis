 Feature: Our software must be easily redistributable
Scenario: Check that we provide an importable package
    When: I import the package {{cookiecutter.project_slug}}
    Then: I see no errors

