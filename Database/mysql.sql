CREATE DATABASE IF NOT EXISTS employees;
USE employees;

CREATE TABLE IF NOT EXISTS employee(
	  Emp_id VARCHAR(20), 
	  First_name VARCHAR(20), 
	  Last_name VARCHAR(20), 
	  primary_skill VARCHAR(50), 
	  location VARCHAR(20) 
	);

	INSERT INTO employee VALUES ('1', 'Sarthak', 'Shah', 'java', 'mars');
	INSERT INTO employee VALUES ('2', 'darshan', 'modi', '.net', 'sun');
	INSERT INTO employee VALUES ('3', 'dixit', 'italiya', 'data', 'saturn');

	SELECT * FROM employee;
