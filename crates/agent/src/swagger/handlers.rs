//! OpenAPI handlers for the agent service

use utoipa::OpenApi;

/// Handler for OpenAPI specification
pub async fn openapi_handler() -> axum::Json<utoipa::openapi::OpenApi> {
    axum::Json(crate::swagger::ApiDoc::openapi())
}

/// Handler for Swagger UI HTML page
pub async fn swagger_ui_handler() -> axum::response::Html<&'static str> {
    axum::response::Html(
        r#"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="Wei Agent API Documentation" />
    <title>Wei Agent API - Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js" crossorigin></script>
    <script>
        window.onload = () => {
            window.ui = SwaggerUIBundle({
                url: '/api-docs/openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.presets.standalone
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "BaseLayout",
                validatorUrl: null,
                docExpansion: "list",
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1
            });
        };
    </script>
</body>
</html>
    "#,
    )
}
