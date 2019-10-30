use ypan2_db;

drop table if exists users;
drop table if exists courses;
drop table if exists A_books;
drop table if exists S_books;
drop table if exists A_book_course;

/* for all users, either a buyer or a seller */
create table users (
    id varchar(20) primary key,
    name varchar(50),
    email varchar(100),
    phnum char(10)
)
engine = InnoDB;

/* for all courses differentiated by deparment, section and professor */
create table courses (
    CRN char(5),
    department varchar(4),
    number char(3),
    professor varchar(50),
    primary key (CRN, professor)
)
engine = InnoDB;

/* for the abstract book, each is associated with one course */
create table A_books (
    id int NOT NULL AUTO_INCREMENT primary key,
    title varchar(50),
    author varchar(30)
)
engine = InnoDB;

/* for each book uploaded by the seller */
create table S_books (
    id int NOT NULL AUTO_INCREMENT primary key,
    foreign key (A_book) references A_books(id),
    foreign key (seller) references users(id),
    foreign key (buyer) references users(id),
    price int,
    sold_status BIT,
    condition varchar(20) CHECK (condition in ('Brand New','Like New',
                                                'Very Good','Good','Acceptable'))
)
engine = InnoDB;

/* associates an A_book with a course */
create table A_book_course(
    foreign key (book) references A_books(id),
    foreign key (CRN) references courses(CRN),
    primary key (book, CRN)
)