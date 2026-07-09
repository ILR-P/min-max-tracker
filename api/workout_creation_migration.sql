alter table if exists exercises_template
    add column if not exists rest_seconds smallint not null default 60 check (rest_seconds >= 0);

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

create index if not exists idx_exercise_working_sets_template_id on exercise_working_sets (exercise_template_id);
