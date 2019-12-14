use textbooks_db;

drop table if exists books;
drop table if exists courses;
drop table if exists users;

/* for all users, either a buyer or a seller */
create table users (
    username varchar(20) NOT NULL primary key,
    name varchar(50),
    email varchar(100),
    pic varchar(50),
    bio varchar(500),
)
engine = InnoDB;

/* for all courses differentiated by deparment, section and professor */
create table courses (
    id int auto_increment NOT NULL primary key,
    department varchar(4),
    number char(3)
)
engine = InnoDB;

/* for each book uploaded by the seller */
create table books (
    id int auto_increment NOT NULL primary key,
    price int,
    sold_status int(1),
    `condition` varchar(20),
    title int,
    author varchar(20),
    `description` varchar(500),
    seller varchar(20),
    course int,
    pic varchar(50),
    professor varchar(50),
    `year` varchar(4), 
    foreign key (course) references courses(id),
    foreign key (seller) references users(username)
)
engine = InnoDB;