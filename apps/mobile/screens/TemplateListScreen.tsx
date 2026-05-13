import React, { useCallback, useEffect, useState } from "react";
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
  createTemplate,
  deleteTemplate,
  fetchTemplates,
  type WorkoutTemplateSummary,
} from "../lib/api";
import type { TemplatesStackParamList } from "../navigation/types";

type Props = NativeStackScreenProps<TemplatesStackParamList, "TemplateList">;

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

export default function TemplateListScreen({ navigation }: Props) {
  const [templates, setTemplates] = useState<WorkoutTemplateSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);

  const debouncedQuery = useDebounce(query, 300);

  const load = useCallback(
    async (pageNum: number, replace: boolean) => {
      setLoading(true);
      try {
        const result = await fetchTemplates(debouncedQuery || undefined, pageNum);
        setTotal(result.total);
        setTemplates((prev) => (replace ? result.items : [...prev, ...result.items]));
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    },
    [debouncedQuery],
  );

  // Reset and reload when query changes
  useEffect(() => {
    setPage(1);
    setTemplates([]);
    load(1, true);
  }, [debouncedQuery, load]);

  // Reload list when navigating back from edit screen
  useEffect(() => {
    return navigation.addListener("focus", () => {
      setPage(1);
      load(1, true);
    });
  }, [navigation, load]);

  const loadMore = () => {
    if (loading || templates.length >= total) return;
    const next = page + 1;
    setPage(next);
    load(next, false);
  };

  const handleCreate = async () => {
    setCreating(true);
    try {
      const template = await createTemplate({ name: "New Template" });
      navigation.navigate("TemplateEdit", { templateId: template.id });
    } catch (e) {
      Alert.alert("Error", "Failed to create template");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = (item: WorkoutTemplateSummary) => {
    Alert.alert("Delete Template", `Delete "${item.name}"? This cannot be undone.`, [
      { text: "Cancel", style: "cancel" },
      {
        text: "Delete",
        style: "destructive",
        onPress: async () => {
          try {
            await deleteTemplate(item.id);
            setTemplates((prev) => prev.filter((t) => t.id !== item.id));
            setTotal((n) => n - 1);
          } catch {
            Alert.alert("Error", "Failed to delete template");
          }
        },
      },
    ]);
  };

  const renderItem = ({ item }: { item: WorkoutTemplateSummary }) => (
    <Pressable
      style={({ pressed }) => [s.card, pressed && s.cardPressed]}
      onPress={() => navigation.navigate("TemplateEdit", { templateId: item.id })}
      onLongPress={() => handleDelete(item)}
    >
      <View style={s.cardTop}>
        <Text style={s.cardName} numberOfLines={1}>
          {item.name}
        </Text>
        {item.estimatedDurationMinutes != null && (
          <Text style={s.cardDuration}>{item.estimatedDurationMinutes} min</Text>
        )}
      </View>
      {item.description ? (
        <Text style={s.cardDesc} numberOfLines={2}>
          {item.description}
        </Text>
      ) : null}
      {item.tags.length > 0 && (
        <View style={s.tagRow}>
          {item.tags.map((tag) => (
            <View key={tag} style={s.tag}>
              <Text style={s.tagText}>{tag}</Text>
            </View>
          ))}
        </View>
      )}
      <Text style={s.cardHint}>Long-press to delete</Text>
    </Pressable>
  );

  return (
    <View style={s.container}>
      {/* Search bar */}
      <View style={s.searchRow}>
        <TextInput
          style={s.searchInput}
          placeholder="Search templates…"
          placeholderTextColor="#6b7280"
          value={query}
          onChangeText={setQuery}
          returnKeyType="search"
          clearButtonMode="while-editing"
        />
      </View>

      <FlatList
        data={templates}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        contentContainerStyle={s.list}
        onEndReached={loadMore}
        onEndReachedThreshold={0.3}
        ListEmptyComponent={
          loading ? null : (
            <View style={s.empty}>
              <Text style={s.emptyText}>No templates yet.</Text>
              <Text style={s.emptyHint}>Tap + to create your first template.</Text>
            </View>
          )
        }
        ListFooterComponent={loading ? <ActivityIndicator color="#f9fafb" style={s.spinner} /> : null}
      />

      {/* FAB */}
      <Pressable
        style={({ pressed }) => [s.fab, pressed && s.fabPressed]}
        onPress={handleCreate}
        disabled={creating}
      >
        {creating ? (
          <ActivityIndicator color="#000" size="small" />
        ) : (
          <Text style={s.fabLabel}>＋</Text>
        )}
      </Pressable>
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
  searchRow: { padding: 12, paddingBottom: 6 },
  searchInput: {
    backgroundColor: "#111",
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    color: "#f9fafb",
    fontSize: 15,
  },
  list: { padding: 12, paddingBottom: 100 },
  card: {
    backgroundColor: "#111",
    borderRadius: 12,
    padding: 16,
    marginBottom: 10,
  },
  cardPressed: { opacity: 0.7 },
  cardTop: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  cardName: { color: "#f9fafb", fontSize: 16, fontWeight: "700", flex: 1 },
  cardDuration: { color: "#9ca3af", fontSize: 13, marginLeft: 8 },
  cardDesc: { color: "#9ca3af", fontSize: 13, marginTop: 4 },
  tagRow: { flexDirection: "row", flexWrap: "wrap", marginTop: 8, gap: 6 },
  tag: {
    backgroundColor: "#1f2937",
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 2,
  },
  tagText: { color: "#d1d5db", fontSize: 11 },
  cardHint: { color: "#374151", fontSize: 11, marginTop: 8 },
  empty: { alignItems: "center", paddingTop: 80 },
  emptyText: { color: "#9ca3af", fontSize: 16 },
  emptyHint: { color: "#6b7280", fontSize: 13, marginTop: 6 },
  spinner: { paddingVertical: 20 },
  fab: {
    position: "absolute",
    right: 20,
    bottom: 24,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: "#f9fafb",
    alignItems: "center",
    justifyContent: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.4,
    shadowRadius: 4,
    elevation: 6,
  },
  fabPressed: { opacity: 0.8 },
  fabLabel: { fontSize: 28, color: "#000", lineHeight: 32 },
});
