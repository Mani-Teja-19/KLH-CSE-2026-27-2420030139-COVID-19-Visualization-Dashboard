-- =======================================================
-- COVID-19 VISUALIZATION DASHBOARD - DATABASE SCHEMA
-- Compatible with MySQL 5.7+ / MySQL 8.0+ / MariaDB
-- =======================================================

CREATE DATABASE IF NOT EXISTS `covid19_dashboard` 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `covid19_dashboard`;

SET FOREIGN_KEY_CHECKS = 0;

-- 1. USERS TABLE
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(80) NOT NULL UNIQUE,
  `email` VARCHAR(120) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `full_name` VARCHAR(120) NOT NULL,
  `role` VARCHAR(50) DEFAULT 'Admin',
  `phone` VARCHAR(20) NULL,
  `avatar` VARCHAR(255) DEFAULT 'default-avatar.png',
  `is_active` BOOLEAN DEFAULT TRUE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `last_login` DATETIME NULL,
  INDEX idx_users_username (`username`),
  INDEX idx_users_email (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. PLACES TABLE
DROP TABLE IF EXISTS `places`;
CREATE TABLE `places` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `place_name` VARCHAR(150) NOT NULL,
  `village_city` VARCHAR(150) NOT NULL,
  `mandal_taluk` VARCHAR(150) NOT NULL,
  `district` VARCHAR(150) NOT NULL,
  `state` VARCHAR(100) NOT NULL DEFAULT 'Maharashtra',
  `pincode` VARCHAR(20) NOT NULL,
  `total_population` INT DEFAULT 0,
  `total_families` INT DEFAULT 0,
  `affected_status` VARCHAR(50) DEFAULT 'Not Affected',
  `positive_cases` INT DEFAULT 0,
  `active_cases` INT DEFAULT 0,
  `recovered_cases` INT DEFAULT 0,
  `death_cases` INT DEFAULT 0,
  `vaccinated_count` INT DEFAULT 0,
  `not_vaccinated_count` INT DEFAULT 0,
  `last_updated` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_places_district (`district`),
  INDEX idx_places_status (`affected_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. MEMBERS TABLE
DROP TABLE IF EXISTS `members`;
CREATE TABLE `members` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `member_code` VARCHAR(50) NOT NULL UNIQUE,
  `full_name` VARCHAR(150) NOT NULL,
  `age` INT NOT NULL,
  `gender` VARCHAR(20) NOT NULL,
  `dob` DATE NULL,
  `mobile_number` VARCHAR(20) NOT NULL,
  `email` VARCHAR(120) NULL,
  `aadhaar_number` VARCHAR(30) NULL,
  `address` TEXT NULL,
  `place_id` INT NULL,
  `occupation` VARCHAR(100) NULL,
  `covid_status` VARCHAR(50) DEFAULT 'Negative',
  `infection_date` DATE NULL,
  `recovery_date` DATE NULL,
  `vaccination_status` VARCHAR(50) DEFAULT 'Not Vaccinated',
  `vaccine_name` VARCHAR(100) NULL,
  `dose1_date` DATE NULL,
  `dose2_date` DATE NULL,
  `booster_date` DATE NULL,
  `hospital_name` VARCHAR(150) NULL,
  `doctor_name` VARCHAR(120) NULL,
  `medical_remarks` TEXT NULL,
  `photo_url` VARCHAR(255) DEFAULT 'default-user.png',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_members_code (`member_code`),
  INDEX idx_members_covid_status (`covid_status`),
  INDEX idx_members_vaccination (`vaccination_status`),
  FOREIGN KEY (`place_id`) REFERENCES `places` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. COVID CASES TABLE
DROP TABLE IF EXISTS `covid_cases`;
CREATE TABLE `covid_cases` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `case_code` VARCHAR(50) NOT NULL UNIQUE,
  `member_id` INT NOT NULL,
  `place_id` INT NULL,
  `admission_date` DATE NOT NULL,
  `covid_variant` VARCHAR(50) DEFAULT 'Delta / Omicron',
  `symptoms` VARCHAR(255) NULL,
  `ct_score` VARCHAR(50) NULL,
  `severity` VARCHAR(50) DEFAULT 'Moderate',
  `quarantine_status` VARCHAR(50) DEFAULT 'Home Isolation',
  `ward_bed_no` VARCHAR(50) NULL,
  `assigned_doctor` VARCHAR(120) NULL,
  `recovery_date` DATE NULL,
  `death_date` DATE NULL,
  `notes` TEXT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_cases_quarantine (`quarantine_status`),
  INDEX idx_cases_severity (`severity`),
  FOREIGN KEY (`member_id`) REFERENCES `members` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`place_id`) REFERENCES `places` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. VACCINATIONS TABLE
DROP TABLE IF EXISTS `vaccinations`;
CREATE TABLE `vaccinations` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `member_id` INT NOT NULL,
  `dose_number` INT NOT NULL,
  `vaccine_name` VARCHAR(100) NOT NULL,
  `vaccination_date` DATE NOT NULL,
  `center_name` VARCHAR(150) NOT NULL,
  `batch_number` VARCHAR(80) NULL,
  `vaccinated_by` VARCHAR(120) NULL,
  `certificate_no` VARCHAR(100) NOT NULL UNIQUE,
  `next_due_date` DATE NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`member_id`) REFERENCES `members` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. HOSPITALS TABLE
DROP TABLE IF EXISTS `hospitals`;
CREATE TABLE `hospitals` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(150) NOT NULL,
  `district` VARCHAR(150) NOT NULL,
  `state` VARCHAR(100) DEFAULT 'Maharashtra',
  `total_beds` INT DEFAULT 100,
  `occupied_beds` INT DEFAULT 0,
  `icu_beds` INT DEFAULT 20,
  `occupied_icu` INT DEFAULT 0,
  `oxygen_cylinders` INT DEFAULT 50,
  `helpline` VARCHAR(50) NULL,
  `address` TEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. NOTIFICATIONS TABLE
DROP TABLE IF EXISTS `notifications`;
CREATE TABLE `notifications` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `title` VARCHAR(150) NOT NULL,
  `message` TEXT NOT NULL,
  `category` VARCHAR(50) DEFAULT 'General',
  `alert_level` VARCHAR(20) DEFAULT 'Medium',
  `is_read` BOOLEAN DEFAULT FALSE,
  `target_url` VARCHAR(255) NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. ACTIVITY LOGS TABLE
DROP TABLE IF EXISTS `activity_logs`;
CREATE TABLE `activity_logs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NULL,
  `action` VARCHAR(100) NOT NULL,
  `module` VARCHAR(80) NOT NULL,
  `details` TEXT NULL,
  `ip_address` VARCHAR(50) NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. SETTINGS TABLE
DROP TABLE IF EXISTS `settings`;
CREATE TABLE `settings` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `setting_key` VARCHAR(100) NOT NULL UNIQUE,
  `setting_value` TEXT NOT NULL,
  `description` VARCHAR(255) NULL,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
