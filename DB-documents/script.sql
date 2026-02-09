drop database if exists boxoffice;
create database if not exists boxoffice;
use boxoffice;

drop table if exists Booking;
drop table if exists Schedule;
drop table if exists Theater;
drop table if exists Movie;
drop table if exists User;

-- ==========================================
-- TABLE: USER
-- Updated with Anubhav, Prakhar, and Manu
-- ==========================================
create table User(
    email_address VARCHAR(50) primary key,
    user_name VARCHAR(50) not null,
    mobile_number BIGINT(10) unique not null,
    date_of_birth DATE not null,
    password VARCHAR(50) not null,
    security_question VARCHAR(50) not null,
    security_answer VARCHAR(50) not null,
    role enum("admin","tech_admin","user") default "user"
) engine='InnoDB';

-- 1. ADMIN (Anubhav)
insert into User (email_address,user_name,mobile_number,date_of_birth,password,security_question,security_answer,role) 
values("anubhav@admin.com", "Anubhav", 9876543210, "1995-08-15", "Admin@123", "What is your favorite food?", "Pizza", "admin");

-- 2. TECH ADMIN (Prakhar)
insert into User (email_address,user_name,mobile_number,date_of_birth,password,security_question,security_answer,role) 
values("prakhar@tech.com", "Prakhar", 9876543211, "1996-05-20", "Tech@123", "What city were you born in?", "Indore", "tech_admin");

-- 3. CUSTOMER (Manu)
insert into User (email_address,user_name,mobile_number,date_of_birth,password,security_question,security_answer,role) 
values("manu@gmail.com", "Manu", 9876543212, "1998-12-10", "User@123", "What was the name of your favorite pet?", "Dog", "user");

-- Extra Users for testing
insert into User (email_address,user_name,mobile_number,date_of_birth,password,security_question,security_answer,role) 
values("rohit@gmail.com", "Rohit", 9876543213, "2000-01-01", "Pass@123", "Where is your favorite place to vacation?", "Goa", "user");


-- ==========================================
-- TABLE: MOVIE
-- Updated with 2026 relevant titles
-- ==========================================
create table Movie(
    movie_name varchar(50) primary key,
    language enum("English","Hindi","Kannada","Tamil","Telugu","Malayalam") not null,
    category enum("Comedy","Action","Horror") not null,
    release_date date not null
) engine=innodb;

insert into Movie (movie_name,language,category,release_date) values("War 2", "Hindi", "Action", "2026-01-26");
insert into Movie (movie_name,language,category,release_date) values("Stree 3", "Hindi", "Horror", "2025-12-20");
insert into Movie (movie_name,language,category,release_date) values("Kantara 2", "Kannada", "Action", "2026-02-01");
insert into Movie (movie_name,language,category,release_date) values("Pushpa The Rule", "Telugu", "Action", "2025-12-15");
insert into Movie (movie_name,language,category,release_date) values("Hera Pheri 3", "Hindi", "Comedy", "2026-01-10");
insert into Movie (movie_name,language,category,release_date) values("The Conjuring 4", "English", "Horror", "2025-10-31");
insert into Movie (movie_name,language,category,release_date) values("Leo", "Tamil", "Action", "2025-11-14");
insert into Movie (movie_name,language,category,release_date) values("Welcome 3", "Hindi", "Comedy", "2025-12-25");
insert into Movie (movie_name,language,category,release_date) values("Deadpool 3", "English", "Action", "2026-02-14");
insert into Movie (movie_name,language,category,release_date) values("Drishyam 3", "Malayalam", "Action", "2026-01-05");


-- ==========================================
-- TABLE: THEATER
-- Updated with Modern Names
-- ==========================================
create table Theater(
    theater_name varchar(50) primary key,
    owner_email varchar(50) not null,
    show_time varchar(50) default "10AM to 1PM,2PM to 5PM,6PM to 9PM" not null,
    seat_capacity integer not null, 
    price_per_ticket float not null,
    foreign key(owner_email) references User(email_address)
) engine='InnoDB';

