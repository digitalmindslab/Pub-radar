import json
import re
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCHERS = ROOT / "researchers.json"
PUBLICATIONS = ROOT / "publications.json"
ALLOWED_TYPES = {"article", "review", "book-chapter", "proceedings-article"}


def get_json(url):
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "Digital-Minds-Publication-Radar/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def normalise_doi(value):
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", (value or "").strip(), flags=re.I).lower()


def draft_blurb(title, venue, year):
    destination = f" in {venue}" if venue else ""
    timing = f" in {year}" if year else ""
    return (
        f'This publication presents the research “{title}”. '
        f"Published{destination}{timing}, it has been identified from its verified DOI record. "
        "Please review this draft and add the study’s key finding and relevance before publishing it on the Digital Minds website."
    )


def main():
    researchers = json.loads(RESEARCHERS.read_text(encoding="utf-8"))
    publications = json.loads(PUBLICATIONS.read_text(encoding="utf-8"))
    by_doi = {normalise_doi(item.get("doi")): item for item in publications if item.get("doi")}
    from_year = date.today().year - 5
    found = 0

    for researcher in researchers:
        author_id = researcher.get("openAlexId", "").rstrip("/").split("/")[-1]
        if not author_id:
            continue
        filters = f"author.id:{author_id},from_publication_date:{from_year}-01-01"
        query = urllib.parse.urlencode({"filter": filters, "sort": "publication_date:desc", "per-page": 100})
        works = get_json(f"https://api.openalex.org/works?{query}").get("results", [])

        for work in works:
            doi = normalise_doi(work.get("doi"))
            if not doi or work.get("type") not in ALLOWED_TYPES:
                continue
            name = researcher.get("name", "Unknown researcher")
            if doi in by_doi:
                names = by_doi[doi].setdefault("researchers", [])
                if name not in names:
                    names.append(name)
                continue
            authors = ", ".join(
                authorship.get("author", {}).get("display_name", "")
                for authorship in work.get("authorships", [])
                if authorship.get("author", {}).get("display_name")
            )
            venue = ((work.get("primary_location") or {}).get("source") or {}).get("display_name", "")
            title = work.get("title") or work.get("display_name") or "Untitled publication"
            year = work.get("publication_year") or ""
            record = {
                "id": doi,
                "doi": doi,
                "title": title,
                "authors": authors,
                "venue": venue,
                "year": year,
                "kind": work.get("type", "article"),
                "kindLabel": work.get("type", "article").replace("-", " "),
                "researcher": name,
                "researchers": [name],
                "status": "new",
                "source": "OpenAlex automation",
                "shortBlurb": draft_blurb(title, venue, year),
                "longBlurb": "",
                "tags": "",
                "fullText": ((work.get("open_access") or {}).get("oa_url") or ""),
                "website": "",
                "notes": "Automatically discovered; DOI and draft blurb require human review.",
            }
            publications.append(record)
            by_doi[doi] = record
            found += 1

    publications.sort(key=lambda item: (-(int(item.get("year") or 0)), item.get("title", "").lower()))
    PUBLICATIONS.write_text(json.dumps(publications, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Found {found} new DOI publication(s).")


if __name__ == "__main__":
    main()
