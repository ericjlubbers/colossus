import type { Exercise, MuscleGroup, EquipmentType } from "@colossus/types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

interface ExerciseApiResponse {
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

// ─── Transformed media type ───────────────────────────────────────────────────

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

// ─── Extended exercise type for detail view ───────────────────────────────────

export interface ExerciseDetail extends Exercise {
  description?: string;
  media: ExerciseMedia[];
}

// ─── Paginated response type ──────────────────────────────────────────────────

export interface PaginatedExercises {
  items: Exercise[];
  total: number;
  page: number;
  pageSize: number;
}

// ─── Transform helpers ────────────────────────────────────────────────────────

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

function transformExercise(raw: ExerciseApiResponse): ExerciseDetail {
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

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${res.statusText}`);
  }

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
  const searchParams = new URLSearchParams();

  if (params.primaryMuscle) searchParams.set("primary_muscle", params.primaryMuscle);
  if (params.equipment) searchParams.set("equipment", params.equipment);
  if (params.q) searchParams.set("q", params.q);
  if (params.page) searchParams.set("page", String(params.page));
  if (params.pageSize) searchParams.set("page_size", String(params.pageSize));

  const qs = searchParams.toString();
  const path = `/exercises${qs ? `?${qs}` : ""}`;

  const raw = await apiFetch<ExerciseListApiResponse>(path);

  return {
    items: raw.items.map(transformExercise),
    total: raw.total,
    page: raw.page,
    pageSize: raw.page_size,
  };
}

export async function fetchExercise(id: string): Promise<ExerciseDetail> {
  const raw = await apiFetch<ExerciseApiResponse>(`/exercises/${id}`);
  return transformExercise(raw);
}
