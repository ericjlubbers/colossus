import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import type { MuscleGroup, EquipmentType } from "@colossus/types";
import { fetchExercises, type Exercise } from "../lib/api";
import type { RootStackParamList } from "../navigation/types";

// ─── Constants ────────────────────────────────────────────────────────────────

const MUSCLE_GROUPS: MuscleGroup[] = [
  "chest", "back", "shoulders", "biceps", "triceps",
  "forearms", "core", "quads", "hamstrings", "glutes", "calves",
];

const EQUIPMENT_TYPES: EquipmentType[] = [
  "barbell", "dumbbell", "cable", "machine",
  "bodyweight", "kettlebell", "band", "other",
];

// Per-muscle accent colors (bg + text)
const MUSCLE_COLORS: Record<MuscleGroup, { bg: string; text: string }> = {
  chest:      { bg: "#3b1a1a", text: "#f87171" },
  back:       { bg: "#1a2a3b", text: "#60a5fa" },
  shoulders:  { bg: "#3b2a1a", text: "#fb923c" },
  biceps:     { bg: "#2e1a3b", text: "#c084fc" },
  triceps:    { bg: "#261a3b", text: "#a78bfa" },
  forearms:   { bg: "#3b2e1a", text: "#fbbf24" },
  core:       { bg: "#3b3a1a", text: "#facc15" },
  quads:      { bg: "#1a3b22", text: "#4ade80" },
  hamstrings: { bg: "#1a3b36", text: "#2dd4bf" },
  glutes:     { bg: "#3b1a2e", text: "#f472b6" },
  calves:     { bg: "#1a393b", text: "#22d3ee" },
};

const PAGE_SIZE = 30;

// ─── Helpers ──────────────────────────────────────────────────────────────────

function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function MuscleBadge({ muscle }: { muscle: MuscleGroup }) {
  const c = MUSCLE_COLORS[muscle];
  return (
    <View style={[styles.badge, { backgroundColor: c.bg }]}>
      <Text style={[styles.badgeText, { color: c.text }]}>{capitalize(muscle)}</Text>
    </View>
  );
}

function EquipmentBadge({ equipment }: { equipment: string }) {
  return (
    <View style={styles.equipBadge}>
      <Text style={styles.equipBadgeText}>{capitalize(equipment)}</Text>
    </View>
  );
}

function ExerciseCard({
  exercise,
  onPress,
}: {
  exercise: Exercise;
  onPress: () => void;
}) {
  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}
    >
      <Text style={styles.cardTitle} numberOfLines={1}>{exercise.name}</Text>
      <View style={styles.cardBadgeRow}>
        <MuscleBadge muscle={exercise.primaryMuscle} />
        <EquipmentBadge equipment={exercise.equipment} />
      </View>
      {exercise.secondaryMuscles.length > 0 && (
        <View style={styles.secondaryRow}>
          {exercise.secondaryMuscles.slice(0, 3).map((m) => (
            <MuscleBadge key={m} muscle={m} />
          ))}
        </View>
      )}
    </Pressable>
  );
}

function ExerciseSkeleton() {
  return (
    <View style={styles.skeleton}>
      <View style={styles.skeletonTitle} />
      <View style={styles.skeletonRow}>
        <View style={styles.skeletonBadge} />
        <View style={[styles.skeletonBadge, { width: 64 }]} />
      </View>
    </View>
  );
}

// ─── Filter Sheet ─────────────────────────────────────────────────────────────

