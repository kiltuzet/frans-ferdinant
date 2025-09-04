-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: bus_depot
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `bus_assignments`
--

DROP TABLE IF EXISTS `bus_assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bus_assignments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_bus` int NOT NULL,
  `id_route` int NOT NULL,
  `assignment_date` date NOT NULL,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `status` enum('scheduled','in_progress','completed','cancelled') DEFAULT 'scheduled',
  PRIMARY KEY (`id`),
  KEY `id_bus` (`id_bus`),
  KEY `id_route` (`id_route`),
  CONSTRAINT `bus_assignments_ibfk_1` FOREIGN KEY (`id_bus`) REFERENCES `buses` (`id`) ON DELETE CASCADE,
  CONSTRAINT `bus_assignments_ibfk_2` FOREIGN KEY (`id_route`) REFERENCES `routes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bus_assignments`
--

LOCK TABLES `bus_assignments` WRITE;
/*!40000 ALTER TABLE `bus_assignments` DISABLE KEYS */;
INSERT INTO `bus_assignments` VALUES (1,1,1,'2023-04-01','06:00:00','14:00:00','completed'),(2,2,2,'2023-04-01','06:00:00','14:00:00','completed'),(3,3,3,'2023-04-01','06:00:00','14:00:00','completed'),(4,4,9,'2023-04-02','05:00:00','07:00:00','completed'),(5,5,10,'2023-04-02','06:30:00','08:30:00','completed'),(6,6,11,'2023-04-02','07:00:00','11:00:00','completed'),(7,7,12,'2023-04-02','08:00:00','12:00:00','completed'),(8,8,13,'2023-04-02','09:00:00','13:30:00','completed'),(9,4,9,'2023-04-03','05:00:00','07:00:00','scheduled'),(10,5,10,'2023-04-03','06:30:00','08:30:00','scheduled'),(11,6,11,'2023-04-03','07:00:00','11:00:00','scheduled'),(12,7,12,'2023-04-03','08:00:00','12:00:00','scheduled'),(13,8,13,'2023-04-03','09:00:00','13:30:00','scheduled');
/*!40000 ALTER TABLE `bus_assignments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `buses`
--

DROP TABLE IF EXISTS `buses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `buses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `mark` varchar(50) NOT NULL,
  `model` varchar(50) NOT NULL,
  `year` int DEFAULT NULL,
  `capacity` int NOT NULL,
  `id_driver` int DEFAULT NULL,
  `registration_number` varchar(20) NOT NULL,
  `status` enum('active','maintenance','decommissioned') DEFAULT 'active',
  PRIMARY KEY (`id`),
  UNIQUE KEY `registration_number` (`registration_number`),
  KEY `id_driver` (`id_driver`),
  KEY `idx_search_buses` (`mark`,`model`,`registration_number`),
  CONSTRAINT `buses_ibfk_1` FOREIGN KEY (`id_driver`) REFERENCES `drivers` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `buses`
--

LOCK TABLES `buses` WRITE;
/*!40000 ALTER TABLE `buses` DISABLE KEYS */;
INSERT INTO `buses` VALUES (1,'ПАЗ','3205',2018,35,1,'А123БВ777','active'),(2,'ЛиАЗ','5256',2020,80,2,'В456ТУ777','active'),(3,'МАЗ','103',2019,70,3,'Е789КХ777','active'),(4,'МАЗ','107',2021,60,4,'А111АА777','active'),(5,'Setra','S 416',2020,50,5,'В222ВВ777','active'),(6,'Mercedes','Sprinter',2022,20,6,'Е333ЕЕ777','active'),(7,'Volvo','9700',2019,55,7,'К444КК777','active'),(8,'НефАЗ','5299',2021,90,8,'М555ММ777','active'),(9,'ПАЗ','4234',2020,45,7,'Н666НН777','active'),(10,'Scania','Touring',2022,60,6,'О777ОО777','active'),(11,'MAN','Lion\'s Coach',2021,58,6,'Р888РР777','active');
/*!40000 ALTER TABLE `buses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `drivers`
--

DROP TABLE IF EXISTS `drivers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drivers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `license_number` varchar(20) NOT NULL,
  `employee_number` varchar(20) NOT NULL,
  `birth_date` date DEFAULT NULL,
  `hire_date` date NOT NULL,
  `status` enum('active','vacation','sick_leave','fired') DEFAULT 'active',
  PRIMARY KEY (`id`),
  UNIQUE KEY `license_number` (`license_number`),
  UNIQUE KEY `employee_number` (`employee_number`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drivers`
--

LOCK TABLES `drivers` WRITE;
/*!40000 ALTER TABLE `drivers` DISABLE KEYS */;
INSERT INTO `drivers` VALUES (1,'Иван','Иванов','AB123456','D001','1980-05-15','2015-03-10','active'),(2,'Петр','Петров','CD654321','D002','1985-07-22','2018-11-05','active'),(3,'Сергей','Сидоров','EF789012','D003','1978-12-30','2012-09-18','active'),(4,'Алексей','Смирнов','GH456789','D004','1982-03-25','2019-05-12','active'),(5,'Дмитрий','Кузнецов','IJ987654','D005','1987-11-08','2020-07-22','active'),(6,'Михаил','Попов','KL654321','D006','1979-09-14','2017-02-18','active'),(7,'Андрей','Васильев','MN321654','D007','1984-06-30','2021-01-15','active'),(8,'Николай','Петров','OP789456','D008','1981-04-12','2018-08-05','active');
/*!40000 ALTER TABLE `drivers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inspections`
--

DROP TABLE IF EXISTS `inspections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inspections` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_bus` int NOT NULL,
  `inspection_date` date NOT NULL,
  `next_inspection_date` date NOT NULL,
  `result` tinyint(1) NOT NULL,
  `comments` text,
  PRIMARY KEY (`id`),
  KEY `id_bus` (`id_bus`),
  CONSTRAINT `inspections_ibfk_1` FOREIGN KEY (`id_bus`) REFERENCES `buses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inspections`
--

LOCK TABLES `inspections` WRITE;
/*!40000 ALTER TABLE `inspections` DISABLE KEYS */;
INSERT INTO `inspections` VALUES (1,1,'2023-01-15','2023-07-15',1,'Заменены тормозные колодки, проверка системы отопления'),(2,2,'2023-02-20','2023-08-20',1,'Проверка двигателя, замена масла'),(3,3,'2023-03-10','2023-09-10',0,'Требуется замена фар, проверка тормозной системы');
/*!40000 ALTER TABLE `inspections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `passengers`
--

DROP TABLE IF EXISTS `passengers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `passengers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_route` int DEFAULT NULL,
  `departure_stop_id` int DEFAULT NULL,
  `arrival_stop_id` int DEFAULT NULL,
  `boarding_time` datetime DEFAULT NULL,
  `disembarkation_time` datetime DEFAULT NULL,
  `ticket_number` varchar(20) DEFAULT NULL,
  `fare` decimal(6,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_route` (`id_route`),
  KEY `fk_departure_stop` (`departure_stop_id`),
  KEY `fk_arrival_stop` (`arrival_stop_id`),
  CONSTRAINT `fk_arrival_stop` FOREIGN KEY (`arrival_stop_id`) REFERENCES `stops` (`id`),
  CONSTRAINT `fk_departure_stop` FOREIGN KEY (`departure_stop_id`) REFERENCES `stops` (`id`),
  CONSTRAINT `passengers_ibfk_1` FOREIGN KEY (`id_route`) REFERENCES `routes` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=145 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `passengers`
--

LOCK TABLES `passengers` WRITE;
/*!40000 ALTER TABLE `passengers` DISABLE KEYS */;
INSERT INTO `passengers` VALUES (1,2,NULL,NULL,'2025-06-24 16:01:30',NULL,'TKT-2-4-3',16.60),(2,10,NULL,NULL,'2025-06-25 12:39:08',NULL,'TKT-10-1-18',76.40),(3,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(4,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(5,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(6,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(7,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(8,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(9,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(10,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(11,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(12,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(13,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(14,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(15,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(16,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(17,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(18,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(19,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(20,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(21,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(22,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(23,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(24,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(25,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(26,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(27,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(28,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(29,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(30,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(31,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(32,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(33,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(34,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(35,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(36,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(37,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(38,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(39,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(40,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(41,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(42,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(43,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(44,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(45,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(46,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(47,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(48,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(49,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(50,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(51,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(52,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(53,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(54,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(55,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(56,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(57,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(58,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(59,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(60,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(61,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(62,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(63,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(64,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(65,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(66,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(67,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(68,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(69,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(70,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(71,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(72,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(73,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(74,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(75,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(76,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(77,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(78,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(79,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(80,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(81,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(82,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(83,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(84,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(85,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(86,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(87,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(88,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(89,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(90,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(91,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(92,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(93,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(94,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(95,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(96,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(97,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(98,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(99,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(100,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(101,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(102,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(103,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(104,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(105,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(106,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(107,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(108,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(109,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(110,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(111,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(112,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(113,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(114,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(115,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(116,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(117,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(118,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(119,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(120,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(121,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(122,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(123,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(124,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(125,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(126,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(127,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(128,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(129,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(130,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(131,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(132,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(133,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(134,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(135,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(136,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(137,10,NULL,NULL,'2025-06-27 15:02:40',NULL,'TKT-10-1-17',76.40),(138,13,NULL,NULL,'2025-06-25 16:29:50',NULL,'TKT-13-1-24',400.00),(139,13,NULL,NULL,'2025-06-25 16:29:50',NULL,'TKT-13-1-24',400.00),(140,13,NULL,NULL,'2025-06-25 16:29:50',NULL,'TKT-13-1-24',400.00),(141,13,NULL,NULL,'2025-06-25 16:29:50',NULL,'TKT-13-1-24',400.00),(142,10,NULL,NULL,'2025-06-25 16:32:03',NULL,'TKT-10-1-17',360.00),(143,10,NULL,NULL,'2025-06-25 16:32:03',NULL,'TKT-10-1-17',360.00),(144,10,NULL,NULL,'2025-06-25 16:32:03',NULL,'TKT-10-1-17',360.00);
/*!40000 ALTER TABLE `passengers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `route_stops`
--

DROP TABLE IF EXISTS `route_stops`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `route_stops` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_route` int NOT NULL,
  `id_stop` int NOT NULL,
  `stop_order` int NOT NULL,
  `arrival_time` time DEFAULT NULL,
  `departure_time` time DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_route` (`id_route`,`id_stop`),
  KEY `id_stop` (`id_stop`),
  CONSTRAINT `route_stops_ibfk_1` FOREIGN KEY (`id_route`) REFERENCES `routes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `route_stops_ibfk_2` FOREIGN KEY (`id_stop`) REFERENCES `stops` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `route_stops`
--

LOCK TABLES `route_stops` WRITE;
/*!40000 ALTER TABLE `route_stops` DISABLE KEYS */;
INSERT INTO `route_stops` VALUES (1,1,1,1,'06:00:00','06:05:00'),(2,1,2,2,'06:15:00','06:17:00'),(3,2,3,1,'06:10:00','06:12:00'),(4,2,4,2,'06:30:00','06:32:00'),(5,3,1,1,'06:20:00','06:22:00'),(6,3,5,2,'06:35:00','06:37:00'),(7,4,6,1,'06:00:00','06:05:00'),(8,4,7,2,'06:15:00','06:17:00'),(9,4,1,3,'06:30:00','06:35:00'),(10,5,8,1,'06:10:00','06:12:00'),(11,5,9,2,'06:25:00','06:27:00'),(12,5,1,3,'06:40:00','06:45:00'),(13,6,4,1,'06:20:00','06:22:00'),(14,6,1,2,'06:40:00','06:42:00'),(15,6,2,3,'07:00:00','07:02:00'),(16,7,10,1,'06:30:00','06:32:00'),(17,7,11,2,'06:40:00','06:42:00'),(18,7,5,3,'06:50:00','06:52:00'),(19,8,12,1,'05:30:00','05:35:00'),(20,8,13,2,'05:45:00','05:47:00'),(21,8,1,3,'06:30:00','06:35:00'),(22,9,1,1,'05:00:00','05:05:00'),(23,9,15,2,'05:20:00','05:22:00'),(24,9,12,3,'05:40:00','06:00:00'),(25,9,16,4,'06:30:00','07:00:00'),(26,10,1,1,'06:30:00','06:35:00'),(27,10,17,2,'07:00:00','07:02:00'),(28,10,18,3,'07:30:00','08:00:00'),(29,11,1,1,'07:00:00','07:05:00'),(30,11,19,2,'08:30:00','08:32:00'),(31,11,20,3,'09:00:00','10:00:00'),(32,12,1,1,'08:00:00','08:05:00'),(33,12,21,2,'10:00:00','10:02:00'),(34,12,22,3,'11:00:00','12:00:00'),(35,13,1,1,'09:00:00','09:05:00'),(36,13,23,2,'11:30:00','11:32:00'),(37,13,24,3,'12:30:00','13:00:00'),(42,16,1,1,'06:00:00','06:05:00'),(43,16,5,2,'06:20:00','06:22:00'),(44,16,9,3,'06:40:00','06:42:00'),(45,16,14,4,'07:00:00','07:20:00'),(46,17,14,1,NULL,NULL),(47,17,28,2,NULL,NULL);
/*!40000 ALTER TABLE `route_stops` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `routes`
--

DROP TABLE IF EXISTS `routes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `routes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `route_number` varchar(10) NOT NULL,
  `route_name` varchar(100) NOT NULL,
  `description` text,
  `distance_km` decimal(6,2) DEFAULT NULL,
  `estimated_time_min` int DEFAULT NULL,
  `base_fare` decimal(6,2) DEFAULT '20.00',
  `is_regular` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Признак рейсового маршрута (1 - рейсовый, 0 - не рейсовый)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `route_number` (`route_number`),
  KEY `idx_search_routes` (`route_number`,`route_name`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `routes`
--

LOCK TABLES `routes` WRITE;
/*!40000 ALTER TABLE `routes` DISABLE KEYS */;
INSERT INTO `routes` VALUES (1,'1','Центр - Южный район','Основной городской маршрут через центр города',12.50,45,0.90,1),(2,'2','Вокзал - Северный микрорайон','Соединяет вокзал с жилыми районами',8.30,30,0.90,1),(3,'3','Кольцевой','Объезжает город по окружной дороге',15.70,55,0.90,1),(4,'4','Восточный экспресс','Связывает восточные районы с центром',10.20,35,0.90,1),(5,'5','Западный скоростной','Экспресс-маршрут в западные районы',14.70,50,0.90,1),(6,'6','Север-Юг','Прямое сообщение между северными и южными районами',18.30,65,0.90,1),(7,'7','Университетский','Обслуживает студенческие городки',8.90,30,0.90,1),(8,'8','Аэропорт-Центр','Связь аэропорта с городским центром',22.10,75,0.90,1),(9,'9','Экспресс в аэропорт','Скоростной маршрут в аэропорт Домодедово',42.50,70,150.00,0),(10,'10','Междугородний: Москва-Подольск','Регулярный междугородний маршрут',38.20,60,120.00,0),(11,'11','Междугородний: Москва-Серпухов','Регулярный междугородний маршрут',99.50,120,250.00,0),(12,'12','Междугородний: Москва-Тверь','Регулярный междугородний маршрут',167.80,180,350.00,0),(13,'13','Междугородний: Москва-Владимир','Регулярный междугородний маршрут',190.00,210,400.00,0),(16,'16','Объездная линия','Маршрут по объездной дороге',28.40,75,80.00,0),(17,'17','Витебск — Гостиница \"Аэропорт\"',NULL,NULL,NULL,20.00,0);
/*!40000 ALTER TABLE `routes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stops`
--

DROP TABLE IF EXISTS `stops`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stops` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `is_terminal` tinyint(1) NOT NULL DEFAULT '0',
  `address` varchar(255) NOT NULL,
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_search_stops` (`name`,`address`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stops`
--

LOCK TABLES `stops` WRITE;
/*!40000 ALTER TABLE `stops` DISABLE KEYS */;
INSERT INTO `stops` VALUES (1,'Центральная площадь',1,'ул. Ленина, 1',55.75582600,37.61730000),(2,'Южный рынок',0,'ул. Садовая, 25',55.74500000,37.62500000),(3,'Железнодорожный вокзал',1,'Привокзальная пл., 3',55.75000000,37.65000000),(4,'Северный микрорайон',1,'ул. Строителей, 15',55.77000000,37.60000000),(5,'Городская больница',0,'ул. Медиков, 7',55.76000000,37.62000000),(6,'Восточный вокзал',1,'ул. Восточная, 1',55.78000000,37.70000000),(7,'Торговый центр \"Восток\"',0,'ул. Магистральная, 15',55.77500000,37.69000000),(8,'Западные ворота',1,'ш. Западное, 5',55.74000000,37.55000000),(9,'Парк Победы',0,'ул. Парковая, 20',55.73500000,37.52000000),(10,'Университет',1,'пр. Науки, 1',55.73000000,37.58000000),(11,'Студенческий городок',0,'ул. Студенческая, 33',55.72500000,37.57000000),(12,'Аэропорт \"Северный\"',1,'Аэропорт',55.81000000,37.65000000),(13,'Гостиница \"Аэропорт\"',0,'ш. Аэропортовское, 10',55.80500000,37.64000000),(14,'Автовокзал \"Северный\"',1,'ул. Транспортная, 10',55.82000000,37.62000000),(15,'ТЦ \"Мегаполис\"',0,'ш. Энтузиастов, 12',55.71500000,37.73000000),(16,'Областная больница',0,'ул. Медицинская, 5',55.68000000,37.75000000),(17,'Городская администрация',0,'пл. Советская, 1',55.65000000,37.78000000),(18,'Ж/д станция \"Восточная\"',1,'ул. Вокзальная, 15',55.72000000,37.85000000),(19,'Аэропорт \"Домодедово\"',1,'Аэропорт Домодедово',55.40861100,37.90638900),(20,'Автовокзал \"Тушинский\"',1,'ул. Тушинская, 1',55.82666700,37.43611100),(21,'Автовокзал \"Щелковский\"',1,'Щелковское ш., 75',55.80944400,37.79888900),(22,'Автовокзал \"Южные ворота\"',1,'ул. Южнопортовая, 24',55.69805600,37.69361100),(23,'Город Подольск (Центр)',1,'пл. Ленина, 1',55.43194400,37.54527800),(24,'Город Серпухов (Вокзал)',1,'пл. Привокзальная, 3',54.91361100,37.41388900),(25,'Город Тверь (Центр)',1,'пл. Ленина, 1',56.85861100,35.91166700),(26,'Город Владимир (Автовокзал)',1,'ул. Вокзальная, 18',56.12805600,40.40583300),(27,'Город Ярославль (Центр)',1,'ул. Свободы, 45',57.62638900,39.89388900),(28,'Витебск',0,'город Витебск',55.17043908,30.22383410),(29,'таганка',0,'соответствующий',55.73992961,37.65755020);
/*!40000 ALTER TABLE `stops` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_permissions`
--

DROP TABLE IF EXISTS `user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `table_name` varchar(64) NOT NULL,
  `can_select` tinyint(1) NOT NULL DEFAULT '0',
  `can_insert` tinyint(1) NOT NULL DEFAULT '0',
  `can_update` tinyint(1) NOT NULL DEFAULT '0',
  `can_delete` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`table_name`),
  CONSTRAINT `user_permissions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_permissions`
--

LOCK TABLES `user_permissions` WRITE;
/*!40000 ALTER TABLE `user_permissions` DISABLE KEYS */;
INSERT INTO `user_permissions` VALUES (1,1,'*',1,1,1,1),(2,2,'route_stops',1,1,1,1),(3,2,'buses',1,1,1,1),(4,2,'bus_assignments',1,1,1,1),(5,2,'stops',1,1,1,1),(6,2,'routes',1,1,1,1);
/*!40000 ALTER TABLE `user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_types`
--

DROP TABLE IF EXISTS `user_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type_name` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `type_name` (`type_name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_types`
--

LOCK TABLES `user_types` WRITE;
/*!40000 ALTER TABLE `user_types` DISABLE KEYS */;
INSERT INTO `user_types` VALUES (1,'Администратор','Полный доступ ко всем функциям системы'),(2,'Диспетчер','Управление маршрутами и назначениями');
/*!40000 ALTER TABLE `user_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `login` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `id_type_user` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `login` (`login`),
  KEY `id_type_user` (`id_type_user`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`id_type_user`) REFERENCES `user_types` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','admin123',1,'2025-06-19 13:21:15'),(2,'manager','manager11',2,'2025-06-19 13:21:15');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-27 15:08:57
