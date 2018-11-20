DROP TABLE IF EXISTS user;
CREATE TABLE user (
  id INT(11) NOT NULL AUTO_INCREMENT,
  username VARCHAR(10) NOT NULL UNIQUE,
  password VARCHAR(50) NOT NULL,
  avatarUrl VARCHAR(100), 
  status VARCHAR(20),
  description VARCHAR(50),
  school VARCHAR(20),
  major VARCHAR(20),
  grade VARCHAR(20),
  openid VARCHAR(50) UNIQUE,  --微信登录
  PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS question;
CREATE TABLE question (
    id INT(11) NOT NULL AUTO_INCREMENT,
    description VARCHAR(60) NOT NULL,
    askDate Date NOT NULL, 
    asker_id INT(11) ,
    answerer_id INT(11) ,
    audioUrl VARCHAR(50) ,
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS listening;
CREATE TABLE listening (
    uid INT(11) NOT NULL,
    qid INT(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS praise;
CREATE TABLE praise (
    uid INT(11) NOT NULL,
    qid INT(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS follow;
CREATE TABLE follow (
    uid INT(11) NOT NULL,  --跟随者id
    followed_uid INT(11) NOT NULL  --被跟随者id
) ENGINE=InnoDB DEFAULT CHARSET=utf8;