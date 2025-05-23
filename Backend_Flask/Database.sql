CREATE DATABASE IF NOT EXISTS splash_rocket;
USE splash_rocket;

CREATE TABLE IF NOT EXISTS rankings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(64) NOT NULL UNIQUE,
    username VARCHAR(255) NOT NULL,
    score INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
