create database if not exists prcwebsite;
use prcwebsite;

create table administration(user_id int not null primary key auto_increment, admin_name varchar(100),username varchar(100), password varchar(100));
create table department (Dept_code varchar(3) not null primary key, description varchar(20));
insert into department values (CM, Children Ministry);
insert into department values (GA, General Annoncement);
insert into department values (MM, Men Ministry);
insert into department values (WM, Women Ministry);
insert into department values (TM, Teen Ministry);
insert into department values (YM, Youth Ministry);
create table announcement (id_number int not null primary key auto_increment, sender_name varchar(50), time_sent datetime , title varchar(100) , announcement text,Dept_code varchar(3));
alter table announcement add foreign key (Dept_code) references department(Dept_code);
create table booknames (book_id varchar(6) not null primary key, book_type varchar(20) );
insert into booknames values (HEAL, HealthBook);
insert into booknames values (INS, InspirationalBook);
insert into booknames values (MAR, MarriageBook);
insert into booknames values (PRAY, PrayerBook);
insert into booknames values (SPIR, SpiritualBook);
insert into booknames values (SSCH, SundaySchoolBook);
create table books(id_number int not null primary key auto_increment,sender_name varchar(100), time_sent datetime, filename varchar(200),location varchar(100), book_id varchar(6),file varchar(60));
alter table books add foreign key (book_id) references booknames (book_id);
create table comments (id_number int not null primary key auto_increment,sender_name varchar(50),time_sent datetime,comment text, contact int );
create table dailydevotion (id_number int not null primary key auto_increment, sender_name varchar(50), time_sent datetime,title varchar(100),passage varchar(50),message text);
create table messages (post_id int not null primary key auto_increment,sender_name varchar(50),time_sent datetime,location varchar(100),filename varchar(50),file varchar(50));
create table prayer_request (id_number int not null primary key auto_increment,sender_name varchar(50),time_sent datetime,prayer text, contact int );
create table testimony (id_number int not null primary key auto_increment,sender_name varchar(50),time_sent datetime,title varchar(100), testimony text );
create table users (user_id int not null primary key auto_increment,firstname varchar(20),lastname varchar(20),day int(2),month varchar(10),year int(4),sex varchar(7),marital_status varchar(10),username varchar(30),email varchar(70),password varchar(150),tel_number varchar(20),day_joined_church int(2),month_joined_church varchar(10),year_joined_church int(4),day_of_baptism int(2),month_of_baptism varchar(10),year_of_baptism int(4),department varchar(10),postion varchar(20),department_1 varchar(20),position_1 varchar(20),service varchar(20),status varchar(20),location varchar(20),house_number varchar(20),hometown varchar(20))