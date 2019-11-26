use textbooks_db;

drop table if exists S_books;
drop table if exists A_book_course;
drop table if exists A_books;
drop table if exists courses;
drop table if exists users;


/* for all users, either a buyer or a seller */
create table users (
    username varchar(20) NOT NULL primary key,
    name varchar(50),
    email varchar(100),
    phnum varchar(10)
)
engine = InnoDB;

/* for all courses differentiated by deparment, section and professor */
create table courses (
    id int auto_increment NOT NULL primary key,
    department varchar(4),
    number char(3),
    professor varchar(50)
)
engine = InnoDB;

/* for the abstract book, each is associated with one course */
create table A_books (
    id int auto_increment primary key,
    title varchar(50),
    author varchar(30)
)
engine = InnoDB;

/* for each book uploaded by the seller */
create table S_books (
    id int auto_increment NOT NULL primary key,
    price int,
    sold_status int(1),
    `condition` varchar(20),
    title int,
    comments varchar(500),
    seller varchar(20),
    buyer varchar(20),
    book int,
    foreign key (book) references A_books(id),
    foreign key (seller) references users(username),
    foreign key (buyer) references users(username)
)
engine = InnoDB;

/* associates an A_book with a course */
create table A_book_course(
    book_id int,
    course_id int,
    foreign key (book_id) references A_books(id),
    foreign key (course_id) references courses(id),
    primary key (book_id, course_id)
)
engine = InnoDB;