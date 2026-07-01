from __future__ import annotations

import csv
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from http.cookies import SimpleCookie
from datetime import date, datetime
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"
DB_NAME = os.environ.get("MYSQL_DATABASE", "literature_management")
MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_CLI = os.environ.get("MYSQL_CLI") or shutil.which("mysql") or r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
APP_USER = os.environ.get("APP_USER", "user")


TEXT = {
    "zh": {
        "app_title": "文献管理系统",
        "subtitle": "MySQL 数据库课程项目",
        "search": "检索",
        "add": "文献入库",
        "analytics": "分析",
        "settings": "设置",
        "favorites": "收藏",
        "login": "登录",
        "logout": "退出登录",
        "username": "用户名",
        "password": "密码",
        "login_title": "登录文献管理平台",
        "login_tip": "请输入账号和密码进入系统。",
        "login_button": "登录",
        "register": "注册",
        "register_title": "注册文献管理账号",
        "register_tip": "创建普通用户账号后即可登录平台。",
        "register_button": "创建账号",
        "back_to_login": "返回登录",
        "email": "邮箱",
        "delete_paper": "删除",
        "status": "状态",
        "status_all": "全部状态",
        "status_pending": "待审核",
        "status_active": "已发布",
        "status_archived": "已归档",
        "set_pending": "设为待审核",
        "set_active": "发布",
        "set_archived": "归档",
        "edit_paper": "修改",
        "edit_paper_title": "修改文献信息",
        "publish_updated_paper": "修改并发布",
        "return_to_search": "返回",
        "export_json": "导出 JSON",
        "export_csv": "导出 CSV",
        "hero_title": "面向用户的文献管理平台",
        "hero_body": "本页面直接连接 MySQL 的 literature_management 数据库，支持文献入库、组合检索、收藏论文、收藏关键词、引用统计、关键词分析和数据导出。",
        "workbench_note": "",
        "papers": "论文",
        "authors": "作者",
        "author_select": "选择作者",
        "add_author": "添加作者",
        "author_name": "作者姓名",
        "author_email": "邮箱",
        "author_orcid": "ORCID",
        "save_author": "保存作者",
        "author_required_tip": "请从作者表中选择作者；若列表中没有，请先在右方添加作者。",
        "author_lookup": "检索作者",
        "author_lookup_placeholder": "按姓名 / 邮箱 / ORCID 检索相近作者",
        "parsed_authors": "PDF 识别作者",
        "keywords": "关键词",
        "add_keyword": "添加",
        "citations": "引用",
        "query_placeholder": "标题 / 摘要 / DOI / 作者",
        "institution": "单位",
        "year": "年份",
        "year_from": "起始年份",
        "year_to": "结束年份",
        "keyword": "关键词",
        "combined_search": "组合检索",
        "paper": "论文",
        "source": "来源",
        "relation": "关系",
        "action": "操作",
        "no_records": "暂无匹配记录",
        "save_paper": "收藏论文",
        "saved_paper": "已收藏",
        "remove_paper": "取消收藏",
        "no_doi": "无 DOI",
        "reference_label": "引用",
        "cited_by_label": "被引",
        "new_paper": "新增文献",
        "title": "标题",
        "abstract": "摘要",
        "publish_date": "发表日期",
        "doi": "DOI",
        "venue": "期刊/会议",
        "type": "类型",
        "save_mysql": "保存到 MySQL",
        "batch_import": "批量导入",
        "csv_tip": "上传 CSV，字段：title, abstract, publish_date, doi, venue_name, venue_type, author_ids, keywords；DOI 与作者 ORCID 必须已登记且不可重复。",
        "choose_csv_file": "选择 CSV 文件",
        "pdf_upload": "PDF 上传解析",
        "pdf_tip": "上传 PDF 后，系统只会从前几页自动提取标题、摘要、作者、DOI、关键词和来源并回填表单；确认后再手动保存。",
        "choose_pdf_file": "选择 PDF 文件",
        "upload_pdf": "上传并解析 PDF",
        "batch_pdf_upload": "批量 PDF 解析",
        "batch_pdf_tip": "一次选择多篇 PDF，系统会逐篇解析并生成待确认表单，确认后再批量保存。",
        "choose_pdf_files": "选择多个 PDF 文件",
        "upload_pdfs": "批量解析 PDF",
        "batch_review_title": "批量解析结果确认",
        "save_batch_mysql": "批量保存到 MySQL",
        "source_file": "来源文件",
        "pdf_prefilled": "PDF 已解析，请检查并修改下方表单后再保存。",
        "pdf_attached": "已关联 PDF 文件",
        "abstract_placeholder": "请填写论文摘要",
        "doi_placeholder": "如 10.1038/s41586-021-03819-2",
        "authors_placeholder": "用分号分隔，如 John Smith; Alice Wang",
        "keywords_placeholder": "用分号分隔，如 Artificial Intelligence; Biology",
        "import_csv": "导入 CSV",
        "data_analysis": "数据分析",
        "year_dist": "年度分布",
        "hot_keywords": "高频关键词",
        "favorite_keyword": "收藏关键词",
        "saved_keyword": "已收藏",
        "remove_keyword": "取消收藏",
        "active_filter": "筛选中",
        "my_favorites": "我的收藏",
        "favorite_papers": "收藏论文",
        "favorite_keywords": "收藏关键词",
        "keyword_lookup": "关键词检索",
        "keyword_lookup_placeholder": "搜索 keyword 表中的任意关键词",
        "keyword_results": "可收藏关键词",
        "empty_favorites": "暂无收藏",
        "none": "无",
        "settings_title": "界面设置",
        "language": "语言",
        "save_settings": "保存设置",
        "db_error": "数据库连接失败：{error}。请确认数据库已初始化，并检查连接配置。",
    },
    "en": {
        "app_title": "Literature Manager",
        "subtitle": "MySQL Database Course Project",
        "search": "Search",
        "add": "Paper Upload",
        "analytics": "Analytics",
        "settings": "Settings",
        "favorites": "Favorites",
        "login": "Login",
        "logout": "Log Out",
        "username": "Username",
        "password": "Password",
        "login_title": "Log In to Literature Manager",
        "login_tip": "Enter your username and password to continue.",
        "login_button": "Log In",
        "register": "Register",
        "register_title": "Create Literature Manager Account",
        "register_tip": "Create a standard user account, then log in to the platform.",
        "register_button": "Create Account",
        "back_to_login": "Back to Login",
        "email": "Email",
        "delete_paper": "Delete",
        "status": "Status",
        "status_all": "All Statuses",
        "status_pending": "Pending",
        "status_active": "Active",
        "status_archived": "Archived",
        "set_pending": "Mark Pending",
        "set_active": "Publish",
        "set_archived": "Archive",
        "edit_paper": "Edit",
        "edit_paper_title": "Edit Paper Metadata",
        "publish_updated_paper": "Save and Publish",
        "return_to_search": "Back to Search",
        "export_json": "Export JSON",
        "export_csv": "Export CSV",
        "hero_title": "User-Facing Literature Management Platform",
        "hero_body": "This page connects directly to MySQL and supports paper ingestion, combined search, paper favorites, keyword favorites, citation statistics, keyword analytics, and data export.",
        "workbench_note": "",
        "papers": "Papers",
        "authors": "Authors",
        "author_select": "Select Authors",
        "add_author": "Add Author",
        "author_name": "Author Name",
        "author_email": "Email",
        "author_orcid": "ORCID",
        "save_author": "Save Author",
        "author_required_tip": "Select authors from the author table. Add a new author below if needed.",
        "author_lookup": "Search Authors",
        "author_lookup_placeholder": "Search similar authors by name / email / ORCID",
        "parsed_authors": "Parsed Authors",
        "keywords": "Keywords",
        "add_keyword": "Add",
        "citations": "Citations",
        "query_placeholder": "Title / abstract / DOI / author",
        "institution": "Institution",
        "year": "Year",
        "year_from": "From Year",
        "year_to": "To Year",
        "keyword": "Keyword",
        "combined_search": "Search",
        "paper": "Paper",
        "source": "Source",
        "relation": "Relation",
        "action": "Action",
        "no_records": "No matching records",
        "save_paper": "Favorite",
        "saved_paper": "Saved",
        "remove_paper": "Unfavorite",
        "no_doi": "No DOI",
        "reference_label": "refs",
        "cited_by_label": "cited by",
        "new_paper": "Upload Paper",
        "title": "Title",
        "abstract": "Abstract",
        "publish_date": "Publish Date",
        "doi": "DOI",
        "venue": "Venue",
        "type": "Type",
        "save_mysql": "Save to MySQL",
        "batch_import": "Batch Import",
        "csv_tip": "Upload a CSV with fields: title, abstract, publish_date, doi, venue_name, venue_type, author_ids, keywords. DOI and author ORCID are required and unique.",
        "choose_csv_file": "Choose CSV file",
        "pdf_upload": "PDF Upload & Metadata Parsing",
        "pdf_tip": "Upload a PDF to prefill the form with extracted metadata. Review it first, then save manually.",
        "choose_pdf_file": "Choose PDF file",
        "upload_pdf": "Upload and Parse PDF",
        "batch_pdf_upload": "Batch PDF Parsing",
        "batch_pdf_tip": "Select multiple PDFs. The system parses each file and creates editable review forms before saving.",
        "choose_pdf_files": "Choose PDF files",
        "upload_pdfs": "Parse PDFs",
        "batch_review_title": "Review Parsed Papers",
        "save_batch_mysql": "Save Batch to MySQL",
        "source_file": "Source File",
        "pdf_prefilled": "PDF parsed. Please review and edit the form below before saving.",
        "pdf_attached": "PDF file attached",
        "abstract_placeholder": "Enter the paper abstract",
        "doi_placeholder": "e.g. 10.1038/s41586-021-03819-2",
        "authors_placeholder": "Separate with semicolons, e.g. John Smith; Alice Wang",
        "keywords_placeholder": "Separate with semicolons, e.g. Artificial Intelligence; Biology",
        "import_csv": "Import CSV",
        "data_analysis": "Data Analytics",
        "year_dist": "Year Distribution",
        "hot_keywords": "Hot Keywords",
        "favorite_keyword": "Favorite Keyword",
        "saved_keyword": "Saved",
        "remove_keyword": "Unfavorite",
        "active_filter": "Active",
        "my_favorites": "My Favorites",
        "favorite_papers": "Favorite Papers",
        "favorite_keywords": "Favorite Keywords",
        "keyword_lookup": "Keyword Search",
        "keyword_lookup_placeholder": "Search any keyword in the keyword table",
        "keyword_results": "Available Keywords",
        "empty_favorites": "No favorites yet",
        "none": "None",
        "settings_title": "Interface Settings",
        "language": "Language",
        "save_settings": "Save Settings",
        "db_error": "Database connection failed: {error}. Please initialize the database and check the connection settings.",
    },
}


MESSAGE_TRANSLATIONS = {
    "文献已保存到 MySQL": "Paper saved to MySQL",
    "设置已保存": "Settings saved",
    "论文已收藏": "Paper added to favorites",
    "已取消收藏论文": "Paper removed from favorites",
    "关键词已收藏": "Keyword added to favorites",
    "已取消收藏关键词": "Keyword removed from favorites",
    "保存失败": "Save failed",
    "设置保存失败": "Failed to save settings",
    "收藏失败": "Favorite action failed",
    "取消收藏失败": "Unfavorite action failed",
    "导入失败": "Import failed",
    "已导入": "Imported",
    "条文献到 MySQL": "papers to MySQL",
    "未找到 CSV 文件": "CSV file not found",
    "未找到 PDF 文件": "PDF file not found",
    "请上传 PDF 文件": "Please upload a PDF file",
    "PDF 已解析并入库": "PDF parsed and saved",
    "PDF 已解析，请检查并修改后再保存": "PDF parsed. Please review and edit before saving",
    "PDF 入库失败": "PDF upload failed",
    "登录失败": "Login failed",
    "用户名或密码错误": "Invalid username or password",
    "请先登录": "Please log in first",
    "标题过短，请填写更完整的信息": "The title is too short. Please enter more complete information",
    "标题不能是重复字符或占位内容": "The title cannot be repeated characters or placeholder content",
    "标题需要包含有效的中文或英文字母": "The title must contain valid Chinese or English letters",
    "摘要过短，请填写更完整的信息": "The abstract is too short. Please enter more complete information",
    "摘要不能是重复字符或占位内容": "The abstract cannot be repeated characters or placeholder content",
    "摘要需要包含有效的中文或英文字母": "The abstract must contain valid Chinese or English letters",
    "DOI 格式不正确，应类似 10.xxxx/xxxxx": "Invalid DOI format. It should look like 10.xxxx/xxxxx",
    "DOI 不能为空，缺少 DOI 的论文不能入库": "DOI is required. Papers without DOI cannot be saved",
    "DOI 已存在，不能重复入库": "This DOI already exists. Duplicate papers cannot be saved",
    "作者过短，请填写更完整的信息": "The author name is too short. Please enter a complete author name",
    "作者不能是重复字符或占位内容": "The author name cannot be repeated characters or placeholder content",
    "作者需要包含有效的中文或英文字母": "The author name must contain valid Chinese or English letters",
    "请至少选择一位已登记 ORCID 的作者": "Please select at least one registered author with ORCID",
    "ORCID 不能为空，缺少 ORCID 的作者不能加入作者表": "ORCID is required. Authors without ORCID cannot be added",
    "ORCID 格式应类似 0000-0000-0000-0000": "ORCID should look like 0000-0000-0000-0000",
    "ORCID 已存在，不能重复添加作者": "This ORCID already exists. Duplicate authors cannot be added",
    "邮箱已存在，不能重复添加作者": "This email already exists. Duplicate authors cannot be added",
    "关键词过短，请填写更完整的信息": "The keyword is too short. Please enter a meaningful keyword",
    "关键词不能是重复字符或占位内容": "The keyword cannot be repeated characters or placeholder content",
    "关键词需要包含有效的中文或英文字母": "The keyword must contain valid Chinese or English letters",
    "期刊/会议过短，请填写更完整的信息": "The venue is too short. Please enter a complete venue name",
    "期刊/会议不能是重复字符或占位内容": "The venue cannot be repeated characters or placeholder content",
    "期刊/会议需要包含有效的中文或英文字母": "The venue must contain valid Chinese or English letters",
    "请至少填写一位作者": "Please enter at least one author",
    "请至少填写一个关键词": "Please enter at least one keyword",
    "日期格式必须为 YYYY-MM-DD": "Date format must be YYYY-MM-DD",
    "发表日期不能晚于今天": "The publication date cannot be later than today",
    "发表年份过早，请检查日期是否正确": "The publication year is too early. Please check the date",
}


