-- One-shot schema for local MySQL (Docker). Safe to re-run: drops and recreates.

CREATE DATABASE IF NOT EXISTS event_sync
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE event_sync;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS conflicts;
DROP TABLE IF EXISTS meetings;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE meetings (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  crm_id VARCHAR(64) NULL,
  event_id VARCHAR(64) NULL,
  sources JSON NOT NULL,
  title VARCHAR(512) NOT NULL,
  client_name VARCHAR(255) NULL,
  client_company VARCHAR(255) NULL,
  relationship_owner VARCHAR(255) NULL,
  organizer VARCHAR(255) NULL,
  attendees JSON NULL,
  start_time DATETIME NULL,
  end_time DATETIME NULL,
  meeting_type VARCHAR(64) NULL,
  location VARCHAR(512) NULL,
  is_recurring TINYINT(1) NULL,
  status VARCHAR(64) NOT NULL,
  notes TEXT NULL,
  description TEXT NULL,
  created_at DATETIME NULL,
  has_conflict TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uq_meetings_crm_id (crm_id),
  UNIQUE KEY uq_meetings_event_id (event_id),
  KEY idx_meetings_start_time (start_time),
  KEY idx_meetings_has_conflict (has_conflict)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE conflicts (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  meeting_id INT UNSIGNED NOT NULL,
  field VARCHAR(64) NOT NULL,
  crm_value JSON NULL,
  calendar_value JSON NULL,
  chosen JSON NULL,
  reason TEXT NOT NULL,
  PRIMARY KEY (id),
  KEY idx_conflicts_meeting_id (meeting_id),
  CONSTRAINT fk_conflicts_meeting
    FOREIGN KEY (meeting_id) REFERENCES meetings (id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
