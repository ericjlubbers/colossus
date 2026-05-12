"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { MuscleGroup, EquipmentType } from "@colossus/types";
import { fetchExercises } from "@/lib/api";

// ─── Constants ────────────────────────────────────────────────────────────────

const MUSCLE_GROUPS: MuscleGroup[] = [
  "chest",
  "back",
  "shoulders",
  "biceps",
  "triceps",
  "forearms",
  "core",
  "quads",
  "hamstrings",
  "glutes",
  "calves",
];

const EQUIPMENT_TYPES: EquipmentType[] = [
  "barbell",
  "dumbbell",
  "cable",
  "machine",
  "bodyweight",
  "kettlebell",
  "band",
  "other",
];

const MUSCLE_COLORS: Record<MuscleGroup, string> = {
  chest: "bg-red-500/20 text-red-400",
  back: "bg-blue-500/20 text-blue-400",
  shoulders: "bg-orange-500/20 text-orange-400",
  biceps: "bg-purple-500/20 text-purple-400",
  triceps: "bg-violet-500/20 text-violet-400",
  forearms: "bg-amber-500/20 text-amber-400",
  core: "bg-yellow-500/20 text-yellow-400",
  quads: "bg-green-500/20 text-green-400",
  hamstrings: "bg-teal-500/20 text-teal-400",
  glutes: "bg-pink-500/20 text-pink-400",
  calves: "bg-cyan-500/20 text-cyan-400",
};

const MUSCLE_COLORS_ACTIVE: Record<MuscleGroup, string> = {
  chest: "bg-red-500 text-white",
  back: "bg-blue-500 text-white",
  shoulders: "bg-orange-500 text-white",
  biceps: "bg-purple-500 text-white",
  triceps: "bg-violet-500 text-white",
  forearms: "bg-amber-500 text-white",
  core: "bg-yellow-500 text-white",
  quads: "bg-green-500 text-white",
  hamstrings: "bg-teal-500 text-white",
  glutes: "bg-pink-500 text-white",
  calves: "bg-cyan-500 text-white",
};

const PAGE_SIZE = 24;

// ─── Helpers ──────────────────────────────────────────────────────────────────

