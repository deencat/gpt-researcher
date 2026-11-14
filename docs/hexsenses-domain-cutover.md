# Hexsenses domain cutover — research app

Queued behind a clean baseline push of the VPS tree. Apply in order; do not flip OAuth or nginx until DNS + TLS for `research.hexsenses.com` are live.

## Status (lookup as of 2026-11-14 HKT)

| Item | State |
|------|--------|
| `research.sixlines.io` | Live on VPS (`187.77.157.124`), nginx + Let’s Encrypt + oauth2-proxy |
| `research.hexsenses.com` | **Not live** — no DNS A/CNAME, no nginx site, no cert |
| Apex `hexsenses.com` | Hostinger parking (`2.57.91.91`), not this VPS |

## 1. DNS

Point `research.hexsenses.com` A (or CNAME→apex that points here) to the research VPS `187.77.157.124`.

## 2. Nginx + SSL

Clone `/etc/nginx/sites-available/research.sixlines.io` → `research.hexsenses.com`, replace `server_name` / cert paths, enable site, then:

```bash
certbot --nginx -d research.hexsenses.com
```

Keep the sixlines vhost enabled until cutover is confirmed.

## 3. Google OAuth (two places)

### A. Google Cloud Console (Authorized redirect URIs)

OAuth client used by oauth2-proxy (`OAUTH2_PROXY_CLIENT_ID` in `/home/webuser/deploy/oauth2-proxy/.env`).

Google allows **multiple** redirect URIs on one client. Add the new URI **without removing** the old one:

| Keep | Add |
|------|-----|
| `https://research.sixlines.io/oauth2/callback` | `https://research.hexsenses.com/oauth2/callback` |

Also add Authorized JavaScript origin (if the client uses origins):

- `https://research.hexsenses.com`

This agent has **no `gcloud` / Console access** on the VPS — Console must be updated in the browser by the project owner.

### B. oauth2-proxy on the VPS (single `--redirect-url`)

Config: `/home/webuser/deploy/oauth2-proxy/docker-compose.yml`

Live today:

- `--redirect-url=https://research.sixlines.io/oauth2/callback`
- `--cookie-domain=research.sixlines.io`
- `--whitelist-domain=research.sixlines.io`

oauth2-proxy takes **one** `--redirect-url` at a time. Switching it to hexsenses before that host is live **breaks** sixlines login. A prepared dual-ready compose lives beside it as `docker-compose.hexsenses.yml` (apply only after DNS/TLS + Console URI are confirmed):

```bash
cd /home/webuser/deploy/oauth2-proxy
docker compose -f docker-compose.hexsenses.yml up -d
```

That file sets:

- redirect → `https://research.hexsenses.com/oauth2/callback`
- cookie/whitelist → `research.hexsenses.com`

## 4. App env hostnames

In `/home/webuser/gpt-researcher/.env` (and Next public URLs), replace `https://research.sixlines.io` with `https://research.hexsenses.com` after the proxy/nginx cutover (e.g. `NEXT_PUBLIC_GPTR_API_URL`).

## Fallback order reminder

Do not delete the sixlines Google redirect URI or disable the sixlines nginx site until `https://research.hexsenses.com` OAuth login succeeds end-to-end.