-- Owners are mapped to generic users or admin for now as per schema logic
insert into Theater(theater_name,owner_email,seat_capacity,price_per_ticket) values ("PVR Phoenix", "anubhav@admin.com", 200, 350);
insert into Theater(theater_name,owner_email,seat_capacity,price_per_ticket) values ("INOX Insignia", "prakhar@tech.com", 150, 500);
insert into Theater(theater_name,owner_email,seat_capacity,price_per_ticket) values ("Cinepolis Nexus", "anubhav@admin.com", 180, 250);
insert into Theater(theater_name,owner_email,seat_capacity,price_per_ticket) values ("IMAX Orbit", "prakhar@tech.com", 300, 600);
insert into Theater(theater_name,owner_email,seat_capacity,price_per_ticket) values ("Miraj Cinemas", "anubhav@admin.com", 120, 200);


-- ==========================================
-- TABLE: SCHEDULE
-- Mapping New Movies to New Theaters
-- ==========================================
create table Schedule(
    schedule_id integer primary key auto_increment,
    theater_name varchar(50) not null,
    movie_name varchar(50) not null,
    start_date date not null,
    end_date date not null,
    foreign key(theater_name) references Theater(theater_name),
    foreign key(movie_name) references Movie(movie_name)
) engine=innodb auto_increment=101;

-- Schedules for Feb 2026
insert into Schedule (theater_name, movie_name, start_date, end_date) values("PVR Phoenix", "War 2", "2026-02-01", "2026-03-01");
insert into Schedule (theater_name, movie_name, start_date, end_date) values("INOX Insignia", "Kantara 2", "2026-02-05", "2026-03-10");
insert into Schedule (theater_name, movie_name, start_date, end_date) values("Cinepolis Nexus", "Hera Pheri 3", "2026-01-20", "2026-02-28");
insert into Schedule (theater_name, movie_name, start_date, end_date) values("IMAX Orbit", "Deadpool 3", "2026-02-14", "2026-03-14");
insert into Schedule (theater_name, movie_name, start_date, end_date) values("Miraj Cinemas", "Stree 3", "2026-01-15", "2026-02-15");

insert into Schedule (theater_name, movie_name, start_date, end_date) values("PVR Phoenix", "Pushpa The Rule", "2026-01-10", "2026-02-15");
insert into Schedule (theater_name, movie_name, start_date, end_date) values("INOX Insignia", "War 2", "2026-02-01", "2026-03-01");
insert into Schedule (theater_name, movie_name, start_date, end_date) values("Cinepolis Nexus", "Welcome 3", "2026-01-25", "2026-02-20");


-- ==========================================
-- TABLE: BOOKING
-- Bookings for 'Manu'
-- ==========================================
create table Booking(
    booking_id integer primary key auto_increment,
    email_address VARCHAR(50) not null,
    movie_name varchar(50) not null,
    theater_name varchar(50) not null,
    date_of_booking date not null,
    time_of_booking varchar(30) not null,
    no_of_tickets_required integer not null,
    total_amount float not null default 0.0,
    status enum("Booked","Cancelled") not null,
    foreign key (email_address) references User(email_address), 
    foreign key(movie_name) references Movie(movie_name),
    foreign key(theater_name) references Theater(theater_name)
) engine='InnoDB' auto_increment=2001;

-- Manu's Bookings
insert into Booking (email_address,movie_name,theater_name,date_of_booking,time_of_booking,no_of_tickets_required,total_amount,status) 
values ("manu@gmail.com", "War 2", "PVR Phoenix", "2026-02-10", "10AM to 1PM", 2, 700, "Booked");

insert into Booking (email_address,movie_name,theater_name,date_of_booking,time_of_booking,no_of_tickets_required,total_amount,status) 
values ("manu@gmail.com", "Hera Pheri 3", "Cinepolis Nexus", "2026-02-08", "2PM to 5PM", 4, 1000, "Booked");

insert into Booking (email_address,movie_name,theater_name,date_of_booking,time_of_booking,no_of_tickets_required,total_amount,status) 
values ("manu@gmail.com", "Kantara 2", "INOX Insignia", "2026-02-12", "6PM to 9PM", 2, 1000, "Booked");

insert into Booking (email_address,movie_name,theater_name,date_of_booking,time_of_booking,no_of_tickets_required,total_amount,status) 
values ("manu@gmail.com", "Stree 3", "Miraj Cinemas", "2026-02-01", "10AM to 1PM", 3, 600, "Cancelled");

-- Rohit's Bookings (Extra user)
insert into Booking (email_address,movie_name,theater_name,date_of_booking,time_of_booking,no_of_tickets_required,total_amount,status) 
values ("rohit@gmail.com", "Deadpool 3", "IMAX Orbit", "2026-02-14", "6PM to 9PM", 2, 1200, "Booked");

select * from User;