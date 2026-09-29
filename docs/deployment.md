# Deployment

FocusLens is packaged as one stateless Docker web service. The browser UI and API share an origin, so no cross-origin configuration is required for the standard deployment.

## Render

The repository includes [`render.yaml`](../render.yaml), which defines a free Docker web service with automatic deployment after GitHub checks pass and an application-level health check at `/api/health`.

1. Sign in to Render with GitHub.
2. Create a Blueprint from this repository.
3. Review the free plan and apply the Blueprint.
4. Wait for `/api/health` to report `ok` before opening the generated HTTPS URL.

No secrets are required. Render supplies `PORT`; the container binds to that value and defaults to `8000` elsewhere.

### Free-tier behavior

Render free services spin down after a period without traffic and can take about a minute to wake. Their filesystem is ephemeral. FocusLens therefore stores its optional numeric SQLite records and generated synthetic model under `/tmp`; they can disappear on restart and are not durable application data.

The camera workflow requires HTTPS outside `localhost`. Render provides managed HTTPS for its `onrender.com` address.

## Local production-container check

```bash
docker build -t focuslens-ai .
docker run --rm -p 8000:8000 focuslens-ai
```

Then check `http://localhost:8000/api/health` and open `http://localhost:8000`.
