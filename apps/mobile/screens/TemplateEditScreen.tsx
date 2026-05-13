import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  FlatList,
  KeyboardAvoidingView,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import {
  addBlock,
  addExerciseToBlock,
  deleteBlock,
  deleteBlockExercise,
  deleteTemplate,
  fetchExercises,
  fetchTemplate,
  reorderBlocks,
  reorderBlockExercises,
  updateBlock,
  updateBlockExercise,
  updateTemplate,
  type Exercise,
  type TemplateBlock,
  type TemplateBlockExercise,
  type TemplateSet,
  type WorkoutTemplate,
} from "../lib/api";
import type { TemplatesStackParamList } from "../navigation/types";

type Props = NativeStackScreenProps<TemplatesStackParamList, "TemplateEdit">;

// ─── Exercise Picker Modal ────────────────────────────────────────────────────

interface ExercisePickerProps {
  visible: boolean;
  onSelect: (exercise: Exercise) => void;
  onClose: () => void;
}

function ExercisePickerModal({ visible, onSelect, onClose }: ExercisePickerProps) {
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [total, setTotal] = useState(0);
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);

  const debouncedQuery = useRef(query);

  useEffect(() => {
    debouncedQuery.current = query;
    const t = setTimeout(async () => {
      if (!visible) return;
      setLoading(true);
      setPage(1);
      try {
        const result = await fetchExercises({ q: query || undefined, page: 1, pageSize: 30 });
        setExercises(result.items);
        setTotal(result.total);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => clearTimeout(t);
  }, [query, visible]);

  // Initial load when modal opens
  useEffect(() => {
    if (!visible) return;
    setQuery("");
    setPage(1);
    setLoading(true);
    fetchExercises({ page: 1, pageSize: 30 })
      .then((result) => {
        setExercises(result.items);
        setTotal(result.total);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [visible]);

  const loadMore = async () => {
    if (loading || exercises.length >= total) return;
    const next = page + 1;
    setPage(next);
    setLoading(true);
    try {
      const result = await fetchExercises({ q: query || undefined, page: next, pageSize: 30 });
      setExercises((prev) => [...prev, ...result.items]);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={onClose}>
      <View style={ps.container}>
        <View style={ps.header}>
          <Text style={ps.title}>Add Exercise</Text>
          <Pressable onPress={onClose} style={ps.closeBtn}>
            <Text style={ps.closeBtnText}>Cancel</Text>
          </Pressable>
        </View>
        <View style={ps.searchRow}>
          <TextInput
            style={ps.searchInput}
            placeholder="Search exercises…"
            placeholderTextColor="#6b7280"
            value={query}
            onChangeText={setQuery}
            autoFocus
            returnKeyType="search"
            clearButtonMode="while-editing"
          />
        </View>
        <FlatList
          data={exercises}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <Pressable
              style={({ pressed }) => [ps.item, pressed && ps.itemPressed]}
              onPress={() => onSelect(item)}
            >
              <Text style={ps.itemName}>{item.name}</Text>
              <Text style={ps.itemMeta}>
                {item.primaryMuscle} · {item.equipment}
              </Text>
            </Pressable>
          )}
          onEndReached={loadMore}
          onEndReachedThreshold={0.3}
          ListFooterComponent={loading ? <ActivityIndicator color="#f9fafb" style={{ padding: 16 }} /> : null}
        />
      </View>
    </Modal>
  );
}

const ps = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#1f2937",
  },
  title: { color: "#f9fafb", fontSize: 17, fontWeight: "700" },
  closeBtn: { paddingHorizontal: 8, paddingVertical: 4 },
  closeBtnText: { color: "#60a5fa", fontSize: 16 },
  searchRow: { padding: 12 },
  searchInput: {
    backgroundColor: "#111",
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    color: "#f9fafb",
    fontSize: 15,
  },
  item: {
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: "#111",
  },
  itemPressed: { backgroundColor: "#111" },
  itemName: { color: "#f9fafb", fontSize: 15, fontWeight: "600" },
  itemMeta: { color: "#9ca3af", fontSize: 12, marginTop: 2, textTransform: "capitalize" },
});

// ─── Set Row ──────────────────────────────────────────────────────────────────

interface SetRowProps {
  set: TemplateSet;
  index: number;
  onUpdate: (index: number, updates: Partial<TemplateSet>) => void;
  onDelete: (index: number) => void;
}

function SetRow({ set, index, onUpdate, onDelete }: SetRowProps) {
  return (
    <View style={ss.row}>
      <View style={ss.badge}>
        <Text style={ss.badgeText}>{set.isWarmup ? "W" : String(set.setNumber)}</Text>
      </View>
      <View style={ss.fields}>
        <TextInput
          style={ss.input}
          placeholder="Reps"
          placeholderTextColor="#4b5563"
          keyboardType="numeric"
          value={set.targetRepsMin != null ? String(set.targetRepsMin) : ""}
          onChangeText={(v) => onUpdate(index, { targetRepsMin: v ? parseInt(v, 10) : undefined })}
        />
        <Text style={ss.sep}>–</Text>
        <TextInput
          style={ss.input}
          placeholder="Max"
          placeholderTextColor="#4b5563"
          keyboardType="numeric"
          value={set.targetRepsMax != null ? String(set.targetRepsMax) : ""}
          onChangeText={(v) => onUpdate(index, { targetRepsMax: v ? parseInt(v, 10) : undefined })}
        />
        <Text style={ss.unit}>reps</Text>
        <TextInput
          style={[ss.input, ss.weightInput]}
          placeholder="lbs"
          placeholderTextColor="#4b5563"
          keyboardType="decimal-pad"
          value={set.targetWeight != null ? String(set.targetWeight) : ""}
          onChangeText={(v) => onUpdate(index, { targetWeight: v ? parseFloat(v) : undefined })}
        />
        <Text style={ss.unit}>lbs</Text>
      </View>
      <Pressable onPress={() => onDelete(index)} style={ss.delBtn}>
        <Text style={ss.delText}>✕</Text>
      </Pressable>
    </View>
  );
}

const ss = StyleSheet.create({
  row: { flexDirection: "row", alignItems: "center", marginBottom: 6 },
  badge: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: "#1f2937",
    alignItems: "center",
    justifyContent: "center",
    marginRight: 8,
  },
  badgeText: { color: "#d1d5db", fontSize: 11, fontWeight: "700" },
  fields: { flex: 1, flexDirection: "row", alignItems: "center", gap: 4 },
  input: {
    backgroundColor: "#1f2937",
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 6,
    color: "#f9fafb",
    fontSize: 13,
    width: 44,
    textAlign: "center",
  },
  weightInput: { width: 56 },
  sep: { color: "#6b7280", fontSize: 12 },
  unit: { color: "#6b7280", fontSize: 11 },
  delBtn: { paddingHorizontal: 8, paddingVertical: 4 },
  delText: { color: "#ef4444", fontSize: 14 },
});

