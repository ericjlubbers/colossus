/**
 * WorkoutFinishScreen — summary shown after finishing a session.
 *
 * Shows: duration, total sets logged, total volume lifted.
 */

import React, { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import { fetchWorkout, type CompletedWorkout } from "../lib/api";
import type { WorkoutStackParamList } from "../navigation/types";

type Props = NativeStackScreenProps<WorkoutStackParamList, "WorkoutFinish">;

function formatDuration(startedAt: string, endedAt?: string): string {
  const start = new Date(startedAt).getTime();
  const end = endedAt ? new Date(endedAt).getTime() : Date.now();
  const totalSeconds = Math.round((end - start) / 1000);
  const h = Math.floor(totalSeconds / 3600);
  const m = Math.floor((totalSeconds % 3600) / 60);
  const s = totalSeconds % 60;
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

function calcVolume(sets: CompletedWorkout["sets"]): number {
  return sets.reduce((sum, s) => {
    const w = s.weight ?? 0;
    const r = s.repsCompleted ?? 0;
    return sum + w * r;
  }, 0);
}

// Group sets by exercise name for display
function groupByExercise(
  sets: CompletedWorkout["sets"],
): { name: string; sets: CompletedWorkout["sets"] }[] {
  const map = new Map<string, CompletedWorkout["sets"]>();
  for (const s of sets) {
    const name = s.exercise?.name ?? s.exerciseId;
    if (!map.has(name)) map.set(name, []);
    map.get(name)!.push(s);
  }
  return Array.from(map.entries()).map(([name, sets]) => ({ name, sets }));
}

export default function WorkoutFinishScreen({ route, navigation }: Props) {
  const { workoutId } = route.params;
  const [workout, setWorkout] = useState<CompletedWorkout | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWorkout(workoutId)
      .then(setWorkout)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [workoutId]);

  if (loading || !workout) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator color="#f9fafb" />
      </View>
    );
  }

  const volume = calcVolume(workout.sets);
  const byExercise = groupByExercise(workout.sets);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>🎉 Workout Complete!</Text>

      {/* Stats row */}
      <View style={styles.statsRow}>
        <View style={styles.statBox}>
          <Text style={styles.statValue}>
            {formatDuration(workout.startedAt, workout.endedAt)}
          </Text>
          <Text style={styles.statLabel}>Duration</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={styles.statValue}>{workout.sets.length}</Text>
          <Text style={styles.statLabel}>Sets</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={styles.statValue}>{volume.toLocaleString()}</Text>
          <Text style={styles.statLabel}>Volume (lbs)</Text>
        </View>
      </View>

      {/* Per-exercise breakdown */}
      {byExercise.map(({ name, sets }) => (
        <View key={name} style={styles.exerciseCard}>
          <Text style={styles.exerciseName}>{name}</Text>
          {sets.map((s) => (
            <Text key={s.id} style={styles.setLine}>
              Set {s.setNumber}: {s.weight != null ? `${s.weight} lbs` : "—"}
              {s.repsCompleted != null ? ` × ${s.repsCompleted} reps` : ""}
              {s.isWarmup ? "  (warmup)" : ""}
            </Text>
          ))}
        </View>
      ))}

      <Pressable
        style={styles.doneBtn}
        onPress={() => navigation.navigate("WorkoutHome")}
      >
        <Text style={styles.doneBtnText}>Done</Text>
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
  centered: { flex: 1, backgroundColor: "#000", alignItems: "center", justifyContent: "center" },
  content: { padding: 20, paddingBottom: 48 },
  heading: { color: "#f9fafb", fontSize: 24, fontWeight: "800", textAlign: "center", marginBottom: 24 },
  statsRow: { flexDirection: "row", justifyContent: "space-around", marginBottom: 28 },
  statBox: { alignItems: "center" },
  statValue: { color: "#2563eb", fontSize: 22, fontWeight: "800" },
  statLabel: { color: "#6b7280", fontSize: 12, marginTop: 4 },
  exerciseCard: {
    backgroundColor: "#111",
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: "#222",
  },
  exerciseName: { color: "#f9fafb", fontWeight: "700", fontSize: 15, marginBottom: 6 },
  setLine: { color: "#9ca3af", fontSize: 13, marginBottom: 2 },
  doneBtn: {
    backgroundColor: "#2563eb",
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: "center",
    marginTop: 24,
  },
  doneBtnText: { color: "#fff", fontWeight: "700", fontSize: 16 },
});
