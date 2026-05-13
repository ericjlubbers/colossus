"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { createTemplate, deleteTemplateApi, fetchTemplates, type WorkoutTemplateSummary } from "@/lib/api";

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useState(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  });
  return debounced;
}

export default function TemplatesPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["templates", search],
    queryFn: () => fetchTemplates(search || undefined),
    staleTime: 30_000,
  });

  const createMutation = useMutation({
    mutationFn: () => createTemplate({ name: "New Template" }),
    onSuccess: (template) => {
      router.push(`/templates/${template.id}`);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteTemplateApi(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["templates"] });
    },
  });

  const handleDelete = (item: WorkoutTemplateSummary) => {
    if (!confirm(`Delete "${item.name}"? This cannot be undone.`)) return;
    deleteMutation.mutate(item.id);
  };

  return (
    <main className="min-h-screen bg-black p-6">
      <div className="mx-auto max-w-3xl">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <Link href="/" className="text-sm text-gray-500 hover:text-gray-400">
              ← Home
            </Link>
            <h1 className="mt-1 text-2xl font-bold text-white">Workout Templates</h1>
          </div>
          <button
            onClick={() => createMutation.mutate()}
            disabled={createMutation.isPending}
            className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-black hover:bg-gray-200 disabled:opacity-60"
          >
            {createMutation.isPending ? "Creating…" : "+ New Template"}
          </button>
        </div>

        {/* Search */}
        <div className="mb-4">
          <input
            type="text"
            placeholder="Search templates…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg bg-gray-900 px-4 py-2.5 text-sm text-white placeholder-gray-600 outline-none focus:ring-1 focus:ring-gray-600"
          />
        </div>

        {/* Template list */}
        {isLoading ? (
          <div className="py-20 text-center text-gray-500">Loading…</div>
        ) : !data?.items.length ? (
          <div className="py-20 text-center">
            <p className="text-gray-400">No templates yet.</p>
            <p className="mt-2 text-sm text-gray-600">
              Click &ldquo;New Template&rdquo; to create your first workout template.
            </p>
          </div>
        ) : (
          <ul className="space-y-3">
            {data.items.map((t) => (
              <li key={t.id}>
                <div className="group flex items-center gap-3 rounded-xl bg-gray-900 p-4 hover:bg-gray-800">
                  <Link href={`/templates/${t.id}`} className="min-w-0 flex-1">
                    <div className="flex items-baseline gap-3">
                      <span className="truncate font-semibold text-white">{t.name}</span>
                      {t.estimatedDurationMinutes != null && (
                        <span className="shrink-0 text-xs text-gray-500">
                          {t.estimatedDurationMinutes} min
                        </span>
                      )}
                    </div>
                    {t.description && (
                      <p className="mt-1 truncate text-sm text-gray-500">{t.description}</p>
                    )}
                    {t.tags.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1.5">
                        {t.tags.map((tag) => (
                          <span
                            key={tag}
                            className="rounded bg-gray-800 px-2 py-0.5 text-xs text-gray-400"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </Link>
                  <button
                    onClick={() => handleDelete(t)}
                    className="hidden rounded px-2 py-1 text-xs text-red-600 hover:bg-red-900/20 group-hover:block"
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  );
}
