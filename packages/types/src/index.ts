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
