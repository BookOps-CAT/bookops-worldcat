1. Update documentation  
    a) update Changelog: version, date, descriptions of changes
    b) rebuild (mkdocs build --clean) & deploy github pages (mkdocs gh-deploy)
2. Verify poetry.lock & requirements are up-to-date  
    a) poetry update / poetry update [package1] [ package2]  
    b) poetry install
3. Update version.py & pyproject.toml
4. Commit changes to repo & run CI & coverage
5. Create a new github release
6. Build package in poetry (poetry build)
7. Publish to PyPI (poetry publish)