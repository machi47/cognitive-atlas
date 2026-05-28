# Tailnet Deployment

Cognitive Atlas is designed to bind to localhost and be exposed through Tailscale Serve, not a public LAN bind.

1. Build and run locally:

```sh
./scripts/build.sh
./scripts/run_api.sh
```

2. In another terminal:

```sh
./scripts/tailscale_serve.sh
tailscale serve localhost:8787
```

Do not use Tailscale Funnel for this private app.