function FilterSheet({
  visible,
  selectedMuscle,
  selectedEquipment,
  onSelectMuscle,
  onSelectEquipment,
  onClear,
  onClose,
}: {
  visible: boolean;
  selectedMuscle: MuscleGroup | null;
  selectedEquipment: EquipmentType | null;
  onSelectMuscle: (m: MuscleGroup | null) => void;
  onSelectEquipment: (e: EquipmentType | null) => void;
  onClear: () => void;
  onClose: () => void;
}) {
  const hasActive = selectedMuscle !== null || selectedEquipment !== null;

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <View style={styles.sheetContainer}>
        {/* Sheet header */}
        <View style={styles.sheetHeader}>
          <Text style={styles.sheetTitle}>Filter Exercises</Text>
          <Pressable onPress={onClose} style={styles.sheetDone} hitSlop={12}>
            <Text style={styles.sheetDoneText}>Done</Text>
          </Pressable>
        </View>

        <ScrollView style={styles.sheetScroll} contentContainerStyle={styles.sheetContent}>
          {/* Muscle group */}
          <Text style={styles.filterSectionLabel}>Muscle Group</Text>
          <View style={styles.filterChipWrap}>
            {MUSCLE_GROUPS.map((m) => {
              const active = selectedMuscle === m;
              const c = MUSCLE_COLORS[m];
              return (
                <Pressable
                  key={m}
                  onPress={() => onSelectMuscle(active ? null : m)}
                  style={[
                    styles.filterChip,
                    active
                      ? { backgroundColor: c.text }
                      : { backgroundColor: c.bg },
                  ]}
                >
                  <Text
                    style={[
                      styles.filterChipText,
                      active ? { color: "#000" } : { color: c.text },
                    ]}
                  >
                    {capitalize(m)}
                  </Text>
                </Pressable>
              );
            })}
          </View>

          {/* Equipment */}
          <Text style={[styles.filterSectionLabel, { marginTop: 24 }]}>Equipment</Text>
          <View style={styles.filterChipWrap}>
            {EQUIPMENT_TYPES.map((e) => {
              const active = selectedEquipment === e;
              return (
                <Pressable
                  key={e}
                  onPress={() => onSelectEquipment(active ? null : e)}
                  style={[
                    styles.filterChip,
                    active
                      ? { backgroundColor: "#fff" }
                      : { backgroundColor: "#1f2937" },
                  ]}
                >
                  <Text
                    style={[
                      styles.filterChipText,
                      active ? { color: "#000" } : { color: "#9ca3af" },
                    ]}
                  >
                    {capitalize(e)}
                  </Text>
                </Pressable>
              );
            })}
          </View>

          {/* Clear */}
          {hasActive && (
            <Pressable onPress={onClear} style={styles.clearBtn}>
              <Text style={styles.clearBtnText}>Clear All Filters</Text>
            </Pressable>
          )}
        </ScrollView>
      </View>
    </Modal>
  );
}

// ─── Main Screen ──────────────────────────────────────────────────────────────

type Props = NativeStackScreenProps<RootStackParamList, "ExerciseList">;

