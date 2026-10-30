"""A friendlier /docs page: Swagger UI with a few settings and some CSS.

Only the look of the page changes. The API itself, and the /openapi.json it
reads, are untouched.
"""

from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

SWAGGER_PARAMETERS = {
    "docExpansion": "list",          # show every endpoint, collapsed
    "defaultModelsExpandDepth": -1,  # hide the long "Schemas" list at the bottom
    "tryItOutEnabled": True,         # request bodies are editable straight away
    "displayRequestDuration": True,
    "syntaxHighlight": {"theme": "obsidian"},
}

DOCS_CSS = """
/* MiniDash docs theme */
body { background: #f4f5fb; }
.swagger-ui, .swagger-ui .opblock-summary-description, .swagger-ui .info p,
.swagger-ui .tab li, .swagger-ui table thead tr th, .swagger-ui .response-col_description {
  font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
.swagger-ui .wrapper { max-width: 1040px; padding: 0 20px 48px; }

/* header card */
.swagger-ui .info {
  margin: 36px 0 28px; padding: 30px 34px; border-radius: 18px; color: #fff;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 55%, #db2777 100%);
  box-shadow: 0 12px 30px rgba(79, 70, 229, 0.28);
}
.swagger-ui .info .title { color: #fff; font-size: 40px; font-weight: 800; letter-spacing: -0.5px; }
.swagger-ui .info .title small { top: -4px; }
.swagger-ui .info .title small pre { background: rgba(255,255,255,0.22); color: #fff; }
.swagger-ui .info p, .swagger-ui .info li, .swagger-ui .info a { color: rgba(255,255,255,0.94); font-size: 15px; }
.swagger-ui .info a { text-decoration: underline; }
.swagger-ui .info code { background: rgba(255,255,255,0.2); color: #fff; padding: 2px 7px; border-radius: 6px; }

/* tighten the space under the header */
.swagger-ui .scheme-container { display: none; }
.swagger-ui .information-container { padding: 0; }

/* section headings */
.swagger-ui .opblock-tag {
  margin: 26px 0 10px; border-bottom: 0; font-size: 22px; font-weight: 700; color: #1f2340;
}
.swagger-ui .opblock-tag small { color: #6b7280; font-size: 14px; font-weight: 400; }

/* endpoint cards */
.swagger-ui .opblock {
  border: 0; border-left: 6px solid; border-radius: 12px; margin: 0 0 12px;
  background: #fff; box-shadow: 0 2px 10px rgba(31, 35, 64, 0.08);
}
.swagger-ui .opblock .opblock-summary { border: 0; padding: 8px 14px; }
.swagger-ui .opblock .opblock-summary-method {
  border-radius: 8px; min-width: 76px; font-size: 13px; letter-spacing: 0.4px; text-shadow: none;
}
.swagger-ui .opblock .opblock-summary-path { font-weight: 600; color: #1f2340; }
.swagger-ui .opblock .opblock-summary-description { color: #6b7280; }
.swagger-ui .opblock.opblock-get    { border-left-color: #3b82f6; background: #fff; }
.swagger-ui .opblock.opblock-post   { border-left-color: #10b981; background: #fff; }
.swagger-ui .opblock.opblock-patch  { border-left-color: #f59e0b; background: #fff; }
.swagger-ui .opblock.opblock-get   .opblock-summary-method { background: #3b82f6; }
.swagger-ui .opblock.opblock-post  .opblock-summary-method { background: #10b981; }
.swagger-ui .opblock.opblock-patch .opblock-summary-method { background: #f59e0b; }
.swagger-ui .opblock.opblock-get   .opblock-section-header,
.swagger-ui .opblock.opblock-post  .opblock-section-header,
.swagger-ui .opblock.opblock-patch .opblock-section-header { background: #f8f9fd; box-shadow: none; }
.swagger-ui .opblock-body pre.microlight { border-radius: 10px; }

/* buttons */
.swagger-ui .btn { border-radius: 8px; font-weight: 600; box-shadow: none; }
.swagger-ui .btn.execute { background: #4f46e5; border-color: #4f46e5; color: #fff; }
.swagger-ui .btn.execute:hover { background: #4338ca; }
.swagger-ui .btn.try-out__btn { border-color: #4f46e5; color: #4f46e5; }
.swagger-ui .btn.cancel { border-color: #dc2626; color: #dc2626; }
"""


def docs_page():
    """Serve Swagger UI with the settings and CSS above."""
    page = get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="MiniDash API",
        swagger_ui_parameters=SWAGGER_PARAMETERS,
    )
    html = page.body.decode().replace("</head>", f"<style>{DOCS_CSS}</style></head>")
    return HTMLResponse(html)
