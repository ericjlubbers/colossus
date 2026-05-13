/**
 * WorkoutSessionScreen — active workout session.
 *
 * Layout:
 *   Header: workout name / elapsed timer
 *   FlatList: one item per exercise block, with set rows beneath
 *   Each set row: weight input | reps input | Complete Set button
 *   Completed sets show a ✓ checkmark and are read-only
 *   "Finish Workout" button at the bottom
 */

import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import {
  fetchTemplate,
  fetchWorkout,
  finishWorkout,
  logSet,
  type CompletedSet,
  type WorkoutTemplate,
  type TemplateBlock,
  type TemplateBlockExercise,
} from "../lib/api";
import type { WorkoutStackParamList } from "../navigation/types";

type Props = NativeStackScreenProps<WorkoutStackParamList, "WorkoutSession">;

// ─── Rest Timer ───────────────────────────────────────────────────────────────

function useRestTimer() {
  const [seconds, setSeconds] = useState(0);
  const [active, setActive] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const start = useCallback((duration: number) => {
    setSeconds(duration);
    setActive(true);
  }, []);

  const cancel = useCallback(() => {
    setActive(false);
    setSeconds(0);
    if (intervalRef.current) clearInterval(intervalRef.current);
  }, []);

  useEffect(() => {
    if (!active) return;
    intervalRef.current = setInterval(() => {
      setSeconds((s) => {
        if (s <= 1) {
          setActive(false);
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [active]);

  return { seconds, active, start, cancel };
}

// ─── Elapsed timer ────────────────────────────────────────────────────────────

function useElapsed(startedAt: string | null) {
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    if (!startedAt) return;
    const origin = new Date(startedAt).getTime();
    const id = setInterval(() => {
      setElapsed(Math.floor((Date.now() - origin) / 1000));
    }, 1000);
    return () => clearInterval(id);
  }, [startedAt]);
  const mm = String(Math.floor(elapsed / 60)).padStart(2, "0");
  const ss = String(elapsed % 60).padStart(2, "0");
  return `${mm}:${ss}`;
}

// ─── Main component ───────────────────────────────────────────────────────────

interface SetRowState {
  weight: string;
  reps: string;
  logged: boolean;
  loggedSetId?: string;
}

interface BlockItem {
  block: TemplateBlock;
}

export default function WorkoutSessionScreen({ route, navigation }: Props) {
  const { workoutId } = route.params;

  const [template, setTemplate] = useState<WorkoutTemplate | null>(null);
  const [templateId, setTemplateId] = useState<string | null>(null);
  const [startedAt, setStartedAt] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [finishing, setFinishing] = useState(false);

  // setStates keyed by `${blockId}-${tbeId}-${setIndex}`
  const [setStates, setSetStates] = useState<Record<string, SetRowState>>({});

  const elapsed = useElapsed(startedAt);
  const restTimer = useRestTimer();

  // Load workout + template
  useEffect(() => {
    (async () => {
      try {
        const workout = await fetchWorkout(workoutId);
        setStartedAt(workout.startedAt);
        setTemplateId(workout.templateId ?? null);

        if (workout.templateId) {
          const tpl = await fetchTemplate(workout.templateId);
          setTemplate(tpl);

          // Seed set-state rows from template
          const initial: Record<string, SetRowState> = {};
          for (const block of tpl.blocks) {
            for (const tbe of block.exercises) {
              tbe.sets.forEach((s, idx) => {
                const key = `${block.id}-${tbe.id}-${idx}`;
                initial[key] = {
                  weight: s.targetWeight != null ? String(s.targetWeight) : "",
                  reps: s.targetRepsMin != null ? String(s.targetRepsMin) : "",
                  logged: false,
                };
              });
            }
          }
          setSetStates(initial);
        }
      } catch (e) {
        console.error(e);
        Alert.alert("Error", "Could not load workout.");
      } finally {
        setLoading(false);
      }
    })();
  }, [workoutId]);

  const handleCompleteSet = useCallback(
    async (
      block: TemplateBlock,
      tbe: TemplateBlockExercise,
      setIndex: number,
    ) => {
      const key = `${block.id}-${tbe.id}-${setIndex}`;
      const state = setStates[key];
      if (!state || state.logged) return;

      const weight = state.weight ? parseFloat(state.weight) : undefined;
      const reps = state.reps ? parseInt(state.reps, 10) : undefined;

      try {
        const logged = await logSet(workoutId, {
          exerciseId: tbe.exerciseId,
          blockId: block.id,
          setNumber: setIndex + 1,
          repsCompleted: reps,
          weight,
          isWarmup: tbe.sets[setIndex]?.isWarmup ?? false,
        });
        setSetStates((prev) => ({
          ...prev,
          [key]: { ...state, logged: true, loggedSetId: logged.id },
        }));

        // Start rest timer
        if (block.restAfterSeconds) {
          restTimer.start(block.restAfterSeconds);
        }
      } catch (e) {
        console.error(e);
        Alert.alert("Error", "Failed to log set. Check your connection and try again.");
      }
    },
    [workoutId, setStates, restTimer],
  );

  const handleFinish = useCallback(async () => {
    Alert.alert("Finish Workout?", "This will end the session.", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Finish",
        style: "default",
        onPress: async () => {
          setFinishing(true);
          try {
            await finishWorkout(workoutId);
            navigation.replace("WorkoutFinish", { workoutId });
          } catch (e) {
            console.error(e);
            Alert.alert("Error", "Failed to finish workout.");
          } finally {
            setFinishing(false);
          }
        },
      },
    ]);
  }, [workoutId, navigation]);

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator color="#f9fafb" />
      </View>
    );
  }

  const blocks: BlockItem[] = (template?.blocks ?? []).map((b) => ({ block: b }));

  return (
    <View style={styles.container}>
      {/* Header bar */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>
          {template?.name ?? "Ad-hoc Workout"}
        </Text>
        <Text style={styles.headerTimer}>{elapsed}</Text>
      </View>

      {/* Rest timer banner */}
      {restTimer.active && (
        <Pressable style={styles.restBanner} onPress={restTimer.cancel}>
          <Text style={styles.restBannerText}>
            ⏱ Rest — {String(Math.floor(restTimer.seconds / 60)).padStart(2, "0")}:
            {String(restTimer.seconds % 60).padStart(2, "0")}  (tap to skip)
          </Text>
        </Pressable>
      )}

      <FlatList
        data={blocks}
        keyExtractor={(item) => item.block.id}
        contentContainerStyle={styles.listContent}
        renderItem={({ item: { block } }) => (
          <View style={[styles.blockCard, block.blockType === "superset" && styles.supersetCard]}>
            {block.blockType === "superset" && (
              <Text style={styles.supersetLabel}>⚡ Superset</Text>
            )}
            {block.exercises.map((tbe) => (
              <View key={tbe.id} style={styles.exerciseSection}>
                <Text style={styles.exerciseName}>
                  {tbe.exercise?.name ?? tbe.exerciseId}
                </Text>
                {tbe.sets.map((templateSet, idx) => {
                  const key = `${block.id}-${tbe.id}-${idx}`;
                  const state = setStates[key] ?? { weight: "", reps: "", logged: false };
                  return (
                    <View key={idx} style={styles.setRow}>
                      <Text style={styles.setNum}>
                        {templateSet.isWarmup ? "W" : idx + 1}
                      </Text>
                      <TextInput
                        style={[styles.input, state.logged && styles.inputDone]}
                        keyboardType="decimal-pad"
                        placeholder="lbs"
                        placeholderTextColor="#4b5563"
                        value={state.weight}
                        editable={!state.logged}
                        onChangeText={(v) =>
                          setSetStates((prev) => ({
                            ...prev,
                            [key]: { ...state, weight: v },
                          }))
                        }
                      />
                      <TextInput
                        style={[styles.input, state.logged && styles.inputDone]}
                        keyboardType="number-pad"
                        placeholder="reps"
                        placeholderTextColor="#4b5563"
                        value={state.reps}
                        editable={!state.logged}
                        onChangeText={(v) =>
                          setSetStates((prev) => ({
                            ...prev,
                            [key]: { ...state, reps: v },
                          }))
                        }
                      />
                      <Pressable
                        style={[
                          styles.completeBtn,
                          state.logged && styles.completeBtnDone,
                        ]}
                        onPress={() => handleCompleteSet(block, tbe, idx)}
                        disabled={state.logged}
                      >
                        <Text style={styles.completeBtnText}>
                          {state.logged ? "✓" : "Log"}
                        </Text>
                      </Pressable>
                    </View>
                  );
                })}
              </View>
            ))}
            {block.restAfterSeconds ? (
              <Text style={styles.restLabel}>
                Rest: {Math.floor(block.restAfterSeconds / 60)}:
                {String(block.restAfterSeconds % 60).padStart(2, "0")}
              </Text>
            ) : null}
          </View>
        )}
        ListEmptyComponent={
          <Text style={styles.empty}>
            No exercises in this template. Log sets below or finish the workout.
          </Text>
        }
        ListFooterComponent={
          <Pressable
            style={[styles.finishBtn, finishing && styles.buttonDisabled]}
            onPress={handleFinish}
            disabled={finishing}
          >
            <Text style={styles.finishBtnText}>
              {finishing ? "Finishing…" : "Finish Workout"}
            </Text>
          </Pressable>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
  centered: { flex: 1, backgroundColor: "#000", alignItems: "center", justifyContent: "center" },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#1f2937",
  },
  headerTitle: { color: "#f9fafb", fontWeight: "700", fontSize: 16 },
  headerTimer: { color: "#2563eb", fontWeight: "700", fontSize: 16 },
  restBanner: {
    backgroundColor: "#1e3a5f",
    paddingVertical: 10,
    alignItems: "center",
  },
  restBannerText: { color: "#93c5fd", fontWeight: "600", fontSize: 14 },
  listContent: { padding: 16, paddingBottom: 40 },
  blockCard: {
    backgroundColor: "#111",
    borderRadius: 12,
    padding: 14,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: "#222",
  },
  supersetCard: { borderColor: "#7c3aed" },
  supersetLabel: { color: "#a78bfa", fontWeight: "700", fontSize: 12, marginBottom: 8 },
  exerciseSection: { marginBottom: 10 },
  exerciseName: { color: "#f9fafb", fontWeight: "700", fontSize: 15, marginBottom: 6 },
  setRow: { flexDirection: "row", alignItems: "center", marginBottom: 6 },
  setNum: {
    color: "#6b7280",
    fontSize: 13,
    fontWeight: "600",
    width: 24,
    textAlign: "center",
  },
  input: {
    flex: 1,
    backgroundColor: "#1f2937",
    color: "#f9fafb",
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 8,
    fontSize: 15,
    marginHorizontal: 4,
    textAlign: "center",
  },
  inputDone: { opacity: 0.4 },
  completeBtn: {
    backgroundColor: "#2563eb",
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 8,
    marginLeft: 4,
    minWidth: 48,
    alignItems: "center",
  },
  completeBtnDone: { backgroundColor: "#166534" },
  completeBtnText: { color: "#fff", fontWeight: "700", fontSize: 14 },
  restLabel: { color: "#6b7280", fontSize: 12, marginTop: 4 },
  empty: {
    color: "#6b7280",
    textAlign: "center",
    marginTop: 32,
    fontSize: 14,
    paddingHorizontal: 24,
  },
  finishBtn: {
    backgroundColor: "#16a34a",
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: "center",
    marginTop: 8,
    marginBottom: 16,
  },
  buttonDisabled: { opacity: 0.5 },
  finishBtnText: { color: "#fff", fontWeight: "700", fontSize: 16 },
});
