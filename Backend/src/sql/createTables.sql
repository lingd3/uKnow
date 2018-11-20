CREATE TABLE IF NOT EXISTS question (
  id INT(11) NOT NULL AUTO_INCREMENT,
  description VARCHAR(60) NOT NULL,
  askDate Date NOT NULL,
  asker_id INT(11),
  answerer_id INT(11),
  audioUrl VARCHAR(50),
  audioSeconds INT(11),
  PRIMARY KEY(id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;
CREATE TABLE IF NOT EXISTS user (
  id INT(11) NOT NULL AUTO_INCREMENT,
  username VARCHAR(10) NOT NULL UNIQUE,
  avatarUrl VARCHAR(100),
  status VARCHAR(20),
  description VARCHAR(50),
  school VARCHAR(20),
  major VARCHAR(20),
  grade VARCHAR(20),
  openid VARCHAR(50) UNIQUE, 
  PRIMARY KEY(id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;
CREATE TABLE IF NOT EXISTS listening (
  uid INT(11) NOT NULL,
  qid INT(11) NOT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8;
CREATE TABLE IF NOT EXISTS comment (
  uid INT(11) NOT NULL,
  qid INT(11) NOT NULL,
  liked INT(11) NOT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8;
CREATE TABLE IF NOT EXISTS follow (
  uid INT(11) NOT NULL,
  followed_uid INT(11) NOT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8;
