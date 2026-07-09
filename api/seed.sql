insert into blocks (name, description)
values
  ('Block 1 - Base Strength', 'Weeks 1-6: accumulate crisp low-volume work with steady loading.'),
  ('Block 2 - Intensification', 'Weeks 7-12: push intensity while keeping volume low.')
on conflict (name) do nothing;

do $$
declare
  block_one_id uuid;
  block_two_id uuid;
  current_week_id uuid;
  current_workout_id uuid;
  workout_names text[] := array['Upper 1', 'Lower 1', 'Upper 2', 'Lower 2', 'Full Body'];
  workout_days int[] := array[1, 2, 3, 4, 5];
  program_week_number int;
  workout_index int;
begin
  select id into block_one_id from blocks where name = 'Block 1 - Base Strength';
  select id into block_two_id from blocks where name = 'Block 2 - Intensification';

  for program_week_number in 1..12 loop
    insert into weeks (block_id, week_number)
    values (
      case when program_week_number <= 6 then block_one_id else block_two_id end,
      program_week_number
    )
    on conflict (block_id, week_number) do nothing
    returning id into current_week_id;

    if current_week_id is null then
      select id into current_week_id from weeks where weeks.week_number = program_week_number limit 1;
    end if;

    for workout_index in 1..5 loop
      current_workout_id := null;
      insert into workouts (week_id, name, day_of_week, workout_summary)
      values (
        current_week_id,
        workout_names[workout_index],
        workout_days[workout_index],
        'Week ' || program_week_number || ' ' || workout_names[workout_index] || ' session.'
      )
      on conflict (week_id, day_of_week, name) do nothing
      returning id into current_workout_id;

      if current_workout_id is null then
        select id into current_workout_id
        from workouts
        where workouts.week_id = current_week_id
          and day_of_week = workout_days[workout_index]
          and name = workout_names[workout_index]
        limit 1;
      end if;

      if workout_names[workout_index] = 'Upper 1' then
        insert into exercises_template (workout_id, exercise_name, warm_up_sets, working_sets, rep_range, rir_target, intensity_technique, notes)
        values
          (current_workout_id, 'Barbell Bench Press', 3, 2, '4-6', '2', 'Top set + back-off', 'Repeat load when both sets stay in range.'),
          (current_workout_id, 'Chest-Supported Row', 2, 2, '6-8', '2-3', null, 'Pause one count at the top.'),
          (current_workout_id, 'Dumbbell Shoulder Press', 2, 2, '6-8', '2', null, 'Keep torso locked and press smoothly.')
        on conflict (workout_id, exercise_name) do nothing;
      elsif workout_names[workout_index] = 'Lower 1' then
        insert into exercises_template (workout_id, exercise_name, warm_up_sets, working_sets, rep_range, rir_target, intensity_technique, notes)
        values
          (current_workout_id, 'Back Squat', 4, 2, '4-6', '2', null, 'Brace hard and stay upright.'),
          (current_workout_id, 'Romanian Deadlift', 2, 2, '6-8', '2-3', null, 'Controlled eccentric, neutral spine.'),
          (current_workout_id, 'Split Squat', 2, 2, '8-10', '2', null, 'Long stride and even pressure through the foot.')
        on conflict (workout_id, exercise_name) do nothing;
      elsif workout_names[workout_index] = 'Upper 2' then
        insert into exercises_template (workout_id, exercise_name, warm_up_sets, working_sets, rep_range, rir_target, intensity_technique, notes)
        values
          (current_workout_id, 'Incline Bench Press', 3, 2, '5-7', '2', null, 'Use a consistent bar path.'),
          (current_workout_id, 'Pull-Up', 2, 2, '5-8', '2-3', null, 'Add load once bodyweight is clean.'),
          (current_workout_id, 'Lateral Raise', 1, 2, '12-15', '2', null, 'Strict reps, no swing.')
        on conflict (workout_id, exercise_name) do nothing;
      elsif workout_names[workout_index] = 'Lower 2' then
        insert into exercises_template (workout_id, exercise_name, warm_up_sets, working_sets, rep_range, rir_target, intensity_technique, notes)
        values
          (current_workout_id, 'Deadlift', 4, 2, '3-5', '2', 'Top set + back-off', 'Explode off the floor.'),
          (current_workout_id, 'Leg Press', 2, 2, '8-10', '2-3', null, 'Full depth without pelvic tuck.'),
          (current_workout_id, 'Hamstring Curl', 1, 2, '10-12', '2', null, 'Squeeze hard at peak contraction.')
        on conflict (workout_id, exercise_name) do nothing;
      else
        insert into exercises_template (workout_id, exercise_name, warm_up_sets, working_sets, rep_range, rir_target, intensity_technique, notes)
        values
          (current_workout_id, 'Front Squat', 3, 2, '4-6', '2', null, 'Stay tall and keep elbows high.'),
          (current_workout_id, 'Chin-Up', 2, 2, '5-8', '2-3', null, 'Dead hang each rep.'),
          (current_workout_id, 'Dumbbell Bench Press', 2, 2, '6-8', '2', null, 'Control the bottom and drive up hard.')
        on conflict (workout_id, exercise_name) do nothing;
      end if;

    end loop;
  end loop;
end $$;
