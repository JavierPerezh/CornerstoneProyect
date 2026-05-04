// app/(main)/_layout.tsx
import { Tabs } from "expo-router";
import { Text } from "react-native";

export default function MainLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: "#16161f",
          borderTopColor: "#2a2a3a",
          height: 62,
          paddingBottom: 10,
        },
        tabBarActiveTintColor: "#6c63ff",
        tabBarInactiveTintColor: "#4a4a6a",
        tabBarLabelStyle: { fontSize: 11, fontWeight: "600" },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Voz",
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 20, color }}>🎙</Text>,
        }}
      />
      <Tabs.Screen
        name="historial"
        options={{
          title: "Historial",
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 20, color }}>📋</Text>,
        }}
      />
      <Tabs.Screen
        name="ajustes"
        options={{
          title: "Ajustes",
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 20, color }}>⚙️</Text>,
        }}
      />
    </Tabs>
  );
}
