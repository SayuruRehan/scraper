# GitHub Actions Daily Scraper Setup

## Quick Start

1. **Push to GitHub:**
   ```bash
   git add .github/workflows/daily-scrape.yml
   git commit -m "Add daily scraper GitHub Action"
   git push
   ```

2. **Verify workflow:**
   - Go to your GitHub repository
   - Click "Actions" tab
   - You should see "Daily Scholarship Scraper"

3. **Test manually:**
   - Click the workflow name
   - Click "Run workflow" button
   - Wait ~2-5 minutes for completion

4. **Download results:**
   - Click on the completed run
   - Scroll to "Artifacts" section
   - Download the CSV file

## Schedule Configuration

The workflow runs at **02:00 UTC** daily. To change the time, edit the cron expression:

```yaml
- cron: '0 2 * * *'  # Format: minute hour day month weekday
```

Examples:
- `'0 8 * * *'` = 08:00 UTC daily
- `'30 14 * * *'` = 14:30 UTC daily
- `'0 0 * * 1'` = Monday at midnight
- `'0 12 * * 1-5'` = Weekdays at noon

**Convert your timezone:** [crontab.guru](https://crontab.guru)

## Data Storage Options

### Option 1: Download Artifacts (Current Setup)
- CSV available in "Actions" > "Artifacts"
- Kept for 30 days
- No repo bloat
- **Best for most users**

### Option 2: Auto-commit to Repo
Enable in workflow file by changing:
```yaml
if: false  # Change to: if: true
```

This commits CSVs to `data/exports/` automatically.

**⚠️ Warning:** This grows repo size over time. Consider using a separate data branch.

### Option 3: Cloud Storage
Add steps to upload to:
- AWS S3
- Google Cloud Storage
- Azure Blob Storage
- Dropbox/OneDrive via API

## GitHub Actions Limits

**Free tier:**
- 2,000 minutes/month
- ~1 run = 3-5 minutes (with detail fetching enabled)
- **You can run ~400-600 times/month** (way more than daily needs)

**Public repos:** Unlimited minutes ✨

## Monitoring

**Email notifications (default):**
- GitHub emails you on workflow failure
- Configure in GitHub Settings > Notifications

**Status badge (optional):**
Add to README.md:
```markdown
![Scraper Status](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/daily-scrape.yml/badge.svg)
```

## Rate Limiting Considerations

Your scraper respects rate limits with `detail_page_delay`. GitHub Actions runs from different IPs each time, so you're unlikely to hit website rate limits.

If a source blocks you:
- Increase `detail_page_delay` in config/sources.json
- Disable `fetch_detail_page` for that source
- Add retry logic (if needed)

## Troubleshooting

**Workflow not running?**
- Check "Actions" are enabled in repo settings
- Verify cron syntax at [crontab.guru](https://crontab.guru)
- GitHub may delay scheduled runs by ~3-15 minutes

**Scraper failing?**
- Click failed run → Click "Run scraper" → View logs
- Check if source websites changed structure
- Verify dependencies in requirements.txt

**Need logs?**
Add after scraping step:
```yaml
- name: Upload logs
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: logs
    path: logs/
```

## Advanced: Multiple Schedules

Run different configs at different times:

```yaml
on:
  schedule:
    - cron: '0 2 * * *'   # Daily full scrape (with detail pages)
    - cron: '0 */6 * * *' # Every 6 hours (list pages only)
```

Add logic to check which schedule triggered:
```yaml
- name: Run scraper
  run: |
    if [ "${{ github.event.schedule }}" = "0 */6 * * *" ]; then
      # Quick scrape logic
      python -m src.run_once --no-detail-pages
    else
      # Full scrape
      python -m src.run_once
    fi
```
