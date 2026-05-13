import type { Exercise, MuscleGroup, EquipmentType } from "@colossus/types";
import type {
  WorkoutTemplate,
  WorkoutTemplateSummary,
  TemplateBlock,
  TemplateBlockExercise,
  TemplateSet,
} from "@colossus/types";

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

// ─── Template API types (snake_case from server) ──────────────────────────────

interface TemplateSetApi {
  set_number: number;
  target_reps_min: number | null;
  target_reps_max: number | null;
  target_weight: number | null;
  weight_type: string;
  is_warmup: boolean;
  notes: string | null;
}

interface TbeApi {
  id: string;
  block_id: string;
  exercise_id: string;
  order_in_block: number;
  sets: TemplateSetApi[];
  progression_override: Record<string, unknown> | null;
  exercise: { id: string; name: string; primary_muscle: string; equipment: string } | null;
}

interface BlockApi {
  id: string;
  template_id: string;
  block_type: string;
  order: number;
  rest_after_seconds: number | null;
  exercises: TbeApi[];
}

interface TemplateApi {
  id: string;
  user_id: string | null;
  name: string;
  description: string | null;
  estimated_duration_minutes: number | null;
  tags: string[];
  created_at: string;
  updated_at: string;
  blocks: BlockApi[];
}

interface TemplateListApi {
  items: Omit<TemplateApi, "blocks">[];
  total: number;
  page: number;
  page_size: number;
}

// ─── Template transform helpers ───────────────────────────────────────────────

function transformTemplateSet(raw: TemplateSetApi): TemplateSet {
  return {
    setNumber: raw.set_number,
    targetRepsMin: raw.target_reps_min ?? undefined,
    targetRepsMax: raw.target_reps_max ?? undefined,
    targetWeight: raw.target_weight ?? undefined,
    weightType: raw.weight_type as TemplateSet["weightType"],
    isWarmup: raw.is_warmup,
    notes: raw.notes ?? undefined,
  };
}

function transformTbe(raw: TbeApi): TemplateBlockExercise {
  return {
    id: raw.id,
    blockId: raw.block_id,
    exerciseId: raw.exercise_id,
    orderInBlock: raw.order_in_block,
    sets: raw.sets.map(transformTemplateSet),
    progressionOverride: raw.progression_override ?? undefined,
    exercise: raw.exercise
      ? {
          id: raw.exercise.id,
          name: raw.exercise.name,
          primaryMuscle: raw.exercise.primary_muscle,
          equipment: raw.exercise.equipment,
        }
      : undefined,
  };
}

function transformBlock(raw: BlockApi): TemplateBlock {
  return {
    id: raw.id,
    templateId: raw.template_id,
    blockType: raw.block_type as TemplateBlock["blockType"],
    order: raw.order,
    restAfterSeconds: raw.rest_after_seconds ?? undefined,
    exercises: raw.exercises.map(transformTbe),
  };
}

function transformTemplate(raw: TemplateApi): WorkoutTemplate {
  return {
    id: raw.id,
    userId: raw.user_id ?? undefined,
    name: raw.name,
    description: raw.description ?? undefined,
    estimatedDurationMinutes: raw.estimated_duration_minutes ?? undefined,
    tags: raw.tags,
    createdAt: raw.created_at,
    updatedAt: raw.updated_at,
    blocks: raw.blocks.map(transformBlock),
  };
}

function transformTemplateSummary(raw: Omit<TemplateApi, "blocks">): WorkoutTemplateSummary {
  return {
    id: raw.id,
    userId: raw.user_id ?? undefined,
    name: raw.name,
    description: raw.description ?? undefined,
    estimatedDurationMinutes: raw.estimated_duration_minutes ?? undefined,
    tags: raw.tags,
    createdAt: raw.created_at,
    updatedAt: raw.updated_at,
  };
}

// ─── Template public API ──────────────────────────────────────────────────────

export interface PaginatedTemplates {
  items: WorkoutTemplateSummary[];
  total: number;
  page: number;
  pageSize: number;
}

export async function fetchTemplates(
  q?: string,
  page = 1,
  pageSize = 50,
): Promise<PaginatedTemplates> {
  const sp = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  if (q) sp.set("q", q);
  const raw = await apiFetch<TemplateListApi>(`/templates?${sp.toString()}`);
  return {
    items: raw.items.map(transformTemplateSummary),
    total: raw.total,
    page: raw.page,
    pageSize: raw.page_size,
  };
}

export async function fetchTemplate(id: string): Promise<WorkoutTemplate> {
  const raw = await apiFetch<TemplateApi>(`/templates/${id}`);
  return transformTemplate(raw);
}

export async function createTemplate(data: {
  name: string;
  description?: string;
  estimatedDurationMinutes?: number;
  tags?: string[];
}): Promise<WorkoutTemplate> {
  const raw = await apiFetch<TemplateApi>("/templates", {
    method: "POST",
    body: JSON.stringify({
      name: data.name,
      description: data.description,
      estimated_duration_minutes: data.estimatedDurationMinutes,
      tags: data.tags ?? [],
    }),
  });
  return transformTemplate(raw);
}