// ─── Block Card ───────────────────────────────────────────────────────────────

interface BlockCardProps {
  block: TemplateBlock;
  blockIndex: number;
  totalBlocks: number;
  templateId: string;
  onMoveUp: (blockId: string) => void;
  onMoveDown: (blockId: string) => void;
  onDeleteBlock: (blockId: string) => void;
  onAddExercise: (blockId: string) => void;
  onDeleteExercise: (blockId: string, tbeId: string) => void;
  onUpdateSets: (blockId: string, tbeId: string, sets: TemplateSet[]) => void;
  onMoveExerciseUp: (blockId: string, tbeId: string) => void;
  onMoveExerciseDown: (blockId: string, tbeId: string) => void;
  onUpdateRest: (blockId: string, seconds: number | null) => void;
}

function BlockCard({
  block,
  blockIndex,
  totalBlocks,
  onMoveUp,
  onMoveDown,
  onDeleteBlock,
  onAddExercise,
  onDeleteExercise,
  onUpdateSets,
  onMoveExerciseUp,
  onMoveExerciseDown,
  onUpdateRest,
}: BlockCardProps) {
  const [editingRest, setEditingRest] = useState(false);
  const [restValue, setRestValue] = useState(
    block.restAfterSeconds != null ? String(block.restAfterSeconds) : "",
  );

  const isSup = block.blockType === "superset";

  const confirmDeleteBlock = () => {
    Alert.alert("Delete Block", "Remove this block and all its exercises?", [
      { text: "Cancel", style: "cancel" },
      { text: "Delete", style: "destructive", onPress: () => onDeleteBlock(block.id) },
    ]);
  };

  const confirmDeleteExercise = (tbe: TemplateBlockExercise) => {
    Alert.alert("Remove Exercise", `Remove "${tbe.exercise?.name ?? "this exercise"}"?`, [
      { text: "Cancel", style: "cancel" },
      {
        text: "Remove",
        style: "destructive",
        onPress: () => onDeleteExercise(block.id, tbe.id),
      },
    ]);
  };

  const handleRestSave = () => {
    const secs = restValue ? parseInt(restValue, 10) : null;
    onUpdateRest(block.id, secs);
    setEditingRest(false);
  };

  return (
    <View style={[bc.card, isSup && bc.cardSup]}>
      {/* Block header */}
      <View style={bc.header}>
        <View style={[bc.typeBadge, isSup && bc.typeBadgeSup]}>
          <Text style={[bc.typeText, isSup && bc.typeTextSup]}>
            {isSup ? "⚡ SUPERSET" : "SET"}
          </Text>
        </View>
        <View style={bc.reorderBtns}>
          {blockIndex > 0 && (
            <Pressable onPress={() => onMoveUp(block.id)} style={bc.reorderBtn}>
              <Text style={bc.reorderText}>↑</Text>
            </Pressable>
          )}
          {blockIndex < totalBlocks - 1 && (
            <Pressable onPress={() => onMoveDown(block.id)} style={bc.reorderBtn}>
              <Text style={bc.reorderText}>↓</Text>
            </Pressable>
          )}
        </View>
        <Pressable onPress={confirmDeleteBlock} style={bc.deleteBtn}>
          <Text style={bc.deleteBtnText}>Delete</Text>
        </Pressable>
      </View>

      {/* Exercises */}
      {block.exercises.map((tbe, ei) => {
        const exName = tbe.exercise?.name ?? `Exercise ${ei + 1}`;
        return (
          <View key={tbe.id} style={bc.exSection}>
            <View style={bc.exHeader}>
              <View style={bc.exReorderBtns}>
                {ei > 0 && (
                  <Pressable onPress={() => onMoveExerciseUp(block.id, tbe.id)} style={bc.reorderBtn}>
                    <Text style={bc.reorderText}>↑</Text>
                  </Pressable>
                )}
                {ei < block.exercises.length - 1 && (
                  <Pressable onPress={() => onMoveExerciseDown(block.id, tbe.id)} style={bc.reorderBtn}>
                    <Text style={bc.reorderText}>↓</Text>
                  </Pressable>
                )}
              </View>
              <Text style={bc.exName} numberOfLines={1}>
                {exName}
              </Text>
              <Pressable onPress={() => confirmDeleteExercise(tbe)} style={bc.exDeleteBtn}>
                <Text style={bc.deleteBtnText}>Remove</Text>
              </Pressable>
            </View>
            {/* Set rows */}
            {tbe.sets.map((set, si) => (
              <SetRow
                key={si}
                set={set}
                index={si}
                onUpdate={(idx, updates) => {
                  const newSets = tbe.sets.map((s, i) =>
                    i === idx ? { ...s, ...updates } : s,
                  );
                  onUpdateSets(block.id, tbe.id, newSets);
                }}
                onDelete={(idx) => {
                  const newSets = tbe.sets
                    .filter((_, i) => i !== idx)
                    .map((s, i) => ({ ...s, setNumber: i + 1 }));
                  onUpdateSets(block.id, tbe.id, newSets);
                }}
              />
            ))}
            <Pressable
              style={bc.addSetBtn}
              onPress={() => {
                const newSet: TemplateSet = {
                  setNumber: tbe.sets.length + 1,
                  weightType: "fixed",
                  isWarmup: false,
                };
                onUpdateSets(block.id, tbe.id, [...tbe.sets, newSet]);
              }}
            >
              <Text style={bc.addSetText}>+ Add Set</Text>
            </Pressable>
          </View>
        );
      })}

      {/* Add exercise button */}
      <Pressable style={bc.addExBtn} onPress={() => onAddExercise(block.id)}>
        <Text style={bc.addExText}>+ Add Exercise</Text>
      </Pressable>

      {/* Rest timer */}
      <View style={bc.restRow}>
        <Text style={bc.restLabel}>Rest:</Text>
        {editingRest ? (
          <View style={bc.restEditRow}>
            <TextInput
              style={bc.restInput}
              value={restValue}
              onChangeText={setRestValue}
              keyboardType="numeric"
              placeholder="90"
              placeholderTextColor="#4b5563"
              autoFocus
              returnKeyType="done"
              onSubmitEditing={handleRestSave}
            />
            <Text style={bc.restUnit}>sec</Text>
            <Pressable onPress={handleRestSave} style={bc.restSaveBtn}>
              <Text style={bc.restSaveText}>Done</Text>
            </Pressable>
          </View>
        ) : (
          <Pressable onPress={() => setEditingRest(true)}>
            <Text style={bc.restValue}>
              {block.restAfterSeconds != null
                ? `${block.restAfterSeconds}s`
                : "Tap to set"}
            </Text>
          </Pressable>
        )}
      </View>
    </View>
  );
}