class DatabaseError(RuntimeError):
    pass


def mysql_args(database: str | None = DB_NAME) -> list[str]:
    args = [
        MYSQL_CLI,
        f"--host={MYSQL_HOST}",
        f"--port={MYSQL_PORT}",
        f"--user={MYSQL_USER}",
        "--default-character-set=utf8mb4",
        "--batch",
        "--raw",
    ]
    if MYSQL_PASSWORD:
        args.append(f"--password={MYSQL_PASSWORD}")
    if database:
        args.append(database)
    return args


def run_sql(sql: str, *, database: str | None = DB_NAME) -> list[dict[str, str | None]]:
    if not Path(MYSQL_CLI).exists() and shutil.which(MYSQL_CLI) is None:
        raise DatabaseError(f"找不到 mysql 客户端：{MYSQL_CLI}")

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".sql", delete=False) as handle:
        handle.write(sql)
        script_path = handle.name
    try:
        proc = subprocess.run(
            mysql_args(database),
            stdin=open(script_path, "rb"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )
    finally:
        Path(script_path).unlink(missing_ok=True)

    stderr = proc.stderr.decode("utf-8", errors="replace").strip()
    if proc.returncode != 0:
        raise DatabaseError(stderr or "MySQL 执行失败")

    text = proc.stdout.decode("utf-8", errors="replace")
    if not text.strip():
        return []
    reader = csv.reader(io.StringIO(text), dialect="excel-tab")
    rows = list(reader)
    if not rows:
        return []
    headers = rows[0]
    result = []
    for row in rows[1:]:
        if len(row) < len(headers):
            row += [""] * (len(headers) - len(row))
        result.append({headers[i]: (None if row[i] == "NULL" else row[i]) for i in range(len(headers))})
    return result


def quote(value: object) -> str:
    if value is None:
        return "NULL"
    text = str(value)
    return "'" + text.replace("\\", "\\\\").replace("'", "''") + "'"


def split_values(value: str | list[str]) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [v.strip() for v in value.replace("；", ";").replace(",", ";").split(";") if v.strip()]


def compact_text(value: object) -> str:
    return re.sub(r"\s+", "", str(value or ""))


def is_repetitive(value: object) -> bool:
    text = compact_text(value).lower()
    return bool(text) and len(set(text)) <= 1


def has_word_content(value: object, minimum: int = 2) -> bool:
    text = str(value or "")
    return len(re.findall(r"[A-Za-z\u4e00-\u9fff]", text)) >= minimum


def validate_meaningful_text(value: object, field_name: str, *, min_len: int, min_word_chars: int = 2) -> str:
    text = str(value or "").strip()
    if len(compact_text(text)) < min_len:
        raise ValueError(f"{field_name}过短，请填写更完整的信息")
    if is_repetitive(text):
        raise ValueError(f"{field_name}不能是重复字符或占位内容")
    if not has_word_content(text, min_word_chars):
        raise ValueError(f"{field_name}需要包含有效的中文或英文字母")
    return text


def validate_doi(value: str) -> str:
    doi = value.strip()
    if not doi:
        return ""
    if not re.fullmatch(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", doi):
        raise ValueError("DOI 格式不正确，应类似 10.xxxx/xxxxx")
    return doi


def require_doi(value: str) -> str:
    doi = validate_doi(value)
    if not doi:
        raise ValueError("DOI 不能为空，缺少 DOI 的论文不能入库")
    return doi


def ensure_unique_paper_doi(doi: str, paper_id: int = 0) -> None:
    clauses = [f"doi = {quote(doi)}"]
    if paper_id > 0:
        clauses.append(f"paper_id <> {paper_id}")
    rows = run_sql(
        "SELECT paper_id FROM paper "
        f"WHERE {' AND '.join(clauses)} "
        "LIMIT 1;"
    )
    if rows:
        raise ValueError("DOI 已存在，不能重复入库")


def selected_keyword_ids(query: dict, key: str = "fav_keyword") -> list[int]:
    raw_values = query.get(key, [])
    if not isinstance(raw_values, list):
        raw_values = [raw_values]
    result: list[int] = []
    for value in raw_values:
        try:
            keyword_id = int(value)
        except (TypeError, ValueError):
            continue
        if keyword_id > 0 and keyword_id not in result:
            result.append(keyword_id)
    return result


def selected_keyword_words(query: dict, key: str = "keyword_filter") -> list[str]:
    raw_values = query.get(key, [])
    if not isinstance(raw_values, list):
        raw_values = [raw_values]
    result: list[str] = []
    for value in raw_values:
        word = str(value or "").strip()
        if word and word not in result:
            result.append(word)
    return result


def selected_int_values(data: dict, key: str) -> list[int]:
    raw_values = data.get(key, [])
    if not isinstance(raw_values, list):
        if isinstance(raw_values, str):
            raw_values = [item for item in re.split(r"[;,，；\s]+", raw_values) if item]
        else:
            raw_values = [raw_values]
    result: list[int] = []
    for value in raw_values:
        try:
            item_id = int(value)
        except (TypeError, ValueError):
            continue
        if item_id > 0 and item_id not in result:
            result.append(item_id)
    return result


def keyword_filter_url(query: dict, keyword_id: int, key: str = "fav_keyword", anchor: str = "") -> str:
    selected = selected_keyword_ids(query, key)
    if keyword_id in selected:
        selected = [item for item in selected if item != keyword_id]
    else:
        selected.append(keyword_id)

    params: list[tuple[str, str]] = []
    for preserved_key in ("q", "year", "year_from", "year_to", "keyword", "institution", "status"):
        value = query.get(preserved_key)
        if value:
            params.append((preserved_key, str(value)))
    for word in selected_keyword_words(query):
        params.append(("keyword_filter", word))
    other_key = "favorite_filter_keyword" if key == "fav_keyword" else "fav_keyword"
    for item in selected_keyword_ids(query, other_key):
        params.append((other_key, str(item)))
    for item in selected:
        params.append((key, str(item)))
    suffix = urllib.parse.urlencode(params)
    return "/" + (f"?{suffix}" if suffix else "") + (f"#{anchor}" if anchor else "")


def keyword_text_filter_url(query: dict, remove_word: str = "") -> str:
    params: list[tuple[str, str]] = []
    for preserved_key in ("q", "year", "year_from", "year_to", "institution", "status"):
        value = query.get(preserved_key)
        if value:
            params.append((preserved_key, str(value)))

    words = selected_keyword_words(query)
    typed = str(query.get("keyword") or "").strip()
    if typed and typed not in words:
        words.append(typed)
    for word in words:
        if word != remove_word:
            params.append(("keyword_filter", word))
    for item in selected_keyword_ids(query, "fav_keyword"):
        params.append(("fav_keyword", str(item)))
    suffix = urllib.parse.urlencode(params)
    return "/" + (f"?{suffix}" if suffix else "") + "#search"


def validate_date(value: str) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value or ""):
        raise ValueError("日期格式必须为 YYYY-MM-DD")
    parsed = date.fromisoformat(value)
    if parsed > date.today():
        raise ValueError("发表日期不能晚于今天")
    if parsed.year < 1900:
        raise ValueError("发表年份过早，请检查日期是否正确")
    return value


def validate_paper_input(data: dict) -> dict:
    title = validate_meaningful_text(data.get("title"), "标题", min_len=5, min_word_chars=3)
    abstract = str(data.get("abstract") or "").strip()
    doi = require_doi(str(data.get("doi") or ""))
    if abstract:
        validate_meaningful_text(abstract, "摘要", min_len=10, min_word_chars=4)

    author_ids = selected_int_values(data, "author_ids")
    authors = split_values(data.get("authors", ""))
    if not author_ids:
        raise ValueError("请至少选择一位已登记 ORCID 的作者")
    if author_ids:
        existing = run_sql(
            "SELECT author_id FROM author "
            f"WHERE author_id IN ({', '.join(str(item) for item in author_ids)});"
        )
        existing_ids = {int(row["author_id"]) for row in existing}
        missing = [item for item in author_ids if item not in existing_ids]
        if missing:
            raise ValueError("选择的作者不存在，请刷新页面后重试")

    keywords = split_values(data.get("keywords", ""))
    if not keywords:
        raise ValueError("请至少填写一个关键词")
    for keyword in keywords:
        validate_meaningful_text(keyword, "关键词", min_len=2, min_word_chars=2)

    venue_name = str(data.get("venue_name") or "").strip()
    if venue_name:
        validate_meaningful_text(venue_name, "期刊/会议", min_len=2, min_word_chars=2)

    return {
        **data,
        "title": title,
        "abstract": abstract,
        "doi": doi,
        "author_ids": author_ids,
        "authors": authors,
        "keywords": keywords,
        "venue_name": venue_name,
    }


def normalize_paper_edit_input(data: dict) -> dict:
    title = str(data.get("title") or "").strip()
    if not title:
        raise ValueError("标题不能为空")
    doi = str(data.get("doi") or "").strip()
    if not doi:
        raise ValueError("DOI 不能为空，缺少 DOI 的论文不能入库")
    author_ids = selected_int_values(data, "author_ids")
    if not author_ids:
        raise ValueError("请至少选择一位已登记 ORCID 的作者")
    return {
        **data,
        "title": title,
        "abstract": str(data.get("abstract") or "").strip(),
        "doi": doi,
        "author_ids": author_ids,
        "authors": split_values(data.get("authors", "")),
        "keywords": split_values(data.get("keywords", "")),
        "venue_name": str(data.get("venue_name") or "").strip(),
    }


def safe_filename(name: str) -> str:
    stem = Path(name or "paper.pdf").name
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._")
    return stem or "paper.pdf"


def guess_keywords(text: str, limit: int = 6) -> list[str]:
    stopwords = {
        "the", "and", "for", "with", "from", "this", "that", "paper", "study",
        "using", "based", "into", "over", "under", "between", "within", "their",
        "analysis", "research", "method", "methods", "result", "results",
    }
    words = re.findall(r"[A-Za-z][A-Za-z-]{3,}", text.lower())
    counts: dict[str, int] = {}
    for word in words:
        normalized = word.strip("-")
        if normalized in stopwords or len(normalized) < 4:
            continue
        counts[normalized] = counts.get(normalized, 0) + 1
    return [word.title() for word, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]]


