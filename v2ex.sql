/*
 Navicat MySQL Data Transfer

 Source Server         : localhost
 Source Server Version : 50531
 Source Host           : localhost
 Source Database       : v2ex

 Target Server Version : 50531
 File Encoding         : utf-8

 Date: 11/30/2013 15:17:47 PM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

USE v2ex;

-- ----------------------------
--  Table structure for `member`
-- ----------------------------
DROP TABLE IF EXISTS `member`;
CREATE TABLE `member` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `num` int(11) DEFAULT NULL,
  `auth` varchar(255) DEFAULT NULL,
  `deactivated` int(11) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  `username_lower` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `email_verified` int(11) DEFAULT NULL,
  `website` varchar(255) DEFAULT NULL,
  `psn` varchar(255) DEFAULT NULL,
  `twitter` varchar(255) DEFAULT NULL,
  `twitter_oauth` int(11) DEFAULT NULL,
  `twitter_oauth_key` varchar(255) DEFAULT NULL,
  `twitter_oauth_secret` varchar(255) DEFAULT NULL,
  `twitter_oauth_string` varchar(255) DEFAULT NULL,
  `twitter_sync` int(11) DEFAULT NULL,
  `twitter_id` int(11) DEFAULT NULL,
  `twitter_name` varchar(255) DEFAULT NULL,
  `twitter_screen_name` varchar(255) DEFAULT NULL,
  `twitter_location` varchar(255) DEFAULT NULL,
  `twitter_description` varchar(255) DEFAULT NULL,
  `twitter_profile_image_url` varchar(255) DEFAULT NULL,
  `twitter_url` varchar(255) DEFAULT NULL,
  `twitter_statuses_count` int(11) DEFAULT NULL,
  `twitter_followers_count` int(11) DEFAULT NULL,
  `twitter_friends_count` int(11) DEFAULT NULL,
  `twitter_favourites_count` int(11) DEFAULT NULL,
  `use_my_css` int(11) DEFAULT NULL,
  `my_css` varchar(255) DEFAULT NULL,
  `my_home` varchar(255) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `tagline` varchar(255) DEFAULT NULL,
  `bio` varchar(255) DEFAULT NULL,
  `avatar_large_url` varchar(255) DEFAULT NULL,
  `avatar_normal_url` varchar(255) DEFAULT NULL,
  `avatar_mini_url` varchar(255) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `last_signin` date DEFAULT NULL,
  `blocked` varchar(255) DEFAULT NULL,
  `l10n` varchar(255) DEFAULT NULL,
  `favorited_nodes` int(11) DEFAULT NULL,
  `favorited_topics` int(11) DEFAULT NULL,
  `favorited_members` int(11) DEFAULT NULL,
  `followers_count` int(11) DEFAULT NULL,
  `level` int(11) DEFAULT NULL,
  `notifications` int(11) DEFAULT NULL,
  `notification_position` int(11) DEFAULT NULL,
  `private_token` varchar(255) DEFAULT NULL,
  `ua` varchar(255) DEFAULT NULL,
  `newbie` int(11) DEFAULT NULL,
  `noob` int(11) DEFAULT NULL,
  `show_home_top` int(11) DEFAULT NULL,
  `show_quick_post` int(11) DEFAULT NULL,
  `btc` varchar(255) DEFAULT NULL,
  `github` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `counter`
-- ----------------------------
DROP TABLE IF EXISTS `counter`;
CREATE TABLE `counter` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `value` int(11) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `last_increased` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;

    
-- ----------------------------
--  Table structure for `section`
-- ----------------------------
DROP TABLE IF EXISTS `section`;
CREATE TABLE `section` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `num` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `title_alternative` varchar(255) DEFAULT NULL,
  `header` varchar(255) DEFAULT NULL,
  `footer` varchar(255) DEFAULT NULL,
  `nodes` int(11) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `node`
-- ----------------------------
DROP TABLE IF EXISTS `node`;
CREATE TABLE `node` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `num` int(11) DEFAULT NULL,
  `section_num` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `title_alternative` varchar(255) DEFAULT NULL,
  `header` text,
  `footer` text,
  `sidebar` text,
  `sidebar_ads` text,
  `category` varchar(255) DEFAULT NULL,
  `topics` int(11) DEFAULT NULL,
  `parent_node_name` varchar(255) DEFAULT NULL,
  `avatar_large_url` varchar(255) DEFAULT NULL,
  `avatar_normal_url` varchar(255) DEFAULT NULL,
  `avatar_mini_url` varchar(255) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

    
-- ----------------------------
--  Table structure for `topic`
-- ----------------------------
DROP TABLE IF EXISTS `topic`;
CREATE TABLE `topic` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `num` int(11) DEFAULT NULL,
  `node_id` int ,
  `node_num` int(11) DEFAULT NULL,  
  `node_name` varchar(255) DEFAULT NULL,
  `node_title` varchar(255) DEFAULT NULL,
  `member_id` int ,
  `member_num` int(11) DEFAULT NULL,  
  `title` varchar(255) DEFAULT NULL,
  `content` text,  
  `content_rendered` text, 
  `content_length`  int(11) DEFAULT NULL,
  `has_content` bool DEFAULT NULL,  
  `hits` int(11) DEFAULT NULL,  
  `stars` int(11) DEFAULT NULL,  
  `replies` int(11) DEFAULT NULL,  
  `created_by` varchar(255) DEFAULT NULL,
  `last_reply_by` varchar(255) DEFAULT NULL,
  `source` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `type_color` varchar(255) DEFAULT NULL,
  `explicit` int(11) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `last_touched` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`node_id`) REFERENCES node(`id`),
  FOREIGN KEY (`member_id`) REFERENCES member(`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `reply`
-- ----------------------------
DROP TABLE IF EXISTS `reply`;
CREATE TABLE `reply` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `num` int(11) DEFAULT NULL,
  `topic_id` int ,
  `topic_num` int(11) DEFAULT NULL,  
  `member_id` int ,
  `member_num` int(11) DEFAULT NULL,  
  `content` text,  
  `source` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `highlighted` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`topic_id`) REFERENCES topic(`id`),
  FOREIGN KEY (`member_id`) REFERENCES member(`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `avartar`
-- ----------------------------
DROP TABLE IF EXISTS `avartar`;
CREATE TABLE `avartar` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `num` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `content` blob,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `note`
-- ----------------------------
DROP TABLE IF EXISTS `note`;
CREATE TABLE `note` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `num` int(11) DEFAULT NULL,
  `member_id` int ,
  `member_num` int(11) DEFAULT NULL,  
  `title` varchar(255) DEFAULT NULL,
  `content` text,  
  `body` text,
  `length` int(11) DEFAULT NULL,
  `edits` int(11) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`member_id`) REFERENCES member(`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `password_reset_token`
-- ----------------------------
DROP TABLE IF EXISTS `password_reset_token`;
CREATE TABLE `password_reset_token` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `token`  varchar(255) DEFAULT NULL,
  `email`  varchar(255) DEFAULT NULL,
  `member_id` int ,
  `valid` int(11) DEFAULT 1,
  `timestamp` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`member_id`) REFERENCES member(`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `place`
-- ----------------------------
DROP TABLE IF EXISTS `place`;
CREATE TABLE `place` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `num` int(11) DEFAULT NULL,
  `ip`  varchar(255) DEFAULT NULL,
  `name`  varchar(255) DEFAULT NULL,
  `visitors` int(11) DEFAULT NULL,
  `longitude` float(7) DEFAULT NULL,
  `latitude` float(7) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL, 
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `place_message`
-- ----------------------------
DROP TABLE IF EXISTS `place_message`;
CREATE TABLE `place_message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `num` int(11) DEFAULT NULL,
  `place_id` int ,
  `place_num` int(11) DEFAULT NULL,
  `member_id` int ,
  `content` text,
  `placemessage_id` int ,
  `source`  varchar(255) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`place_id`) REFERENCES place(`id`),
  FOREIGN KEY (`member_id`) REFERENCES member(`id`),
  FOREIGN KEY (`placemessage_id`) REFERENCES place_message(`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `checkin`
-- ----------------------------
DROP TABLE IF EXISTS `checkin`;
CREATE TABLE `checkin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `place_id` int ,
  `member_id` int ,
  `last_checked_in` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`place_id`) REFERENCES place(`id`),
  FOREIGN KEY (`member_id`) REFERENCES member(`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `site`
-- ----------------------------
DROP TABLE IF EXISTS `site`;
CREATE TABLE `site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `num` int(11) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `slogan` varchar(255) DEFAULT NULL,
  `description` text,
  `domain` varchar(255) DEFAULT NULL,
  `analytics` varchar(255) DEFAULT NULL,
  `home_categories` varchar(255) DEFAULT NULL,
  `meta` varchar(255) DEFAULT NULL,
  `home_top` varchar(255) DEFAULT NULL,
  `theme` varchar(255) DEFAULT NULL,
  `l10n` varchar(255) DEFAULT NULL,
  `use_topic_types` int(255) DEFAULT NULL,
  `topic_types` varchar(255) DEFAULT NULL,
  `topic_view_level` int(11) DEFAULT NULL,
  `topic_create_level` int(11) DEFAULT NULL,
  `topic_reply_level` int(11) DEFAULT NULL,
  `data_migration_mode` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `minisite`
-- ----------------------------
DROP TABLE IF EXISTS `minisite`;
CREATE TABLE `minisite` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `num` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `description` text,
  `pages` int(11) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `page`
-- ----------------------------
DROP TABLE IF EXISTS `page`;
CREATE TABLE `page` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `num` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `minisite_id` int ,
  `content` text,
  `content_rendered` text,
  `content_type` varchar(255) DEFAULT 'text/html' ,
  `weight` int(11) DEFAULT NULL,
  `mode` int(11) DEFAULT NULL,
  `hits` int(11) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`minisite_id`) REFERENCES minisite(`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `node_bookmark`
-- ----------------------------
DROP TABLE IF EXISTS `node_bookmark`;
CREATE TABLE `node_bookmark` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `node_id` int ,
  `member_id` int ,
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`node_id`) REFERENCES node(`id`),
  FOREIGN KEY (`member_id`) REFERENCES member(`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `topic_bookmark`
-- ----------------------------
DROP TABLE IF EXISTS `topic_bookmark`;
CREATE TABLE `topic_bookmark` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `topic_id` int ,
  `member_id` int ,
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`topic_id`) REFERENCES topic(`id`),
  FOREIGN KEY (`member_id`) REFERENCES member(`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `member_bookmark`
-- ----------------------------
DROP TABLE IF EXISTS `member_bookmark`;
CREATE TABLE `member_bookmark` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `member_id` int ,
  `member_num` int(11) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`member_id`) REFERENCES member(`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `notification`
-- ----------------------------
DROP TABLE IF EXISTS `notification`;
CREATE TABLE `notification` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `num` int(11) DEFAULT NULL,
  `member_id` int ,
  `for_member_num` int(11) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `payload` text,
  `label1` varchar(255) DEFAULT NULL,
  `link1` varchar(255) DEFAULT NULL,
  `label2` varchar(255) DEFAULT NULL,
  `link2` varchar(255) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`member_id`) REFERENCES member(`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
    

-- ----------------------------
--  Table structure for `item`
-- ----------------------------
DROP TABLE IF EXISTS `item`;
CREATE TABLE `item` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `description` text,
  `price` varchar(255) DEFAULT NULL,
  `category` varchar(255) DEFAULT 'gadgets' ,
  `column` int(11) DEFAULT NULL,
  `link_official` varchar(255) DEFAULT NULL,
  `link_picture` varchar(255) DEFAULT NULL,
  `link_buy` varchar(255) DEFAULT NULL,
  `node_name` varchar(255) DEFAULT NULL,
  `published` int(11) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
    


SET FOREIGN_KEY_CHECKS = 1;