const bc = StyleSheet.create({
  card: {
    backgroundColor: "#111",
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: "#1f2937",
  },
  cardSup: { borderColor: "#7c3aed" },
  header: { flexDirection: "row", alignItems: "center", marginBottom: 12 },
  typeBadge: {
    backgroundColor: "#1f2937",
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  typeBadgeSup: { backgroundColor: "#4c1d95" },
  typeText: { color: "#9ca3af", fontSize: 11, fontWeight: "700", letterSpacing: 0.5 },
  typeTextSup: { color: "#c4b5fd" },
  reorderBtns: { flexDirection: "row", marginLeft: "auto" },
  reorderBtn: { paddingHorizontal: 6, paddingVertical: 4 },
  reorderText: { color: "#6b7280", fontSize: 16 },
  deleteBtn: {
    marginLeft: 8,
    paddingHorizontal: 8,
    paddingVertical: 4,
    backgroundColor: "#1f2937",
    borderRadius: 6,
  },
  deleteBtnText: { color: "#f87171", fontSize: 12 },
  exSection: {
    borderTopWidth: 1,
    borderTopColor: "#1f2937",
    paddingTop: 10,
    marginBottom: 8,
  },
  exHeader: { flexDirection: "row", alignItems: "center", marginBottom: 8 },
  exReorderBtns: { flexDirection: "row", marginRight: 4 },
  exName: { flex: 1, color: "#e5e7eb", fontSize: 14, fontWeight: "600" },
  exDeleteBtn: {
    paddingHorizontal: 6,
    paddingVertical: 3,
    backgroundColor: "#1f2937",
    borderRadius: 6,
    marginLeft: 8,
  },
  addSetBtn: {
    alignSelf: "flex-start",
    paddingHorizontal: 10,
    paddingVertical: 6,
    backgroundColor: "#1f2937",
    borderRadius: 6,
    marginTop: 4,
    marginBottom: 4,
  },
  addSetText: { color: "#9ca3af", fontSize: 13 },
  addExBtn: {
    borderWidth: 1,
    borderColor: "#374151",
    borderStyle: "dashed",
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: "center",
    marginTop: 8,
  },
  addExText: { color: "#9ca3af", fontSize: 14 },
  restRow: { flexDirection: "row", alignItems: "center", marginTop: 10, gap: 8 },
  restLabel: { color: "#6b7280", fontSize: 13 },
  restEditRow: { flexDirection: "row", alignItems: "center", gap: 6 },
  restInput: {
    backgroundColor: "#1f2937",
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 4,
    color: "#f9fafb",
    fontSize: 13,
    width: 56,
    textAlign: "center",
  },
  restUnit: { color: "#6b7280", fontSize: 12 },
  restSaveBtn: { paddingHorizontal: 8, paddingVertical: 4 },
  restSaveText: { color: "#60a5fa", fontSize: 13 },
  restValue: { color: "#9ca3af", fontSize: 13 },
});

// ─── Main Screen ──────────────────────────────────────────────────────────────

export default function TemplateEditScreen({ route, navigation }: Props) {
  const { templateId } = route.params;

  const [template, setTemplate] = useState<WorkoutTemplate | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Picker state
  const [pickerVisible, setPickerVisible] = useState(false);
  const [pickerTargetBlockId, setPickerTargetBlockId] = useState<string | null>(null);

  // Debounced metadata save
  const nameRef = useRef("");
  const descRef = useRef<string | undefined>(undefined);
  const durationRef = useRef<number | undefined>(undefined);
  const saveMetaTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const scheduleSaveMeta = useCallback(() => {
    if (saveMetaTimer.current) clearTimeout(saveMetaTimer.current);
    saveMetaTimer.current = setTimeout(async () => {
      if (!template) return;
      setSaving(true);
      try {
        const updated = await updateTemplate(templateId, {
          name: nameRef.current,
          description: descRef.current ?? null,
          estimatedDurationMinutes: durationRef.current ?? null,
        });
        setTemplate((prev) => prev ? { ...prev, name: updated.name, description: updated.description, estimatedDurationMinutes: updated.estimatedDurationMinutes } : prev);
        navigation.setOptions({ title: nameRef.current || "Edit Template" });
      } catch (e) {
        console.error("Save metadata failed", e);
      } finally {
        setSaving(false);
      }
    }, 800);
  }, [template, templateId, navigation]);

  // Load template on mount
  useEffect(() => {
    fetchTemplate(templateId)
      .then((t) => {
        setTemplate(t);
        nameRef.current = t.name;
        descRef.current = t.description;
        durationRef.current = t.estimatedDurationMinutes;
        navigation.setOptions({ title: t.name });
      })
      .catch(() => Alert.alert("Error", "Failed to load template"))
      .finally(() => setLoading(false));
  }, [templateId, navigation]);

  // Block operations
  const handleAddBlock = useCallback(
    async (type: "set" | "superset") => {
      if (!template) return;
      const order = template.blocks.length;
      try {
        const block = await addBlock(templateId, { blockType: type, order });
        setTemplate((prev) =>
          prev ? { ...prev, blocks: [...prev.blocks, block] } : prev,
        );
      } catch {
        Alert.alert("Error", "Failed to add block");
      }
    },
    [template, templateId],
  );

  const handleDeleteBlock = useCallback(
    async (blockId: string) => {
      try {
        await deleteBlock(templateId, blockId);
        setTemplate((prev) => {
          if (!prev) return prev;
          const blocks = prev.blocks
            .filter((b) => b.id !== blockId)
            .map((b, i) => ({ ...b, order: i }));
          return { ...prev, blocks };
        });
      } catch {
        Alert.alert("Error", "Failed to delete block");
      }
    },
    [templateId],
  );

  const handleMoveBlock = useCallback(
    async (blockId: string, direction: "up" | "down") => {
      if (!template) return;
      const idx = template.blocks.findIndex((b) => b.id === blockId);
      if (idx < 0) return;
      const swapIdx = direction === "up" ? idx - 1 : idx + 1;
      if (swapIdx < 0 || swapIdx >= template.blocks.length) return;

      const newBlocks = [...template.blocks];
      [newBlocks[idx], newBlocks[swapIdx]] = [newBlocks[swapIdx], newBlocks[idx]];
      const reordered = newBlocks.map((b, i) => ({ ...b, order: i }));
      setTemplate((prev) => prev ? { ...prev, blocks: reordered } : prev);

      try {
        await reorderBlocks(
          templateId,
          reordered.map((b) => ({ id: b.id, order: b.order })),
        );
      } catch {
        Alert.alert("Error", "Failed to reorder blocks");
      }
    },
    [template, templateId],
  );

  const handleUpdateRest = useCallback(
    async (blockId: string, seconds: number | null) => {
      try {
        const updated = await updateBlock(templateId, blockId, { restAfterSeconds: seconds });
        setTemplate((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            blocks: prev.blocks.map((b) => (b.id === blockId ? { ...b, restAfterSeconds: updated.restAfterSeconds } : b)),
          };
        });
      } catch {
        Alert.alert("Error", "Failed to update rest time");
      }
    },
    [templateId],
  );

  // Exercise operations
  const openPicker = useCallback((blockId: string) => {
    setPickerTargetBlockId(blockId);
    setPickerVisible(true);
  }, []);

  const handleExerciseSelected = useCallback(
    async (exercise: Exercise) => {
      setPickerVisible(false);
      if (!pickerTargetBlockId || !template) return;
      const block = template.blocks.find((b) => b.id === pickerTargetBlockId);
      if (!block) return;
      const orderInBlock = block.exercises.length;
      try {
        const tbe = await addExerciseToBlock(templateId, pickerTargetBlockId, {
          exerciseId: exercise.id,
          orderInBlock,
          sets: [{ setNumber: 1, weightType: "fixed", isWarmup: false }],
        });
        setTemplate((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            blocks: prev.blocks.map((b) =>
              b.id === pickerTargetBlockId
                ? { ...b, exercises: [...b.exercises, tbe] }
                : b,
            ),
          };
        });
      } catch {
        Alert.alert("Error", "Failed to add exercise");
      }
    },
    [pickerTargetBlockId, template, templateId],
  );

  const handleDeleteExercise = useCallback(
    async (blockId: string, tbeId: string) => {
      try {
        await deleteBlockExercise(templateId, blockId, tbeId);
        setTemplate((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            blocks: prev.blocks.map((b) =>
              b.id === blockId
                ? { ...b, exercises: b.exercises.filter((e) => e.id !== tbeId) }
                : b,
            ),
          };
        });
      } catch {
        Alert.alert("Error", "Failed to remove exercise");
      }
    },
    [templateId],
  );

  const handleUpdateSets = useCallback(
    async (blockId: string, tbeId: string, sets: TemplateSet[]) => {
      // Optimistic update
      setTemplate((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          blocks: prev.blocks.map((b) =>
            b.id === blockId
              ? {
                  ...b,
                  exercises: b.exercises.map((e) =>
                    e.id === tbeId ? { ...e, sets } : e,
                  ),
                }
              : b,
          ),
        };
      });
      try {
        await updateBlockExercise(templateId, blockId, tbeId, { sets });
      } catch (e) {
        console.error("Failed to save sets", e);
      }
    },
    [templateId],
  );

  const handleMoveExercise = useCallback(
    async (blockId: string, tbeId: string, direction: "up" | "down") => {
      if (!template) return;
      const block = template.blocks.find((b) => b.id === blockId);
      if (!block) return;
      const idx = block.exercises.findIndex((e) => e.id === tbeId);
      if (idx < 0) return;
      const swapIdx = direction === "up" ? idx - 1 : idx + 1;
      if (swapIdx < 0 || swapIdx >= block.exercises.length) return;

      const newExercises = [...block.exercises];
      [newExercises[idx], newExercises[swapIdx]] = [newExercises[swapIdx], newExercises[idx]];
      const reordered = newExercises.map((e, i) => ({ ...e, orderInBlock: i }));

      setTemplate((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          blocks: prev.blocks.map((b) =>
            b.id === blockId ? { ...b, exercises: reordered } : b,
          ),
        };
      });

      try {
        await reorderBlockExercises(
          templateId,
          blockId,
          reordered.map((e) => ({ id: e.id, orderInBlock: e.orderInBlock })),
        );
      } catch {
        Alert.alert("Error", "Failed to reorder exercises");
      }
    },
    [template, templateId],
  );

  const handleDeleteTemplate = () => {
    Alert.alert("Delete Template", "Permanently delete this template?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Delete",
        style: "destructive",
        onPress: async () => {
          try {
            await deleteTemplate(templateId);
            navigation.goBack();
          } catch {
            Alert.alert("Error", "Failed to delete template");
          }
        },
      },
    ]);
  };

  if (loading) {
    return (
      <View style={s.centered}>
        <ActivityIndicator color="#f9fafb" size="large" />
      </View>
    );
  }

  if (!template) {
    return (
      <View style={s.centered}>
        <Text style={s.errorText}>Template not found</Text>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      style={s.flex}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <ScrollView style={s.scroll} contentContainerStyle={s.content} keyboardShouldPersistTaps="handled">
        {/* Metadata card */}
        <View style={s.metaCard}>
          <Text style={s.metaLabel}>Name</Text>
          <TextInput
            style={s.metaInput}
            defaultValue={template.name}
            onChangeText={(v) => {
              nameRef.current = v;
              scheduleSaveMeta();
            }}
            placeholder="Template name"
            placeholderTextColor="#4b5563"
            returnKeyType="done"
          />
          <Text style={[s.metaLabel, s.metaLabelSpaced]}>Description</Text>
          <TextInput
            style={[s.metaInput, s.metaTextarea]}
            defaultValue={template.description ?? ""}
            onChangeText={(v) => {
              descRef.current = v || undefined;
              scheduleSaveMeta();
            }}
            placeholder="Optional description"
            placeholderTextColor="#4b5563"
            multiline
            numberOfLines={2}
          />
          <View style={s.durationRow}>
            <Text style={[s.metaLabel, { marginBottom: 0 }]}>Duration (min)</Text>
            <TextInput
              style={[s.metaInput, s.durationInput]}
              defaultValue={
                template.estimatedDurationMinutes != null
                  ? String(template.estimatedDurationMinutes)
                  : ""
              }
              onChangeText={(v) => {
                durationRef.current = v ? parseInt(v, 10) : undefined;
                scheduleSaveMeta();
              }}
              keyboardType="numeric"
              placeholder="–"
              placeholderTextColor="#4b5563"
              returnKeyType="done"
            />
          </View>
          {saving && <ActivityIndicator size="small" color="#6b7280" style={s.savingSpinner} />}
        </View>

        {/* Blocks */}
        {template.blocks.map((block, bi) => (
          <BlockCard
            key={block.id}
            block={block}
            blockIndex={bi}
            totalBlocks={template.blocks.length}
            templateId={templateId}
            onMoveUp={(id) => handleMoveBlock(id, "up")}
            onMoveDown={(id) => handleMoveBlock(id, "down")}
            onDeleteBlock={handleDeleteBlock}
            onAddExercise={openPicker}
            onDeleteExercise={handleDeleteExercise}
            onUpdateSets={handleUpdateSets}
            onMoveExerciseUp={(bid, eid) => handleMoveExercise(bid, eid, "up")}
            onMoveExerciseDown={(bid, eid) => handleMoveExercise(bid, eid, "down")}
            onUpdateRest={handleUpdateRest}
          />
        ))}

        {/* Add block buttons */}
        <View style={s.addBlockRow}>
          <Pressable style={s.addBlockBtn} onPress={() => handleAddBlock("set")}>
            <Text style={s.addBlockText}>+ Add Set Block</Text>
          </Pressable>
          <Pressable
            style={[s.addBlockBtn, s.addBlockBtnSup]}
            onPress={() => handleAddBlock("superset")}
          >
            <Text style={[s.addBlockText, s.addBlockTextSup]}>⚡ Add Superset</Text>
          </Pressable>
        </View>

        {/* Delete template */}
        <Pressable style={s.deleteTemplateBtn} onPress={handleDeleteTemplate}>
          <Text style={s.deleteTemplateText}>Delete Template</Text>
        </Pressable>
      </ScrollView>

      {/* Exercise picker modal */}
      <ExercisePickerModal
        visible={pickerVisible}
        onSelect={handleExerciseSelected}
        onClose={() => setPickerVisible(false)}
      />
    </KeyboardAvoidingView>
  );
}

