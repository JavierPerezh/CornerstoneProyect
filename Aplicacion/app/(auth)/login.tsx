// app/(auth)/login.tsx
// Login por codigo_registro (6 dígitos) — no hay email/password en la BD
import React, { useState, useEffect } from "react";
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ActivityIndicator, KeyboardAvoidingView, Platform, Alert,
} from "react-native";
import { router } from "expo-router";
import { login, getCodigoRegistro } from "../../services/auth";

export default function LoginScreen() {
  const [codigo, setCodigo] = useState("");
  const [loading, setLoading] = useState(false);

  // Pre-rellenar si ya inició sesión antes
  useEffect(() => {
    getCodigoRegistro().then((c) => { if (c) setCodigo(c); });
  }, []);

  const handleLogin = async () => {
    const trimmed = codigo.trim();
    if (trimmed.length !== 6 || !/^\d{6}$/.test(trimmed)) {
      Alert.alert("Código inválido", "El código de registro debe ser de 6 dígitos.");
      return;
    }
    try {
      setLoading(true);
      await login(trimmed);
      router.replace("/(main)");
    } catch (e: any) {
      Alert.alert("Acceso denegado", e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <View style={styles.card}>
        {/* Logo / título */}
        <View style={styles.logoArea}>
          <Text style={styles.logoIcon}>🤱</Text>
          <Text style={styles.title}>Cornerst</Text>
          <Text style={styles.subtitle}>Sistema de acompañamiento posparto</Text>
        </View>

        <Text style={styles.label}>Código de registro</Text>
        <TextInput
          style={styles.input}
          placeholder="_ _ _ _ _ _"
          placeholderTextColor="#3a3a5a"
          value={codigo}
          onChangeText={(t) => setCodigo(t.replace(/\D/g, "").slice(0, 6))}
          keyboardType="number-pad"
          maxLength={6}
          textAlign="center"
        />
        <Text style={styles.hint}>
          Ingresa el código de 6 dígitos que te entregó el sistema Cornerst.
        </Text>

        <TouchableOpacity
          style={[styles.button, (loading || codigo.length < 6) && styles.buttonDisabled]}
          onPress={handleLogin}
          disabled={loading || codigo.length < 6}
        >
          {loading
            ? <ActivityIndicator color="#fff" />
            : <Text style={styles.buttonText}>Entrar</Text>
          }
        </TouchableOpacity>

        {/* Aviso demo */}
        <TouchableOpacity
          style={styles.demoBtn}
          onPress={() => setCodigo("123456")}
        >
          <Text style={styles.demoText}>Usar código demo (123456)</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1, backgroundColor: "#0d0d14",
    justifyContent: "center", padding: 24,
  },
  card: {
    backgroundColor: "#16161f", borderRadius: 20,
    padding: 28, borderWidth: 1, borderColor: "#2a2a3a",
  },
  logoArea: { alignItems: "center", marginBottom: 28 },
  logoIcon: { fontSize: 48, marginBottom: 8 },
  title:    { fontSize: 28, fontWeight: "800", color: "#e0e0ff" },
  subtitle: { fontSize: 13, color: "#6a6a8a", marginTop: 4, textAlign: "center" },

  label: { color: "#8a8ab0", fontSize: 13, fontWeight: "600", marginBottom: 8 },
  input: {
    backgroundColor: "#1e1e2e", borderRadius: 14, padding: 16,
    color: "#e0e0ff", fontSize: 28, fontWeight: "700",
    letterSpacing: 12, marginBottom: 10,
    borderWidth: 1, borderColor: "#2a2a3a",
  },
  hint: { color: "#4a4a6a", fontSize: 12, marginBottom: 20, lineHeight: 17 },

  button: {
    backgroundColor: "#6c63ff", borderRadius: 12,
    padding: 16, alignItems: "center",
  },
  buttonDisabled: { opacity: 0.4 },
  buttonText: { color: "#fff", fontWeight: "700", fontSize: 16 },

  demoBtn:  { alignItems: "center", marginTop: 16 },
  demoText: { color: "#3a3a6a", fontSize: 12 },
});
