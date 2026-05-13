export type TemplatesStackParamList = {
  TemplateList: undefined;
  TemplateEdit: { templateId: string };
};

export type ExercisesStackParamList = {
  ExerciseList: undefined;
  ExerciseDetail: { exerciseId: string; exerciseName: string };
};

export type WorkoutStackParamList = {
  WorkoutHome: undefined;
  WorkoutSession: { workoutId: string };
  WorkoutFinish: { workoutId: string };
};

/** @deprecated Use ExercisesStackParamList instead */
export type RootStackParamList = ExercisesStackParamList;
