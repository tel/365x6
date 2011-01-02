begin transaction;
drop table if exists photos;
create table photos(
    id integer primary key autoincrement,
	ts timestamp default current_timestamp,
	photographer char(255) not null,
	description text default null,
	hash char(64) unique not null,
	foreign key (photographer) references photographers(id)
);

drop table if exists days;
create table days(
	id integer primary key autoincrement,
	ts timestamp default current_timestamp,
	color char(32) default '#222'
);

drop table if exists joiner;
create table joiner(
    photo_id integer,
    day_id integer,
    photographer_id integer,
    unique (day_id, photographer_id),
    foreign key (photo_id) references photos(id),
    foreign key (day_id) references days(id),
    foreign key (photographer_id) references photographers(id)
);

drop table if exists photographers;
create table photographers(
    id integer primary key,
    name char(255) unique not null  
);
insert into photographers values (1, 'Joe');
insert into photographers values (2, 'Henry');
insert into photographers values (3, 'Janet');
insert into photographers values (4, 'Megan');
insert into photographers values (5, 'Kento');
insert into photographers values (6, 'Chanh');
commit;
