# 文献管理系统 MySQL 数据库说明

本目录是课程期末项目的正式 MySQL 数据库部分，适用于 MySQL 8.0。

## 1. 文件说明

```text
mysql/
  schema.sql
    建库、建表、主键、外键、唯一约束、检查约束、索引、全文索引、视图、触发器、存储过程

  seed_data.sql
    干净初始化数据：只创建管理员账号和界面偏好，不插入演示论文、作者、关键词或引用
```

## 2. 执行顺序

推荐方式：回到 `提交包` 根目录，双击：

```text
init_mysql_db.bat
```

按提示输入 MySQL 用户名和密码，脚本会自动按顺序执行本目录下的三个 SQL 文件。

备用命令行执行：

```bash
mysql -u root -p < mysql/schema.sql
mysql -u root -p literature_management < mysql/seed_data.sql
```

最终版本采用用户提供数据：新增作者必须填写非空且唯一的 ORCID；新增论文必须填写非空且唯一的 DOI，并选择作者表中已有作者。

MySQL Workbench 执行：

1. `File -> Open SQL Script...` 打开 `schema.sql`，点击闪电执行。
2. 打开 `seed_data.sql`，点击闪电执行。

## 3. 用户提供数据规则

- 作者去重：以 `author.orcid_id` 为唯一识别号，同名但 ORCID 不同的作者可以同时存在。
- 论文去重：以 `paper.doi` 为唯一识别号，重复 DOI 会被拒绝。
- 缺少 ORCID 的作者不能加入作者表；缺少 DOI 的论文不能加入论文表。
- CSV 批量导入时应提供 `author_ids` 字段，引用已经在作者表中登记过 ORCID 的作者。

## 4. 执行后检查

执行完成后，可以在 Workbench 中运行：

```sql
USE literature_management;
SELECT COUNT(*) AS paper_count FROM paper;
SELECT * FROM v_paper_detail ORDER BY paper_id DESC LIMIT 20;
```

## 5. 数据库对象

核心实体表：

- `sys_user`：系统用户
- `paper`：论文元数据
- `venue`：期刊、会议、预印本等来源
- `author`：作者
- `keyword`：关键词和领域词

核心关联表：

- `paper_author`：论文和作者的多对多关系
- `paper_keyword`：论文和关键词/领域词的多对多关系
- `favorite`：用户收藏论文
- `favorite_keyword`：用户收藏关键词
- `citation`：论文引用论文的自关联关系

高级对象：

- `v_paper_detail`：论文详情聚合视图，包含作者、关键词、引用数和被引数
- `sp_create_paper`：新增论文存储过程
- `trg_paper_before_insert` / `trg_paper_before_update`：禁止未来发表日期
- `trg_citation_before_insert` / `trg_citation_before_update`：禁止论文自引用
- `ftx_paper_title_abstract`：标题和摘要全文索引

## 6. 数据来源

最终版本采用用户提供数据。论文、作者、关键词等业务数据由用户通过平台录入、PDF 解析后确认录入，或通过 CSV 批量导入。

为支持去重和数据质量控制，系统以 DOI 识别论文、以 ORCID 识别作者：缺少 DOI 的论文和缺少 ORCID 的作者都会被拒绝。

## 7. 与网站平台配合

数据库导入完成后，回到 `提交包` 根目录启动平台：

```bash
python app_mysql.py
```

或在 Windows 下双击：

```text
start_mysql_app.bat
```

浏览器访问：

```text
http://127.0.0.1:8000
```
