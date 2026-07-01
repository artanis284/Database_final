# 文献管理系统 Literature Management System

本项目是数据库及实现课程期末项目，使用 MySQL 8.0 + Python 实现一个面向用户的文献管理平台。

GitHub 仓库链接：https://github.com/artanis284/Database_final

## 环境要求
- MySQL 8.0
- MySQL Workbench
- Python 3.10 或以上
- PDF 解析依赖：`python -m pip install -r requirements.txt`

## 数据库初始化
推荐方式：确认 MySQL 服务已启动后，双击：

```text
init_mysql_db.bat
```

按提示输入 MySQL 用户名和密码，脚本会自动依次执行：

1. `mysql/schema.sql`
2. `mysql/seed_data.sql`

`seed_data.sql` 会创建课程演示默认管理员账号：用户名 `admin`，密码 `admin123`。普通用户可在登录页自行注册。

备用命令行方式：
```bash
mysql -u root -p < mysql/schema.sql
mysql -u root -p literature_management < mysql/seed_data.sql
```
注意：`schema.sql` 会覆盖同名数据库。

## 启动平台
```bash
python -m pip install -r requirements.txt
python app_mysql.py
```
Windows 下可双击 `start_mysql_app.bat`。脚本会优先使用系统 Python，并在缺少依赖时提示安装命令。启动后访问 `http://127.0.0.1:8000`。

## 功能验证
- 使用默认管理员账号 `admin` / `admin123` 登录，检查审核、修改、归档、删除等管理员功能。
- 注册普通用户并登录。
- 使用标题、作者、年份范围、关键词进行组合检索。
- 上传 PDF，检查系统是否预填表单但不直接入库。
- 新增论文，普通用户提交后状态为 pending。
- 新增作者必须填写唯一 ORCID；新增论文必须填写唯一 DOI，并选择作者表中的作者。
- 管理员筛选 pending 论文，发布为 active。
- 管理员修改、归档、重新发布或删除论文。
- 收藏论文和关键词，在收藏页使用关键词筛选收藏论文。
- 导出 JSON 和 CSV。

## 目录结构
```text
Database_final/
  app_mysql.py
  init_mysql_db.bat
  start_mysql_app.bat
  requirements.txt
  services/
    pdf_parser.py
  static/
    style.css
  mysql/
    schema.sql
    seed_data.sql
    README.md
  docs/
    期末项目报告.md
    MySQL数据库设计说明.md
    代码文档.md
    用户手册.md
    ER图.png
```

## 测试 SQL
```sql
USE literature_management;
SELECT COUNT(*) AS paper_count FROM paper;
SELECT * FROM v_paper_detail ORDER BY paper_id DESC LIMIT 20;
SELECT status, COUNT(*) FROM paper GROUP BY status;
```
