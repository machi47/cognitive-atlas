# Deployment

## Mac Local

```sh
./scripts/install.sh
./scripts/dev.sh
```

## Local Production

```sh
./scripts/build.sh
./scripts/run_api.sh
```

## Tailscale Serve

```sh
./scripts/tailscale_serve.sh
tailscale serve localhost:8787
```

Do not use Funnel unless the privacy model changes.

## systemd User Service

```sh
./scripts/install_systemd.sh
systemctl --user start cognitive-atlas.service
```

## Backups

```sh
./scripts/backup.sh
```

Restore by stopping the service and replacing `data/cognitive_atlas.db` with a backup copy.

