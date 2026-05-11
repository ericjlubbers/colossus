import { StatusBar } from "expo-status-bar";
import { Text, View } from "react-native";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";

export default function App() {
  return (
    <SafeAreaProvider>
      <SafeAreaView
        style={{ flex: 1, backgroundColor: "#000", alignItems: "center", justifyContent: "center" }}
      >
        <View style={{ alignItems: "center" }}>
          <Text style={{ color: "#ffffff", fontSize: 40, fontWeight: "bold", letterSpacing: 2 }}>
            COLOSSUS
          </Text>
          <Text style={{ color: "#6b7280", marginTop: 8, fontSize: 14 }}>
            Your self-hosted fitness tracker
          </Text>
        </View>
        <StatusBar style="light" />
      </SafeAreaView>
    </SafeAreaProvider>
  );
}
