# Digital Minds Publication Radar

This GitHub Pages site checks confirmed Digital Minds researchers for new DOI publications and asks for approval before adding them to the shared publication inbox.

## How the approval workflow works

1. The GitHub Action runs once a day and can also be started manually from the **Actions** tab.
2. It checks each confirmed OpenAlex researcher ID for DOI-bearing articles, reviews, book chapters, and conference papers from the last five years.
3. If it finds anything new, it opens a pull request titled **Review newly discovered Digital Minds publications**.
4. A team member checks the researcher, DOI, details, and draft blurb.
5. **Merge** means approve. **Close** means reject.
6. After a merge, GitHub Pages redeploys and the approved records appear in the website's Inbox.

No pull request is created when nothing has changed.

## One-time GitHub setup

Upload every file and folder in this package to the root of the repository. Keep these exact paths:

- `index.html`
- `README.md`
- `researchers.json`
- `publications.json`
- `scripts/check_publications.py`
- `.github/workflows/check-publications.yml`

Then open **Settings → Actions → General → Workflow permissions**. Select **Read and write permissions**, tick **Allow GitHub Actions to create and approve pull requests**, and save.

Open the **Actions** tab, choose **Check for new publications**, select **Run workflow**, and wait for the first check.

## Adding confirmed researchers to the automatic check

1. Add and confirm researchers on the website as usual.
2. Open **Researchers**.
3. Click **Export automation file**. This downloads `researchers.json`.
4. Replace the repository's existing `researchers.json` with the downloaded file.

The next scheduled or manual check will include those researchers. Only confirmed matches with an OpenAlex ID are exported.

## Important limitation

Approved discoveries in `publications.json` are shared with everyone. Status changes, edited blurbs, and internal notes made inside the website are still saved only in that person's browser. A database and sign-in would be needed for fully shared team editing.
