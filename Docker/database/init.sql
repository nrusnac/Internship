-- Create tables for employee management system

-- Departments table
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100)
);

-- Employees table (references departments via foreign key)
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    salary DECIMAL(10, 2),
    hire_date DATE,
    department_id INTEGER NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- Insert sample departments
INSERT INTO departments (name, location) VALUES
    ('Engineering', 'New York'),
    ('Sales', 'Los Angeles'),
    ('Marketing', 'Chicago'),
    ('HR', 'New York');

-- Insert sample employees
INSERT INTO employees (name, email, salary, hire_date, department_id) VALUES
    ('Alice Johnson', 'alice@company.com', 95000.00, '2022-01-15', 1),
    ('Bob Smith', 'bob@company.com', 85000.00, '2022-03-20', 1),
    ('Carol White', 'carol@company.com', 75000.00, '2022-06-10', 2),
    ('David Brown', 'david@company.com', 70000.00, '2023-01-05', 2),
    ('Emma Davis', 'emma@company.com', 65000.00, '2023-02-14', 3),
    ('Frank Miller', 'frank@company.com', 60000.00, '2023-03-01', 4);

-- Create predictions table for ML model results
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    input_data TEXT NOT NULL,
    prediction_result TEXT NOT NULL,
    confidence DECIMAL(5, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
