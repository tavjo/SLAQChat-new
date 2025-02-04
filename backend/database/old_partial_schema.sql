-- MySQL dump 10.13  Distrib 8.4.0, for macos13.2 (x86_64)
--
-- Host: 10.79.5.19    Database: seek_production
-- ------------------------------------------------------
-- Server version	5.5.5-10.5.22-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `projects`
--

DROP TABLE IF EXISTS `projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projects` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `web_page` text DEFAULT NULL,
  `wiki_page` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `description` text DEFAULT NULL,
  `avatar_id` int(11) DEFAULT NULL,
  `default_policy_id` int(11) DEFAULT NULL,
  `first_letter` varchar(1) DEFAULT NULL,
  `site_credentials` varchar(255) DEFAULT NULL,
  `site_root_uri` varchar(255) DEFAULT NULL,
  `last_jerm_run` datetime DEFAULT NULL,
  `uuid` varchar(255) DEFAULT NULL,
  `programme_id` int(11) DEFAULT NULL,
  `default_license` varchar(255) DEFAULT 'CC-BY-4.0',
  `use_default_policy` tinyint(1) DEFAULT 0,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `samples`
--

DROP TABLE IF EXISTS `samples`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `samples` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `sample_type_id` int(11) DEFAULT NULL,
  `json_metadata` text DEFAULT NULL,
  `uuid` varchar(255) DEFAULT NULL,
  `contributor_id` int(11) DEFAULT NULL,
  `policy_id` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `first_letter` varchar(1) DEFAULT NULL,
  `other_creators` text DEFAULT NULL,
  `originating_data_file_id` int(11) DEFAULT NULL,
  `deleted_contributor` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=153998 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projects_samples`
--

DROP TABLE IF EXISTS `projects_samples`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projects_samples` (
  `project_id` int(11) DEFAULT NULL,
  `sample_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sample_types`
--

DROP TABLE IF EXISTS `sample_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sample_types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `uuid` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `first_letter` varchar(1) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `uploaded_template` tinyint(1) DEFAULT 0,
  `contributor_id` int(11) DEFAULT NULL,
  `deleted_contributor` varchar(255) DEFAULT NULL,
  `template_id` int(11) DEFAULT NULL,
  `other_creators` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=126 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projects_sample_types`
--

DROP TABLE IF EXISTS `projects_sample_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projects_sample_types` (
  `project_id` int(11) DEFAULT NULL,
  `sample_type_id` int(11) DEFAULT NULL,
  KEY `index_projects_sample_types_on_project_id` (`project_id`) USING BTREE,
  KEY `index_projects_sample_types_on_sample_type_id_and_project_id` (`sample_type_id`,`project_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assays`
--

DROP TABLE IF EXISTS `assays`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assays` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text DEFAULT NULL,
  `description` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `study_id` int(11) DEFAULT NULL,
  `contributor_id` int(11) DEFAULT NULL,
  `first_letter` varchar(1) DEFAULT NULL,
  `assay_class_id` int(11) DEFAULT NULL,
  `uuid` varchar(255) DEFAULT NULL,
  `policy_id` int(11) DEFAULT NULL,
  `assay_type_uri` varchar(255) DEFAULT NULL,
  `technology_type_uri` varchar(255) DEFAULT NULL,
  `suggested_assay_type_id` int(11) DEFAULT NULL,
  `suggested_technology_type_id` int(11) DEFAULT NULL,
  `other_creators` text DEFAULT NULL,
  `deleted_contributor` varchar(255) DEFAULT NULL,
  `sample_type_id` int(11) DEFAULT NULL,
  `position` int(11) DEFAULT NULL,
  `assay_stream_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index_assays_on_sample_type_id` (`sample_type_id`),
  KEY `index_assays_on_assay_stream_id` (`assay_stream_id`)
) ENGINE=InnoDB AUTO_INCREMENT=157 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `studies`
--

DROP TABLE IF EXISTS `studies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `studies` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text DEFAULT NULL,
  `description` text DEFAULT NULL,
  `investigation_id` int(11) DEFAULT NULL,
  `experimentalists` text DEFAULT NULL,
  `begin_date` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `first_letter` varchar(1) DEFAULT NULL,
  `uuid` varchar(255) DEFAULT NULL,
  `policy_id` int(11) DEFAULT NULL,
  `contributor_id` int(11) DEFAULT NULL,
  `other_creators` text DEFAULT NULL,
  `deleted_contributor` varchar(255) DEFAULT NULL,
  `position` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `investigations`
--

DROP TABLE IF EXISTS `investigations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `investigations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `first_letter` varchar(1) DEFAULT NULL,
  `uuid` varchar(255) DEFAULT NULL,
  `policy_id` int(11) DEFAULT NULL,
  `contributor_id` int(11) DEFAULT NULL,
  `other_creators` text DEFAULT NULL,
  `deleted_contributor` varchar(255) DEFAULT NULL,
  `position` int(11) DEFAULT NULL,
  `is_isa_json_compliant` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `investigations_projects`
--

DROP TABLE IF EXISTS `investigations_projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `investigations_projects` (
  `project_id` int(11) DEFAULT NULL,
  `investigation_id` int(11) DEFAULT NULL,
  KEY `index_investigations_projects_inv_proj_id` (`investigation_id`,`project_id`) USING BTREE,
  KEY `index_investigations_projects_on_project_id` (`project_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sops`
--

DROP TABLE IF EXISTS `sops`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sops` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `contributor_id` int(11) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `version` int(11) DEFAULT 1,
  `first_letter` varchar(1) DEFAULT NULL,
  `other_creators` text DEFAULT NULL,
  `uuid` varchar(255) DEFAULT NULL,
  `policy_id` int(11) DEFAULT NULL,
  `doi` varchar(255) DEFAULT NULL,
  `license` varchar(255) DEFAULT NULL,
  `deleted_contributor` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index_sops_on_contributor` (`contributor_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=421 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projects_sops`
--

DROP TABLE IF EXISTS `projects_sops`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projects_sops` (
  `project_id` int(11) DEFAULT NULL,
  `sop_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `institutions`
--

DROP TABLE IF EXISTS `institutions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `institutions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `web_page` text DEFAULT NULL,
  `country` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `avatar_id` int(11) DEFAULT NULL,
  `first_letter` varchar(1) DEFAULT NULL,
  `uuid` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `work_groups`
--

DROP TABLE IF EXISTS `work_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `work_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `institution_id` int(11) DEFAULT NULL,
  `project_id` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index_work_groups_on_project_id` (`project_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=89 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `group_memberships`
--

DROP TABLE IF EXISTS `group_memberships`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `group_memberships` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `person_id` int(11) DEFAULT NULL,
  `work_group_id` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `time_left_at` datetime DEFAULT NULL,
  `has_left` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `index_group_memberships_on_person_id` (`person_id`) USING BTREE,
  KEY `index_group_memberships_on_work_group_id_and_person_id` (`work_group_id`,`person_id`) USING BTREE,
  KEY `index_group_memberships_on_work_group_id` (`work_group_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=380 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `people`
--

DROP TABLE IF EXISTS `people`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `people` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `first_name` varchar(255) DEFAULT NULL,
  `last_name` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(255) DEFAULT NULL,
  `skype_name` varchar(255) DEFAULT NULL,
  `web_page` text DEFAULT NULL,
  `description` text DEFAULT NULL,
  `avatar_id` int(11) DEFAULT NULL,
  `status_id` int(11) DEFAULT 0,
  `first_letter` varchar(10) DEFAULT NULL,
  `uuid` varchar(255) DEFAULT NULL,
  `roles_mask` int(11) DEFAULT 0,
  `orcid` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `login` varchar(255) DEFAULT NULL,
  `crypted_password` varchar(64) DEFAULT NULL,
  `salt` varchar(40) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `remember_token` varchar(255) DEFAULT NULL,
  `remember_token_expires_at` datetime DEFAULT NULL,
  `activation_code` varchar(40) DEFAULT NULL,
  `activated_at` datetime DEFAULT NULL,
  `person_id` int(11) DEFAULT NULL,
  `reset_password_code` varchar(255) DEFAULT NULL,
  `reset_password_code_until` datetime DEFAULT NULL,
  `posts_count` int(11) DEFAULT 0,
  `last_seen_at` datetime DEFAULT NULL,
  `uuid` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `publications`
--

DROP TABLE IF EXISTS `publications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `publications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pubmed_id` int(11) DEFAULT NULL,
  `title` text DEFAULT NULL,
  `abstract` text DEFAULT NULL,
  `published_date` date DEFAULT NULL,
  `journal` varchar(255) DEFAULT NULL,
  `first_letter` varchar(1) DEFAULT NULL,
  `contributor_id` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `doi` varchar(255) DEFAULT NULL,
  `uuid` varchar(255) DEFAULT NULL,
  `policy_id` int(11) DEFAULT NULL,
  `citation` text DEFAULT NULL,
  `deleted_contributor` varchar(255) DEFAULT NULL,
  `registered_mode` int(11) DEFAULT NULL,
  `booktitle` text DEFAULT NULL,
  `publisher` varchar(255) DEFAULT NULL,
  `editor` text DEFAULT NULL,
  `publication_type_id` int(11) DEFAULT NULL,
  `url` text DEFAULT NULL,
  `version` int(11) DEFAULT 1,
  `license` varchar(255) DEFAULT NULL,
  `other_creators` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index_publications_on_contributor` (`contributor_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projects_publications`
--

DROP TABLE IF EXISTS `projects_publications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projects_publications` (
  `project_id` int(11) DEFAULT NULL,
  `publication_id` int(11) DEFAULT NULL,
  KEY `index_projects_publications_on_project_id` (`project_id`) USING BTREE,
  KEY `index_projects_publications_on_publication_id_and_project_id` (`publication_id`,`project_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assay_assets`
--

DROP TABLE IF EXISTS `assay_assets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assay_assets` (
  `id` int(11) NOT NULL AUTO_INCREMENT
  `assay_id` int(11) DEFAULT NULL,
  `asset_id` int(11) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `relationship_type_id` int(11) DEFAULT NULL,
  `asset_type` varchar(255) DEFAULT NULL,
  `direction` int(11) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `index_assay_assets_on_assay_id` (`assay_id`) USING BTREE,
  KEY `index_assay_assets_on_asset_id_and_asset_type` (`asset_id`,`asset_type`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=234076 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-23 11:22:12
