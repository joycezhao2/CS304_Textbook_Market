use textbooks_db;

load data local infile 'courses.csv' 
into table courses
fields terminated by ',' 
(department, number)
lines terminated by '\n';
