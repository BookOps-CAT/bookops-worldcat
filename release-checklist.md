1. Update documentation  
    a) rebuild & deploy github pages
2. Run CI & coverage
3. Create a new github release
4. Update version.py & pyproject.toml
5. Verify poetry.lock & requirements are up-to-date  
    a) poetry update / poetry update [package1] [ package2]  
    b) poetry install
6. Build package in poetry (poetry build)
7. Publish to PyPI (poetry publish)