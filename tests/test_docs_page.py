"""The /docs page is Swagger UI with our own settings and CSS. Only its look changes."""

def docs_html(client):
    response = client.get("/docs")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    return response.text


def test_docs_page_loads_the_api_description_and_our_title(client):
    html = docs_html(client)

    assert "<title>MiniDash API</title>" in html
    assert "/openapi.json" in html


def test_docs_page_carries_our_theme(client):
    html = docs_html(client)

    assert "<style>" in html and "MiniDash docs theme" in html
    assert html.index("MiniDash docs theme") < html.index("</head>")


def test_docs_page_uses_the_friendly_swagger_settings(client):
    html = docs_html(client)

    assert '"tryItOutEnabled": true' in html
    assert '"defaultModelsExpandDepth": -1' in html
    assert '"docExpansion": "list"' in html


def test_docs_page_is_not_listed_as_an_api_endpoint(client):
    paths = client.get("/openapi.json").json()["paths"]

    assert "/docs" not in paths


def test_the_other_docs_pages_still_work(client):
    assert client.get("/openapi.json").status_code == 200
    assert client.get("/redoc").status_code == 200
