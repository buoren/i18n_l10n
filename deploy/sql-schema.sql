-- Database Schema for i18n-l10n application
-- This file contains the SQL DDL for creating all tables

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS i18n_l10n_db;
USE i18n_l10n_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Greetings table
CREATE TABLE IF NOT EXISTS greetings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    greeting_text TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45) NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- Counters table
CREATE TABLE IF NOT EXISTS counters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    counter_value INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_session_id (session_id)
);

-- Translation tags table
CREATE TABLE IF NOT EXISTS translation_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application VARCHAR(255) NOT NULL,
    tag TEXT NOT NULL,
    context VARCHAR(500) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_application (application)
);

-- Translations table
CREATE TABLE IF NOT EXISTS translations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    translation_tag_id INT NOT NULL,
    language ENUM(
        'en-US', 'en-GB', 'es-ES', 'es-MX', 'fr-FR', 'fr-CA', 'de-DE', 'it-IT',
        'pt-BR', 'pt-PT', 'ru-RU', 'ja-JP', 'ko-KR', 'zh-CN', 'zh-TW', 'ar-SA',
        'hi-IN', 'nl-NL', 'sv-SE', 'no-NO', 'da-DK', 'fi-FI', 'pl-PL', 'cs-CZ',
        'hu-HU', 'ro-RO', 'bg-BG', 'hr-HR', 'sk-SK', 'sl-SI', 'et-EE', 'lv-LV',
        'lt-LT', 'el-GR', 'tr-TR', 'uk-UA', 'th-TH', 'vi-VN', 'id-ID', 'ms-MY',
        'tl-PH'
    ) NOT NULL,
    text TEXT NOT NULL,
    is_plural BOOLEAN DEFAULT FALSE,
    plural_form VARCHAR(50) NULL,
    author_id INT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_translation_tag_id (translation_tag_id),
    INDEX idx_language (language),
    INDEX idx_active (is_active),
    UNIQUE KEY unique_translation (translation_tag_id, language, plural_form)
);

-- API Keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    key VARCHAR(255) NOT NULL UNIQUE,
    description VARCHAR(255) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INT NULL,
    application VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at DATETIME NULL,
    last_used_at DATETIME NULL,
    INDEX idx_key (key),
    INDEX idx_user_id (user_id),
    INDEX idx_application (application),
    INDEX idx_active (is_active)
);

-- Insert some initial translation tags
INSERT IGNORE INTO translation_tags (application, tag, context) VALUES
('i18n-l10n-app', 'Hello World', 'Main greeting message displayed on the homepage'),
('i18n-l10n-app', 'Welcome to the i18n/l10n Testing App', 'Subtitle explaining the purpose of the application'),
('i18n-l10n-app', 'Your Name', 'Label for the name input field'),
('i18n-l10n-app', 'Enter your name here...', 'Placeholder text for the name input field'),
('i18n-l10n-app', 'Say Hello', 'Button text to trigger greeting'),
('i18n-l10n-app', 'Click Counter', 'Section title for the counter functionality'),
('i18n-l10n-app', 'Reset', 'Button text to reset the counter'),
('i18n-l10n-app', 'Recent Greetings', 'Section title for displaying recent greetings'),
('i18n-l10n-app', 'Language Selection', 'Section title for language selection'),
('i18n-l10n-app', 'Coming Soon', 'Placeholder text for future features'),
('i18n-l10n-app', 'Database connected and storing data', 'Status message indicating database connectivity'),
('i18n-l10n-app', 'Built with ❤️ using NiceGUI + MySQL', 'Footer message showing technology stack'),
('i18n-l10n-app', 'Refresh Greetings', 'Button text to refresh the greetings list'),
('i18n-l10n-app', 'No greetings yet', 'Message shown when no greetings are available');

-- Insert sample translations for "Hello World"
INSERT IGNORE INTO translations (translation_tag_id, language, text) VALUES
((SELECT id FROM translation_tags WHERE tag = 'Hello World' AND application = 'i18n-l10n-app'), 'en-US', 'Hello World'),
((SELECT id FROM translation_tags WHERE tag = 'Hello World' AND application = 'i18n-l10n-app'), 'es-ES', 'Hola Mundo'),
((SELECT id FROM translation_tags WHERE tag = 'Hello World' AND application = 'i18n-l10n-app'), 'fr-FR', 'Bonjour le Monde'),
((SELECT id FROM translation_tags WHERE tag = 'Hello World' AND application = 'i18n-l10n-app'), 'de-DE', 'Hallo Welt'),
((SELECT id FROM translation_tags WHERE tag = 'Hello World' AND application = 'i18n-l10n-app'), 'it-IT', 'Ciao Mondo'),
((SELECT id FROM translation_tags WHERE tag = 'Hello World' AND application = 'i18n-l10n-app'), 'pt-BR', 'Olá Mundo'),
((SELECT id FROM translation_tags WHERE tag = 'Hello World' AND application = 'i18n-l10n-app'), 'ru-RU', 'Привет, мир'),
((SELECT id FROM translation_tags WHERE tag = 'Hello World' AND application = 'i18n-l10n-app'), 'ja-JP', 'こんにちは世界'),
((SELECT id FROM translation_tags WHERE tag = 'Hello World' AND application = 'i18n-l10n-app'), 'ko-KR', '안녕하세요 세계'),
((SELECT id FROM translation_tags WHERE tag = 'Hello World' AND application = 'i18n-l10n-app'), 'zh-CN', '你好世界');

-- Show created tables
SHOW TABLES;

-- Show sample data
SELECT 'Translation Tags:' as info;
SELECT * FROM translation_tags LIMIT 5;

SELECT 'Sample Translations:' as info;
SELECT t.tag, tr.language, tr.text 
FROM translation_tags t 
JOIN translations tr ON t.id = tr.translation_tag_id 
WHERE t.tag = 'Hello World' 
LIMIT 10;
