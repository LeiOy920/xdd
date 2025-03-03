CREATE DATABASE IF NOT EXISTS MovieDB;
USE MovieDB;
CREATE TABLE moviedetail (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Primary key, auto increment',
    movie_image TEXT COMMENT 'Path to the movie image',
    movie_name VARCHAR(255) NOT NULL COMMENT 'Movie title',
    director VARCHAR(255) COMMENT 'Director of the movie',
    screenwriter TEXT COMMENT 'Screenwriter(s)',
    starring TEXT COMMENT 'Main actors/actresses',
    genre VARCHAR(255) COMMENT 'Genre of the movie',
    production_country_region VARCHAR(255) COMMENT 'Production country or region',
    language VARCHAR(255) COMMENT 'Language of the movie',
    release_date DATE COMMENT 'Release date',
    runtime INT COMMENT 'Duration of the movie in minutes',
    also_known_as TEXT COMMENT 'Alternative titles',
    douban_rating DECIMAL(3, 1) COMMENT 'Douban rating score',
    review_file_path TEXT COMMENT 'Path to the review file'
);

CREATE TABLE sentiment_score (
    id INT AUTO_INCREMENT PRIMARY KEY,
    m_id INT COMMENT 'Foreign key referencing moviedetail(id)',
    very_like INT DEFAULT 0 COMMENT 'Number of very like votes',
    s_like INT DEFAULT 0 COMMENT 'Number of like votes',
    normal INT DEFAULT 0 COMMENT 'Number of neutral votes',
    dislike INT DEFAULT 0 COMMENT 'Number of dislike votes',
    very_dislike INT DEFAULT 0 COMMENT 'Number of very dislike votes',
    total_references INT DEFAULT 0 COMMENT 'Total number of references',
    average_score DECIMAL(3, 2),
    FOREIGN KEY (m_id) REFERENCES moviedetail(id)
);

CREATE TABLE rankings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ranking_type VARCHAR(255) COMMENT 'Type of ranking',
    r_rank INT COMMENT 'Ranking position',
    movie_name VARCHAR(255) COMMENT 'Name of the movie',
    quantity DECIMAL(10, 2) COMMENT 'Quantity (box office amount or rating count)'
);

CREATE TABLE box_office_trend (
    id INT AUTO_INCREMENT PRIMARY KEY,
    m_id INT COMMENT 'Foreign key referencing moviedetail(id)',
    date DATE COMMENT 'Date',
    quantity DECIMAL(15, 2) COMMENT 'Box office quantity',
    FOREIGN KEY (m_id) REFERENCES moviedetail(id)
);

CREATE TABLE map_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    region VARCHAR(255) COMMENT 'Region name',
    m_rank INT COMMENT 'Ranking in the region',
    movie_name VARCHAR(255) COMMENT 'Name of the movie',
    rating DECIMAL(3, 1) COMMENT 'Rating in this region'
);

CREATE TABLE person (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) COMMENT 'Person name',
    box_office_amount DECIMAL(15, 2) COMMENT 'Total box office amount',
    movie_count INT COMMENT 'Number of movies involved',
    age INT COMMENT 'Age',
    gender ENUM('Male', 'Female') COMMENT 'Gender',
    constellation VARCHAR(50) COMMENT 'Constellation',
    graduate_school VARCHAR(255) COMMENT 'Graduated school',
    career TEXT COMMENT 'Career path'
);

CREATE TABLE die_graph_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_name VARCHAR(255) COMMENT 'Data name',
    chart_type VARCHAR(255) COMMENT 'Chart type',
    data_file_path TEXT COMMENT 'Path to the data file'
);

