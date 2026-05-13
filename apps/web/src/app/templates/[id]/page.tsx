"use client";

import {
  DndContext,
  DragEndEvent,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { use, useCallback, useRef, useState } from "react";
import {
  addBlockApi,
  addExerciseToBlockApi,
  deleteBlockApi,
  deleteBlockExerciseApi,
  deleteTemplateApi,
  fetchExercises,
  fetchTemplate,
  reorderBlockExercisesApi,
  reorderBlocksApi,
  updateBlockApi,
  updateBlockExerciseApi,
  updateTemplateApi,
  type Exercise,
  type TemplateBlock,
  type TemplateBlockExercise,
  type TemplateSet,
  type WorkoutTemplate,
} from "@/lib/api";
import { useRouter } from "next/navigation";

// ─── Sortable block wrapper ───────────────────────────────────────────────────

function SortableBlock({
  block,
  children,
}: {
  block: TemplateBlock;
  children: (dragHandleProps: React.HTMLAttributes<HTMLElement>) => React.ReactNode;
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: block.id });

  return (
    <div
      ref={setNodeRef}
      style={{
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.5 : 1,
      }}
    >
      {children({ ...attributes, ...listeners })}
    </div>
  );
}

// ─── Sortable exercise wrapper ────────────────────────────────────────────────

function SortableExercise({
  tbe,
  children,
}: {
  tbe: TemplateBlockExercise;
  children: (dragHandleProps: React.HTMLAttributes<HTMLElement>) => React.ReactNode;
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: tbe.id });

  return (
    <div
      ref={setNodeRef}
      style={{
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.5 : 1,
      }}
    >
      {children({ ...attributes, ...listeners })}
    </div>
  );
}

// ─── Exercise picker panel ────────────────────────────────────────────────────

interface ExercisePickerProps {
  onSelect: (exercise: Exercise) => void;
}

