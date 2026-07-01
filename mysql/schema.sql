-- 文献管理系统 MySQL 8.0 数据库设计
-- 执行方式：mysql -u root -p < mysql/schema.sql

DROP DATABASE IF EXISTS literature_management;
CREATE DATABASE literature_management
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;
USE literature_management;

-- 1. 用户与权限
CREATE TABLE sys_user (
  user_id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(64) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
  email VARCHAR(128),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT uk_sys_user_username UNIQUE (username),
  CONSTRAINT uk_sys_user_email UNIQUE (email)
) ENGINE=InnoDB COMMENT='系统用户';

-- 2. 期刊、会议、预印本等发表来源
CREATE TABLE venue (
  venue_id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  venue_type ENUM('journal', 'conference', 'preprint', 'other') NOT NULL,
  publisher VARCHAR(255),
  publish_year SMALLINT UNSIGNED,
  location VARCHAR(255),
  website VARCHAR(512),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uk_venue_name_year UNIQUE (name, publish_year),
  CONSTRAINT ck_venue_year CHECK (publish_year IS NULL OR publish_year BETWEEN 1900 AND 2100)
) ENGINE=InnoDB COMMENT='文献来源';

-- 3. 论文主表
CREATE TABLE paper (
  paper_id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(512) NOT NULL,
  abstract TEXT,
  publish_date DATE NOT NULL,
  pdf_path VARCHAR(512),
  doi VARCHAR(128) NOT NULL,
  external_citation_count INT UNSIGNED NOT NULL DEFAULT 0,
  status ENUM('pending', 'active', 'archived') NOT NULL DEFAULT 'active',
  venue_id BIGINT UNSIGNED,
  created_by BIGINT UNSIGNED,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT uk_paper_doi UNIQUE (doi),
  CONSTRAINT ck_paper_doi_not_empty CHECK (TRIM(doi) <> ''),
  CONSTRAINT fk_paper_venue FOREIGN KEY (venue_id)
    REFERENCES venue(venue_id)
    ON UPDATE CASCADE
    ON DELETE SET NULL,
  CONSTRAINT fk_paper_created_by FOREIGN KEY (created_by)
    REFERENCES sys_user(user_id)
    ON UPDATE CASCADE
    ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='论文元数据';

-- 4. 作者与机构
CREATE TABLE author (
  author_id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(128) NOT NULL,
  email VARCHAR(128),
  orcid_id VARCHAR(32) NOT NULL,
  homepage VARCHAR(512),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uk_author_email UNIQUE (email),
  CONSTRAINT uk_author_orcid UNIQUE (orcid_id),
  CONSTRAINT ck_author_orcid_not_empty CHECK (TRIM(orcid_id) <> '')
) ENGINE=InnoDB COMMENT='作者';

CREATE TABLE institution (
  institution_id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  address VARCHAR(512),
  website VARCHAR(512),
  CONSTRAINT uk_institution_name UNIQUE (name)
) ENGINE=InnoDB COMMENT='机构';

CREATE TABLE author_institution (
  author_id BIGINT UNSIGNED NOT NULL,
  institution_id BIGINT UNSIGNED NOT NULL,
  start_year SMALLINT UNSIGNED,
  end_year SMALLINT UNSIGNED,
  PRIMARY KEY (author_id, institution_id),
  CONSTRAINT fk_ai_author FOREIGN KEY (author_id)
    REFERENCES author(author_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_ai_institution FOREIGN KEY (institution_id)
    REFERENCES institution(institution_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT ck_ai_year CHECK (
    start_year IS NULL OR end_year IS NULL OR start_year <= end_year
  )
) ENGINE=InnoDB COMMENT='作者-机构关系';

-- 5. 关键词与标签
CREATE TABLE keyword (
  keyword_id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  word VARCHAR(128) NOT NULL,
  category VARCHAR(64) NOT NULL DEFAULT 'topic',
  CONSTRAINT uk_keyword_word_category UNIQUE (word, category)
) ENGINE=InnoDB COMMENT='关键词';

CREATE TABLE tag (
  tag_id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  name VARCHAR(64) NOT NULL,
  color CHAR(7) NOT NULL DEFAULT '#2563eb',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uk_tag_user_name UNIQUE (user_id, name),
  CONSTRAINT fk_tag_user FOREIGN KEY (user_id)
    REFERENCES sys_user(user_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT ck_tag_color CHECK (color REGEXP '^#[0-9A-Fa-f]{6}$')
) ENGINE=InnoDB COMMENT='用户自定义标签';

CREATE TABLE user_preference (
  user_id BIGINT UNSIGNED PRIMARY KEY,
  language ENUM('zh', 'en') NOT NULL DEFAULT 'zh',
  font_family ENUM('system', 'serif', 'mono') NOT NULL DEFAULT 'system',
  font_size ENUM('normal', 'large') NOT NULL DEFAULT 'normal',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_pref_user FOREIGN KEY (user_id)
    REFERENCES sys_user(user_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='用户界面偏好设置';

-- 6. 多对多关联表
CREATE TABLE paper_author (
  paper_id BIGINT UNSIGNED NOT NULL,
  author_id BIGINT UNSIGNED NOT NULL,
  author_order INT UNSIGNED NOT NULL,
  is_corresponding BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (paper_id, author_id),
  CONSTRAINT uk_paper_author_order UNIQUE (paper_id, author_order),
  CONSTRAINT fk_pa_paper FOREIGN KEY (paper_id)
    REFERENCES paper(paper_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_pa_author FOREIGN KEY (author_id)
    REFERENCES author(author_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT ck_pa_author_order CHECK (author_order > 0)
) ENGINE=InnoDB COMMENT='论文-作者关系';

CREATE TABLE paper_keyword (
  paper_id BIGINT UNSIGNED NOT NULL,
  keyword_id BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (paper_id, keyword_id),
  CONSTRAINT fk_pk_paper FOREIGN KEY (paper_id)
    REFERENCES paper(paper_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_pk_keyword FOREIGN KEY (keyword_id)
    REFERENCES keyword(keyword_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='论文-关键词关系';

CREATE TABLE favorite (
  user_id BIGINT UNSIGNED NOT NULL,
  paper_id BIGINT UNSIGNED NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, paper_id),
  CONSTRAINT fk_favorite_user FOREIGN KEY (user_id)
    REFERENCES sys_user(user_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_favorite_paper FOREIGN KEY (paper_id)
    REFERENCES paper(paper_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='用户收藏';

CREATE TABLE favorite_keyword (
  user_id BIGINT UNSIGNED NOT NULL,
  keyword_id BIGINT UNSIGNED NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, keyword_id),
  CONSTRAINT fk_fk_user FOREIGN KEY (user_id)
    REFERENCES sys_user(user_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_fk_keyword FOREIGN KEY (keyword_id)
    REFERENCES keyword(keyword_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='用户收藏关键词';

CREATE TABLE paper_tag (
  paper_id BIGINT UNSIGNED NOT NULL,
  tag_id BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (paper_id, tag_id),
  CONSTRAINT fk_pt_paper FOREIGN KEY (paper_id)
    REFERENCES paper(paper_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_pt_tag FOREIGN KEY (tag_id)
    REFERENCES tag(tag_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='论文-标签关系';

-- 7. 引用关系：Paper 对 Paper 的自关联
CREATE TABLE citation (
  citing_paper_id BIGINT UNSIGNED NOT NULL,
  cited_paper_id BIGINT UNSIGNED NOT NULL,
  context VARCHAR(512),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (citing_paper_id, cited_paper_id),
  CONSTRAINT fk_citation_citing FOREIGN KEY (citing_paper_id)
    REFERENCES paper(paper_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_citation_cited FOREIGN KEY (cited_paper_id)
    REFERENCES paper(paper_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='引用关系';

-- 8. 版本记录
CREATE TABLE paper_version (
  version_id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  paper_id BIGINT UNSIGNED NOT NULL,
  version_no INT UNSIGNED NOT NULL,
  update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  change_log VARCHAR(512) NOT NULL,
  operator_id BIGINT UNSIGNED,
  CONSTRAINT uk_paper_version UNIQUE (paper_id, version_no),
  CONSTRAINT fk_pv_paper FOREIGN KEY (paper_id)
    REFERENCES paper(paper_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_pv_operator FOREIGN KEY (operator_id)
    REFERENCES sys_user(user_id)
    ON UPDATE CASCADE
    ON DELETE SET NULL,
  CONSTRAINT ck_pv_version_no CHECK (version_no > 0)
) ENGINE=InnoDB COMMENT='论文元数据版本';

-- 9. 审计日志：用于记录关键数据变更
CREATE TABLE audit_log (
  log_id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  table_name VARCHAR(64) NOT NULL,
  record_id BIGINT UNSIGNED NOT NULL,
  action_type ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
  action_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  detail JSON
) ENGINE=InnoDB COMMENT='审计日志';

-- 10. 检索与聚合索引
CREATE INDEX idx_paper_title ON paper(title);
CREATE INDEX idx_paper_publish_date ON paper(publish_date);
CREATE INDEX idx_paper_status ON paper(status);
CREATE INDEX idx_author_name ON author(name);
CREATE INDEX idx_keyword_word ON keyword(word);
CREATE INDEX idx_citation_cited ON citation(cited_paper_id);
CREATE INDEX idx_paper_created_by ON paper(created_by);

-- MySQL 全文索引：支持标题和摘要全文检索
CREATE FULLTEXT INDEX ftx_paper_title_abstract ON paper(title, abstract);

-- 11. 视图：汇总论文详情，便于检索页面直接读取
CREATE OR REPLACE VIEW v_paper_detail AS
SELECT
  p.paper_id,
  p.title,
  p.abstract,
  p.publish_date,
  p.doi,
  p.status,
  v.name AS venue_name,
  v.venue_type,
  GROUP_CONCAT(DISTINCT a.name ORDER BY pa.author_order SEPARATOR '; ') AS authors,
  GROUP_CONCAT(DISTINCT i.name ORDER BY i.name SEPARATOR '; ') AS institutions,
  GROUP_CONCAT(DISTINCT CASE WHEN k.category <> 'source' THEN k.word END ORDER BY k.word SEPARATOR '; ') AS keywords,
  COUNT(DISTINCT c_out.cited_paper_id) AS reference_count,
  COUNT(DISTINCT c_in.citing_paper_id) AS cited_by_count,
  p.external_citation_count AS external_citation_count
FROM paper p
LEFT JOIN venue v ON p.venue_id = v.venue_id
LEFT JOIN paper_author pa ON p.paper_id = pa.paper_id
LEFT JOIN author a ON pa.author_id = a.author_id
LEFT JOIN author_institution ai ON a.author_id = ai.author_id
LEFT JOIN institution i ON ai.institution_id = i.institution_id
LEFT JOIN paper_keyword pk ON p.paper_id = pk.paper_id
LEFT JOIN keyword k ON pk.keyword_id = k.keyword_id
LEFT JOIN citation c_out ON p.paper_id = c_out.citing_paper_id
LEFT JOIN citation c_in ON p.paper_id = c_in.cited_paper_id
GROUP BY
  p.paper_id, p.title, p.abstract, p.publish_date, p.doi, p.status,
  p.external_citation_count, v.name, v.venue_type;

-- 12. 触发器：创建论文时自动生成版本记录和审计日志
DELIMITER //

CREATE TRIGGER trg_paper_after_insert
AFTER INSERT ON paper
FOR EACH ROW
BEGIN
  INSERT INTO paper_version(paper_id, version_no, change_log, operator_id)
  VALUES (NEW.paper_id, 1, '创建文献记录', NEW.created_by);

  INSERT INTO audit_log(table_name, record_id, action_type, detail)
  VALUES (
    'paper',
    NEW.paper_id,
    'INSERT',
    JSON_OBJECT('title', NEW.title, 'doi', NEW.doi)
  );
END//

CREATE TRIGGER trg_paper_before_insert
BEFORE INSERT ON paper
FOR EACH ROW
BEGIN
  IF NEW.publish_date > CURRENT_DATE THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'publish_date cannot be later than today';
  END IF;
END//

CREATE TRIGGER trg_paper_before_update
BEFORE UPDATE ON paper
FOR EACH ROW
BEGIN
  IF NEW.publish_date > CURRENT_DATE THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'publish_date cannot be later than today';
  END IF;
END//

CREATE TRIGGER trg_paper_after_update
AFTER UPDATE ON paper
FOR EACH ROW
BEGIN
  INSERT INTO audit_log(table_name, record_id, action_type, detail)
  VALUES (
    'paper',
    NEW.paper_id,
    'UPDATE',
    JSON_OBJECT(
      'old_title', OLD.title,
      'new_title', NEW.title,
      'old_status', OLD.status,
      'new_status', NEW.status
    )
  );
END//

CREATE TRIGGER trg_citation_before_insert
BEFORE INSERT ON citation
FOR EACH ROW
BEGIN
  IF NEW.citing_paper_id = NEW.cited_paper_id THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'citation cannot reference itself';
  END IF;
END//

CREATE TRIGGER trg_citation_before_update
BEFORE UPDATE ON citation
FOR EACH ROW
BEGIN
  IF NEW.citing_paper_id = NEW.cited_paper_id THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'citation cannot reference itself';
  END IF;
END//

-- 13. 存储过程：封装新增论文的核心事务
CREATE PROCEDURE sp_create_paper(
  IN p_title VARCHAR(512),
  IN p_abstract TEXT,
  IN p_publish_date DATE,
  IN p_doi VARCHAR(128),
  IN p_venue_name VARCHAR(255),
  IN p_venue_type VARCHAR(32),
  IN p_created_by BIGINT UNSIGNED,
  OUT o_paper_id BIGINT UNSIGNED
)
BEGIN
  DECLARE v_venue_id BIGINT UNSIGNED;

  IF p_doi IS NULL OR TRIM(p_doi) = '' THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'paper DOI is required';
  END IF;

  START TRANSACTION;

  IF p_venue_name IS NOT NULL AND p_venue_name <> '' THEN
    SELECT MAX(venue_id) INTO v_venue_id
    FROM venue
    WHERE name = p_venue_name AND publish_year = YEAR(p_publish_date);

    IF v_venue_id IS NULL THEN
      INSERT INTO venue(name, venue_type, publish_year)
      VALUES (p_venue_name, COALESCE(NULLIF(p_venue_type, ''), 'other'), YEAR(p_publish_date));
      SET v_venue_id = LAST_INSERT_ID();
    END IF;
  END IF;

  INSERT INTO paper(title, abstract, publish_date, doi, venue_id, created_by)
  VALUES (p_title, p_abstract, p_publish_date, p_doi, v_venue_id, p_created_by);

  SET o_paper_id = LAST_INSERT_ID();

  COMMIT;
END//

DELIMITER ;
