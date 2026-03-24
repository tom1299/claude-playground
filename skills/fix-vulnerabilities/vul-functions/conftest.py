def pytest_addoption(parser):
    parser.addoption(
        "--with-dependencies",
        action="store_true",
        default=False,
        help="Honor pytest-dependency markers (skips dependents when a dependency fails)",
    )

def pytest_collection_modifyitems(config, items):
    if not config.getoption("--with-dependencies"):
        for item in items:
            item.own_markers = [m for m in item.own_markers if m.name != "dependency"]