function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debounced;
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function MuscleBadge({
  muscle,
  size = "sm",
}: {
  muscle: MuscleGroup;
  size?: "sm" | "xs";
}) {
  const sizeClass = size === "sm" ? "px-2.5 py-1 text-xs" : "px-2 py-0.5 text-[11px]";
  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${sizeClass} ${MUSCLE_COLORS[muscle]}`}
    >
      {capitalize(muscle)}
    </span>
  );
}

function EquipmentBadge({ equipment }: { equipment: string }) {
  return (
    <span className="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium bg-gray-700/50 text-gray-300">
      {capitalize(equipment)}
    </span>
  );
}

function SkeletonCard() {
  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 p-5 animate-pulse">
      <div className="h-5 w-3/4 rounded bg-gray-800 mb-4" />
      <div className="flex gap-2 mb-3">
        <div className="h-6 w-16 rounded-full bg-gray-800" />
        <div className="h-6 w-20 rounded-full bg-gray-800" />
      </div>
      <div className="flex gap-1.5 flex-wrap">
        <div className="h-5 w-14 rounded-full bg-gray-800" />
        <div className="h-5 w-16 rounded-full bg-gray-800" />
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function ExercisesPage() {
  const [search, setSearch] = useState("");
  const [selectedMuscle, setSelectedMuscle] = useState<MuscleGroup | null>(null);
  const [selectedEquipment, setSelectedEquipment] = useState<EquipmentType | null>(null);
  const [page, setPage] = useState(1);
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);

  const debouncedSearch = useDebounce(search, 300);

  // Reset page when filters change
  const prevFiltersRef = useRef({ muscle: selectedMuscle, equipment: selectedEquipment, q: debouncedSearch });
  useEffect(() => {
    const prev = prevFiltersRef.current;
    if (
      prev.muscle !== selectedMuscle ||
      prev.equipment !== selectedEquipment ||
      prev.q !== debouncedSearch
    ) {
      setPage(1);
      prevFiltersRef.current = { muscle: selectedMuscle, equipment: selectedEquipment, q: debouncedSearch };
    }
  }, [selectedMuscle, selectedEquipment, debouncedSearch]);

  const queryParams = useMemo(
    () => ({
      primaryMuscle: selectedMuscle ?? undefined,
      equipment: selectedEquipment ?? undefined,
      q: debouncedSearch || undefined,
      page,
      pageSize: PAGE_SIZE,
    }),
    [selectedMuscle, selectedEquipment, debouncedSearch, page],
  );

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["exercises", queryParams],
    queryFn: () => fetchExercises(queryParams),
  });

  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;

  const clearFilters = useCallback(() => {
    setSearch("");
    setSelectedMuscle(null);
    setSelectedEquipment(null);
    setPage(1);
  }, []);

  const hasActiveFilters = selectedMuscle !== null || selectedEquipment !== null || search !== "";

  // ── Filter sidebar content (shared between desktop & mobile) ──

  const filterContent = (
    <div className="space-y-6">
      {/* Muscle Group Filter */}
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">
          Muscle Group
        </h3>
        <div className="flex flex-wrap gap-2">
          {MUSCLE_GROUPS.map((muscle) => (
            <button
              key={muscle}
              onClick={() =>
                setSelectedMuscle((prev) => (prev === muscle ? null : muscle))
              }
              className={`rounded-full px-3 py-1.5 text-xs font-medium transition-all ${
                selectedMuscle === muscle
                  ? MUSCLE_COLORS_ACTIVE[muscle]
                  : `${MUSCLE_COLORS[muscle]} hover:opacity-80`
              }`}
            >
              {capitalize(muscle)}
            </button>
          ))}
        </div>
      </div>

      {/* Equipment Filter */}
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">
          Equipment
        </h3>
        <div className="flex flex-wrap gap-2">
          {EQUIPMENT_TYPES.map((equip) => (
            <button
              key={equip}
              onClick={() =>
                setSelectedEquipment((prev) => (prev === equip ? null : equip))
              }
              className={`rounded-full px-3 py-1.5 text-xs font-medium transition-all ${
                selectedEquipment === equip
                  ? "bg-white text-gray-900"
                  : "bg-gray-700/50 text-gray-300 hover:bg-gray-700 hover:text-gray-100"
              }`}
            >
              {capitalize(equip)}
            </button>
          ))}
        </div>
      </div>

      {/* Clear Filters */}
      {hasActiveFilters && (
        <button
          onClick={clearFilters}
          className="w-full rounded-lg border border-gray-700 py-2 text-sm text-gray-400 hover:text-white hover:border-gray-500 transition-colors"
        >
          Clear All Filters
        </button>
      )}
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-white">
          Exercise Library
        </h1>
        <p className="mt-2 text-gray-400">
          Browse and discover exercises for your training.
        </p>
      </div>

      {/* Search Bar */}
      <div className="mb-6 flex gap-3">
        <div className="relative flex-1">
          <svg
            className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            type="text"
            placeholder="Search exercises..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-xl border border-gray-800 bg-gray-900 py-3 pl-10 pr-4 text-sm text-gray-100 placeholder-gray-500 focus:border-gray-600 focus:outline-none focus:ring-1 focus:ring-gray-600 transition-colors"
          />
        </div>
        {/* Mobile filter toggle */}
        <button
          onClick={() => setMobileFiltersOpen((v) => !v)}
          className="lg:hidden rounded-xl border border-gray-800 bg-gray-900 px-4 py-3 text-sm text-gray-400 hover:text-white hover:border-gray-600 transition-colors flex items-center gap-2"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
            />
          </svg>
          Filters
          {hasActiveFilters && (
            <span className="h-2 w-2 rounded-full bg-blue-500" />
          )}
        </button>
      </div>

      {/* Mobile filters drawer */}
      {mobileFiltersOpen && (
        <div className="lg:hidden mb-6 rounded-xl border border-gray-800 bg-gray-900 p-5">
          {filterContent}
        </div>
      )}

      <div className="flex gap-8">
        {/* Desktop sidebar */}
        <aside className="hidden lg:block w-64 shrink-0">
          <div className="sticky top-[4.5rem]">{filterContent}</div>
        </aside>

        {/* Content area */}
        <div className="flex-1 min-w-0">
          {/* Results count */}
          {data && !isLoading && (
            <p className="text-sm text-gray-500 mb-4">
              {data.total} exercise{data.total !== 1 ? "s" : ""} found
              {hasActiveFilters ? " matching your filters" : ""}
            </p>
          )}

          {/* Error state */}
          {isError && (
            <div className="rounded-xl border border-red-900/50 bg-red-950/30 p-8 text-center">
              <p className="text-red-400 font-medium">Failed to load exercises</p>
              <p className="text-sm text-red-400/70 mt-1">
                {error instanceof Error ? error.message : "An unexpected error occurred."}
              </p>
            </div>
          )}

          {/* Loading state */}
          {isLoading && (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
              {Array.from({ length: 12 }).map((_, i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          )}

          {/* Empty state */}
          {data && data.items.length === 0 && !isLoading && (
            <div className="rounded-xl border border-gray-800 bg-gray-900/50 py-16 text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-700"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p className="mt-4 text-gray-400 font-medium">
                No exercises found
              </p>
              <p className="mt-1 text-sm text-gray-600">
                Try adjusting your search or filters.
              </p>
              {hasActiveFilters && (
                <button
                  onClick={clearFilters}
                  className="mt-4 rounded-lg bg-gray-800 px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 transition-colors"
                >
                  Clear Filters
                </button>
              )}
            </div>
          )}

          {/* Exercise grid */}
          {data && data.items.length > 0 && (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                {data.items.map((exercise) => (
                  <Link
                    key={exercise.id}
                    href={`/exercises/${exercise.id}`}
                    className="group rounded-xl border border-gray-800 bg-gray-900 p-5 transition-all hover:border-gray-700 hover:bg-gray-900/80 hover:shadow-lg hover:shadow-black/20"
                  >
                    <h3 className="text-sm font-semibold text-white group-hover:text-blue-400 transition-colors truncate">
                      {exercise.name}
                    </h3>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <MuscleBadge muscle={exercise.primaryMuscle} />
                      <EquipmentBadge equipment={exercise.equipment} />
                    </div>
                    {exercise.secondaryMuscles.length > 0 && (
                      <div className="mt-2.5 flex flex-wrap gap-1.5">
                        {exercise.secondaryMuscles.map((m) => (
                          <MuscleBadge key={m} muscle={m} size="xs" />
                        ))}
                      </div>
                    )}
                  </Link>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="mt-8 flex items-center justify-center gap-3">
                  <button
                    disabled={page <= 1}
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    className="rounded-lg border border-gray-800 bg-gray-900 px-4 py-2 text-sm font-medium text-gray-300 transition-colors hover:border-gray-700 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:border-gray-800 disabled:hover:text-gray-300"
                  >
                    ← Previous
                  </button>
                  <span className="text-sm text-gray-500">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    disabled={page >= totalPages}
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    className="rounded-lg border border-gray-800 bg-gray-900 px-4 py-2 text-sm font-medium text-gray-300 transition-colors hover:border-gray-700 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:border-gray-800 disabled:hover:text-gray-300"
                  >
                    Next →
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
