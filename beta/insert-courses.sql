
use textbooks_db;

load data local infile 'courses.csv' 
into table courses
fields terminated by ',' 
lines terminated by '\n'
(department, number);