export default function ExerciseListScreen({ navigation }: Props) {
  const [search, setSearch] = useState("");
  const [selectedMuscle, setSelectedMuscle] = useState<MuscleGroup | null>(null);
  const [selectedEquipment, setSelectedEquipment] = useState<EquipmentType | null>(null);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [page, setPage] = useState(1);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const debouncedSearch = useDebounce(search, 300);

  // Track previous filters to reset page on change
  const prevFilters = useRef({ muscle: selectedMuscle, equip: selectedEquipment, q: debouncedSearch });

  const load = useCallback(
    async (pageNum: number, replace: boolean) => {
      if (pageNum === 1) setLoading(true);
      else setLoadingMore(true);
      setError(null);
      try {
        const res = await fetchExercises({
          primaryMuscle: selectedMuscle ?? undefined,
          equipment: selectedEquipment ?? undefined,
          q: debouncedSearch || undefined,
          page: pageNum,
          pageSize: PAGE_SIZE,
        });
        setTotal(res.total);
        setExercises((prev) => (replace ? res.items : [...prev, ...res.items]));
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load exercises");
      } finally {
        setLoading(false);
        setLoadingMore(false);
      }
    },
    [selectedMuscle, selectedEquipment, debouncedSearch],
  );

  // Reset and reload when filters change
  useEffect(() => {
    const prev = prevFilters.current;
    const changed =
      prev.muscle !== selectedMuscle ||
      prev.equip !== selectedEquipment ||
      prev.q !== debouncedSearch;

    if (changed) {
      prevFilters.current = { muscle: selectedMuscle, equip: selectedEquipment, q: debouncedSearch };
      setPage(1);
      load(1, true);
    }
  }, [selectedMuscle, selectedEquipment, debouncedSearch, load]);

  // Initial load
  useEffect(() => {
    load(1, true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleLoadMore = useCallback(() => {
    const hasMore = exercises.length < total;
    if (!loadingMore && !loading && hasMore) {
      const next = page + 1;
      setPage(next);
      load(next, false);
    }
  }, [exercises.length, total, loadingMore, loading, page, load]);

  const handleClearFilters = useCallback(() => {
    setSelectedMuscle(null);
    setSelectedEquipment(null);
    setSearch("");
  }, []);

  const hasActiveFilters = selectedMuscle !== null || selectedEquipment !== null || search !== "";
  const activeFilterCount =
    (selectedMuscle ? 1 : 0) + (selectedEquipment ? 1 : 0);

  return (
    <View style={styles.container}>
      {/* Search + filter row */}
      <View style={styles.searchRow}>
        <View style={styles.searchBox}>
          <Text style={styles.searchIcon}>⌕</Text>
          <TextInput
            style={styles.searchInput}
            placeholder="Search exercises…"
            placeholderTextColor="#6b7280"
            value={search}
            onChangeText={setSearch}
            autoCorrect={false}
            autoCapitalize="none"
            clearButtonMode="while-editing"
          />
        </View>
        <Pressable
          onPress={() => setFiltersOpen(true)}
          style={[styles.filterBtn, hasActiveFilters && styles.filterBtnActive]}
        >
          <Text style={styles.filterBtnText}>
            {activeFilterCount > 0 ? `Filters (${activeFilterCount})` : "Filters"}
          </Text>
        </Pressable>
      </View>

      {/* Results count */}
      {!loading && (
        <Text style={styles.resultCount}>
          {total} exercise{total !== 1 ? "s" : ""}
          {hasActiveFilters ? " (filtered)" : ""}
        </Text>
      )}

      {/* Exercise list */}
      {loading ? (
        <FlatList
          data={Array.from({ length: 8 })}
          keyExtractor={(_, i) => String(i)}
          renderItem={() => <ExerciseSkeleton />}
          contentContainerStyle={styles.listContent}
          scrollEnabled={false}
        />
      ) : error ? (
        <View style={styles.centerState}>
          <Text style={styles.errorText}>{error}</Text>
          <Pressable onPress={() => load(1, true)} style={styles.retryBtn}>
            <Text style={styles.retryText}>Retry</Text>
          </Pressable>
        </View>
      ) : exercises.length === 0 ? (
        <View style={styles.centerState}>
          <Text style={styles.emptyText}>No exercises found.</Text>
          {hasActiveFilters && (
            <Pressable onPress={handleClearFilters} style={styles.retryBtn}>
              <Text style={styles.retryText}>Clear Filters</Text>
            </Pressable>
          )}
        </View>
      ) : (
        <FlatList
          data={exercises}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <ExerciseCard
              exercise={item}
              onPress={() => navigation.navigate("ExerciseDetail", { exerciseId: item.id, exerciseName: item.name })}
            />
          )}
          contentContainerStyle={styles.listContent}
          onEndReached={handleLoadMore}
          onEndReachedThreshold={0.4}
          ListFooterComponent={
            loadingMore ? (
              <ActivityIndicator color="#6b7280" style={{ marginVertical: 16 }} />
            ) : null
          }
        />
      )}

      {/* Filter sheet */}
      <FilterSheet
        visible={filtersOpen}
        selectedMuscle={selectedMuscle}
        selectedEquipment={selectedEquipment}
        onSelectMuscle={setSelectedMuscle}
        onSelectEquipment={setSelectedEquipment}
        onClear={handleClearFilters}
        onClose={() => setFiltersOpen(false)}
      />
    </View>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },

  // Search row
  searchRow: { flexDirection: "row", gap: 10, paddingHorizontal: 16, paddingTop: 12, paddingBottom: 8 },
  searchBox: {
    flex: 1, flexDirection: "row", alignItems: "center",
    backgroundColor: "#111827", borderRadius: 12, borderWidth: 1, borderColor: "#1f2937",
    paddingHorizontal: 12, height: 44,
  },
  searchIcon: { color: "#6b7280", fontSize: 18, marginRight: 8 },
  searchInput: { flex: 1, color: "#f3f4f6", fontSize: 15 },
  filterBtn: {
    backgroundColor: "#111827", borderRadius: 12, borderWidth: 1,
    borderColor: "#1f2937", paddingHorizontal: 14, height: 44, justifyContent: "center",
  },
  filterBtnActive: { borderColor: "#3b82f6", backgroundColor: "#1e3a5f" },
  filterBtnText: { color: "#9ca3af", fontSize: 14, fontWeight: "600" },

  // Count
  resultCount: { color: "#4b5563", fontSize: 12, paddingHorizontal: 16, paddingBottom: 8 },

  // Cards
  listContent: { paddingHorizontal: 16, paddingBottom: 24 },
  card: {
    backgroundColor: "#111827", borderRadius: 14, borderWidth: 1,
    borderColor: "#1f2937", padding: 14, marginBottom: 10,
  },
  cardPressed: { opacity: 0.75 },
  cardTitle: { color: "#f9fafb", fontSize: 16, fontWeight: "600", marginBottom: 8 },
  cardBadgeRow: { flexDirection: "row", gap: 6, flexWrap: "wrap" },
  secondaryRow: { flexDirection: "row", gap: 4, flexWrap: "wrap", marginTop: 6 },

  // Badges
  badge: { borderRadius: 20, paddingHorizontal: 10, paddingVertical: 3 },
  badgeText: { fontSize: 12, fontWeight: "600" },
  equipBadge: { backgroundColor: "#1f2937", borderRadius: 20, paddingHorizontal: 10, paddingVertical: 3 },
  equipBadgeText: { color: "#9ca3af", fontSize: 12, fontWeight: "500" },

  // Skeleton
  skeleton: {
    backgroundColor: "#111827", borderRadius: 14, borderWidth: 1,
    borderColor: "#1f2937", padding: 14, marginBottom: 10,
  },
  skeletonTitle: { height: 18, width: "70%", backgroundColor: "#1f2937", borderRadius: 8, marginBottom: 10 },
  skeletonRow: { flexDirection: "row", gap: 6 },
  skeletonBadge: { height: 24, width: 52, backgroundColor: "#1f2937", borderRadius: 20 },

  // States
  centerState: { flex: 1, alignItems: "center", justifyContent: "center", paddingHorizontal: 32 },
  errorText: { color: "#f87171", fontSize: 15, textAlign: "center", marginBottom: 16 },
  emptyText: { color: "#6b7280", fontSize: 15, textAlign: "center", marginBottom: 16 },
  retryBtn: {
    backgroundColor: "#1f2937", borderRadius: 10, paddingHorizontal: 20, paddingVertical: 10,
  },
  retryText: { color: "#d1d5db", fontSize: 14, fontWeight: "600" },

  // Filter sheet
  sheetContainer: { flex: 1, backgroundColor: "#0a0a0a" },
  sheetHeader: {
    flexDirection: "row", alignItems: "center", justifyContent: "space-between",
    paddingHorizontal: 20, paddingTop: 20, paddingBottom: 16,
    borderBottomWidth: 1, borderBottomColor: "#1f2937",
  },
  sheetTitle: { color: "#f9fafb", fontSize: 18, fontWeight: "700" },
  sheetDone: { paddingHorizontal: 4 },
  sheetDoneText: { color: "#3b82f6", fontSize: 16, fontWeight: "600" },
  sheetScroll: { flex: 1 },
  sheetContent: { paddingHorizontal: 20, paddingVertical: 20 },
  filterSectionLabel: {
    color: "#6b7280", fontSize: 11, fontWeight: "700",
    textTransform: "uppercase", letterSpacing: 1, marginBottom: 12,
  },
  filterChipWrap: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  filterChip: { borderRadius: 20, paddingHorizontal: 14, paddingVertical: 6 },
  filterChipText: { fontSize: 13, fontWeight: "600" },
  clearBtn: {
    marginTop: 28, borderRadius: 12, borderWidth: 1, borderColor: "#374151",
    paddingVertical: 12, alignItems: "center",
  },
  clearBtnText: { color: "#9ca3af", fontSize: 14, fontWeight: "600" },
});
