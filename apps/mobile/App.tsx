import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";
import ExerciseDetailScreen from "./screens/ExerciseDetailScreen";
import ExerciseListScreen from "./screens/ExerciseListScreen";
import type { RootStackParamList } from "./navigation/types";

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Stack.Navigator
          screenOptions={{
            headerStyle: { backgroundColor: "#000" },
            headerTintColor: "#f9fafb",
            headerTitleStyle: { fontWeight: "700" },
            contentStyle: { backgroundColor: "#000" },
          }}
        >
          <Stack.Screen
            name="ExerciseList"
            component={ExerciseListScreen}
            options={{ title: "Exercise Library" }}
          />
          <Stack.Screen
            name="ExerciseDetail"
            component={ExerciseDetailScreen}
            options={({ route }) => ({ title: route.params.exerciseName })}
          />
        </Stack.Navigator>
      </NavigationContainer>
      <StatusBar style="light" />
    </SafeAreaProvider>
  );
}
