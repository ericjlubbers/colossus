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
import type { MuscleGroup } from "@colossus/types";
import { fetchExercise, type Exercise } from "../lib/api";
import type { RootStackParamList } from "../navigation/types";

// ─── Constants ────────────────────────────────────────────────────────────────

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

// ─── Helpers ──────────────────────────────────────────────────────────────────

function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function MuscleBadge({ muscle, large }: { muscle: MuscleGroup; large?: boolean }) {
  const c = MUSCLE_COLORS[muscle];
  return (
    <View style={[styles.badge, { backgroundColor: c.bg }, large && styles.badgeLg]}>
      <Text style={[styles.badgeText, { color: c.text }, large && styles.badgeTextLg]}>
        {capitalize(muscle)}
      </Text>
    </View>
  );
}

function EquipmentBadge({ equipment }: { equipment: string }) {
  return (
    <View style={[styles.badge, styles.equipBadge]}>
      <Text style={[styles.badgeText, styles.equipBadgeText]}>{capitalize(equipment)}</Text>
    </View>
  );
}

function InfoRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}</Text>
      <View style={styles.infoValue}>{children}</View>
    </View>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {children}
    </View>
  );
}

// ─── Main Screen ──────────────────────────────────────────────────────────────

type Props = NativeStackScreenProps<RootStackParamList, "ExerciseDetail">;

export default function ExerciseDetailScreen({ route }: Props) {
  const { exerciseId } = route.params;

  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<"about" | "instructions">("about");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchExercise(exerciseId)
      .then((ex) => { if (!cancelled) setExercise(ex); })
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [exerciseId]);

  if (loading) {
    return (
      <View style={styles.centerState}>
        <ActivityIndicator color="#6b7280" size="large" />
      </View>
    );
  }

  if (error || !exercise) {
    return (
      <View style={styles.centerState}>
        <Text style={styles.errorText}>{error ?? "Exercise not found."}</Text>
      </View>
    );
  }

  const primaryColor = MUSCLE_COLORS[exercise.primaryMuscle];
  const steps = exercise.instructions
    ? exercise.instructions
        .split("\n")
        .map((l) => l.trim())
        .filter(Boolean)
    : [];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Hero accent bar */}
      <View style={[styles.accentBar, { backgroundColor: primaryColor.text }]} />

      {/* Title */}
      <Text style={styles.title}>{exercise.name}</Text>

      {/* Primary muscle + equipment */}
      <View style={styles.badgeRow}>
        <MuscleBadge muscle={exercise.primaryMuscle} large />
        <EquipmentBadge equipment={exercise.equipment} />
        {exercise.isCustom && (
          <View style={[styles.badge, styles.customBadge]}>
            <Text style={[styles.badgeText, styles.customBadgeText]}>Custom</Text>
          </View>
        )}
      </View>

      {/* Secondary muscles */}
      {exercise.secondaryMuscles.length > 0 && (
        <InfoRow label="Also targets">
          <View style={styles.badgeRow}>
            {exercise.secondaryMuscles.map((m) => (
              <MuscleBadge key={m} muscle={m} />
            ))}
          </View>
        </InfoRow>
      )}

      {/* Tab bar */}
      <View style={styles.tabBar}>
        {(["about", "instructions"] as const).map((t) => (
          <Pressable
            key={t}
            onPress={() => setTab(t)}
            style={[styles.tab, tab === t && styles.tabActive]}
          >
            <Text style={[styles.tabText, tab === t && styles.tabTextActive]}>
              {t === "about" ? "About" : "Instructions"}
            </Text>
          </Pressable>
        ))}
      </View>

      {/* Tab content */}
      {tab === "about" ? (
        <Section title="">
          {exercise.description ? (
            <Text style={styles.bodyText}>{exercise.description}</Text>
          ) : (
            <Text style={styles.placeholderText}>No description available.</Text>
          )}
        </Section>
      ) : (
        <Section title="">
          {steps.length > 0 ? (
            steps.map((step, i) => (
              <View key={i} style={styles.stepRow}>
                <View style={[styles.stepNum, { borderColor: primaryColor.text }]}>
                  <Text style={[styles.stepNumText, { color: primaryColor.text }]}>
                    {i + 1}
                  </Text>
                </View>
                <Text style={styles.stepText}>
                  {/* Strip leading "1. " style prefixes that may come from seed data */}
                  {step.replace(/^\d+\.\s*/, "")}
                </Text>
              </View>
            ))
          ) : (
            <Text style={styles.placeholderText}>No instructions available.</Text>
          )}
        </Section>
      )}
    </ScrollView>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
  content: { paddingBottom: 40 },
  centerState: { flex: 1, backgroundColor: "#000", alignItems: "center", justifyContent: "center", padding: 24 },
  errorText: { color: "#f87171", fontSize: 15, textAlign: "center" },

  accentBar: { height: 4, width: 48, borderRadius: 2, marginHorizontal: 20, marginTop: 20, marginBottom: 16 },
  title: { color: "#f9fafb", fontSize: 26, fontWeight: "700", paddingHorizontal: 20, marginBottom: 12 },

  badgeRow: { flexDirection: "row", flexWrap: "wrap", gap: 8, paddingHorizontal: 20, marginBottom: 4 },
  badge: { borderRadius: 20, paddingHorizontal: 10, paddingVertical: 4 },
  badgeLg: { paddingHorizontal: 14, paddingVertical: 6 },
  badgeText: { fontSize: 12, fontWeight: "600" },
  badgeTextLg: { fontSize: 14 },
  equipBadge: { backgroundColor: "#1f2937" },
  equipBadgeText: { color: "#9ca3af" },
  customBadge: { backgroundColor: "#1a2e1a" },
  customBadgeText: { color: "#4ade80" },

  infoRow: { paddingHorizontal: 20, marginTop: 12 },
  infoLabel: { color: "#6b7280", fontSize: 11, fontWeight: "700", textTransform: "uppercase", letterSpacing: 1, marginBottom: 8 },
  infoValue: {},

  tabBar: {
    flexDirection: "row", marginHorizontal: 20, marginTop: 24, marginBottom: 4,
    backgroundColor: "#111827", borderRadius: 12, padding: 4,
  },
  tab: { flex: 1, paddingVertical: 9, alignItems: "center", borderRadius: 9 },
  tabActive: { backgroundColor: "#1f2937" },
  tabText: { color: "#6b7280", fontSize: 14, fontWeight: "600" },
  tabTextActive: { color: "#f9fafb" },

  section: { paddingHorizontal: 20, paddingTop: 20 },
  sectionTitle: { color: "#6b7280", fontSize: 11, fontWeight: "700", textTransform: "uppercase", letterSpacing: 1, marginBottom: 12 },

  bodyText: { color: "#d1d5db", fontSize: 15, lineHeight: 24 },
  placeholderText: { color: "#4b5563", fontSize: 15, fontStyle: "italic" },

  stepRow: { flexDirection: "row", gap: 14, marginBottom: 16, alignItems: "flex-start" },
  stepNum: {
    width: 28, height: 28, borderRadius: 14, borderWidth: 1.5,
    alignItems: "center", justifyContent: "center", flexShrink: 0, marginTop: 1,
  },
  stepNumText: { fontSize: 12, fontWeight: "700" },
  stepText: { flex: 1, color: "#d1d5db", fontSize: 15, lineHeight: 24 },
});