function ExercisePicker({ onSelect }: ExercisePickerProps) {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleSearch = (v: string) => {
    setQuery(v);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => setDebouncedQuery(v), 300);
  };

  const { data, isLoading } = useQuery({
    queryKey: ["exercises-picker", debouncedQuery],
    queryFn: () =>
      fetchExercises({ q: debouncedQuery || undefined, page: 1, pageSize: 60 }),
    staleTime: 60_000,
  });

  return (
    <div className="flex h-full flex-col">
      <div className="p-3">
        <input
          type="text"
          placeholder="Search exercises…"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          className="w-full rounded-lg bg-gray-900 px-3 py-2 text-sm text-white placeholder-gray-600 outline-none focus:ring-1 focus:ring-gray-600"
        />
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-4 text-center text-sm text-gray-500">Loading…</div>
        ) : (
          data?.items.map((ex) => (
            <button
              key={ex.id}
              onClick={() => onSelect(ex)}
              className="w-full border-b border-gray-900 px-3 py-2.5 text-left hover:bg-gray-900"
            >
              <div className="text-sm font-medium text-white">{ex.name}</div>
              <div className="mt-0.5 text-xs capitalize text-gray-500">
                {ex.primaryMuscle} · {ex.equipment}
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
}

// ─── Set row ──────────────────────────────────────────────────────────────────

interface SetRowProps {
  set: TemplateSet;
  index: number;
  onChange: (index: number, updates: Partial<TemplateSet>) => void;
  onDelete: (index: number) => void;
}

function SetRow({ set, index, onChange, onDelete }: SetRowProps) {
  return (
    <div className="flex items-center gap-2 py-1">
      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-gray-800 text-xs font-bold text-gray-400">
        {set.isWarmup ? "W" : set.setNumber}
      </span>
      <input
        type="number"
        placeholder="Min"
        value={set.targetRepsMin ?? ""}
        onChange={(e) =>
          onChange(index, { targetRepsMin: e.target.value ? parseInt(e.target.value) : undefined })
        }
        className="w-14 rounded bg-gray-800 px-2 py-1 text-center text-sm text-white outline-none focus:ring-1 focus:ring-gray-600"
      />
      <span className="text-gray-600">–</span>
      <input
        type="number"
        placeholder="Max"
        value={set.targetRepsMax ?? ""}
        onChange={(e) =>
          onChange(index, { targetRepsMax: e.target.value ? parseInt(e.target.value) : undefined })
        }
        className="w-14 rounded bg-gray-800 px-2 py-1 text-center text-sm text-white outline-none focus:ring-1 focus:ring-gray-600"
      />
      <span className="text-xs text-gray-500">reps</span>
      <input
        type="number"
        placeholder="lbs"
        value={set.targetWeight ?? ""}
        onChange={(e) =>
          onChange(index, {
            targetWeight: e.target.value ? parseFloat(e.target.value) : undefined,
          })
        }
        className="w-16 rounded bg-gray-800 px-2 py-1 text-center text-sm text-white outline-none focus:ring-1 focus:ring-gray-600"
      />
      <span className="text-xs text-gray-500">lbs</span>
      <button
        onClick={() => onDelete(index)}
        className="ml-auto text-xs text-red-700 hover:text-red-500"
      >
        ✕
      </button>
    </div>
  );
}

// ─── Block card ───────────────────────────────────────────────────────────────

interface BlockCardProps {
  block: TemplateBlock;
  templateId: string;
  dragHandleProps: React.HTMLAttributes<HTMLElement>;
  selectedExercise: Exercise | null;
  onDelete: () => void;
  onAddExercise: () => void;
  onDeleteExercise: (tbeId: string) => void;
  onSaveSets: (tbeId: string, sets: TemplateSet[]) => void;
  onExerciseDragEnd: (blockId: string, event: DragEndEvent) => void;
  onUpdateRest: (seconds: number | null) => void;
}

function BlockCard({
  block,
  dragHandleProps,
  onDelete,
  onAddExercise,
  onDeleteExercise,
  onSaveSets,
  onExerciseDragEnd,
  onUpdateRest,
}: BlockCardProps) {
  const [localSets, setLocalSets] = useState<Record<string, TemplateSet[]>>({});
  const [savingTbeId, setSavingTbeId] = useState<string | null>(null);
  const [restDraft, setRestDraft] = useState<string>(
    block.restAfterSeconds != null ? String(block.restAfterSeconds) : "",
  );

  const isSup = block.blockType === "superset";

  const exSensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const getSets = (tbe: TemplateBlockExercise) =>
    localSets[tbe.id] ?? tbe.sets;

  const handleSetChange = (tbe: TemplateBlockExercise, idx: number, updates: Partial<TemplateSet>) => {
    const current = getSets(tbe);
    setLocalSets((prev) => ({
      ...prev,
      [tbe.id]: current.map((s, i) => (i === idx ? { ...s, ...updates } : s)),
    }));
  };

  const handleSetDelete = (tbe: TemplateBlockExercise, idx: number) => {
    const current = getSets(tbe);
    setLocalSets((prev) => ({
      ...prev,
      [tbe.id]: current
        .filter((_, i) => i !== idx)
        .map((s, i) => ({ ...s, setNumber: i + 1 })),
    }));
  };

  const handleAddSet = (tbe: TemplateBlockExercise) => {
    const current = getSets(tbe);
    setLocalSets((prev) => ({
      ...prev,
      [tbe.id]: [
        ...current,
        { setNumber: current.length + 1, weightType: "fixed" as const, isWarmup: false },
      ],
    }));
  };

  const handleSaveSets = async (tbe: TemplateBlockExercise) => {
    setSavingTbeId(tbe.id);
    await onSaveSets(tbe.id, getSets(tbe));
    setSavingTbeId(null);
  };

  return (
    <div
      className={`rounded-xl border bg-gray-950 p-4 ${
        isSup ? "border-purple-800" : "border-gray-800"
      }`}
    >
      {/* Block header */}
      <div className="mb-3 flex items-center gap-2">
        {/* Drag handle */}
        <span
          {...dragHandleProps}
          className="cursor-grab px-1 text-gray-600 hover:text-gray-400 active:cursor-grabbing"
          title="Drag to reorder"
        >
          ⠿
        </span>
        <span
          className={`rounded px-2 py-0.5 text-xs font-bold tracking-wider ${
            isSup
              ? "bg-purple-900/50 text-purple-300"
              : "bg-gray-800 text-gray-400"
          }`}
        >
          {isSup ? "⚡ SUPERSET" : "SET"}
        </span>
        <div className="ml-auto flex items-center gap-2">
          <span className="text-xs text-gray-600">Rest:</span>
          <input
            type="number"
            value={restDraft}
            onChange={(e) => setRestDraft(e.target.value)}
            onBlur={() =>
              onUpdateRest(restDraft ? parseInt(restDraft) : null)
            }
            placeholder="–"
            className="w-14 rounded bg-gray-800 px-2 py-1 text-center text-xs text-white outline-none focus:ring-1 focus:ring-gray-600"
          />
          <span className="text-xs text-gray-600">sec</span>
          <button
            onClick={onDelete}
            className="ml-2 rounded px-2 py-1 text-xs text-red-700 hover:bg-red-900/20 hover:text-red-500"
          >
            Delete block
          </button>
        </div>
      </div>

      {/* Exercises — sortable */}
      <DndContext
        sensors={exSensors}
        collisionDetection={closestCenter}
        onDragEnd={(event) => onExerciseDragEnd(block.id, event)}
      >
        <SortableContext
          items={block.exercises.map((e) => e.id)}
          strategy={verticalListSortingStrategy}
        >
          {block.exercises.map((tbe) => (
            <SortableExercise key={tbe.id} tbe={tbe}>
              {(exDragHandleProps) => (
                <div className="mb-3 border-t border-gray-800 pt-3">
                  <div className="mb-2 flex items-center gap-2">
                    <span
                      {...exDragHandleProps}
                      className="cursor-grab text-gray-600 hover:text-gray-400 active:cursor-grabbing"
                    >
                      ⠿
                    </span>
                    <span className="flex-1 text-sm font-semibold text-gray-200">
                      {tbe.exercise?.name ?? tbe.exerciseId}
                    </span>
                    <span className="text-xs capitalize text-gray-600">
                      {tbe.exercise?.primaryMuscle}
                    </span>
                    <button
                      onClick={() => onDeleteExercise(tbe.id)}
                      className="text-xs text-red-800 hover:text-red-600"
                    >
                      Remove
                    </button>
                  </div>

                  {/* Set rows */}
                  <div className="pl-8">
                    {getSets(tbe).map((set, si) => (
                      <SetRow
                        key={si}
                        set={set}
                        index={si}
                        onChange={(idx, updates) => handleSetChange(tbe, idx, updates)}
                        onDelete={(idx) => handleSetDelete(tbe, idx)}
                      />
                    ))}
                    <div className="mt-1 flex items-center gap-3">
                      <button
                        onClick={() => handleAddSet(tbe)}
                        className="text-xs text-gray-500 hover:text-gray-300"
                      >
                        + Add set
                      </button>
                      <button
                        onClick={() => handleSaveSets(tbe)}
                        disabled={savingTbeId === tbe.id}
                        className="text-xs text-blue-600 hover:text-blue-400 disabled:opacity-50"
                      >
                        {savingTbeId === tbe.id ? "Saving…" : "Save sets"}
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </SortableExercise>
          ))}
        </SortableContext>
      </DndContext>

      {/* Add exercise */}
      <button
        onClick={onAddExercise}
        className="mt-2 w-full rounded-lg border border-dashed border-gray-700 py-2 text-sm text-gray-500 hover:border-gray-500 hover:text-gray-300"
      >
        + Add Exercise
      </button>
    </div>
  );
}

// ─── Main editor page ─────────────────────────────────────────────────────────

export default function TemplateEditorPage({ params }: { params: Promise<{ id: string }> }) {
  const { id: templateId } = use(params);
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: template, isLoading } = useQuery<WorkoutTemplate>({
    queryKey: ["template", templateId],
    queryFn: () => fetchTemplate(templateId),
    staleTime: 30_000,
  });

  // Name / description debounce
  const nameRef = useRef("");
  const descRef = useRef<string | null>(null);
  const durationRef = useRef<number | null>(null);
  const metaSaveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Picker state
  const [pickerTargetBlockId, setPickerTargetBlockId] = useState<string | null>(null);

  const [localBlocks, setLocalBlocks] = useState<TemplateBlock[] | null>(null);
  const blocks = localBlocks ?? template?.blocks ?? [];

  // Sync localBlocks when template loads (first time only)
  const syncedRef = useRef(false);
  if (template && !syncedRef.current) {
    syncedRef.current = true;
    nameRef.current = template.name;
    descRef.current = template.description ?? null;
    durationRef.current = template.estimatedDurationMinutes ?? null;
  }

  const invalidateTemplate = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ["template", templateId] });
    setLocalBlocks(null);
  }, [queryClient, templateId]);

  // ── Metadata save ──────────────────────────────────────────────────────────
  const scheduleSaveMeta = () => {
    if (metaSaveTimer.current) clearTimeout(metaSaveTimer.current);
    metaSaveTimer.current = setTimeout(async () => {
      await updateTemplateApi(templateId, {
        name: nameRef.current,
        description: descRef.current,
        estimatedDurationMinutes: durationRef.current,
      });
      queryClient.invalidateQueries({ queryKey: ["template", templateId] });
    }, 800);
  };

  // ── Block mutations ────────────────────────────────────────────────────────
  const addBlockMutation = useMutation({
    mutationFn: (type: "set" | "superset") =>
      addBlockApi(templateId, { blockType: type, order: blocks.length }),
    onSuccess: invalidateTemplate,
  });

  const deleteBlockMutation = useMutation({
    mutationFn: (blockId: string) => deleteBlockApi(templateId, blockId),
    onSuccess: invalidateTemplate,
  });

  const updateRestMutation = useMutation({
    mutationFn: ({ blockId, seconds }: { blockId: string; seconds: number | null }) =>
      updateBlockApi(templateId, blockId, { restAfterSeconds: seconds }),
    onSuccess: invalidateTemplate,
  });

  // ── Block drag reorder ─────────────────────────────────────────────────────
  const blockSensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const handleBlockDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const oldIdx = blocks.findIndex((b) => b.id === active.id);
    const newIdx = blocks.findIndex((b) => b.id === over.id);
    const reordered = arrayMove(blocks, oldIdx, newIdx).map((b, i) => ({ ...b, order: i }));
    setLocalBlocks(reordered);

    await reorderBlocksApi(
      templateId,
      reordered.map((b) => ({ id: b.id, order: b.order })),
    );
    invalidateTemplate();
  };

  // ── Exercise mutations ─────────────────────────────────────────────────────
  const handleAddExercise = async (exercise: Exercise) => {
    if (!pickerTargetBlockId) return;
    const block = blocks.find((b) => b.id === pickerTargetBlockId);
    if (!block) return;
    await addExerciseToBlockApi(templateId, pickerTargetBlockId, {
      exerciseId: exercise.id,
      orderInBlock: block.exercises.length,
      sets: [{ setNumber: 1, weightType: "fixed", isWarmup: false }],
    });
    setPickerTargetBlockId(null);
    invalidateTemplate();
  };

  const handleDeleteExercise = async (blockId: string, tbeId: string) => {
    if (!confirm("Remove this exercise from the block?")) return;
    await deleteBlockExerciseApi(templateId, blockId, tbeId);
    invalidateTemplate();
  };

  const handleSaveSets = async (blockId: string, tbeId: string, sets: TemplateSet[]) => {
    await updateBlockExerciseApi(templateId, blockId, tbeId, { sets });
    invalidateTemplate();
  };

  const handleExerciseDragEnd = async (blockId: string, event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const block = blocks.find((b) => b.id === blockId);
    if (!block) return;

    const oldIdx = block.exercises.findIndex((e) => e.id === active.id);
    const newIdx = block.exercises.findIndex((e) => e.id === over.id);
    const reordered = arrayMove(block.exercises, oldIdx, newIdx).map((e, i) => ({
      ...e,
      orderInBlock: i,
    }));
    setLocalBlocks(
      blocks.map((b) => (b.id === blockId ? { ...b, exercises: reordered } : b)),
    );

    await reorderBlockExercisesApi(
      templateId,
      blockId,
      reordered.map((e) => ({ id: e.id, orderInBlock: e.orderInBlock })),
    );
    invalidateTemplate();
  };

  // ── Delete template ────────────────────────────────────────────────────────
  const handleDeleteTemplate = async () => {
    if (!confirm("Permanently delete this template?")) return;
    await deleteTemplateApi(templateId);
    router.push("/templates");
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-black">
        <div className="text-gray-500">Loading…</div>
      </div>
    );
  }

  if (!template) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-black">
        <div className="text-gray-400">Template not found.</div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-black">
      {/* ── Left panel: Exercise picker ─────────────────────────────────── */}
      <aside className="sticky top-0 h-screen w-72 shrink-0 overflow-hidden border-r border-gray-900">
        <div className="flex h-full flex-col">
          <div className="border-b border-gray-900 px-4 py-3">
            <p className="text-xs font-bold uppercase tracking-wider text-gray-500">
              Exercise Library
            </p>
            {pickerTargetBlockId && (
              <p className="mt-1 text-xs text-blue-400">
                Click an exercise to add it to the selected block
              </p>
            )}
          </div>
          <div className="min-h-0 flex-1">
            <ExercisePicker onSelect={handleAddExercise} />
          </div>
        </div>
      </aside>

      {/* ── Right panel: Template canvas ────────────────────────────────── */}
      <main className="min-w-0 flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-2xl">
          {/* Breadcrumb */}
          <Link href="/templates" className="text-sm text-gray-500 hover:text-gray-400">
            ← Templates
          </Link>

          {/* Template metadata */}
          <div className="mt-2 mb-6 rounded-xl border border-gray-800 bg-gray-950 p-4">
            <input
              type="text"
              defaultValue={template.name}
              onChange={(e) => {
                nameRef.current = e.target.value;
                scheduleSaveMeta();
              }}
              placeholder="Template name"
              className="w-full bg-transparent text-xl font-bold text-white outline-none placeholder-gray-700 focus:placeholder-gray-600"
            />
            <textarea
              defaultValue={template.description ?? ""}
              onChange={(e) => {
                descRef.current = e.target.value || null;
                scheduleSaveMeta();
              }}
              placeholder="Description (optional)"
              rows={2}
              className="mt-2 w-full resize-none bg-transparent text-sm text-gray-400 outline-none placeholder-gray-700"
            />
            <div className="mt-3 flex items-center gap-3">
              <label className="text-xs text-gray-600">Duration (min):</label>
              <input
                type="number"
                defaultValue={template.estimatedDurationMinutes ?? ""}
                onChange={(e) => {
                  durationRef.current = e.target.value ? parseInt(e.target.value) : null;
                  scheduleSaveMeta();
                }}
                placeholder="–"
                className="w-16 rounded bg-gray-800 px-2 py-1 text-center text-sm text-white outline-none focus:ring-1 focus:ring-gray-600"
              />
              <button
                onClick={handleDeleteTemplate}
                className="ml-auto text-xs text-red-800 hover:text-red-600"
              >
                Delete template
              </button>
            </div>
          </div>

          {/* Picker target indicator */}
          {pickerTargetBlockId && (
            <div className="mb-4 flex items-center justify-between rounded-lg border border-blue-900 bg-blue-950/30 px-4 py-2">
              <span className="text-sm text-blue-300">
                Select an exercise from the left panel to add it
              </span>
              <button
                onClick={() => setPickerTargetBlockId(null)}
                className="text-xs text-blue-500 hover:text-blue-300"
              >
                Cancel
              </button>
            </div>
          )}

          {/* Blocks */}
          <DndContext
            sensors={blockSensors}
            collisionDetection={closestCenter}
            onDragEnd={handleBlockDragEnd}
          >
            <SortableContext
              items={blocks.map((b) => b.id)}
              strategy={verticalListSortingStrategy}
            >
              <div className="space-y-4">
                {blocks.map((block) => (
                  <SortableBlock key={block.id} block={block}>
                    {(dragHandleProps) => (
                      <BlockCard
                        block={block}
                        templateId={templateId}
                        dragHandleProps={dragHandleProps}
                        selectedExercise={null}
                        onDelete={() => {
                          if (confirm("Delete this block and all its exercises?"))
                            deleteBlockMutation.mutate(block.id);
                        }}
                        onAddExercise={() => setPickerTargetBlockId(block.id)}
                        onDeleteExercise={(tbeId) => handleDeleteExercise(block.id, tbeId)}
                        onSaveSets={(tbeId, sets) =>
                          handleSaveSets(block.id, tbeId, sets)
                        }
                        onExerciseDragEnd={handleExerciseDragEnd}
                        onUpdateRest={(seconds) =>
                          updateRestMutation.mutate({ blockId: block.id, seconds })
                        }
                      />
                    )}
                  </SortableBlock>
                ))}
              </div>
            </SortableContext>
          </DndContext>

          {/* Add block buttons */}
          <div className="mt-6 flex gap-3">
            <button
              onClick={() => addBlockMutation.mutate("set")}
              disabled={addBlockMutation.isPending}
              className="flex-1 rounded-lg border border-dashed border-gray-700 py-3 text-sm text-gray-500 hover:border-gray-500 hover:text-gray-300 disabled:opacity-50"
            >
              + Add Set Block
            </button>
            <button
              onClick={() => addBlockMutation.mutate("superset")}
              disabled={addBlockMutation.isPending}
              className="flex-1 rounded-lg border border-dashed border-purple-900 py-3 text-sm text-purple-600 hover:border-purple-700 hover:text-purple-400 disabled:opacity-50"
            >
              ⚡ Add Superset
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
