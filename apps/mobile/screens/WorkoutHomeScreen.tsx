/**
 * WorkoutHomeScreen — pick a template to start from, or start an ad-hoc session.
 */

import React, { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import { fetchTemplates, startWorkout, type WorkoutTemplateSummary } from "../lib/api";
import type { WorkoutStackParamList } from "../navigation/types";

type Props = NativeStackScreenProps<WorkoutStackParamList, "WorkoutHome">;

export default function WorkoutHomeScreen({ navigation }: Props) {
  const [templates, setTemplates] = useState<WorkoutTemplateSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [starting, setStarting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const result = await fetchTemplates(undefined, 1);
      setTemplates(result.items);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleStart = useCallback(
    async (templateId?: string) => {
      setStarting(true);
      try {
        const workout = await startWorkout(templateId);
        navigation.replace("WorkoutSession", { workoutId: workout.id });
      } catch (e) {
        Alert.alert("Error", "Failed to start workout. Please try again.");
        console.error(e);
      } finally {
        setStarting(false);
      }
    },
    [navigation],
  );

  return (
    <View style={styles.container}>
      <Pressable
        style={[styles.adHocButton, starting && styles.buttonDisabled]}
        onPress={() => handleStart()}
        disabled={starting}
      >
        <Text style={styles.adHocButtonText}>
          {starting ? "Starting…" : "🏋️ Start Empty Workout"}
        </Text>
      </Pressable>

      <Text style={styles.sectionLabel}>OR PICK A TEMPLATE</Text>

      {loading ? (
        <ActivityIndicator color="#f9fafb" style={{ marginTop: 32 }} />
      ) : (
        <FlatList
          data={templates}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.list}
          renderItem={({ item }) => (
            <Pressable
              style={styles.card}
              onPress={() => handleStart(item.id)}
              disabled={starting}
            >
              <Text style={styles.cardName}>{item.name}</Text>
              {item.description ? (
                <Text style={styles.cardDesc} numberOfLines={2}>
                  {item.description}
                </Text>
              ) : null}
              {item.estimatedDurationMinutes ? (
                <Text style={styles.cardMeta}>~{item.estimatedDurationMinutes} min</Text>
              ) : null}
            </Pressable>
          )}
          ListEmptyComponent={
            <Text style={styles.empty}>No templates yet. Start an empty workout above.</Text>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000", paddingTop: 16 },
  adHocButton: {
    marginHorizontal: 16,
    backgroundColor: "#2563eb",
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: "center",
  },
  buttonDisabled: { opacity: 0.5 },
  adHocButtonText: { color: "#fff", fontWeight: "700", fontSize: 16 },
  sectionLabel: {
    color: "#6b7280",
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 1,
    marginTop: 28,
    marginBottom: 8,
    marginHorizontal: 20,
  },
  list: { paddingHorizontal: 16, paddingBottom: 32 },
  card: {
    backgroundColor: "#111",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: "#222",
  },
  cardName: { color: "#f9fafb", fontWeight: "700", fontSize: 16 },
  cardDesc: { color: "#9ca3af", fontSize: 13, marginTop: 4 },
  cardMeta: { color: "#6b7280", fontSize: 12, marginTop: 6 },
  empty: { color: "#6b7280", textAlign: "center", marginTop: 32, fontSize: 14 },
});
