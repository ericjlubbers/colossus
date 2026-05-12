"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useParams } from "next/navigation";
import type { MuscleGroup } from "@colossus/types";
import { fetchExercise } from "@/lib/api";
import type { ExerciseMedia } from "@/lib/api";

// ─── Badge colors ─────────────────────────────────────────────────────────────

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

// ─── Helpers ──────────────────────────────────────────────────────────────────

function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function MuscleBadge({
  muscle,
  size = "md",
}: {
  muscle: MuscleGroup;
  size?: "md" | "sm";
}) {
  const sizeClass = size === "md" ? "px-3 py-1.5 text-sm" : "px-2.5 py-1 text-xs";
  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${sizeClass} ${MUSCLE_COLORS[muscle]}`}
    >
      {capitalize(muscle)}
    </span>
  );
}

function EquipmentBadge({
  equipment,
  size = "md",
}: {
  equipment: string;
  size?: "md" | "sm";
}) {
  const sizeClass = size === "md" ? "px-3 py-1.5 text-sm" : "px-2.5 py-1 text-xs";
  return (
    <span
      className={`inline-flex items-center rounded-full font-medium bg-gray-700/50 text-gray-300 ${sizeClass}`}
    >
      {capitalize(equipment)}
    </span>
  );
}

function MediaViewer({ media }: { media: ExerciseMedia[] }) {
  if (media.length === 0) return null;

  const videos = media.filter((m) => m.mediaType === "video" && m.url);
  const images = media.filter((m) => m.mediaType === "image" && m.url);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-white">Media</h2>
      {videos.length > 0 && (
        <div className="grid grid-cols-1 gap-4">
          {videos.map((v) => (
            <video
              key={v.id}
              src={v.url!}
              controls
              className="w-full rounded-xl border border-gray-800 bg-black"
            />
          ))}
        </div>
      )}
      {images.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {images.map((img) => (
            /* eslint-disable-next-line @next/next/no-img-element */
            <img
              key={img.id}
              src={img.url!}
              alt="Exercise demonstration"
              className="w-full rounded-xl border border-gray-800 object-cover"
            />
          ))}
        </div>
      )}
    </div>
  );
}

function DetailSkeleton() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="h-4 w-32 rounded bg-gray-800" />
      <div className="h-9 w-2/3 rounded bg-gray-800" />
      <div className="flex gap-3">
        <div className="h-8 w-20 rounded-full bg-gray-800" />
        <div className="h-8 w-24 rounded-full bg-gray-800" />
      </div>
      <div className="space-y-3 pt-4">
        <div className="h-4 w-full rounded bg-gray-800" />
        <div className="h-4 w-5/6 rounded bg-gray-800" />
        <div className="h-4 w-4/6 rounded bg-gray-800" />
      </div>
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function ExerciseDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;

  const { data: exercise, isLoading, isError, error } = useQuery({
    queryKey: ["exercise", id],
    queryFn: () => fetchExercise(id),
    enabled: !!id,
  });

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back link */}
      <Link
        href="/exercises"
        className="inline-flex items-center gap-1.5 text-sm text-gray-400 hover:text-white transition-colors mb-6"
      >
        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 19l-7-7 7-7"
          />
        </svg>
        Back to Exercises
      </Link>

      {/* Loading */}
      {isLoading && <DetailSkeleton />}

      {/* Error / 404 */}
      {isError && (
        <div className="rounded-xl border border-red-900/50 bg-red-950/30 p-12 text-center">
          {error instanceof Error && error.message.includes("404") ? (
            <>
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
              <p className="mt-4 text-lg font-medium text-gray-300">
                Exercise Not Found
              </p>
              <p className="mt-1 text-sm text-gray-500">
                This exercise may have been removed or the link is incorrect.
              </p>
              <Link
                href="/exercises"
                className="mt-6 inline-block rounded-lg bg-gray-800 px-5 py-2.5 text-sm font-medium text-gray-300 hover:bg-gray-700 transition-colors"
              >
                Browse Exercises
              </Link>
            </>
          ) : (
            <>
              <p className="text-red-400 font-medium">
                Failed to load exercise
              </p>
              <p className="text-sm text-red-400/70 mt-1">
                {error instanceof Error
                  ? error.message
                  : "An unexpected error occurred."}
              </p>
            </>
          )}
        </div>
      )}

      {/* Exercise details */}
      {exercise && (
        <div className="space-y-8">
          {/* Title */}
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">
              {exercise.name}
            </h1>
            {exercise.isCustom && (
              <span className="mt-2 inline-block rounded-full bg-blue-500/20 px-2.5 py-0.5 text-xs font-medium text-blue-400">
                Custom
              </span>
            )}
          </div>

          {/* Primary badges */}
          <div className="flex flex-wrap gap-3">
            <MuscleBadge muscle={exercise.primaryMuscle} />
            <EquipmentBadge equipment={exercise.equipment} />
          </div>

          {/* Secondary muscles */}
          {exercise.secondaryMuscles.length > 0 && (
            <div>
              <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">
                Secondary Muscles
              </h2>
              <div className="flex flex-wrap gap-2">
                {exercise.secondaryMuscles.map((m) => (
                  <MuscleBadge key={m} muscle={m} size="sm" />
                ))}
              </div>
            </div>
          )}

          {/* Description */}
          {exercise.description && (
            <div>
              <h2 className="text-lg font-semibold text-white mb-3">
                Description
              </h2>
              <p className="text-gray-300 leading-relaxed">
                {exercise.description}
              </p>
            </div>
          )}

          {/* Instructions */}
          {exercise.instructions && (
            <div>
              <h2 className="text-lg font-semibold text-white mb-3">
                Instructions
              </h2>
              <ol className="space-y-3">
                {exercise.instructions
                  .split("\n")
                  .filter((line) => line.trim() !== "")
                  .map((step, i) => (
                    <li key={i} className="flex gap-3">
                      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-gray-800 text-xs font-semibold text-gray-400">
                        {i + 1}
                      </span>
                      <p className="text-gray-300 leading-relaxed pt-0.5">
                        {step.trim().replace(/^\d+\.\s*/, "")}
                      </p>
                    </li>
                  ))}
              </ol>
            </div>
          )}

          {/* Media */}
          <MediaViewer media={exercise.media} />
        </div>
      )}
    </div>
  );
}
