import pytest
import time
from context import HGECtx, HGECtxError


def pytest_addoption(parser):
    parser.addoption(
        "--hge-url", metavar="HGE_URL", help="url for graphql-engine", required=True
    )
    parser.addoption(
        "--pg-url", metavar="PG_URL", help="url for connecting to Postgres directly", required=True
    )
    parser.addoption(
        "--hge-key", metavar="HGE_KEY", help="admin secret key for graphql-engine", required=False
    )
    parser.addoption(
        "--hge-webhook", metavar="HGE_WEBHOOK", help="url for graphql-engine's access control webhook", required=False
    )
    parser.addoption(
        "--test-webhook-insecure", action="store_true",
        help="Run Test cases for insecure https webhook"
    )
    parser.addoption(
        "--hge-jwt-key-file", metavar="HGE_JWT_KEY_FILE", help="File containting the private key used to encode jwt tokens using RS512 algorithm", required=False
    )
    parser.addoption(
        "--hge-jwt-conf", metavar="HGE_JWT_CONF", help="The JWT conf", required=False
    )

    parser.addoption(
        "--test-cors", action="store_true",
        required=False,
        help="Run testcases for CORS configuration"
    )

    parser.addoption(
        "--test-metadata-disabled", action="store_true",
        help="Run Test cases with metadata queries being disabled"
    )

    parser.addoption(
        "--test-graphql-disabled", action="store_true",
        help="Run Test cases with GraphQL queries being disabled"
    )


@pytest.fixture(scope='session')
def hge_ctx(request):
    print("create hge_ctx")
    hge_url = request.config.getoption('--hge-url')
    pg_url = request.config.getoption('--pg-url')
    hge_key = request.config.getoption('--hge-key')
    hge_webhook = request.config.getoption('--hge-webhook')
    webhook_insecure = request.config.getoption('--test-webhook-insecure')
    hge_jwt_key_file = request.config.getoption('--hge-jwt-key-file')
    hge_jwt_conf = request.config.getoption('--hge-jwt-conf')
    test_cors = request.config.getoption('--test-cors')
    metadata_disabled = request.config.getoption('--test-metadata-disabled')
    try:
        hge_ctx = HGECtx(
            hge_url=hge_url,
            pg_url=pg_url,
            hge_key=hge_key,
            hge_webhook=hge_webhook,
            webhook_insecure=webhook_insecure,
            hge_jwt_key_file=hge_jwt_key_file,
            hge_jwt_conf=hge_jwt_conf,
            metadata_disabled=metadata_disabled
        )
    except HGECtxError as e:
        pytest.exit(str(e))

    yield hge_ctx  # provide the fixture value
    print("teardown hge_ctx")
    hge_ctx.teardown()
    time.sleep(2)

@pytest.fixture(scope='class')
def setup_ctrl(request, hge_ctx):
    """
    This fixure is used to store the state of test setup in some test classes.
    Used primarily when teardown is skipped in some test cases in the class where the test is not expected to change the database state.
    """
    setup_ctrl = { "setupDone" : False }
    yield setup_ctrl
    hge_ctx.may_skip_test_teardown = False
    request.cls().do_teardown(setup_ctrl, hge_ctx)
