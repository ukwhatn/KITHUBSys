-- --------------------------------------------------------
-- ホスト:                          localhost
-- サーバーのバージョン:                   10.7.1-MariaDB-1:10.7.1+maria~focal - mariadb.org binary distribution
-- サーバー OS:                      debian-linux-gnu
-- HeidiSQL バージョン:               11.3.0.6295
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT = @@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS = @@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS = 0 */;
/*!40101 SET @OLD_SQL_MODE = @@SQL_MODE, SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES = @@SQL_NOTES, SQL_NOTES = 0 */;


GRANT SELECT, INSERT, UPDATE, DELETE ON Master.* TO application;

CREATE DATABASE IF NOT EXISTS `Master` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;
USE `Master`;

DROP TABLE IF EXISTS `config`;
CREATE TABLE IF NOT EXISTS `config`
(
    `id`    int(11)      NOT NULL AUTO_INCREMENT,
    `name`  varchar(50)  NOT NULL,
    `value` varchar(200) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  DEFAULT CHARSET = utf8mb4;

DROP TABLE IF EXISTS `discord_accounts`;

CREATE TABLE `discord_accounts`
(
    `discord_user_id`            bigint(20)  NOT NULL,
    `discord_user_name`          varchar(50) NOT NULL,
    `discord_user_discriminator` varchar(4)  NOT NULL,
    `member_id`                  int(11)     NOT NULL,
    `latest_updated`             datetime    NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
    PRIMARY KEY (`discord_user_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

DROP TABLE IF EXISTS `members`;

CREATE TABLE `members`
(
    `id`                  int(11) unsigned NOT NULL AUTO_INCREMENT,
    `student_number`      varchar(15)      NOT NULL,
    `first_name`          varchar(20)      NOT NULL,
    `last_name`           varchar(20)      NOT NULL,
    `first_name_phonetic` varchar(20)      NOT NULL,
    `last_name_phonetic`  varchar(20)      NOT NULL,
    `nickname`            varchar(20)               DEFAULT NULL,
    `department`          int(11)          NOT NULL,
    `grade`               tinyint(1)       NOT NULL,
    `mail`                varchar(100)     NOT NULL,
    `phone`               varchar(11)               DEFAULT NULL,
    `is_board_member`     tinyint(1)       NOT NULL DEFAULT 0,
    `date_added`          datetime         NOT NULL DEFAULT current_timestamp(),
    `lastest_updated`     datetime         NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
    PRIMARY KEY (`id`),
    UNIQUE KEY `student_number` (`student_number`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;



/*!40101 SET SQL_MODE = IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS = IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT = @OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES = IFNULL(@OLD_SQL_NOTES, 1) */;
