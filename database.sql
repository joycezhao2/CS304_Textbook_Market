use ypan2_db;

drop table if exists users;
drop table if exists courses;
drop table if exists A_books;
drop table if exists S_books;
drop table if exists A_book_course;

/* for all users, either a buyer or a seller */
create table users (
    username varchar(20) NOT NULL primary key,
    name varchar(50),
    email varchar(100),
    phnum varchar(10),
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
    id int auto_increment primary key,
    title varchar(50),
    author varchar(30),
    )
    engine = InnoDB;

/* for each book uploaded by the seller */
create table S_books (
    id int auto_increment NOT NULL primary key,
    price int,
    sold_status BIT,
    condition varchar(20),
    book int,
    seller varchar(20),
    buyer varchar(20),
    index (book),
    index (seller),
    index (buyer),
    foreign key (book) references A_books(id),
    foreign key (seller) references users(username),
    foreign key (buyer) references users(username)
        on delete CASCADE
        on update CASCADE
    )
    engine = InnoDB;

/* associates an A_book with a course */
create table A_book_course(
    book int,
    CRN char(5),
    index (book),
    index (CRN),
    primary key (book, CRN)
    foreign key (book) references A_books(id),
    foreign key (CRN) references courses(CRN)
        on delete CASCADE
        on update CASCADE
    )
    engine = InnoDB;