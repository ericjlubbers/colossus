// ─── Units ────────────────────────────────────────────────────────────────────

/** Primary weight unit — lbs by default, kg as display toggle. */
export type WeightUnit = "lbs" | "kg";

// ─── User ─────────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  username: string;
  email: string;
  /** Preferred display unit (lbs is the storage canonical unit). */
  weightUnit: WeightUnit;
  createdAt: string; // ISO 8601
  updatedAt: string;
}

// ─── Exercise ─────────────────────────────────────────────────────────────────

export type MuscleGroup =
  | "chest"
  | "back"
  | "shoulders"
  | "biceps"
  | "triceps"
  | "forearms"
  | "core"
  | "quads"
  | "hamstrings"
  | "glutes"
  | "calves";

export type EquipmentType =
  | "barbell"
  | "dumbbell"
  | "cable"
  | "machine"
  | "bodyweight"
  | "kettlebell"
  | "band"
  | "other";

export interface Exercise {
  id: string;
  name: string;
  primaryMuscle: MuscleGroup;
  secondaryMuscles: MuscleGroup[];
  equipment: EquipmentType;
  instructions?: string;
  /** MinIO presigned URL or CDN path for demo video. */
  videoUrl?: string;
  thumbnailUrl?: string;
  /** true = created by user, false = seeded from library */
  isCustom: boolean;
  createdAt: string;
  updatedAt: string;
}

// ─── Workout Templates ────────────────────────────────────────────────────────

export type BlockType = "set" | "superset";
export type WeightType = "fixed" | "pct_1rm" | "auto";

export interface TemplateSet {
  setNumber: number;
  targetRepsMin?: number;
  targetRepsMax?: number;
  targetWeight?: number;
  weightType: WeightType;
  isWarmup: boolean;
  notes?: string;
}

export interface TemplateBlockExercise {
  id: string;
  blockId: string;
  exerciseId: string;
  orderInBlock: number;
  sets: TemplateSet[];
  progressionOverride?: Record<string, unknown>;
  exercise?: {
    id: string;
    name: string;
    primaryMuscle: string;
    equipment: string;
  };
}

export interface TemplateBlock {
  id: string;
  templateId: string;
  blockType: BlockType;
  order: number;
  restAfterSeconds?: number;
  exercises: TemplateBlockExercise[];
}

export interface WorkoutTemplate {
  id: string;
  userId?: string;
  name: string;
  description?: string;
  estimatedDurationMinutes?: number;
  tags: string[];
  createdAt: string;
  updatedAt: string;
  blocks: TemplateBlock[];
}

export interface WorkoutTemplateSummary {
  id: string;
  userId?: string;
  name: string;
  description?: string;
  estimatedDurationMinutes?: number;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

// ─── Workout Sessions (Phase 3) ───────────────────────────────────────────────

export interface CompletedSet {
  id: string;
  workoutId: string;
  exerciseId: string;
  blockId?: string;
  setNumber: number;
  repsCompleted?: number;
  weight?: number;
  isWarmup: boolean;
  isFailure: boolean;
  rpe?: number;
  notes?: string;
  loggedAt: string;
  exercise?: {
    id: string;
    name: string;
    primaryMuscle: string;
    equipment: string;
  };
}

export interface CompletedWorkout {
  id: string;
  userId?: string;
  templateId?: string;
  notes?: string;
  startedAt: string;
  endedAt?: string;
  createdAt: string;
  sets: CompletedSet[];
  template?: {
    id: string;
    name: string;
    description?: string;
  };
}

// ─── API responses ────────────────────────────────────────────────────────────

export interface HealthResponse {
  status: "ok";
  app: string;
  version: string;
}

export interface TokenPair {
  accessToken: string;
  refreshToken: string;
  tokenType: "bearer";
}