const s = StyleSheet.create({
  flex: { flex: 1, backgroundColor: "#000" },
  centered: { flex: 1, backgroundColor: "#000", alignItems: "center", justifyContent: "center" },
  errorText: { color: "#9ca3af", fontSize: 16 },
  scroll: { flex: 1 },
  content: { padding: 14, paddingBottom: 60 },
  metaCard: {
    backgroundColor: "#111",
    borderRadius: 12,
    padding: 14,
    marginBottom: 14,
  },
  metaLabel: { color: "#6b7280", fontSize: 11, fontWeight: "700", textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 6 },
  metaLabelSpaced: { marginTop: 12 },
  metaInput: {
    backgroundColor: "#1f2937",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    color: "#f9fafb",
    fontSize: 15,
  },
  metaTextarea: { height: 56, textAlignVertical: "top" },
  durationRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginTop: 12 },
  durationInput: { width: 72, textAlign: "center", fontSize: 15 },
  savingSpinner: { marginTop: 10 },
  addBlockRow: { flexDirection: "row", gap: 10, marginBottom: 16 },
  addBlockBtn: {
    flex: 1,
    borderWidth: 1,
    borderColor: "#374151",
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: "center",
  },
  addBlockBtnSup: { borderColor: "#7c3aed" },
  addBlockText: { color: "#9ca3af", fontSize: 14, fontWeight: "600" },
  addBlockTextSup: { color: "#c4b5fd" },
  deleteTemplateBtn: {
    borderWidth: 1,
    borderColor: "#7f1d1d",
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: "center",
    marginTop: 8,
  },
  deleteTemplateText: { color: "#f87171", fontSize: 14 },
});