export async function updateTemplateApi(
  id: string,
  data: Partial<{
    name: string;
    description: string | null;
    estimatedDurationMinutes: number | null;
    tags: string[];
  }>,
): Promise<WorkoutTemplate> {
  const body: Record<string, unknown> = {};
  if ("name" in data) body.name = data.name;
  if ("description" in data) body.description = data.description;
  if ("estimatedDurationMinutes" in data)
    body.estimated_duration_minutes = data.estimatedDurationMinutes;
  if ("tags" in data) body.tags = data.tags;
  const raw = await apiFetch<TemplateApi>(`/templates/${id}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
  return transformTemplate(raw);
}

export async function deleteTemplateApi(id: string): Promise<void> {
  await apiFetch(`/templates/${id}`, { method: "DELETE" });
}

export async function addBlockApi(
  templateId: string,
  data: { blockType: "set" | "superset"; order: number; restAfterSeconds?: number },
): Promise<TemplateBlock> {
  const raw = await apiFetch<BlockApi>(`/templates/${templateId}/blocks`, {
    method: "POST",
    body: JSON.stringify({
      block_type: data.blockType,
      order: data.order,
      rest_after_seconds: data.restAfterSeconds,
    }),
  });
  return transformBlock(raw);
}

export async function updateBlockApi(
  templateId: string,
  blockId: string,
  data: Partial<{ blockType: "set" | "superset"; order: number; restAfterSeconds: number | null }>,
): Promise<TemplateBlock> {
  const body: Record<string, unknown> = {};
  if ("blockType" in data) body.block_type = data.blockType;
  if ("order" in data) body.order = data.order;
  if ("restAfterSeconds" in data) body.rest_after_seconds = data.restAfterSeconds;
  const raw = await apiFetch<BlockApi>(`/templates/${templateId}/blocks/${blockId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
  return transformBlock(raw);
}

export async function deleteBlockApi(templateId: string, blockId: string): Promise<void> {
  await apiFetch(`/templates/${templateId}/blocks/${blockId}`, { method: "DELETE" });
}

export async function reorderBlocksApi(
  templateId: string,
  items: { id: string; order: number }[],
): Promise<WorkoutTemplate> {
  const raw = await apiFetch<TemplateApi>(`/templates/${templateId}/blocks/reorder`, {
    method: "PATCH",
    body: JSON.stringify({ items }),
  });
  return transformTemplate(raw);
}

export async function addExerciseToBlockApi(
  templateId: string,
  blockId: string,
  data: { exerciseId: string; orderInBlock: number; sets?: TemplateSet[] },
): Promise<TemplateBlockExercise> {
  const raw = await apiFetch<TbeApi>(
    `/templates/${templateId}/blocks/${blockId}/exercises`,
    {
      method: "POST",
      body: JSON.stringify({
        exercise_id: data.exerciseId,
        order_in_block: data.orderInBlock,
        sets: (data.sets ?? []).map((s) => ({
          set_number: s.setNumber,
          target_reps_min: s.targetRepsMin ?? null,
          target_reps_max: s.targetRepsMax ?? null,
          target_weight: s.targetWeight ?? null,
          weight_type: s.weightType,
          is_warmup: s.isWarmup,
          notes: s.notes ?? null,
        })),
      }),
    },
  );
  return transformTbe(raw);
}

export async function updateBlockExerciseApi(
  templateId: string,
  blockId: string,
  tbeId: string,
  data: Partial<{
    orderInBlock: number;
    sets: TemplateSet[];
    progressionOverride: Record<string, unknown> | null;
  }>,
): Promise<TemplateBlockExercise> {
  const body: Record<string, unknown> = {};
  if ("orderInBlock" in data) body.order_in_block = data.orderInBlock;
  if ("sets" in data && data.sets) {
    body.sets = data.sets.map((s) => ({
      set_number: s.setNumber,
      target_reps_min: s.targetRepsMin ?? null,
      target_reps_max: s.targetRepsMax ?? null,
      target_weight: s.targetWeight ?? null,
      weight_type: s.weightType,
      is_warmup: s.isWarmup,
      notes: s.notes ?? null,
    }));
  }
  if ("progressionOverride" in data) body.progression_override = data.progressionOverride;
  const raw = await apiFetch<TbeApi>(
    `/templates/${templateId}/blocks/${blockId}/exercises/${tbeId}`,
    { method: "PATCH", body: JSON.stringify(body) },
  );
  return transformTbe(raw);
}

export async function deleteBlockExerciseApi(
  templateId: string,
  blockId: string,
  tbeId: string,
): Promise<void> {
  await apiFetch(`/templates/${templateId}/blocks/${blockId}/exercises/${tbeId}`, {
    method: "DELETE",
  });
}

export async function reorderBlockExercisesApi(
  templateId: string,
  blockId: string,
  items: { id: string; orderInBlock: number }[],
): Promise<TemplateBlock> {
  const raw = await apiFetch<BlockApi>(
    `/templates/${templateId}/blocks/${blockId}/exercises/reorder`,
    {
      method: "PATCH",
      body: JSON.stringify({
        items: items.map((i) => ({ id: i.id, order_in_block: i.orderInBlock })),
      }),
    },
  );
  return transformBlock(raw);
}

// Re-export template types
export type {
  WorkoutTemplate,
  WorkoutTemplateSummary,
  TemplateBlock,
  TemplateBlockExercise,
  TemplateSet,
  CompletedWorkout,
  CompletedSet,
} from "@colossus/types";

// ─── Workout session API types (snake_case) ───────────────────────────────────

interface CompletedSetApi {
  id: string;
  workout_id: string;
  exercise_id: string;
  block_id: string | null;
  set_number: number;
  reps_completed: number | null;
  weight: string | null;
  is_warmup: boolean;
  is_failure: boolean;
  rpe: string | null;
  notes: string | null;
  logged_at: string;
  exercise: { id: string; name: string; primary_muscle: string; equipment: string } | null;
}

interface CompletedWorkoutApi {
  id: string;
  user_id: string | null;
  template_id: string | null;
  notes: string | null;
  started_at: string;
  ended_at: string | null;
  created_at: string;
  sets: CompletedSetApi[];
  template: { id: string; name: string; description: string | null } | null;
}

function transformCompletedSet(raw: CompletedSetApi): import("@colossus/types").CompletedSet {
  return {
    id: raw.id,
    workoutId: raw.workout_id,
    exerciseId: raw.exercise_id,
    blockId: raw.block_id ?? undefined,
    setNumber: raw.set_number,
    repsCompleted: raw.reps_completed ?? undefined,
    weight: raw.weight != null ? parseFloat(raw.weight) : undefined,
    isWarmup: raw.is_warmup,
    isFailure: raw.is_failure,
    rpe: raw.rpe != null ? parseFloat(raw.rpe) : undefined,
    notes: raw.notes ?? undefined,
    loggedAt: raw.logged_at,
    exercise: raw.exercise
      ? {
          id: raw.exercise.id,
          name: raw.exercise.name,
          primaryMuscle: raw.exercise.primary_muscle,
          equipment: raw.exercise.equipment,
        }
      : undefined,
  };
}

function transformCompletedWorkout(
  raw: CompletedWorkoutApi,
): import("@colossus/types").CompletedWorkout {
  return {
    id: raw.id,
    userId: raw.user_id ?? undefined,
    templateId: raw.template_id ?? undefined,
    notes: raw.notes ?? undefined,
    startedAt: raw.started_at,
    endedAt: raw.ended_at ?? undefined,
    createdAt: raw.created_at,
    sets: raw.sets.map(transformCompletedSet),
    template: raw.template
      ? {
          id: raw.template.id,
          name: raw.template.name,
          description: raw.template.description ?? undefined,
        }
      : undefined,
  };
}

// ─── Workout public API ───────────────────────────────────────────────────────

export async function startWorkoutApi(templateId?: string): Promise<import("@colossus/types").CompletedWorkout> {
  const raw = await apiFetch<CompletedWorkoutApi>("/workouts", {
    method: "POST",
    body: JSON.stringify({ template_id: templateId ?? null }),
  });
  return transformCompletedWorkout(raw);
}

export async function fetchWorkoutApi(id: string): Promise<import("@colossus/types").CompletedWorkout> {
  const raw = await apiFetch<CompletedWorkoutApi>(`/workouts/${id}`);
  return transformCompletedWorkout(raw);
}

export async function finishWorkoutApi(id: string): Promise<import("@colossus/types").CompletedWorkout> {
  const raw = await apiFetch<CompletedWorkoutApi>(`/workouts/${id}/finish`, {
    method: "POST",
  });
  return transformCompletedWorkout(raw);
}

export interface LogSetParams {
  exerciseId: string;
  blockId?: string;
  setNumber: number;
  repsCompleted?: number;
  weight?: number;
  isWarmup?: boolean;
  isFailure?: boolean;
  rpe?: number;
  notes?: string;
}

export async function logSetApi(
  workoutId: string,
  params: LogSetParams,
): Promise<import("@colossus/types").CompletedSet> {
  const raw = await apiFetch<CompletedSetApi>(`/workouts/${workoutId}/sets`, {
    method: "POST",
    body: JSON.stringify({
      exercise_id: params.exerciseId,
      block_id: params.blockId ?? null,
      set_number: params.setNumber,
      reps_completed: params.repsCompleted ?? null,
      weight: params.weight ?? null,
      is_warmup: params.isWarmup ?? false,
      is_failure: params.isFailure ?? false,
      rpe: params.rpe ?? null,
      notes: params.notes ?? null,
    }),
  });
  return transformCompletedSet(raw);
}

export async function deleteSetApi(workoutId: string, setId: string): Promise<void> {
  await apiFetch(`/workouts/${workoutId}/sets/${setId}`, { method: "DELETE" });
}

