import type { MuscleGroup, EquipmentType } from "@colossus/types";

const API_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://10.0.0.50:8000";

// ─── Raw API response types (snake_case) ──────────────────────────────────────

interface ExerciseMediaApiResponse {
  id: string;
  media_type: string;
  storage_path: string;
  source_url: string | null;
  is_primary: boolean;
  url: string | null;
  demo_start_seconds: number | null;
  demo_end_seconds: number | null;
}

export interface ExerciseApiResponse {
  id: string;
  name: string;
  description: string | null;
  instructions: string | null;
  primary_muscle: string;
  secondary_muscles: string[];
  equipment: string;
  is_custom: boolean;
  created_by: string | null;
  created_at: string;
  updated_at: string;
  media: ExerciseMediaApiResponse[];
}

interface ExerciseListApiResponse {
  items: ExerciseApiResponse[];
  total: number;
  page: number;
  page_size: number;
}

// ─── App-facing types ─────────────────────────────────────────────────────────

export interface ExerciseMedia {
  id: string;
  mediaType: string;
  storagePath: string;
  sourceUrl: string | null;
  isPrimary: boolean;
  url: string | null;
  demoStartSeconds: number | null;
  demoEndSeconds: number | null;
}

export interface Exercise {
  id: string;
  name: string;
  description?: string;
  instructions?: string;
  primaryMuscle: MuscleGroup;
  secondaryMuscles: MuscleGroup[];
  equipment: EquipmentType;
  isCustom: boolean;
  createdAt: string;
  updatedAt: string;
  media: ExerciseMedia[];
}

export interface PaginatedExercises {
  items: Exercise[];
  total: number;
  page: number;
  pageSize: number;
}

// ─── Transforms ───────────────────────────────────────────────────────────────

function transformMedia(raw: ExerciseMediaApiResponse): ExerciseMedia {
  return {
    id: raw.id,
    mediaType: raw.media_type,
    storagePath: raw.storage_path,
    sourceUrl: raw.source_url,
    isPrimary: raw.is_primary,
    url: raw.url,
    demoStartSeconds: raw.demo_start_seconds,
    demoEndSeconds: raw.demo_end_seconds,
  };
}

function transformExercise(raw: ExerciseApiResponse): Exercise {
  return {
    id: raw.id,
    name: raw.name,
    description: raw.description ?? undefined,
    instructions: raw.instructions ?? undefined,
    primaryMuscle: raw.primary_muscle as MuscleGroup,
    secondaryMuscles: raw.secondary_muscles as MuscleGroup[],
    equipment: raw.equipment as EquipmentType,
    isCustom: raw.is_custom,
    createdAt: raw.created_at,
    updatedAt: raw.updated_at,
    media: (raw.media ?? []).map(transformMedia),
  };
}

// ─── Fetch helpers ────────────────────────────────────────────────────────────

async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`);
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json() as Promise<T>;
}

// ─── Public API ───────────────────────────────────────────────────────────────

export interface FetchExercisesParams {
  primaryMuscle?: string;
  equipment?: string;
  q?: string;
  page?: number;
  pageSize?: number;
}

export async function fetchExercises(
  params: FetchExercisesParams = {},
): Promise<PaginatedExercises> {
  const sp = new URLSearchParams();
  if (params.primaryMuscle) sp.set("primary_muscle", params.primaryMuscle);
  if (params.equipment) sp.set("equipment", params.equipment);
  if (params.q) sp.set("q", params.q);
  if (params.page) sp.set("page", String(params.page));
  if (params.pageSize) sp.set("page_size", String(params.pageSize));

  const qs = sp.toString();
  const raw = await apiFetch<ExerciseListApiResponse>(`/exercises${qs ? `?${qs}` : ""}`);

  return {
    items: raw.items.map(transformExercise),
    total: raw.total,
    page: raw.page,
    pageSize: raw.page_size,
  };
}

export async function fetchExercise(id: string): Promise<Exercise> {
  const raw = await apiFetch<ExerciseApiResponse>(`/exercises/${id}`);
  return transformExercise(raw);
}