def extract_pdf_text(pdf_path: Path) -> str:
    try:
        import pdfplumber  # type: ignore

        chunks: list[str] = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages[:3]:
                text = page.extract_text() or ""
                if text:
                    chunks.append(text)
        return "\n".join(chunks)
    except Exception:
        pass

    try:
        from PyPDF2 import PdfReader  # type: ignore

        reader = PdfReader(str(pdf_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages[:3])
    except Exception:
        return ""


def parse_pdf_metadata(pdf_path: Path, original_name: str) -> dict:
    from services.pdf_parser import parse_pdf_metadata as parse_with_rule_parser

    result = parse_with_rule_parser(str(pdf_path))
    return {
        "title": result.get("title") or "",
        "abstract": result.get("abstract") or "",
        "publish_date": result.get("publish_date") or date.today().isoformat(),
        "doi": result.get("doi") or "",
        "venue_name": result.get("venue_name") or "",
        "venue_type": result.get("venue_type") or "conference",
        "authors": "; ".join(result.get("authors") or []),
        "keywords": "; ".join(result.get("keywords") or []),
    }


def init_check() -> None:
    run_sql("SELECT 1 AS ok;")


def current_user_id(username: str | None = None) -> int:
    active_user = username or APP_USER
    rows = run_sql(f"SELECT user_id FROM sys_user WHERE username = {quote(active_user)} LIMIT 1;")
    return int(rows[0]["user_id"]) if rows else 1


def current_user_role(username: str | None = None) -> str:
    if not username:
        return "user"
    rows = run_sql(f"SELECT role FROM sys_user WHERE username = {quote(username)} LIMIT 1;")
    return str(rows[0]["role"]) if rows else "user"


def authenticate_user(username: str, password: str) -> dict[str, str | None] | None:
    rows = run_sql(
        f"""
        SELECT user_id, username, role
        FROM sys_user
        WHERE username = {quote(username)}
          AND password_hash = SHA2({quote(password)}, 256)
        LIMIT 1;
        """
    )
    return rows[0] if rows else None


def register_user(username: str, password: str, email: str = "") -> None:
    username = username.strip()
    email = email.strip()
    if not re.fullmatch(r"[A-Za-z0-9_]{3,32}", username):
        raise ValueError("用户名需为 3-32 位字母、数字或下划线")
    if len(password) < 6:
        raise ValueError("密码至少需要 6 位")
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValueError("邮箱格式不正确")
    exists = run_sql(f"SELECT user_id FROM sys_user WHERE username = {quote(username)} LIMIT 1;")
    if exists:
        raise ValueError("用户名已存在")
    run_sql(
        "INSERT INTO sys_user(username, password_hash, role, email) VALUES "
        f"({quote(username)}, SHA2({quote(password)}, 256), 'user', {quote(email or None)});"
    )
    user_id = current_user_id(username)
    run_sql(
        "INSERT IGNORE INTO user_preference(user_id, language, font_family, font_size) "
        f"VALUES ({user_id}, 'zh', 'system', 'normal');"
    )


def login_cookie_username(headers) -> str:
    cookie = SimpleCookie(headers.get("Cookie", ""))
    morsel = cookie.get("lm_user")
    if not morsel:
        return ""
    return urllib.parse.unquote(morsel.value)


def login_cookie_header(username: str) -> str:
    return f"lm_user={urllib.parse.quote(username)}; Path=/; HttpOnly; SameSite=Lax"


def clear_login_cookie_header() -> str:
    return "lm_user=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax"


def preferences(user_id: int) -> dict[str, str]:
    run_sql(
        "INSERT IGNORE INTO user_preference(user_id, language, font_family, font_size) "
        f"VALUES ({user_id}, 'zh', 'system', 'normal');"
    )
    rows = run_sql(
        f"""
        SELECT language
        FROM user_preference
        WHERE user_id = {user_id}
        LIMIT 1;
        """
    )
    pref = rows[0] if rows else {}
    language = pref.get("language") or "zh"
    return {
        "language": language if language in TEXT else "zh",
    }


def update_preferences(user_id: int, data: dict) -> None:
    language = data.get("language") if data.get("language") in {"zh", "en"} else "zh"
    run_sql(
        "INSERT INTO user_preference(user_id, language, font_family, font_size) VALUES "
        f"({user_id}, {quote(language)}, 'system', 'normal') "
        "ON DUPLICATE KEY UPDATE "
        "language = VALUES(language);"
    )


def author_options(term: str = "") -> list[dict[str, str | None]]:
    term = str(term or "").strip()
    where = ""
    if term:
        like = quote("%" + term + "%")
        where = f"WHERE name LIKE {like} OR email LIKE {like} OR orcid_id LIKE {like}"
    return run_sql(
        f"""
        SELECT author_id, name, email, orcid_id
        FROM author
        {where}
        ORDER BY name, author_id
        LIMIT 200;
        """
    )


def author_ids_by_names(names: str | list[str]) -> list[int]:
    wanted = split_values(names)
    if not wanted:
        return []
    found: list[int] = []
    for name in wanted:
        rows = run_sql(
            "SELECT author_id FROM author "
            f"WHERE LOWER(name) = LOWER({quote(name)}) "
            "ORDER BY author_id LIMIT 1;"
        )
        if rows:
            author_id = int(rows[0]["author_id"])
            if author_id not in found:
                found.append(author_id)
    return found


def authors_by_ids(author_ids: list[int] | set[int]) -> list[dict[str, str | None]]:
    clean_ids = sorted({int(item) for item in author_ids if int(item) > 0})
    if not clean_ids:
        return []
    return run_sql(
        "SELECT author_id, name, email, orcid_id FROM author "
        f"WHERE author_id IN ({', '.join(str(item) for item in clean_ids)}) "
        "ORDER BY name, author_id;"
    )


def create_author(data: dict) -> int:
    name = validate_meaningful_text(data.get("name"), "作者", min_len=2, min_word_chars=2)
    email = str(data.get("email") or "").strip()
    orcid_id = str(data.get("orcid_id") or "").strip()
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValueError("邮箱格式不正确")
    if not orcid_id:
        raise ValueError("ORCID 不能为空，缺少 ORCID 的作者不能加入作者表")
    if not re.fullmatch(r"\d{4}-\d{4}-\d{4}-[\dX]{4}", orcid_id):
        raise ValueError("ORCID 格式应类似 0000-0000-0000-0000")
    rows = run_sql(
        "SELECT author_id FROM author "
        f"WHERE orcid_id = {quote(orcid_id)} "
        "ORDER BY author_id LIMIT 1;"
    )
    if rows:
        raise ValueError("ORCID 已存在，不能重复添加作者")
    if email:
        rows = run_sql(
            "SELECT author_id FROM author "
            f"WHERE email = {quote(email)} "
            "ORDER BY author_id LIMIT 1;"
        )
        if rows:
            raise ValueError("邮箱已存在，不能重复添加作者")
    result = run_sql(
        "INSERT INTO author(name, email, orcid_id) VALUES "
        f"({quote(name)}, {quote(email or None)}, {quote(orcid_id)});"
        "SELECT LAST_INSERT_ID() AS author_id;"
    )
    return int(result[-1]["author_id"]) if result else 0


def create_paper(data: dict, user_id: int = 1) -> int:
    data = validate_paper_input(data)
    ensure_unique_paper_doi(data["doi"])
    title = data.get("title", "").strip()
    if not title:
        raise ValueError("标题不能为空")
    publish_date = validate_date(data.get("publish_date") or date.today().isoformat())
    venue_type = data.get("venue_type") or "other"
    if venue_type not in {"journal", "conference", "preprint", "other"}:
        venue_type = "other"

    statements = [
        "SET @new_paper_id = NULL",
        (
            "CALL sp_create_paper("
            f"{quote(title)}, "
            f"{quote(data.get('abstract', ''))}, "
            f"{quote(publish_date)}, "
            f"{quote(data.get('doi'))}, "
            f"{quote(data.get('venue_name') or None)}, "
            f"{quote(venue_type)}, "
            f"{int(user_id or 1)}, @new_paper_id)"
        ),
    ]

    for order, author_id in enumerate(data.get("author_ids") or [], 1):
        statements.append(
            "INSERT IGNORE INTO paper_author(paper_id, author_id, author_order, is_corresponding) "
            f"SELECT @new_paper_id, author_id, {order}, {1 if order == 1 else 0} "
            f"FROM author WHERE author_id = {int(author_id)} LIMIT 1"
        )

    for keyword in data.get("keywords") or []:
        statements.append(
            "INSERT IGNORE INTO keyword(word, category) "
            f"VALUES ({quote(keyword)}, 'topic')"
        )
        statements.append(
            "INSERT IGNORE INTO paper_keyword(paper_id, keyword_id) "
            f"SELECT @new_paper_id, keyword_id FROM keyword "
            f"WHERE word = {quote(keyword)} AND category = 'topic' LIMIT 1"
        )

    statements.append("SELECT @new_paper_id AS paper_id")
    rows = run_sql(";\n".join(statements) + ";")
    paper_id = int(rows[-1]["paper_id"]) if rows and rows[-1].get("paper_id") else 0
    pdf_path = str(data.get("pdf_path") or "").strip()
    if paper_id and pdf_path.startswith("/static/uploads/"):
        run_sql(f"UPDATE paper SET pdf_path = {quote(pdf_path)} WHERE paper_id = {paper_id};")
    status = str(data.get("status") or "").strip()
    if paper_id and status in {"pending", "active", "archived"}:
        update_paper_status(paper_id, status)
    return paper_id


def paper_edit_data(paper_id: int) -> dict:
    if paper_id <= 0:
        raise ValueError("论文编号无效")
    rows = run_sql(
        f"""
        SELECT
          p.paper_id, p.title, p.abstract, p.publish_date, p.doi, p.pdf_path, p.status,
          COALESCE(v.name, '') AS venue_name,
          COALESCE(v.venue_type, 'other') AS venue_type
        FROM paper p
        LEFT JOIN venue v ON p.venue_id = v.venue_id
        WHERE p.paper_id = {paper_id}
        LIMIT 1;
        """
    )
    if not rows:
        raise ValueError("论文不存在")
    data = dict(rows[0])
    author_rows = run_sql(
        "SELECT author_id FROM paper_author "
        f"WHERE paper_id = {paper_id} "
        "ORDER BY author_order, author_id;"
    )
    keyword_rows = run_sql(
        "SELECT k.word FROM paper_keyword pk "
        "JOIN keyword k ON pk.keyword_id = k.keyword_id "
        f"WHERE pk.paper_id = {paper_id} AND k.category <> 'source' "
        "ORDER BY k.word;"
    )
    data["author_ids"] = [int(row["author_id"]) for row in author_rows]
    data["keywords"] = "; ".join(str(row["word"]) for row in keyword_rows)
    return data


def update_paper(paper_id: int, data: dict, user_id: int = 1) -> None:
    if paper_id <= 0:
        raise ValueError("论文编号无效")
    data = normalize_paper_edit_input(data)
    ensure_unique_paper_doi(data["doi"], paper_id)
    publish_date = validate_date(data.get("publish_date") or date.today().isoformat())
    venue_type = data.get("venue_type") or "other"
    if venue_type not in {"journal", "conference", "preprint", "other"}:
        venue_type = "other"

    statements = ["SET @venue_id = NULL"]
    venue_name = data.get("venue_name") or ""
    if venue_name:
        statements.extend(
            [
                (
                    "SELECT MAX(venue_id) INTO @venue_id FROM venue "
                    f"WHERE name = {quote(venue_name)} AND publish_year = YEAR({quote(publish_date)})"
                ),
                (
                    "INSERT INTO venue(name, venue_type, publish_year) "
                    f"SELECT {quote(venue_name)}, {quote(venue_type)}, YEAR({quote(publish_date)}) "
                    "WHERE @venue_id IS NULL"
                ),
                "SET @venue_id = COALESCE(@venue_id, LAST_INSERT_ID())",
            ]
        )
    statements.extend(
        [
            (
                "UPDATE paper SET "
                f"title = {quote(data.get('title'))}, "
                f"abstract = {quote(data.get('abstract') or '')}, "
                f"publish_date = {quote(publish_date)}, "
                f"doi = {quote(data.get('doi'))}, "
                "venue_id = @venue_id, "
                f"pdf_path = {quote(data.get('pdf_path') or None)}, "
                "status = 'active' "
                f"WHERE paper_id = {paper_id}"
            ),
            f"DELETE FROM paper_author WHERE paper_id = {paper_id}",
        ]
    )
    for order, author_id in enumerate(data.get("author_ids") or [], 1):
        statements.append(
            "INSERT IGNORE INTO paper_author(paper_id, author_id, author_order, is_corresponding) "
            f"SELECT {paper_id}, author_id, {order}, {1 if order == 1 else 0} "
            f"FROM author WHERE author_id = {int(author_id)} LIMIT 1"
        )
    statements.append(f"DELETE FROM paper_keyword WHERE paper_id = {paper_id}")
    for keyword in data.get("keywords") or []:
        statements.append(
            "INSERT IGNORE INTO keyword(word, category) "
            f"VALUES ({quote(keyword)}, 'topic')"
        )
        statements.append(
            "INSERT IGNORE INTO paper_keyword(paper_id, keyword_id) "
            f"SELECT {paper_id}, keyword_id FROM keyword "
            f"WHERE word = {quote(keyword)} AND category = 'topic' LIMIT 1"
        )
    statements.append(
        "INSERT INTO paper_version(paper_id, version_no, change_log, operator_id) "
        f"SELECT {paper_id}, COALESCE(MAX(version_no), 0) + 1, '管理员修改并发布', {int(user_id or 1)} "
        "FROM paper_version "
        f"WHERE paper_id = {paper_id}"
    )
    run_sql(";\n".join(statements) + ";")


def paper_rows(query: dict, user_id: int | None = None, is_admin: bool = False) -> list[dict[str, str | None]]:
    clauses = ["1 = 1"]
    selected = selected_keyword_ids(query)
    selected_words = selected_keyword_words(query)
    typed_keyword = str(query.get("keyword") or "").strip()
    if typed_keyword and typed_keyword not in selected_words:
        selected_words.append(typed_keyword)
    if query.get("q"):
        q = f"%{query['q']}%"
        clauses.append(
            "("
            f"title LIKE {quote(q)} OR abstract LIKE {quote(q)} OR doi LIKE {quote(q)} "
            f"OR authors LIKE {quote(q)} OR institutions LIKE {quote(q)}"
            ")"
        )
    if query.get("institution"):
        clauses.append(f"institutions LIKE {quote('%' + query['institution'] + '%')}")
    if query.get("year") and re.fullmatch(r"\d{4}", str(query["year"])):
        clauses.append(f"YEAR(publish_date) = {int(query['year'])}")
    if query.get("year_from") and re.fullmatch(r"\d{4}", str(query["year_from"])):
        clauses.append(f"YEAR(publish_date) >= {int(query['year_from'])}")
    if query.get("year_to") and re.fullmatch(r"\d{4}", str(query["year_to"])):
        clauses.append(f"YEAR(publish_date) <= {int(query['year_to'])}")
    if is_admin:
        status_filter = str(query.get("status") or "").strip()
        if status_filter in {"pending", "active", "archived"}:
            clauses.append(f"status = {quote(status_filter)}")
    else:
        clauses.append("status = 'active'")
    for word in selected_words:
        clauses.append(
            "paper_id IN ("
            "SELECT pk.paper_id FROM paper_keyword pk "
            "JOIN keyword k ON pk.keyword_id = k.keyword_id "
            f"WHERE k.word = {quote(word)} AND k.category <> 'source'"
            ")"
        )
    if selected:
        selected_csv = ", ".join(str(item) for item in selected)
        clauses.append(
            "paper_id IN ("
            "SELECT paper_id FROM paper_keyword "
            f"WHERE keyword_id IN ({selected_csv}) "
            "GROUP BY paper_id "
            f"HAVING COUNT(DISTINCT keyword_id) = {len(selected)}"
            ")"
        )
    where = " AND ".join(clauses)
    return run_sql(
        f"""
        SELECT
          paper_id, title, abstract, publish_date, doi, venue_name,
          status,
          authors, institutions, keywords,
          reference_count AS ref_count,
          cited_by_count,
          EXISTS(
            SELECT 1 FROM favorite f
            WHERE f.paper_id = v_paper_detail.paper_id
              AND f.user_id = {int(user_id or 0)}
          ) AS is_favorite
        FROM v_paper_detail
        WHERE {where}
        ORDER BY publish_date DESC, paper_id DESC;
        """
    )


def stats(user_id: int) -> dict:
    rows = run_sql(
        """
        SELECT
          (SELECT COUNT(*) FROM paper) AS papers,
          (SELECT COUNT(*) FROM author) AS authors,
          (SELECT COUNT(*) FROM keyword WHERE category <> 'source') AS keywords,
          (SELECT COUNT(*) FROM citation) AS citations;
        """
    )
    summary = rows[0] if rows else {"papers": 0, "authors": 0, "keywords": 0, "citations": 0}
    return {
        "papers": int(summary["papers"] or 0),
        "authors": int(summary["authors"] or 0),
        "keywords": int(summary["keywords"] or 0),
        "citations": int(summary["citations"] or 0),
        "by_year": run_sql(
            """
            SELECT YEAR(publish_date) AS year, COUNT(*) AS n
            FROM paper
            GROUP BY YEAR(publish_date)
            ORDER BY year;
            """
        ),
        "hot_keywords": run_sql(
            f"""
            SELECT
              k.keyword_id,
              k.word,
              COUNT(*) AS n,
              EXISTS(
                SELECT 1 FROM favorite_keyword fk
                WHERE fk.keyword_id = k.keyword_id
                  AND fk.user_id = {user_id}
              ) AS is_favorite
            FROM keyword k
            JOIN paper_keyword pk ON k.keyword_id = pk.keyword_id
            WHERE k.category <> 'source'
            GROUP BY k.keyword_id, k.word
            ORDER BY n DESC, k.word
            LIMIT 8;
            """
        ),
    }


def keyword_options(term: str = "") -> list[dict[str, str | None]]:
    term = str(term or "").strip()
    where = "WHERE k.category <> 'source'"
    if term:
        like = quote("%" + term + "%")
        where += f" AND k.word LIKE {like}"
    return run_sql(
        f"""
        SELECT k.word, COUNT(pk.paper_id) AS paper_count
        FROM keyword k
        LEFT JOIN paper_keyword pk ON k.keyword_id = pk.keyword_id
        {where}
        GROUP BY k.keyword_id, k.word
        ORDER BY k.word
        LIMIT 200;
        """
    )


def favorite_paper(user_id: int, paper_id: int) -> None:
    run_sql(f"INSERT IGNORE INTO favorite(user_id, paper_id) VALUES ({user_id}, {paper_id});")


def unfavorite_paper(user_id: int, paper_id: int) -> None:
    run_sql(f"DELETE FROM favorite WHERE user_id = {user_id} AND paper_id = {paper_id};")


def delete_paper(paper_id: int) -> None:
    if paper_id <= 0:
        raise ValueError("论文编号无效")
    run_sql(f"DELETE FROM paper WHERE paper_id = {paper_id};")


def update_paper_status(paper_id: int, status: str) -> None:
    if paper_id <= 0:
        raise ValueError("论文编号无效")
    if status not in {"pending", "active", "archived"}:
        raise ValueError("论文状态无效")
    run_sql(f"UPDATE paper SET status = {quote(status)} WHERE paper_id = {paper_id};")


def favorite_keyword(user_id: int, word: str = "", keyword_id: int = 0) -> None:
    if keyword_id > 0:
        run_sql(
            "INSERT IGNORE INTO favorite_keyword(user_id, keyword_id) "
            f"SELECT {user_id}, keyword_id FROM keyword "
            f"WHERE keyword_id = {keyword_id} AND category <> 'source' LIMIT 1;"
        )
        return
    run_sql(
        "INSERT IGNORE INTO favorite_keyword(user_id, keyword_id) "
        "SELECT "
        f"{user_id}, keyword_id FROM keyword "
        f"WHERE word = {quote(word)} AND category <> 'source' "
        "ORDER BY FIELD(category, 'topic', 'field'), keyword_id LIMIT 1;"
    )


def unfavorite_keyword(user_id: int, keyword_id: int) -> None:
    run_sql(f"DELETE FROM favorite_keyword WHERE user_id = {user_id} AND keyword_id = {keyword_id};")


def keyword_lookup_rows(user_id: int, query: dict) -> list[dict[str, str | None]]:
    term = str(query.get("keyword_lookup") or "").strip()
    if not term:
        return []
    return run_sql(
        f"""
        SELECT
          k.keyword_id,
          k.word,
          k.category,
          COUNT(pk.paper_id) AS paper_count,
          EXISTS(
            SELECT 1 FROM favorite_keyword fk
            WHERE fk.user_id = {user_id}
              AND fk.keyword_id = k.keyword_id
          ) AS is_favorite
        FROM keyword k
        LEFT JOIN paper_keyword pk ON k.keyword_id = pk.keyword_id
        WHERE k.category <> 'source'
          AND k.word LIKE {quote('%' + term + '%')}
        GROUP BY k.keyword_id, k.word, k.category
        ORDER BY is_favorite DESC, paper_count DESC, k.word
        LIMIT 24;
        """
    )


def user_favorites(user_id: int, query: dict | None = None) -> dict[str, list[dict[str, str | None]]]:
    query = query or {}
    favorite_selected = selected_keyword_ids(query, "favorite_filter_keyword")
    paper_filter = ""
    if favorite_selected:
        selected_csv = ", ".join(str(item) for item in favorite_selected)
        paper_filter = (
            "AND v.paper_id IN ("
            "SELECT paper_id FROM paper_keyword "
            f"WHERE keyword_id IN ({selected_csv}) "
            "GROUP BY paper_id "
            f"HAVING COUNT(DISTINCT keyword_id) = {len(favorite_selected)}"
            ")"
        )
    return {
        "papers": run_sql(
            f"""
            SELECT v.paper_id, v.title, v.doi, v.publish_date, v.keywords
            FROM favorite f
            JOIN v_paper_detail v ON f.paper_id = v.paper_id
            WHERE f.user_id = {user_id}
              {paper_filter}
            ORDER BY f.created_at DESC, v.paper_id DESC
            LIMIT 30;
            """
        ),
        "keywords": run_sql(
            f"""
            SELECT k.keyword_id, k.word, k.category, fk.created_at
            FROM favorite_keyword fk
            JOIN keyword k ON fk.keyword_id = k.keyword_id
            WHERE fk.user_id = {user_id}
            ORDER BY fk.created_at DESC, k.word
            LIMIT 12;
            """
        ),
        "keyword_lookup": keyword_lookup_rows(user_id, query),
    }


def parse_query(raw_query: str) -> dict:
    parsed = urllib.parse.parse_qs(raw_query)
    result: dict[str, str | list[str]] = {}
    for key, values in parsed.items():
        if key in {"fav_keyword", "favorite_filter_keyword", "keyword_filter"}:
            result[key] = values
        elif values:
            result[key] = values[0]
    return result


def html_escape(value: object) -> str:
    import html

    return html.escape("" if value is None else str(value), quote=True)


def translate_message(message: str, language: str) -> str:
    if language != "en" or not message:
        return message
    result = message
    for source, target in MESSAGE_TRANSLATIONS.items():
        result = result.replace(source, target)
    result = result.replace("：", ": ")
    return result


def render_login(message: str = "", language: str = "zh") -> bytes:
    pref_language = language if language in TEXT else "zh"
    t = TEXT[pref_language]
    message = translate_message(message, pref_language)
    html = f"""<!doctype html>
<html lang="{html_escape(pref_language)}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{t['login_title']}</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body class="login-page">
  <main class="login-shell">
    <section class="login-card">
      <h1>{t['login_title']}</h1>
      <p>{t['login_tip']}</p>
      {f"<p class='message'>{html_escape(message)}</p>" if message else ""}
      <form method="post" action="/login">
        <label>{t['username']}<input name="username" autocomplete="username" required></label>
        <label>{t['password']}<input type="password" name="password" autocomplete="current-password" required></label>
        <button>{t['login_button']}</button>
      </form>
      <a class="login-link-button" href="/register">{t['register']}</a>
    </section>
  </main>
</body>
</html>"""
    return html.encode("utf-8")


def render_register(message: str = "", language: str = "zh") -> bytes:
    pref_language = language if language in TEXT else "zh"
    t = TEXT[pref_language]
    message = translate_message(message, pref_language)
    html = f"""<!doctype html>
<html lang="{html_escape(pref_language)}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{t['register_title']}</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body class="login-page">
  <main class="login-shell">
    <section class="login-card">
      <h1>{t['register_title']}</h1>
      <p>{t['register_tip']}</p>
      {f"<p class='message'>{html_escape(message)}</p>" if message else ""}
      <form method="post" action="/register">
        <label>{t['username']}<input name="username" autocomplete="username" required></label>
        <label>{t['password']}<input type="password" name="password" autocomplete="new-password" required minlength="6"></label>
        <label>{t['email']}<input type="email" name="email" autocomplete="email"></label>
        <button>{t['register_button']}</button>
      </form>
      <a class="login-link-button" href="/login">{t['back_to_login']}</a>
    </section>
  </main>
</body>
</html>"""
    return html.encode("utf-8")


def render_index(
    message: str = "",
    query: dict | None = None,
    username: str | None = None,
    draft: dict | None = None,
    batch_drafts: list[dict] | None = None,
    scroll_to: str = "",
) -> bytes:
    query = query or {}
    try:
        user_id = current_user_id(username)
        is_admin = current_user_role(username) == "admin"
        pref = preferences(user_id)
        t = TEXT[pref["language"]]
        papers = paper_rows(query, user_id, is_admin)
        s = stats(user_id)
        fav = user_favorites(user_id, query)
        authors_available = author_options()
        keywords_available = keyword_options()
        db_error = ""
    except Exception as exc:
        user_id = 1
        is_admin = False
        pref = {"language": "zh"}
        t = TEXT["zh"]
        papers = []
        s = {"papers": 0, "authors": 0, "keywords": 0, "citations": 0, "by_year": [], "hot_keywords": []}
        fav = {"papers": [], "keywords": []}
        authors_available = []
        keywords_available = []
        db_error = str(exc)
    message = translate_message(message, pref["language"])
    draft = draft or {}
    batch_drafts = batch_drafts or []
    draft_type = draft.get("venue_type") or "journal"
    if draft_type not in {"journal", "conference", "preprint", "other"}:
        draft_type = "other"
    pdf_draft_note = (
        f"<p class='inline-note'>{html_escape(t['pdf_attached'])}：{html_escape(draft.get('pdf_path'))}</p>"
        if draft.get("pdf_path") else ""
    )

    def safe_author_ids_by_names(names: str | list[str]) -> list[int]:
        try:
            return author_ids_by_names(names)
        except Exception:
            return []

    parsed_author_note = (
        f"<p class='inline-note'>{t['parsed_authors']}：{html_escape(draft.get('authors'))}</p>"
        if draft.get("authors") else ""
    )
    main_selected_author_ids = set(selected_int_values(draft, "author_ids") or safe_author_ids_by_names(draft.get("authors", "")))

    def author_select_html(name: str, selected_ids: set[int]) -> str:
        combined_authors = list(authors_available)
        existing_ids = {int(row["author_id"]) for row in combined_authors}
        for row in authors_by_ids(selected_ids):
            if int(row["author_id"]) not in existing_ids:
                combined_authors.append(row)
                existing_ids.add(int(row["author_id"]))
        combined_authors.sort(key=lambda row: (str(row.get("name") or ""), int(row["author_id"])))
        options = "\n".join(
            f"""<option value="{html_escape(row['author_id'])}" data-label="{html_escape(row.get('name'))}{' | ORCID: ' + html_escape(row.get('orcid_id')) if row.get('orcid_id') else ''}{' | ' + html_escape(row.get('email')) if row.get('email') else ''}">{html_escape(row.get('name'))}{' | ORCID: ' + html_escape(row.get('orcid_id')) if row.get('orcid_id') else ''}{' | ' + html_escape(row.get('email')) if row.get('email') else ''}</option>"""
            for row in combined_authors
            if int(row["author_id"]) not in selected_ids
        )
        chips = "\n".join(
            f"""
            <span class="choice-chip" data-value="{html_escape(row['author_id'])}">
              <span>{html_escape(row.get('name'))}{' | ORCID: ' + html_escape(row.get('orcid_id')) if row.get('orcid_id') else ''}{' | ' + html_escape(row.get('email')) if row.get('email') else ''}</span>
              <button type="button" class="choice-chip-close" aria-label="remove">&times;</button>
              <input type="hidden" name="{name}" value="{html_escape(row['author_id'])}">
            </span>
            """
            for row in combined_authors
            if int(row["author_id"]) in selected_ids
        )
        return f"""
        <label class="token-picker" data-token-picker="author" data-hidden-name="{html_escape(name)}">{t['author_select']}
          <input type="search" class="author-filter" placeholder="{t['author_lookup_placeholder']}" data-author-filter>
          <select data-token-select size="6">
            {options}
          </select>
          <div class="choice-chip-list" data-token-list>{chips}</div>
        </label>
        <p class="field-help">{t['author_required_tip']}</p>
        """

    def keyword_token_html(name: str, value: str | list[str]) -> str:
        words = split_values(value) if not isinstance(value, list) else [str(item).strip() for item in value if str(item).strip()]
        words = list(dict.fromkeys(words))
        chips = "\n".join(
            f"""
            <span class="choice-chip" data-value="{html_escape(word)}">
              <span>{html_escape(word)}</span>
              <button type="button" class="choice-chip-close" aria-label="remove">&times;</button>
              <input type="hidden" name="{html_escape(name)}" value="{html_escape(word)}">
            </span>
            """
            for word in words
        )
        return f"""
        <label class="token-picker" data-token-picker="keyword" data-hidden-name="{html_escape(name)}">{t['keywords']}
          <div class="token-add-row">
            <input type="text" class="keyword-filter-input" placeholder="{t['keywords_placeholder']}" data-free-keyword-input>
            <button type="button" class="small secondary" data-free-keyword-add>{t['add_keyword']}</button>
          </div>
          <div class="choice-chip-list" data-token-list>{chips}</div>
        </label>
        """

    def status_label(value: str | None) -> str:
        return {
            "pending": t["status_pending"],
            "active": t["status_active"],
            "archived": t["status_archived"],
        }.get(str(value or "active"), str(value or "active"))

    def status_action_buttons(row: dict[str, str | None]) -> str:
        if not is_admin:
            return ""
        current_status = str(row.get("status") or "active")
        buttons = [
            f"""
            <form method="get" action="/papers/edit">
              <input type="hidden" name="paper_id" value="{html_escape(row.get('paper_id'))}">
              <button class="small secondary">{t['edit_paper']}</button>
            </form>
            """
        ]
        if current_status == "pending":
            buttons.append(
                f"""
                <form method="post" action="/papers/status">
                  <input type="hidden" name="paper_id" value="{html_escape(row.get('paper_id'))}">
                  <input type="hidden" name="status" value="active">
                  <button class="small secondary">{t['set_active']}</button>
                </form>
                """
            )
        if current_status == "archived":
            buttons.append(
                f"""
                <form method="post" action="/papers/status">
                  <input type="hidden" name="paper_id" value="{html_escape(row.get('paper_id'))}">
                  <input type="hidden" name="status" value="active">
                  <button class="small secondary">{t['set_active']}</button>
                </form>
                """
            )
        if current_status != "archived":
            buttons.append(
                f"""
                <form method="post" action="/papers/status">
                  <input type="hidden" name="paper_id" value="{html_escape(row.get('paper_id'))}">
                  <input type="hidden" name="status" value="archived">
                  <button class="small secondary">{t['set_archived']}</button>
                </form>
                """
            )
        return "".join(buttons)

    rows = "\n".join(
        f"""
        <tr>
          <td><strong>{html_escape(row.get('title'))}</strong><span>{html_escape(row.get('doi') or t['no_doi'])}</span>{f"<i class='status-badge status-{html_escape(row.get('status') or 'active')}'>{html_escape(status_label(row.get('status')))}</i>" if is_admin else ""}</td>
          <td>{html_escape(row.get('authors') or '-')}<span>{html_escape(row.get('institutions') or '-')}</span></td>
          <td>{html_escape(row.get('venue_name') or '-')}<span>{html_escape(row.get('publish_date'))}</span></td>
          <td>{html_escape(row.get('keywords') or '-')}</td>
          <td><b>{html_escape(row.get('ref_count') or 0)}</b> {t['reference_label']} / <b>{html_escape(row.get('cited_by_count') or 0)}</b> {t['cited_by_label']}</td>
          <td>
            <div class="row-actions">
              <form method="post" action="{'/unfavorite/paper' if str(row.get('is_favorite')) == '1' else '/favorite/paper'}">
                <input type="hidden" name="paper_id" value="{html_escape(row.get('paper_id'))}">
                <button class="small secondary" title="{t['remove_paper'] if str(row.get('is_favorite')) == '1' else t['save_paper']}">{t['remove_paper'] if str(row.get('is_favorite')) == "1" else t['save_paper']}</button>
              </form>
              {f'''
              <form method="post" action="/delete/paper" onsubmit="return confirm('{t['delete_paper']}?');">
                <input type="hidden" name="paper_id" value="{html_escape(row.get('paper_id'))}">
                <button class="small danger" title="{t['delete_paper']}">{t['delete_paper']}</button>
              </form>
              ''' if is_admin else ""}
              {status_action_buttons(row)}
            </div>
          </td>
        </tr>
        """
        for row in papers
    )
    selected_keywords = set(selected_keyword_ids(query, "fav_keyword"))
    favorite_selected_keywords = set(selected_keyword_ids(query, "favorite_filter_keyword"))
    favorite_keyword_filters = "\n".join(
        f"""
        <a class="keyword-pill {'active' if int(r['keyword_id']) in selected_keywords else ''}" href="{html_escape(keyword_filter_url(query, int(r['keyword_id'])))}" aria-pressed="{'true' if int(r['keyword_id']) in selected_keywords else 'false'}">
          <span>{html_escape(r['word'])}</span>
          {f"<b>{t['active_filter']}</b>" if int(r['keyword_id']) in selected_keywords else ""}
        </a>
        """
        for r in fav["keywords"]
    )
    typed_keyword = str(query.get("keyword") or "").strip()
    search_keyword_filters = selected_keyword_words(query)
    if typed_keyword and typed_keyword not in search_keyword_filters:
        search_keyword_filters.append(typed_keyword)
    search_keyword_pills = "\n".join(
        f"""
        <a class="keyword-pill active removable" href="{html_escape(keyword_text_filter_url(query, word))}" aria-label="移除 {html_escape(word)}">
          <span>{html_escape(word)}</span><b class="pill-close">&times;</b>
        </a>
        """
        for word in search_keyword_filters
    )
    keyword_options_html = "\n".join(
        f"""<option value="{html_escape(row.get('word'))}">{html_escape(row.get('word'))} | {html_escape(row.get('paper_count') or 0)}</option>"""
        for row in keywords_available
        if row.get("word") not in search_keyword_filters
    )
    status_filter_control = (
        f"""
        <select name="status">
          <option value="">{t['status_all']}</option>
          <option value="pending" {"selected" if query.get("status") == "pending" else ""}>{t['status_pending']}</option>
          <option value="active" {"selected" if query.get("status") == "active" else ""}>{t['status_active']}</option>
          <option value="archived" {"selected" if query.get("status") == "archived" else ""}>{t['status_archived']}</option>
        </select>
        """
        if is_admin else ""
    )
    year_bars = "\n".join(
        f"<li><span>{html_escape(r['year'])}</span><i style='--w:{max(12, int(r['n']) * 28)}px'></i><b>{r['n']}</b></li>"
        for r in s["by_year"]
    )
    keyword_tags = "\n".join(
        f"""
        <form method="post" action="{'/unfavorite/keyword' if str(r.get('is_favorite')) == '1' else '/favorite/keyword'}" class="keyword-action">
          <input type="hidden" name="word" value="{html_escape(r['word'])}">
          <input type="hidden" name="keyword_id" value="{html_escape(r.get('keyword_id'))}">
          <button class="tag {'selected' if str(r.get('is_favorite')) == '1' else ''}" title="{t['remove_keyword'] if str(r.get('is_favorite')) == '1' else t['favorite_keyword']}">{html_escape(r['word'])}<b>{r['n']}</b></button>
        </form>
        """
        for r in s["hot_keywords"]
    )
    favorite_papers = "\n".join(
        f"""
        <li>
          <strong>{html_escape(r['title'])}</strong>
          <span>{html_escape(r.get('doi') or r.get('publish_date') or '')}</span>
          <span>{html_escape(r.get('keywords') or '')}</span>
          <form method="post" action="/unfavorite/paper">
            <input type="hidden" name="paper_id" value="{html_escape(r['paper_id'])}">
            <button class="small secondary">{t['remove_paper']}</button>
          </form>
        </li>
        """
        for r in fav["papers"]
    )
    favorite_keywords = "\n".join(
        f"""
        <div class="favorite-keyword-row">
          <a class="keyword-pill {'active' if int(r['keyword_id']) in favorite_selected_keywords else ''}" href="{html_escape(keyword_filter_url(query, int(r['keyword_id']), 'favorite_filter_keyword', 'favorites'))}" aria-pressed="{'true' if int(r['keyword_id']) in favorite_selected_keywords else 'false'}">
            <span>{html_escape(r['word'])}</span>
            {f"<b>{t['active_filter']}</b>" if int(r['keyword_id']) in favorite_selected_keywords else ""}
          </a>
          <form method="post" action="/unfavorite/keyword">
            <input type="hidden" name="keyword_id" value="{html_escape(r['keyword_id'])}">
            <button class="icon-button" title="{t['remove_keyword']}" aria-label="{t['remove_keyword']}">x</button>
          </form>
        </div>
        """
        for r in fav["keywords"]
    )
    keyword_lookup_hidden = "".join(
        f'<input type="hidden" name="fav_keyword" value="{html_escape(item)}">'
        for item in selected_keyword_ids(query, "fav_keyword")
    ) + "".join(
        f'<input type="hidden" name="favorite_filter_keyword" value="{html_escape(item)}">'
        for item in selected_keyword_ids(query, "favorite_filter_keyword")
    )
    keyword_lookup_results = "\n".join(
        f"""
        <form method="post" action="{'/unfavorite/keyword' if str(r.get('is_favorite')) == '1' else '/favorite/keyword'}" class="keyword-action">
          <input type="hidden" name="keyword_id" value="{html_escape(r['keyword_id'])}">
          <button class="tag {'selected' if str(r.get('is_favorite')) == '1' else ''}" title="{t['remove_keyword'] if str(r.get('is_favorite')) == '1' else t['favorite_keyword']}">
            {html_escape(r['word'])}<b>{html_escape(r.get('paper_count') or 0)}</b>
          </button>
        </form>
        """
        for r in fav.get("keyword_lookup", [])
    )
    batch_items = []
    for idx, item in enumerate(batch_drafts):
        item_type = item.get("venue_type") or "journal"
        if item_type not in {"journal", "conference", "preprint", "other"}:
            item_type = "other"
        batch_items.append(
            f"""
            <div class="batch-paper">
              <input type="hidden" name="pdf_path_{idx}" value="{html_escape(item.get('pdf_path', ''))}">
              <p class="inline-note">{t['source_file']}：{html_escape(item.get('source_filename') or item.get('pdf_path') or '')}</p>
              {f"<p class='inline-note'>{t['parsed_authors']}：{html_escape(item.get('authors'))}</p>" if item.get('authors') else ""}
              <label>{t['title']}<input name="title_{idx}" value="{html_escape(item.get('title', ''))}" required></label>
              <label>{t['abstract']}<textarea name="abstract_{idx}" rows="3" placeholder="{t['abstract_placeholder']}">{html_escape(item.get('abstract', ''))}</textarea></label>
              <div class="two">
                <label>{t['publish_date']}<input type="date" name="publish_date_{idx}" value="{html_escape(item.get('publish_date') or date.today().isoformat())}" required></label>
                <label>{t['doi']}<input name="doi_{idx}" value="{html_escape(item.get('doi', ''))}" placeholder="{t['doi_placeholder']}" required></label>
              </div>
              <div class="two">
                <label>{t['venue']}<input name="venue_name_{idx}" value="{html_escape(item.get('venue_name', ''))}"></label>
                <label>{t['type']}<select name="venue_type_{idx}"><option value="journal" {"selected" if item_type == "journal" else ""}>journal</option><option value="conference" {"selected" if item_type == "conference" else ""}>conference</option><option value="preprint" {"selected" if item_type == "preprint" else ""}>preprint</option><option value="other" {"selected" if item_type == "other" else ""}>other</option></select></label>
              </div>
              {author_select_html(f"author_ids_{idx}", set(safe_author_ids_by_names(item.get("authors", ""))))}
              {keyword_token_html(f"keywords_{idx}", item.get('keywords', ''))}
            </div>
            """
        )
    batch_review = (
        f"""
        <section id="batch-review" class="panel batch-review">
          <h3>{t['batch_review_title']}</h3>
          <form method="post" action="/papers/batch">
            <input type="hidden" name="count" value="{len(batch_drafts)}">
            {''.join(batch_items)}
            <button>{t['save_batch_mysql']}</button>
          </form>
        </section>
        """
        if batch_drafts else ""
    )
    current_name = html_escape(username or APP_USER)
    scroll_script = (
        "<script>window.addEventListener('load',function(){"
        f"var el=document.getElementById('{html_escape(scroll_to)}');"
        "if(el){el.scrollIntoView({block:'start'});}"
        "});</script>"
        if scroll_to else ""
    )
    author_filter_script = """
<script>
var authorSearchTimers = new WeakMap();
var keywordSearchTimers = new WeakMap();
function selectedTokenValues(picker) {
  var values = {};
  Array.prototype.forEach.call(picker.querySelectorAll('[data-token-list] .choice-chip'), function (chip) {
    values[chip.getAttribute('data-value')] = true;
  });
  return values;
}
function addToken(picker, value, label) {
  var hiddenName = picker.getAttribute('data-hidden-name');
  var list = picker.querySelector('[data-token-list]');
  if (!hiddenName || !list || !value || selectedTokenValues(picker)[value]) return;
  var chip = document.createElement('span');
  chip.className = 'choice-chip';
  chip.setAttribute('data-value', value);
  chip.innerHTML = '<span></span><button type="button" class="choice-chip-close" aria-label="remove">&times;</button>';
  chip.querySelector('span').textContent = label || value;
  var hidden = document.createElement('input');
  hidden.type = 'hidden';
  hidden.name = hiddenName;
  hidden.value = value;
  chip.appendChild(hidden);
  list.appendChild(chip);
}
function syncTokenOptions(select, items, valueKey) {
  var picker = select.closest('[data-token-picker]');
  var selected = picker ? selectedTokenValues(picker) : {};
  select.innerHTML = '';
  items.forEach(function (item) {
    var value = String(item[valueKey]);
    if (selected[value]) return;
    var option = document.createElement('option');
    option.value = value;
    option.textContent = item.label;
    option.setAttribute('data-label', item.label);
    select.appendChild(option);
  });
}
document.addEventListener('input', function (event) {
  var input = event.target.closest('[data-author-filter]');
  if (!input) return;
  var picker = input.closest('[data-token-picker]');
  var select = picker ? picker.querySelector('[data-token-select]') : null;
  if (!select) return;
  var term = input.value.trim().toLowerCase();
  clearTimeout(authorSearchTimers.get(input));
  authorSearchTimers.set(input, setTimeout(function () {
    fetch('/api/authors?q=' + encodeURIComponent(term))
      .then(function (response) { return response.json(); })
      .then(function (authors) { syncTokenOptions(select, authors, 'author_id'); });
  }, 180));
});
document.addEventListener('change', function (event) {
  var select = event.target.closest('[data-token-select]');
  if (!select || !select.value) return;
  var picker = select.closest('[data-token-picker]');
  if (!picker) return;
  var option = select.options[select.selectedIndex];
  addToken(picker, select.value, option ? option.getAttribute('data-label') || option.textContent : select.value);
  if (option) option.remove();
  select.value = '';
  var input = picker.querySelector('input[type="search"]');
  if (input) input.value = '';
});
function addFreeKeyword(buttonOrInput) {
  var picker = buttonOrInput.closest('[data-token-picker="keyword"]');
  if (!picker) return;
  var input = picker.querySelector('[data-free-keyword-input]');
  if (!input) return;
  var value = input.value.trim();
  if (!value) return;
  addToken(picker, value, value);
  input.value = '';
}
document.addEventListener('click', function (event) {
  var button = event.target.closest('[data-free-keyword-add]');
  if (!button) return;
  addFreeKeyword(button);
});
document.addEventListener('keydown', function (event) {
  var input = event.target.closest('[data-free-keyword-input]');
  if (!input || event.key !== 'Enter') return;
  event.preventDefault();
  addFreeKeyword(input);
});
document.addEventListener('click', function (event) {
  var close = event.target.closest('.choice-chip-close');
  if (!close) return;
  close.closest('.choice-chip').remove();
});
document.addEventListener('input', function (event) {
  var input = event.target.closest('[data-keyword-filter]');
  if (!input) return;
  var box = input.closest('.keyword-select-box');
  var select = box ? box.querySelector('[data-keyword-select]') : null;
  if (!select) return;
  var term = input.value.trim().toLowerCase();
  clearTimeout(keywordSearchTimers.get(input));
  keywordSearchTimers.set(input, setTimeout(function () {
    fetch('/api/keywords?q=' + encodeURIComponent(term))
      .then(function (response) { return response.json(); })
      .then(function (keywords) {
        select.innerHTML = '';
        var empty = document.createElement('option');
        empty.value = '';
        empty.textContent = '--';
        select.appendChild(empty);
        keywords.forEach(function (item) {
          var option = document.createElement('option');
          option.value = item.word;
          option.textContent = item.label;
          select.appendChild(option);
        });
      });
  }, 180));
});
document.addEventListener('change', function (event) {
  var select = event.target.closest('[data-keyword-select]');
  if (!select || !select.value) return;
  var form = select.closest('form');
  if (!form) return;
  var selectedWord = select.value;
  var exists = Array.prototype.some.call(
    form.querySelectorAll('input[name="keyword_filter"]'),
    function (input) { return input.value === selectedWord; }
  );
  if (!exists) {
    var hidden = document.createElement('input');
    hidden.type = 'hidden';
    hidden.name = 'keyword_filter';
    hidden.value = selectedWord;
    form.appendChild(hidden);
  }
  select.value = '';
  var keywordField = form.querySelector('select[name="keyword"]');
  if (keywordField) keywordField.name = '';
  if (form.requestSubmit) {
    form.requestSubmit();
  } else {
    form.submit();
  }
});
</script>
"""
    html = f"""<!doctype html>
<html lang="{html_escape(pref['language'])}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{t['app_title']}</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <aside>
    <h1>{t['app_title']}</h1>
    <p>{t['subtitle']}</p>
    <nav>
      <a href="#search">{t['search']}</a>
      <a href="#add">{t['add']}</a>
      <a href="#analytics">{t['analytics']}</a>
      <a href="#favorites">{t['favorites']}</a>
      <a href="#settings">{t['settings']}</a>
      <a href="/export/json">{t['export_json']}</a>
      <a href="/export/csv">{t['export_csv']}</a>
      <a href="/logout">{t['logout']}</a>
    </nav>
    <p class="signed-in">{current_name}</p>
  </aside>
  <main>
    <section class="hero">
      <div>
        <h2>{t['hero_title']}</h2>
        <p>{t['hero_body']}</p>
      </div>
      <div class="metrics">
        <div><strong>{s['papers']}</strong><span>{t['papers']}</span></div>
        <div><strong>{s['authors']}</strong><span>{t['authors']}</span></div>
        <div><strong>{s['keywords']}</strong><span>{t['keywords']}</span></div>
        <div><strong>{s['citations']}</strong><span>{t['citations']}</span></div>
      </div>
    </section>
    {f"<p class='message'>{html_escape(message)}</p>" if message else ""}
    {f"<p class='message'>{html_escape(t['db_error'].format(error=db_error))}</p>" if db_error else ""}
    <section id="search" class="panel">
      <form class="search" method="get" action="/#search">
        <input name="q" placeholder="{t['query_placeholder']}" value="{html_escape(query.get('q',''))}">
        <input name="year" placeholder="{t['year']}" value="{html_escape(query.get('year',''))}">
        <input name="year_from" placeholder="{t['year_from']}" value="{html_escape(query.get('year_from',''))}">
        <input name="year_to" placeholder="{t['year_to']}" value="{html_escape(query.get('year_to',''))}">
        {status_filter_control}
        <div class="keyword-select-box">
          <input type="search" class="keyword-filter-input" placeholder="{t['keyword']}" data-keyword-filter>
          <select name="keyword" data-keyword-select>
            <option value="">-- {t['keyword']} --</option>
            {keyword_options_html}
          </select>
        </div>
        <input name="institution" placeholder="{t['institution']}" value="{html_escape(query.get('institution',''))}">
        {''.join(f'<input type="hidden" name="fav_keyword" value="{html_escape(item)}">' for item in selected_keyword_ids(query))}
        {''.join(f'<input type="hidden" name="keyword_filter" value="{html_escape(word)}">' for word in search_keyword_filters)}
        <button>{t['combined_search']}</button>
      </form>
      <div class="filter-strip">
        <span>{t['keyword']}</span>
        <div>{search_keyword_pills or f"<span class='muted'>{t['none']}</span>"}</div>
      </div>
      <div class="filter-strip">
        <span>{t['favorite_keywords']}</span>
        <div>{favorite_keyword_filters or f"<span class='muted'>{t['empty_favorites']}</span>"}</div>
      </div>
      <table>
        <thead><tr><th>{t['paper']}</th><th>{t['authors']}</th><th>{t['source']}</th><th>{t['keywords']}</th><th>{t['relation']}</th><th>{t['action']}</th></tr></thead>
        <tbody>{rows or f"<tr><td colspan='6'>{t['no_records']}</td></tr>"}</tbody>
      </table>
    </section>
    <section id="add" class="grid">
      <form class="panel" method="post" action="/papers">
        <h3>{t['new_paper']}</h3>
        {pdf_draft_note}
        {parsed_author_note}
        <input type="hidden" name="pdf_path" value="{html_escape(draft.get('pdf_path', ''))}">
        <label>{t['title']}<input name="title" value="{html_escape(draft.get('title', ''))}" required></label>
        <label>{t['abstract']}<textarea name="abstract" rows="3" placeholder="{t['abstract_placeholder']}">{html_escape(draft.get('abstract', ''))}</textarea></label>
        <div class="two">
          <label>{t['publish_date']}<input type="date" name="publish_date" value="{html_escape(draft.get('publish_date') or date.today().isoformat())}" required></label>
          <label>{t['doi']}<input name="doi" value="{html_escape(draft.get('doi', ''))}" placeholder="{t['doi_placeholder']}" required></label>
        </div>
        <div class="two">
          <label>{t['venue']}<input name="venue_name" value="{html_escape(draft.get('venue_name', ''))}"></label>
          <label>{t['type']}<select name="venue_type"><option value="journal" {"selected" if draft_type == "journal" else ""}>journal</option><option value="conference" {"selected" if draft_type == "conference" else ""}>conference</option><option value="preprint" {"selected" if draft_type == "preprint" else ""}>preprint</option><option value="other" {"selected" if draft_type == "other" else ""}>other</option></select></label>
        </div>
        {author_select_html("author_ids", main_selected_author_ids)}
        {keyword_token_html("keywords", draft.get('keywords', ''))}
        <button>{t['save_mysql']}</button>
      </form>
      <form class="panel compact-panel" method="post" action="/authors">
        <h3>{t['add_author']}</h3>
        <label>{t['author_name']}<input name="name" required></label>
        <label>{t['author_email']}<input type="email" name="email"></label>
        <label>{t['author_orcid']}<input name="orcid_id" placeholder="0000-0000-0000-0000" required></label>
        <button class="secondary">{t['save_author']}</button>
      </form>
      <form class="panel" method="post" action="/import/csv" enctype="multipart/form-data">
        <h3>{t['batch_import']}</h3>
        <p>{t['csv_tip']}</p>
        <label class="file-upload">
          <input id="csv-file" type="file" name="file" accept=".csv" required>
          <span>{t['choose_csv_file']}</span>
        </label>
        <button>{t['import_csv']}</button>
      </form>
      <form class="panel" method="post" action="/upload/pdf" enctype="multipart/form-data">
        <h3>{t['pdf_upload']}</h3>
        <p>{t['pdf_tip']}</p>
        <label class="file-upload">
          <input id="pdf-file" type="file" name="file" accept=".pdf,application/pdf" required>
          <span>{t['choose_pdf_file']}</span>
        </label>
        <button>{t['upload_pdf']}</button>
      </form>
      <form class="panel" method="post" action="/upload/pdfs" enctype="multipart/form-data">
        <h3>{t['batch_pdf_upload']}</h3>
        <p>{t['batch_pdf_tip']}</p>
        <label class="file-upload">
          <input id="pdf-files" type="file" name="file" accept=".pdf,application/pdf" multiple required>
          <span>{t['choose_pdf_files']}</span>
        </label>
        <button>{t['upload_pdfs']}</button>
      </form>
    </section>
    {batch_review}
    <section id="analytics" class="panel analytics">
      <h3>{t['data_analysis']}</h3>
      <div class="analytics-grid">
        <div><h4>{t['year_dist']}</h4><ul class="bars">{year_bars}</ul></div>
        <div><h4>{t['hot_keywords']}</h4><div class="tags">{keyword_tags}</div></div>
      </div>
    </section>
    <section id="favorites" class="panel analytics">
      <h3>{t['my_favorites']}</h3>
      <div class="keyword-lookup">
        <form class="keyword-lookup-form" method="get" action="/#favorites">
          <input name="keyword_lookup" placeholder="{t['keyword_lookup_placeholder']}" value="{html_escape(query.get('keyword_lookup', ''))}">
          {keyword_lookup_hidden}
          <button>{t['keyword_lookup']}</button>
        </form>
        <div class="lookup-results">
          <span>{t['keyword_results']}</span>
          <div>{keyword_lookup_results or f"<span class='muted'>{t['empty_favorites']}</span>"}</div>
        </div>
      </div>
      <div class="analytics-grid">
        <div><h4>{t['favorite_keywords']}</h4><div class="favorite-keywords">{favorite_keywords or f"<span class='muted'>{t['empty_favorites']}</span>"}</div></div>
        <div><h4>{t['favorite_papers']}</h4><ul class="favorite-list">{favorite_papers or f"<li>{t['empty_favorites']}</li>"}</ul></div>
      </div>
    </section>
    <section id="settings" class="panel">
      <h3>{t['settings_title']}</h3>
      <form class="settings-form" method="post" action="/settings">
        <label>{t['language']}
          <select name="language">
            <option value="zh" {"selected" if pref["language"] == "zh" else ""}>中文</option>
            <option value="en" {"selected" if pref["language"] == "en" else ""}>English</option>
          </select>
        </label>
        <button>{t['save_settings']}</button>
      </form>
    </section>
  </main>
  {scroll_script}
  {author_filter_script}
</body>
</html>"""
    return html.encode("utf-8")


def render_paper_edit(paper_id: int, username: str, message: str = "") -> bytes:
    user_id = current_user_id(username)
    pref = preferences(user_id)
    t = TEXT[pref["language"]]
    message = translate_message(message, pref["language"])
    paper = paper_edit_data(paper_id)
    selected_author_ids = set(selected_int_values(paper, "author_ids"))
    authors_available = author_options("")
    combined_authors = list(authors_available)
    existing_ids = {int(row["author_id"]) for row in combined_authors}
    for row in authors_by_ids(selected_author_ids):
        if int(row["author_id"]) not in existing_ids:
            combined_authors.append(row)
            existing_ids.add(int(row["author_id"]))
    combined_authors.sort(key=lambda row: (str(row.get("name") or ""), int(row["author_id"])))
    author_options_html = "\n".join(
        f"""<option value="{html_escape(row['author_id'])}" data-label="{html_escape(row.get('name'))}{' | ORCID: ' + html_escape(row.get('orcid_id')) if row.get('orcid_id') else ''}{' | ' + html_escape(row.get('email')) if row.get('email') else ''}">{html_escape(row.get('name'))}{' | ORCID: ' + html_escape(row.get('orcid_id')) if row.get('orcid_id') else ''}{' | ' + html_escape(row.get('email')) if row.get('email') else ''}</option>"""
        for row in combined_authors
        if int(row["author_id"]) not in selected_author_ids
    )
    author_chips_html = "\n".join(
        f"""
        <span class="choice-chip" data-value="{html_escape(row['author_id'])}">
          <span>{html_escape(row.get('name'))}{' | ORCID: ' + html_escape(row.get('orcid_id')) if row.get('orcid_id') else ''}{' | ' + html_escape(row.get('email')) if row.get('email') else ''}</span>
          <button type="button" class="choice-chip-close" aria-label="remove">&times;</button>
          <input type="hidden" name="author_ids" value="{html_escape(row['author_id'])}">
        </span>
        """
        for row in combined_authors
        if int(row["author_id"]) in selected_author_ids
    )
    keyword_chips_html = "\n".join(
        f"""
        <span class="choice-chip" data-value="{html_escape(word)}">
          <span>{html_escape(word)}</span>
          <button type="button" class="choice-chip-close" aria-label="remove">&times;</button>
          <input type="hidden" name="keywords" value="{html_escape(word)}">
        </span>
        """
        for word in split_values(paper.get("keywords") or "")
    )
    paper_type = str(paper.get("venue_type") or "other")
    if paper_type not in {"journal", "conference", "preprint", "other"}:
        paper_type = "other"
    message_html = f"<div class='message'>{html_escape(message)}</div>" if message else ""
    html = f"""<!doctype html>
<html lang="{html_escape(pref['language'])}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{t['edit_paper_title']} - {t['app_title']}</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body class="plain-page">
  <main class="single-page">
    <section class="edit-layout">
      <form class="panel" method="post" action="/papers/update">
        <h3>{t['edit_paper_title']}</h3>
        {message_html}
        <input type="hidden" name="paper_id" value="{html_escape(paper.get('paper_id'))}">
        <input type="hidden" name="pdf_path" value="{html_escape(paper.get('pdf_path') or '')}">
        <label>{t['title']}<input name="title" value="{html_escape(paper.get('title') or '')}" required></label>
        <label>{t['abstract']}<textarea name="abstract" rows="4" placeholder="{t['abstract_placeholder']}">{html_escape(paper.get('abstract') or '')}</textarea></label>
        <div class="two">
          <label>{t['publish_date']}<input type="date" name="publish_date" value="{html_escape(paper.get('publish_date') or date.today().isoformat())}" required></label>
          <label>{t['doi']}<input name="doi" value="{html_escape(paper.get('doi') or '')}" placeholder="{t['doi_placeholder']}" required></label>
        </div>
        <div class="two">
          <label>{t['venue']}<input name="venue_name" value="{html_escape(paper.get('venue_name') or '')}"></label>
          <label>{t['type']}<select name="venue_type"><option value="journal" {"selected" if paper_type == "journal" else ""}>journal</option><option value="conference" {"selected" if paper_type == "conference" else ""}>conference</option><option value="preprint" {"selected" if paper_type == "preprint" else ""}>preprint</option><option value="other" {"selected" if paper_type == "other" else ""}>other</option></select></label>
        </div>
        <label class="token-picker" data-token-picker="author" data-hidden-name="author_ids">{t['author_select']}
          <input type="search" class="author-filter" placeholder="{t['author_lookup_placeholder']}" data-author-filter>
          <select data-token-select size="8">
            {author_options_html}
          </select>
          <div class="choice-chip-list" data-token-list>{author_chips_html}</div>
        </label>
        <p class="field-help">{t['author_required_tip']}</p>
        <label class="token-picker" data-token-picker="keyword" data-hidden-name="keywords">{t['keywords']}
          <div class="token-add-row">
            <input type="text" class="keyword-filter-input" placeholder="{t['keywords_placeholder']}" data-free-keyword-input>
            <button type="button" class="small secondary" data-free-keyword-add>{t['add_keyword']}</button>
          </div>
          <div class="choice-chip-list" data-token-list>{keyword_chips_html}</div>
        </label>
        <div class="row-actions">
          <button>{t['publish_updated_paper']}</button>
          <a class="button-link secondary" href="/#search">{t['return_to_search']}</a>
        </div>
      </form>
      <form class="panel compact-panel" method="post" action="/authors">
        <h3>{t['add_author']}</h3>
        <input type="hidden" name="return_edit_paper_id" value="{html_escape(paper.get('paper_id'))}">
        <label>{t['author_name']}<input name="name" required></label>
        <label>{t['author_email']}<input type="email" name="email"></label>
        <label>{t['author_orcid']}<input name="orcid_id" placeholder="0000-0000-0000-0000" required></label>
        <button>{t['save_author']}</button>
      </form>
    </section>
  </main>
  <script>
var authorSearchTimers = new WeakMap();
function selectedTokenValues(picker) {{
  var values = {{}};
  Array.prototype.forEach.call(picker.querySelectorAll('[data-token-list] .choice-chip'), function (chip) {{
    values[chip.getAttribute('data-value')] = true;
  }});
  return values;
}}
function addToken(picker, value, label) {{
  var hiddenName = picker.getAttribute('data-hidden-name');
  var list = picker.querySelector('[data-token-list]');
  if (!hiddenName || !list || !value || selectedTokenValues(picker)[value]) return;
  var chip = document.createElement('span');
  chip.className = 'choice-chip';
  chip.setAttribute('data-value', value);
  chip.innerHTML = '<span></span><button type="button" class="choice-chip-close" aria-label="remove">&times;</button>';
  chip.querySelector('span').textContent = label || value;
  var hidden = document.createElement('input');
  hidden.type = 'hidden';
  hidden.name = hiddenName;
  hidden.value = value;
  chip.appendChild(hidden);
  list.appendChild(chip);
}}
function syncTokenOptions(select, items, valueKey) {{
  var picker = select.closest('[data-token-picker]');
  var selected = picker ? selectedTokenValues(picker) : {{}};
  select.innerHTML = '';
  items.forEach(function (item) {{
    var value = String(item[valueKey]);
    if (selected[value]) return;
    var option = document.createElement('option');
    option.value = value;
    option.textContent = item.label;
    option.setAttribute('data-label', item.label);
    select.appendChild(option);
  }});
}}
document.addEventListener('input', function (event) {{
  var input = event.target.closest('[data-author-filter]');
  if (!input) return;
  var picker = input.closest('[data-token-picker]');
  var select = picker ? picker.querySelector('[data-token-select]') : null;
  if (!select) return;
  var term = input.value.trim().toLowerCase();
  clearTimeout(authorSearchTimers.get(input));
  authorSearchTimers.set(input, setTimeout(function () {{
    fetch('/api/authors?q=' + encodeURIComponent(term))
      .then(function (response) {{ return response.json(); }})
      .then(function (authors) {{ syncTokenOptions(select, authors, 'author_id'); }});
  }}, 180));
}});
document.addEventListener('change', function (event) {{
  var select = event.target.closest('[data-token-select]');
  if (!select || !select.value) return;
  var picker = select.closest('[data-token-picker]');
  if (!picker) return;
  var option = select.options[select.selectedIndex];
  addToken(picker, select.value, option ? option.getAttribute('data-label') || option.textContent : select.value);
  if (option) option.remove();
  select.value = '';
  var input = picker.querySelector('input[type="search"]');
  if (input) input.value = '';
}});
function addFreeKeyword(buttonOrInput) {{
  var picker = buttonOrInput.closest('[data-token-picker="keyword"]');
  if (!picker) return;
  var input = picker.querySelector('[data-free-keyword-input]');
  if (!input) return;
  var value = input.value.trim();
  if (!value) return;
  addToken(picker, value, value);
  input.value = '';
}}
document.addEventListener('click', function (event) {{
  var button = event.target.closest('[data-free-keyword-add]');
  if (!button) return;
  addFreeKeyword(button);
}});
document.addEventListener('keydown', function (event) {{
  var input = event.target.closest('[data-free-keyword-input]');
  if (!input || event.key !== 'Enter') return;
  event.preventDefault();
  addFreeKeyword(input);
}});
document.addEventListener('click', function (event) {{
  var close = event.target.closest('.choice-chip-close');
  if (!close) return;
  close.closest('.choice-chip').remove();
}});
  </script>
</body>
</html>"""
    return html.encode("utf-8")


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        if path.startswith("/static/"):
            return str(STATIC_DIR / path.removeprefix("/static/"))
        return str(BASE_DIR)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            username = self.current_username()
            if not username:
                self.redirect("/login?msg=" + urllib.parse.quote("请先登录"))
                return
            query = parse_query(parsed.query)
            message = query.pop("msg", "")
            self.send_html(render_index(message=message, query=query, username=username))
        elif parsed.path == "/login":
            query = parse_query(parsed.query)
            self.send_html(render_login(query.get("msg", "")))
        elif parsed.path == "/register":
            query = parse_query(parsed.query)
            self.send_html(render_register(query.get("msg", "")))
        elif parsed.path == "/papers/edit":
            username = self.current_username()
            if not username:
                self.redirect("/login?msg=" + urllib.parse.quote("请先登录"))
                return
            if current_user_role(username) != "admin":
                self.send_error(HTTPStatus.FORBIDDEN)
                return
            query = parse_query(parsed.query)
            try:
                paper_id = int(query.get("paper_id") or 0)
                self.send_html(render_paper_edit(paper_id, username, str(query.get("msg") or "")))
            except Exception as exc:
                self.send_html(render_index(f"打开修改页面失败：{exc}", username=username, scroll_to="search"), status=HTTPStatus.BAD_REQUEST)
        elif parsed.path == "/logout":
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", "/login")
            self.send_header("Set-Cookie", clear_login_cookie_header())
            self.end_headers()
        elif parsed.path == "/export/json":
            if not self.current_username():
                self.redirect("/login?msg=" + urllib.parse.quote("请先登录"))
                return
            self.export_json()
        elif parsed.path == "/export/csv":
            if not self.current_username():
                self.redirect("/login?msg=" + urllib.parse.quote("请先登录"))
                return
            self.export_csv()
        elif parsed.path == "/api/authors":
            if not self.current_username():
                self.send_error(HTTPStatus.UNAUTHORIZED)
                return
            query = parse_query(parsed.query)
            self.api_authors(str(query.get("q") or ""))
        elif parsed.path == "/api/keywords":
            if not self.current_username():
                self.send_error(HTTPStatus.UNAUTHORIZED)
                return
            query = parse_query(parsed.query)
            self.api_keywords(str(query.get("q") or ""))
        else:
            super().do_GET()

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/login":
            data = self.read_form()
            user = authenticate_user(data.get("username", "").strip(), data.get("password", ""))
            if user:
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header("Location", "/")
                self.send_header("Set-Cookie", login_cookie_header(str(user["username"])))
                self.end_headers()
            else:
                self.send_html(render_login("登录失败：用户名或密码错误"), status=HTTPStatus.UNAUTHORIZED)
            return
        if parsed.path == "/register":
            data = self.read_form()
            try:
                register_user(data.get("username", ""), data.get("password", ""), data.get("email", ""))
                self.redirect("/login?msg=" + urllib.parse.quote("注册成功，请登录"))
            except Exception as exc:
                self.send_html(render_register(f"注册失败：{exc}"), status=HTTPStatus.BAD_REQUEST)
            return

        username = self.current_username()
        if not username:
            self.redirect("/login?msg=" + urllib.parse.quote("请先登录"))
            return

        if parsed.path == "/papers":
            data = self.read_form()
            try:
                data["status"] = "active" if current_user_role(username) == "admin" else "pending"
                create_paper(data, current_user_id(username))
                self.redirect_with_msg("文献已保存到 MySQL", "add")
            except Exception as exc:
                self.send_html(render_index(f"保存失败：{exc}", username=username, scroll_to="add"), status=HTTPStatus.BAD_REQUEST)
        elif parsed.path == "/papers/update":
            data = self.read_form()
            try:
                if current_user_role(username) != "admin":
                    raise PermissionError("仅管理员可以修改论文")
                paper_id = int(data.get("paper_id") or 0)
                update_paper(paper_id, data, current_user_id(username))
                self.redirect_with_msg("论文已修改并发布", "search")
            except Exception as exc:
                paper_id = int(data.get("paper_id") or 0) if str(data.get("paper_id") or "").isdigit() else 0
                if paper_id:
                    self.send_html(render_paper_edit(paper_id, username, f"修改失败：{exc}"), status=HTTPStatus.BAD_REQUEST)
                else:
                    self.send_html(render_index(f"修改失败：{exc}", username=username, scroll_to="search"), status=HTTPStatus.BAD_REQUEST)
        elif parsed.path == "/authors":
            data = self.read_form()
            return_edit_paper_id = int(data.get("return_edit_paper_id") or 0) if str(data.get("return_edit_paper_id") or "").isdigit() else 0
            try:
                create_author(data)
                if return_edit_paper_id:
                    self.redirect(
                        "/papers/edit?paper_id="
                        + str(return_edit_paper_id)
                        + "&msg="
                        + urllib.parse.quote("作者已添加，请在作者列表中选择")
                    )
                else:
                    self.redirect_with_msg("作者已添加，请在作者列表中选择", "add")
            except Exception as exc:
                if return_edit_paper_id:
                    self.send_html(
                        render_paper_edit(return_edit_paper_id, username, f"添加作者失败：{exc}"),
                        status=HTTPStatus.BAD_REQUEST,
                    )
                else:
                    self.send_html(render_index(f"添加作者失败：{exc}", username=username, scroll_to="add"), status=HTTPStatus.BAD_REQUEST)
        elif parsed.path == "/papers/batch":
            self.save_batch_papers(username)
        elif parsed.path == "/import/csv":
            self.import_csv(username)
        elif parsed.path == "/upload/pdf":
            self.upload_pdf(username)
        elif parsed.path == "/upload/pdfs":
            self.upload_pdfs(username)
        elif parsed.path == "/settings":
            data = self.read_form()
            try:
                update_preferences(current_user_id(username), data)
                self.redirect_with_msg("设置已保存", "settings")
            except Exception as exc:
                self.send_html(render_index(f"设置保存失败：{exc}", username=username, scroll_to="settings"), status=HTTPStatus.BAD_REQUEST)
        elif parsed.path == "/favorite/paper":
            data = self.read_form()
            try:
                favorite_paper(current_user_id(username), int(data.get("paper_id") or 0))
                self.redirect_with_msg("论文已收藏", "search")
            except Exception as exc:
                self.send_html(render_index(f"收藏失败：{exc}", username=username, scroll_to="search"), status=HTTPStatus.BAD_REQUEST)
        elif parsed.path == "/unfavorite/paper":
            data = self.read_form()
            try:
                unfavorite_paper(current_user_id(username), int(data.get("paper_id") or 0))
                self.redirect_with_msg("已取消收藏论文", "favorites")
            except Exception as exc:
                self.send_html(render_index(f"取消收藏失败：{exc}", username=username, scroll_to="favorites"), status=HTTPStatus.BAD_REQUEST)
        elif parsed.path == "/delete/paper":
            data = self.read_form()
            try:
                if current_user_role(username) != "admin":
                    raise PermissionError("仅管理员可以删除论文")
                delete_paper(int(data.get("paper_id") or 0))
                self.redirect_with_msg("论文已删除", "search")
            except Exception as exc:
                self.send_html(render_index(f"删除失败：{exc}", username=username, scroll_to="search"), status=HTTPStatus.FORBIDDEN)
        elif parsed.path == "/papers/status":
            data = self.read_form()
            try:
                if current_user_role(username) != "admin":
                    raise PermissionError("仅管理员可以修改论文状态")
                paper_id = int(data.get("paper_id") or 0)
                target_status = str(data.get("status") or "")
                current_rows = run_sql(f"SELECT status FROM paper WHERE paper_id = {paper_id} LIMIT 1;")
                current_status = str(current_rows[0]["status"]) if current_rows else ""
                if target_status == "pending":
                    raise ValueError("已审核论文不需要重新设为待审核")
                if target_status == "active" and current_status not in {"pending", "archived"}:
                    raise ValueError("只有待审核或已归档论文可以发布")
                update_paper_status(paper_id, target_status)
                self.redirect_with_msg("论文状态已更新", "search")
            except Exception as exc:
                self.send_html(render_index(f"状态更新失败：{exc}", username=username, scroll_to="search"), status=HTTPStatus.FORBIDDEN)
        elif parsed.path == "/favorite/keyword":
            data = self.read_form()
            try:
                favorite_keyword(
                    current_user_id(username),
                    data.get("word", ""),
                    int(data.get("keyword_id") or 0),
                )
                self.redirect_with_msg("关键词已收藏", "favorites")
            except Exception as exc:
                self.send_html(render_index(f"收藏失败：{exc}", username=username, scroll_to="favorites"), status=HTTPStatus.BAD_REQUEST)
        elif parsed.path == "/unfavorite/keyword":
            data = self.read_form()
            try:
                unfavorite_keyword(current_user_id(username), int(data.get("keyword_id") or 0))
                self.redirect_with_msg("已取消收藏关键词", "favorites")
            except Exception as exc:
                self.send_html(render_index(f"取消收藏失败：{exc}", username=username, scroll_to="favorites"), status=HTTPStatus.BAD_REQUEST)
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def current_username(self) -> str:
        username = login_cookie_username(self.headers)
        if not username:
            return ""
        rows = run_sql(f"SELECT username FROM sys_user WHERE username = {quote(username)} LIMIT 1;")
        return str(rows[0]["username"]) if rows else ""

    def read_form(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        parsed = urllib.parse.parse_qs(body)
        return {
            key: values if key in {"author_ids", "keywords"} or key.startswith("author_ids_") or key.startswith("keywords_") else values[0]
            for key, values in parsed.items()
        }

    def read_multipart_file(self, field_name: str = "file") -> tuple[str, bytes]:
        files = self.read_multipart_files(field_name)
        if not files:
            raise ValueError("未找到上传文件")
        return files[0]

    def read_multipart_files(self, field_name: str = "file") -> list[tuple[str, bytes]]:
        length = int(self.headers.get("Content-Length", 0))
        content_type = self.headers.get("Content-Type", "")
        body = self.rfile.read(length)
        if "multipart/form-data" not in content_type or "boundary=" not in content_type:
            raise ValueError("需要 multipart/form-data")
        boundary = content_type.split("boundary=", 1)[-1].strip().strip('"').encode()
        files: list[tuple[str, bytes]] = []
        for part in body.split(b"--" + boundary):
            header, _, content = part.partition(b"\r\n\r\n")
            if not content or f'name="{field_name}"'.encode() not in header:
                continue
            filename_match = re.search(rb'filename="([^"]*)"', header)
            filename = filename_match.group(1).decode("utf-8", errors="replace") if filename_match else ""
            payload = content.rsplit(b"\r\n", 1)[0]
            if filename or payload:
                files.append((filename, payload))
        if not files:
            raise ValueError("未找到上传文件")
        return files

    def import_csv(self, username: str) -> None:
        try:
            _, csv_bytes = self.read_multipart_file("file")
        except Exception as exc:
            self.send_html(render_index(f"导入失败：{exc}", username=username, scroll_to="add"), status=HTTPStatus.BAD_REQUEST)
            return
        if not csv_bytes:
            self.send_html(render_index("导入失败：未找到 CSV 文件", username=username, scroll_to="add"), status=HTTPStatus.BAD_REQUEST)
            return
        reader = csv.DictReader(io.StringIO(csv_bytes.decode("utf-8-sig")))
        count = 0
        try:
            for row in reader:
                if row.get("title"):
                    row["status"] = "active" if current_user_role(username) == "admin" else "pending"
                    create_paper(row, current_user_id(username))
                    count += 1
            self.redirect_with_msg(f"已导入 {count} 条文献到 MySQL", "add")
        except Exception as exc:
            self.send_html(render_index(f"导入失败：{exc}", username=username, scroll_to="add"), status=HTTPStatus.BAD_REQUEST)

    def upload_pdf(self, username: str) -> None:
        try:
            filename, pdf_bytes = self.read_multipart_file("file")
            if not pdf_bytes:
                raise ValueError("未找到 PDF 文件")
            if not filename.lower().endswith(".pdf") and not pdf_bytes.startswith(b"%PDF"):
                raise ValueError("请上传 PDF 文件")

            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            stored_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_filename(filename)}"
            pdf_path = UPLOAD_DIR / stored_name
            pdf_path.write_bytes(pdf_bytes)

            data = parse_pdf_metadata(pdf_path, filename)
            data["pdf_path"] = f"/static/uploads/{stored_name}"
            self.send_html(
                render_index(
                    "PDF 已解析，请检查并修改后再保存",
                    username=username,
                    draft=data,
                    scroll_to="add",
                )
            )
        except Exception as exc:
            self.send_html(render_index(f"PDF 入库失败：{exc}", username=username, scroll_to="add"), status=HTTPStatus.BAD_REQUEST)

    def upload_pdfs(self, username: str) -> None:
        try:
            files = self.read_multipart_files("file")
            drafts: list[dict] = []
            errors: list[str] = []
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            for index, (filename, pdf_bytes) in enumerate(files, 1):
                try:
                    if not pdf_bytes:
                        raise ValueError("空文件")
                    if not filename.lower().endswith(".pdf") and not pdf_bytes.startswith(b"%PDF"):
                        raise ValueError("不是 PDF 文件")
                    stored_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{index}_{safe_filename(filename)}"
                    pdf_path = UPLOAD_DIR / stored_name
                    pdf_path.write_bytes(pdf_bytes)
                    data = parse_pdf_metadata(pdf_path, filename)
                    data["pdf_path"] = f"/static/uploads/{stored_name}"
                    data["source_filename"] = filename
                    drafts.append(data)
                except Exception as exc:
                    errors.append(f"{filename or '未命名文件'}：{exc}")
            if not drafts:
                raise ValueError("未成功解析任何 PDF；" + "；".join(errors))
            message = f"已解析 {len(drafts)} 篇 PDF，请检查后批量保存"
            if errors:
                message += "；部分文件失败：" + "；".join(errors[:3])
            self.send_html(
                render_index(
                    message,
                    username=username,
                    batch_drafts=drafts,
                    scroll_to="batch-review",
                )
            )
        except Exception as exc:
            self.send_html(render_index(f"批量解析失败：{exc}", username=username, scroll_to="add"), status=HTTPStatus.BAD_REQUEST)

    def save_batch_papers(self, username: str) -> None:
        data = self.read_form()
        try:
            count = int(data.get("count") or 0)
            if count <= 0:
                raise ValueError("没有可保存的批量解析结果")
            items: list[dict] = []
            for index in range(count):
                item = {
                    "title": data.get(f"title_{index}", ""),
                    "abstract": data.get(f"abstract_{index}", ""),
                    "publish_date": data.get(f"publish_date_{index}", ""),
                    "doi": data.get(f"doi_{index}", ""),
                    "venue_name": data.get(f"venue_name_{index}", ""),
                    "venue_type": data.get(f"venue_type_{index}", ""),
                    "author_ids": data.get(f"author_ids_{index}", []),
                    "keywords": data.get(f"keywords_{index}", ""),
                    "pdf_path": data.get(f"pdf_path_{index}", ""),
                    "status": "active" if current_user_role(username) == "admin" else "pending",
                }
                validate_paper_input(item)
                items.append(item)
            saved = 0
            user_id = current_user_id(username)
            for item in items:
                create_paper(item, user_id)
                saved += 1
            self.redirect_with_msg(f"已批量保存 {saved} 篇文献到 MySQL", "add")
        except Exception as exc:
            self.send_html(render_index(f"批量保存失败：{exc}", username=username, scroll_to="add"), status=HTTPStatus.BAD_REQUEST)

    def export_json(self) -> None:
        payload = json.dumps(paper_rows({}), ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Disposition", "attachment; filename=literature_mysql_export.json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def export_csv(self) -> None:
        data = paper_rows({})
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=data[0].keys() if data else ["title"])
        writer.writeheader()
        writer.writerows(data)
        payload = out.getvalue().encode("utf-8-sig")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/csv; charset=utf-8")
        self.send_header("Content-Disposition", "attachment; filename=literature_mysql_export.csv")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def api_authors(self, term: str) -> None:
        rows = author_options(term)
        payload = json.dumps(
            [
                {
                    "author_id": row.get("author_id"),
                    "label": (
                        str(row.get("name") or "")
                        + (f" | ORCID: {row.get('orcid_id')}" if row.get("orcid_id") else "")
                        + (f" | {row.get('email')}" if row.get("email") else "")
                    ),
                }
                for row in rows
            ],
            ensure_ascii=False,
        ).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def api_keywords(self, term: str) -> None:
        rows = keyword_options(term)
        payload = json.dumps(
            [
                {
                    "word": row.get("word"),
                    "label": f"{row.get('word')} | {row.get('paper_count') or 0}",
                }
                for row in rows
            ],
            ensure_ascii=False,
        ).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def send_html(self, payload: bytes, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", location)
        self.end_headers()

    def redirect_with_msg(self, message: str, anchor: str = "") -> None:
        suffix = "#" + anchor if anchor else ""
        self.redirect("/?msg=" + urllib.parse.quote(message) + suffix)

    def log_message(self, fmt: str, *args: object) -> None:
        print("[%s] %s" % (datetime.now().strftime("%H:%M:%S"), fmt % args))


def main() -> None:
    port = int(os.environ.get("PORT", sys.argv[1] if len(sys.argv) > 1 else 8000))
    print("正在连接 MySQL：", f"{MYSQL_USER}@{MYSQL_HOST}:{MYSQL_PORT}/{DB_NAME}")
    print("如需指定密码，请先设置环境变量 MYSQL_PASSWORD")
    try:
        init_check()
        print("MySQL 连接成功")
    except Exception as exc:
        print("MySQL 连接检查失败：", exc)
        print("网页仍会启动，并在首页显示具体错误。")
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"文献管理平台已启动：http://127.0.0.1:{port}")
    print("按 Ctrl+C 停止服务")
    server.serve_forever()


if __name__ == "__main__":
    main()
