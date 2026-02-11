create table users(
    user_id int not null auto_increment,
    email varchar(255) not null unique,
    password varchar(255) not null,
    job varchar(50) not null,
    created_at datetime default current_timestamp,
    primary key (user_id)
);


create table analysis_runs(
    run_id int not null auto_increment,
    location varchar(100) not null,
    soil_type varchar(50) not null,
    past_window int not null,
    forecast_window int not null,
    risk_level varchar(20) not null,
    primary_reason text,
    rain_analysis text,
    soil_analysis text,
    forecast_issued_at datetime not null,
    metrics_json text,
    primary key (run_id)
);


create table my_map(
    view_id int not null auto_increment,
    user_id int null,
    run_id int not null,
    user_job varchar(50),
    location varchar(100) not null,
    soil_type varchar(50) not null,
    past_window int,
    forecast_window int,
    created_at datetime default current_timestamp,
    primary key (view_id),
    constraint fk_user foreign key (user_id) references users (user_id) on delete set null,
    constraint fk_run foreign key (run_id) references analysis_runs (run_id) on delete cascade
);


create table obs_hist(
    location varchar(100) not null,
    date date not null,
    rainfall decimal(5, 2),
    smd_wd decimal(5,2),
    smd_md decimal(5, 2),
    smd_pd decimal(5, 2),
    soil_temp decimal(4, 2),
    updated_at datetime default current_timestamp on update current_timestamp,
    primary key (location, date)
);


create table forecast_cache (
    location varchar(100) not null,
    issued_at datetime not null,
    precip decimal(5, 2),
    fetched_at datetime default current_timestamp,
    primary key(location, issued_at)
);