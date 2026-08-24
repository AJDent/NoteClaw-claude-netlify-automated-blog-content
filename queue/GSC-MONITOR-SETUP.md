# GSC Index Monitor — one-time setup

`queue/gsc_index_monitor.py` reports which live blog pages Google has **not** indexed yet, so
you only spend manual Request-Indexing clicks on pages that actually need them. It uses the
Search Console **URL Inspection API** (read-only — Google has no API to *trigger* indexing).

This needs a Google service account with read access to the Search Console property. ~10 minutes,
done once.

## Steps (you do these — they involve your Google account + credentials)

1. **Install the library**
   ```bash
   pip install --user google-auth
   ```

2. **Google Cloud Console** (https://console.cloud.google.com)
   - Create or pick a project.
   - APIs & Services → **Enable APIs** → search **"Google Search Console API"** → Enable.

3. **Create a service account**
   - IAM & Admin → Service Accounts → **Create service account** (name it e.g. `tnc-gsc-monitor`).
   - No roles are needed. Finish.
   - Open it → **Keys** → Add key → **Create new key** → **JSON** → download the file.

4. **Store the key** (never paste its contents anywhere)
   ```bash
   mkdir -p ~/.secrets
   mv ~/Downloads/<the-file>.json ~/.secrets/gsc-service-account.json
   chmod 600 ~/.secrets/gsc-service-account.json
   ```

5. **Grant it access in Search Console** (https://search.google.com/search-console)
   - Open the **takenotescapital.com** property → **Settings** → **Users and permissions** →
     **Add user**.
   - Paste the service account email (ends in `…iam.gserviceaccount.com`, it's in the JSON as
     `client_email`). Permission **Restricted** is enough (read-only).

6. **Test it**
   ```bash
   cd ~/tnc-blog && python3 queue/gsc_index_monitor.py
   ```
   You'll get a line per page (indexed / not) and a list of what still needs a manual request.

## Running it on a schedule (optional, after step 6 works)
- Post the not-indexed list to #tnc-blog-reviews:
  ```bash
  python3 queue/gsc_index_monitor.py --discord
  ```
- Wire it to a weekly systemd user timer, or fold it into the monthly audit. (Tell NoteClaw when
  the setup is done and it'll schedule it.)

## Notes
- The API is read-only. You still click **Request Indexing** in Search Console for the URLs it
  flags — this just tells you *which* ones, precisely.
- IndexNow (Bing/Yandex) is already automatic on publish; this monitor is the Google side.
