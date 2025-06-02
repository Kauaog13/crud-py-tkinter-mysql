CREATE DATABASE IF NOT EXISTS facsenac DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE facsenac;

CREATE TABLE IF NOT EXISTS alunos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    sobrenome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    cpf VARCHAR(14) UNIQUE,     
    data_nascimento DATE,        
    cidade VARCHAR(100) DEFAULT 'Brasília',
    uf VARCHAR(2) DEFAULT 'DF',
    curso ENUM('ADS', 'GTI', 'CD', 'IA', 'BI', 'SI') NOT NULL
);

-- Inserir alguns dados de exemplo:
-- INSERT INTO alunos (nome, sobrenome, telefone, email, cpf, data_nascimento, cidade, uf, curso) VALUES
-- ('Ana', 'Silva', '61999998888', 'ana.silva@email.com', '111.222.333-44', '2000-10-15', 'Brasília', 'DF', 'ADS'),
-- ('Bruno', 'Costa', '61988887777', 'bruno.costa@email.com', '555.666.777-88', '1999-05-20', 'Gama', 'DF', 'GTI');