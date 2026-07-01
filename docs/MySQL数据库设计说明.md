# MySQL 数据库设计说明

核心实体包括 User、Paper、Venue、Author、Institution、Keyword、Tag、Citation、PaperVersion、AuditLog。主要联系如下：
- Venue 与 Paper 为一对多关系，Paper 通过 venue_id 引用 Venue。
- Paper 与 Author 为多对多关系，通过 paper_author 维护作者顺序和通讯作者标记。
- Author 与 Institution 为多对多关系，通过 author_institution 维护任职起止年份。
- Paper 与 Keyword 为多对多关系，通过 paper_keyword 维护论文主题词。
- Paper 与 Paper 之间存在自关联多对多引用关系，通过 citation 表保存 citing_paper_id 与 cited_paper_id。
- User 与 Paper 之间通过 favorite 表表示收藏论文；User 与 Keyword 之间通过 favorite_keyword 表表示收藏关键词。
- Paper 与 PaperVersion 是一对多关系，用于保存元数据版本；AuditLog 记录关键增改行为。
ER 图已生成为图片文件 docs/ER图.png，报告 PDF 中应插入该图片；Mermaid 源码仅作为开发过程中的辅助材料，不作为报告正文展示。

## 表结构定义

本系统数据库名为 literature_management，采用 utf8mb4 字符集。逻辑设计将论文、作者、机构、来源、关键词等概念拆分为独立实体表，并用关联表维护多对多关系。
期中设计中 Institution 表本身存在 3NF 风险：如果在 institution 表内同时保存 address 和 country，而 country 可以由 address 中的国家/地区信息推导，则存在 institution_id -> address -> country 的传递依赖。country 不是由主键直接描述的独立事实，而是依赖另一个非主属性 address。期末版本删除 institution.country，仅保留 name、address、website，从而消除该传递依赖。
当前模型满足 1NF：表中字段均为原子值，作者列表、关键词列表、引用列表不再存入 paper 单字段，而是由 paper_author、paper_keyword、citation 表维护。
当前模型满足 2NF：带联合主键的关联表中，非主属性依赖完整联合主键。例如 paper_author 的 author_order 描述某篇论文中的某位作者顺序，依赖 paper_id 与 author_id 共同确定的关系。
当前模型满足 3NF：每张实体表只描述一个主题，非主属性不依赖其他非主属性。例如 paper 只保存 venue_id，不直接冗余 venue_name/publisher；author 不直接冗余机构信息；keyword 独立维护词汇与类别；institution 不再保存可由 address 推导的 country。

## 完整性与高级对象

- sys_user：user_id PK; username UK; password_hash; role; email UK; created_at; updated_at。用途：系统用户、角色与登录凭据。
- user_preference：user_id PK/FK; language; font_family; font_size; updated_at。用途：用户界面语言等偏好。
- paper：paper_id PK; title; abstract; publish_date; pdf_path; doi NOT NULL UK; external_citation_count; status; venue_id FK; created_by FK。用途：论文元数据主表，DOI 用于论文去重。
- venue：venue_id PK; name; venue_type; publisher; publish_year; location; website; created_at。用途：期刊、会议、预印本等来源。
- author：author_id PK; name; email UK; orcid_id NOT NULL UK; homepage; created_at。用途：作者基本信息，ORCID 用于作者去重。
- institution：institution_id PK; name UK; address; website。用途：机构信息，已删除 country 以满足 3NF。
- author_institution：author_id PK/FK; institution_id PK/FK; start_year; end_year。用途：作者与机构多对多关系。
- keyword：keyword_id PK; word; category; UNIQUE(word, category)。用途：关键词、领域词与主题词。
- paper_author：paper_id PK/FK; author_id PK/FK; author_order; is_corresponding。用途：论文与作者关系及顺序。
- paper_keyword：paper_id PK/FK; keyword_id PK/FK。用途：论文与关键词关系。
- favorite：user_id PK/FK; paper_id PK/FK; created_at。用途：用户收藏论文。
- favorite_keyword：user_id PK/FK; keyword_id PK/FK; created_at。用途：用户收藏关键词。
- tag：tag_id PK; user_id FK; name; color; created_at。用途：用户自定义标签。
- paper_tag：paper_id PK/FK; tag_id PK/FK。用途：论文与标签关系。
- citation：citing_paper_id PK/FK; cited_paper_id PK/FK; context; created_at。用途：论文内部引用关系。
- paper_version：version_id PK; paper_id FK; version_no; update_time; change_log; operator_id。用途：论文元数据版本记录。
- audit_log：log_id PK; table_name; record_id; action_type; action_time; detail JSON。用途：关键数据变更审计日志。
完整 SQL 定义见 mysql/schema.sql。
