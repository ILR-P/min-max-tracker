create extension if not exists pgcrypto;

create table if not exists blocks (
    id uuid primary key default gen_random_uuid(),
    owner_user_id uuid references auth.users (id) on delete cascade,
    name text not null,
    description text
);

create table if not exists weeks (
    id uuid primary key default gen_random_uuid(),
    block_id uuid not null references blocks (id) on delete cascade,
    week_number smallint not null check (week_number between 1 and 12),
    constraint weeks_block_week_unique unique (block_id, week_number)
);

create table if not exists workouts (
    id uuid primary key default gen_random_uuid(),
    week_id uuid not null references weeks (id) on delete cascade,
    name text not null,
    day_of_week smallint not null check (day_of_week between 1 and 7),
    workout_summary text,
    constraint workouts_week_day_unique unique (week_id, day_of_week, name)
);

create table if not exists exercises_template (
    id uuid primary key default gen_random_uuid(),
    workout_id uuid not null references workouts (id) on delete cascade,
    exercise_name text not null,
    warm_up_sets smallint not null default 0 check (warm_up_sets >= 0),
    working_sets smallint not null default 1 check (working_sets between 1 and 2),
    rep_range text not null,
    rir_target text,
    intensity_technique text,
    rest_seconds smallint not null default 60 check (rest_seconds >= 0),
    notes text,
    constraint exercises_template_workout_name_unique unique (workout_id, exercise_name)
);

create table if not exists exercise_working_sets (
    id uuid primary key default gen_random_uuid(),
    exercise_template_id uuid not null references exercises_template (id) on delete cascade,
    set_number smallint not null check (set_number between 1 and 4),
    load numeric(8, 2) not null check (load >= 0),
    reps smallint not null check (reps >= 0),
    rest_seconds smallint not null default 60 check (rest_seconds >= 0),
    notes text,
    constraint exercise_working_sets_unique unique (exercise_template_id, set_number)
);

create table if not exists user_logs (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    exercise_template_id uuid not null references exercises_template (id) on delete cascade,
    set_number smallint not null check (set_number between 1 and 2),
    load numeric(8, 2) not null check (load >= 0),
    reps smallint not null check (reps >= 0),
    logged_date date not null default current_date,
    constraint user_logs_unique_set unique (user_id, exercise_template_id, logged_date, set_number)
);

create index if not exists idx_weeks_block_id on weeks (block_id);
create index if not exists idx_weeks_block_week on weeks (block_id, week_number);
create index if not exists idx_workouts_week_id_day on workouts (week_id, day_of_week);
create index if not exists idx_exercises_template_workout_id on exercises_template (workout_id);
create index if not exists idx_exercise_working_sets_template_id on exercise_working_sets (exercise_template_id);
create index if not exists idx_user_logs_user_template_date on user_logs (user_id, exercise_template_id, logged_date desc);
create unique index if not exists idx_blocks_global_name on blocks (name) where owner_user_id is null;
create unique index if not exists idx_blocks_owner_name on blocks (owner_user_id, name) where owner_user_id is not null;

