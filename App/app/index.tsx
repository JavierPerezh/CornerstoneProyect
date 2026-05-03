import { useEffect } from "react";
import { View, ActivityIndicator } from "react-native";
import { router } from "expo-router";

export default function SplashRedirect() {
  useEffect(() => {
    // Pequeño retardo para asegurar que el layout está listo
    const timeout = setTimeout(() => {
      router.replace("/(auth)/login");
    }, 100);
    return () => clearTimeout(timeout);
  }, []);

  return (
    <View style={{ flex: 1, backgroundColor: "#0d0d14", justifyContent: "center", alignItems: "center" }}>
      <ActivityIndicator color="#6c63ff" size="large" />
    </View>
  );
}
