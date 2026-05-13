import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { StatusBar } from "expo-status-bar";
import { Text } from "react-native";
import { SafeAreaProvider } from "react-native-safe-area-context";
import ExerciseDetailScreen from "./screens/ExerciseDetailScreen";
import ExerciseListScreen from "./screens/ExerciseListScreen";
import TemplateListScreen from "./screens/TemplateListScreen";
import TemplateEditScreen from "./screens/TemplateEditScreen";
import WorkoutHomeScreen from "./screens/WorkoutHomeScreen";
import WorkoutSessionScreen from "./screens/WorkoutSessionScreen";
import WorkoutFinishScreen from "./screens/WorkoutFinishScreen";
import type {
  TemplatesStackParamList,
  ExercisesStackParamList,
  WorkoutStackParamList,
} from "./navigation/types";

const ExercisesStack = createNativeStackNavigator<ExercisesStackParamList>();
const TemplatesStack = createNativeStackNavigator<TemplatesStackParamList>();
const WorkoutStack = createNativeStackNavigator<WorkoutStackParamList>();
const Tab = createBottomTabNavigator();

const NAV_OPTS = {
  headerStyle: { backgroundColor: "#000" },
  headerTintColor: "#f9fafb",
  headerTitleStyle: { fontWeight: "700" as const },
  contentStyle: { backgroundColor: "#000" },
};

function ExercisesNavigator() {
  return (
    <ExercisesStack.Navigator screenOptions={NAV_OPTS}>
      <ExercisesStack.Screen
        name="ExerciseList"
        component={ExerciseListScreen}
        options={{ title: "Exercise Library" }}
      />
      <ExercisesStack.Screen
        name="ExerciseDetail"
        component={ExerciseDetailScreen}
        options={({ route }) => ({ title: route.params.exerciseName })}
      />
    </ExercisesStack.Navigator>
  );
}

function TemplatesNavigator() {
  return (
    <TemplatesStack.Navigator screenOptions={NAV_OPTS}>
      <TemplatesStack.Screen
        name="TemplateList"
        component={TemplateListScreen}
        options={{ title: "My Templates" }}
      />
      <TemplatesStack.Screen
        name="TemplateEdit"
        component={TemplateEditScreen}
        options={{ title: "Edit Template" }}
      />
    </TemplatesStack.Navigator>
  );
}

function WorkoutNavigator() {
  return (
    <WorkoutStack.Navigator screenOptions={NAV_OPTS}>
      <WorkoutStack.Screen
        name="WorkoutHome"
        component={WorkoutHomeScreen}
        options={{ title: "Start Workout" }}
      />
      <WorkoutStack.Screen
        name="WorkoutSession"
        component={WorkoutSessionScreen}
        options={{ title: "Active Workout", gestureEnabled: false }}
      />
      <WorkoutStack.Screen
        name="WorkoutFinish"
        component={WorkoutFinishScreen}
        options={{ title: "Workout Summary", gestureEnabled: false }}
      />
    </WorkoutStack.Navigator>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Tab.Navigator
          screenOptions={{
            headerShown: false,
            tabBarStyle: { backgroundColor: "#111", borderTopColor: "#222" },
            tabBarActiveTintColor: "#f9fafb",
            tabBarInactiveTintColor: "#6b7280",
          }}
        >
          <Tab.Screen
            name="Templates"
            component={TemplatesNavigator}
            options={{
              tabBarLabel: "Templates",
              tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 18 }}>⚡</Text>,
            }}
          />
          <Tab.Screen
            name="Exercises"
            component={ExercisesNavigator}
            options={{
              tabBarLabel: "Exercises",
              tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 18 }}>💪</Text>,
            }}
          />
          <Tab.Screen
            name="Workout"
            component={WorkoutNavigator}
            options={{
              tabBarLabel: "Workout",
              tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 18 }}>🏋️</Text>,
            }}
          />
        </Tab.Navigator>
      </NavigationContainer>
      <StatusBar style="light" />
    </SafeAreaProvider>
  );
}
