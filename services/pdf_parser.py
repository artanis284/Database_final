"""
PDF metadata parser used by the literature management platform.
It uses rule-based extraction so the course project remains easy to explain
and reproduce on a standard Python installation.
"""

import re


def parse_pdf_metadata(filepath):
    """
    Parse PDF metadata and return:
    {
        'title': str, 'authors': [str], 'abstract': str,
        'venue_name': str, 'venue_type': str,
        'publish_date': str (YYYY-MM-DD), 'doi': str, 'keywords': [str]
    }
    Unknown fields are returned as empty values.
    """
    result = {
        "title": "",
        "authors": [],
        "abstract": "",
        "venue_name": "",
        "venue_type": "conference",
        "publish_date": None,
        "doi": "",
        "keywords": [],
    }

    try:
        import pdfplumber

        text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages[:3]:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # 1. Title
        for line in lines[:10]:
            clean = line.strip()
            if len(clean) > 10 and not clean.startswith("©") and not clean.startswith("http"):
                if not re.match(r"^[\w\s,;.@-]+@[\w.]+", clean):
                    if not re.match(r"^[\w\s,;]+$", clean):
                        result["title"] = clean
                        break

        # 2. Authors
        author_patterns = [
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
            r"([A-Z][a-z]+\s+[A-Z]\.?\s*[A-Z][a-z]+)",
        ]
        authors_found = set()
        for line in lines[:20]:
            if line == result.get("title", ""):
                continue
            if re.search(r"[,;]|\band\b", line) and len(line) < 200:
                parts = re.split(r"[,;]|\band\b", line)
                for part in parts:
                    part = part.strip()
                    if 2 < len(part) < 60 and not re.search(r"[@\d]", part):
                        if not re.match(r"^(university|college|institute|department|school)", part, re.IGNORECASE):
                            authors_found.add(part)
            for pattern in author_patterns:
                found = re.findall(pattern, line)
                for item in found:
                    item = item.strip()
                    if 3 < len(item) < 50 and not re.search(r"[@\d]", item):
                        authors_found.add(item)

        result["authors"] = list(authors_found)[:10]

        # 3. Abstract
        abstract_text = ""
        capture = False
        for line in lines:
            if re.match(r"^(abstract|摘要|ABSTRACT)", line, re.IGNORECASE):
                capture = True
                remaining = re.sub(r"^(abstract|摘要|ABSTRACT)[:：\s-]*", "", line, flags=re.IGNORECASE)
                if remaining.strip():
                    abstract_text += remaining.strip()
                continue
            if capture:
                if re.match(r"^(1\.|I\.|introduction|keywords|keyword|关键词|引言)", line, re.IGNORECASE):
                    break
                if len(abstract_text) < 2000:
                    abstract_text += " " + line

        result["abstract"] = abstract_text.strip()[:3000]

        # 4. DOI
        doi_pattern = r"(10\.\d{4,}/[^\s]+)"
        for line in lines:
            match = re.search(doi_pattern, line)
            if match:
                result["doi"] = match.group(1).rstrip(".,;")
                break

        # 5. Venue
        venue_patterns = [
            r"(conference|proceedings|symposium|workshop)\s+(?:on\s+)?([^,.;\d]{5,80})",
            r"(?:published\s+(?:in|at))\s+([^,.;\d]{5,80})",
            r"([^,.;\d]{5,80})\s+(?:conference|proceedings|journal)",
            r"(journal|transactions)\s+(?:of\s+)?([^,.;\d]{5,80})",
        ]
        for line in lines[:30]:
            for pattern in venue_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    venue_name = groups[-1].strip() if len(groups) > 1 else groups[0].strip()
                    if len(venue_name) > 5:
                        result["venue_name"] = venue_name
                        if "journal" in line.lower() or "transactions" in line.lower():
                            result["venue_type"] = "journal"
                        else:
                            result["venue_type"] = "conference"
                        break
            if result["venue_name"]:
                break

        # 6. Date
        date_patterns = [
            r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})",
            r"(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}",
            r"(?:published|date|received).*?(\d{4})",
            r"©\s*(\d{4})",
            r"(\d{4})\s+(?:IEEE|ACM|Springer|Elsevier)",
        ]
        for line in lines[:40]:
            for pattern in date_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    if match.lastindex and match.lastindex >= 3:
                        y, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                        if 1900 <= y <= 2030 and 1 <= month <= 12 and 1 <= day <= 31:
                            result["publish_date"] = f"{y:04d}-{month:02d}-{day:02d}"
                    else:
                        y = int(match.group(1))
                        if 1950 <= y <= 2030:
                            result["publish_date"] = f"{y}-01-01"
                    break
            if result["publish_date"]:
                break

        # 7. Keywords
        keywords_found = []
        capture_kw = False
        for line in lines:
            if re.match(r"^(keywords|keyword|关键词|index terms)", line, re.IGNORECASE):
                capture_kw = True
                remaining = re.sub(r"^(keywords|keyword|关键词|index terms)[:：\s-]*", "", line, flags=re.IGNORECASE)
                if remaining.strip():
                    keywords_found.extend([item.strip() for item in re.split(r"[,;，；]", remaining) if item.strip()])
                continue
            if capture_kw:
                if re.match(r"^(1\.|I\.|introduction|abstract)", line, re.IGNORECASE):
                    break
                keywords_found.extend([item.strip() for item in re.split(r"[,;，；]", line) if item.strip()])

        result["keywords"] = [item.rstrip(".") for item in keywords_found if 2 < len(item) < 50][:15]

    except ImportError:
        try:
            from PyPDF2 import PdfReader

            reader = PdfReader(filepath)
            text = "\n".join(page.extract_text() or "" for page in reader.pages[:3])
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            if lines and len(lines[0]) > 5:
                result["title"] = lines[0]
        except Exception:
            pass
    except Exception:
        pass

    return result
