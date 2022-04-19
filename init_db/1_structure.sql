# CONFIG
SET @OLD_CHARACTER_SET_CLIENT = @@CHARACTER_SET_CLIENT;
SET NAMES utf8;
SET NAMES utf8mb4;
SET @OLD_FOREIGN_KEY_CHECKS = @@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS = 0;
SET @OLD_SQL_MODE = @@SQL_MODE, SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';
SET @OLD_SQL_NOTES = @@SQL_NOTES, SQL_NOTES = 0;

# PERMISSION
# ACCOUNT CREATE -> docker-compose.yml
GRANT SELECT, INSERT, UPDATE, DELETE ON Master.* TO application;

# CREATE DATABASE "Master"
CREATE DATABASE IF NOT EXISTS `Master` DEFAULT CHARACTER SET utf8mb4;
USE `Master`;

DROP TABLE IF EXISTS `config`;
CREATE TABLE `config`
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
    `latest_updated`     datetime         NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
    PRIMARY KEY (`id`),
    UNIQUE KEY `student_number` (`student_number`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;



SET SQL_MODE = IFNULL(@OLD_SQL_MODE, '');
SET FOREIGN_KEY_CHECKS = IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1);
SET CHARACTER_SET_CLIENT = @OLD_CHARACTER_SET_CLIENT;
SET SQL_NOTES = IFNULL(@OLD_SQL_NOTES, 1);
