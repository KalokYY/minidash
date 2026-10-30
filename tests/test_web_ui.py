"""The customer web page. These tests check what the server serves and that the page
stays in step with the API. How the page behaves in a browser was checked by hand."""

import re
from pathlib import Path

STATIC = Path(__file__).resolve().parent.parent / "src" / "minidash" / "static"

def page_js():
    return (STATIC / "app.js").read_text(encoding="utf-8")

def spec(client):
    return client.get("/openapi.json").json()

def test_home_page_is_served(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "<title>MiniDash" in response.text
    assert "/static/app.css" in response.text
    assert "/static/app.js" in response.text

def test_the_pages_css_and_javascript_are_served(client):
    css = client.get("/static/app.css")
    script = client.get("/static/app.js")

    assert css.status_code == 200 and css.headers["content-type"].startswith("text/css")
    assert script.status_code == 200 and "javascript" in script.headers["content-type"]

def test_the_page_is_not_listed_as_an_api_endpoint(client):
    paths = spec(client)["paths"]

    assert "/" not in paths
    assert not any(path.startswith("/static") for path in paths)

def test_every_api_call_the_page_makes_is_a_real_endpoint(client):
    patterns = [re.compile(re.sub(r"\{[^}]+\}", "[^/]+", path)) for path in spec(client)["paths"]]
    calls = re.findall(r"api\(\s*[`'\"](/[^`'\"]*)[`'\"]", page_js())

    assert len(calls) >= 5  # restaurants, menu, place order, get order, cancel
    for call in calls:
        concrete = re.sub(r"\$\{[^}]*\}", "1", call)
        assert any(pattern.fullmatch(concrete) for pattern in patterns), f"the page calls {call}, which is not an endpoint"

def test_the_order_form_sends_every_field_the_api_expects(client):
    schemas = spec(client)["components"]["schemas"]
    script = page_js()
    body = re.search(r"const body = \{.*?\n  \};", script, re.S).group(0)  # where the page builds the request

    for model in ("OrderIn", "OrderItemIn"):
        for name in schemas[model]["required"]:
            assert re.search(rf"\b{name}\b\s*[:,}}]", body), f"the request body built by the page has no {name}"  # as a key
    for name in schemas["OrderIn"]["properties"]:
        if name not in schemas["OrderIn"]["required"]:
            assert f"body.{name} =" in script, f"the page never sets the optional field {name}"

def test_the_page_sends_scheduled_times_with_a_timezone(client):
    # The date picker gives local time without an offset; toISOString() adds one (UTC).
    assert "new Date(checkout.when).toISOString()" in page_js()

def test_the_page_never_builds_html_from_text(client):
    script = page_js()

    for unsafe in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write"):
        assert unsafe not in script, f"the page uses {unsafe}, which could run text typed by a customer"
