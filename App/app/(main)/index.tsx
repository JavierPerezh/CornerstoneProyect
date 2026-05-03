// app/(main)/index.tsx
import React from "react";
import {
  View, Text, TouchableOpacity, StyleSheet,
  ScrollView, ActivityIndicator,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { useVoiceSession, SessionStatus } from "../../hooks/useVoiceSession";
import { logout } from "../../services/auth";

const STATUS_LABEL: Record<SessionStatus, string> = {
  idle:       "Mantén presionado para hablar",
  recording:  "🎙  Grabando... suelta para enviar",
  sending:    "Subiendo audio...",
  processing: "Procesando con IA (puede tardar ~10 seg)...",
  playing:    "🔊  Reproduciendo respuesta",
  error:      "Ocurrió un error",
};

const STATUS_COLOR: Record<SessionStatus, string> = {
  idle:       "#6c63ff",
  recording:  "#e05252",
  sending:    "#f0a500",
  processing: "#f0a500",
  playing:    "#3db87a",
  error:      "#e05252",
};

const STATUS_ICON: Record<SessionStatus, string> = {
  idle:       "🎙",
  recording:  "⏹",
  sending:    "⏳",
  processing: "⏳",
  playing:    "🔊",
  error:      "⚠️",
};

export default function VozScreen() {
  const { status, response, error, startRecording, stopAndSend, reset } =
    useVoiceSession();

  const isBusy = status === "sending" || status === "processing" || status === "playing";

  const handleLogout = async () => {
    await logout();
    router.replace("/(auth)/login");
  };

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.container}>
        {/* ── Header ── */}
        <View style={styles.header}>
          <View>
            <Text style={styles.headerTitle}>Cornerst</Text>
            <Text style={styles.headerSub}>Asistente posparto</Text>
          </View>
          <TouchableOpacity onPress={handleLogout} style={styles.logoutBtn} hitSlop={12}>
            <Text style={styles.logoutText}>Salir</Text>
          </TouchableOpacity>
        </View>

        {/* ── Área de respuesta ── */}
        <ScrollView
          style={styles.responseArea}
          contentContainerStyle={styles.responseContent}
          keyboardShouldPersistTaps="handled"
        >
          {!response && !error && status === "idle" && (
            <Text style={styles.placeholder}>
              Presiona el botón y cuéntame cómo te sientes hoy...
            </Text>
          )}

          {error && (
            <View style={styles.errorCard}>
              <Text style={styles.errorTitle}>⚠ Error</Text>
              <Text style={styles.errorText}>{error}</Text>
              <TouchableOpacity onPress={reset} style={styles.retryBtn}>
                <Text style={styles.retryText}>Reintentar</Text>
              </TouchableOpacity>
            </View>
          )}

          {response && (
            <View style={styles.bubbleAI}>
              <Text style={styles.bubbleLabel}>Cornerst IA</Text>
              <Text style={styles.bubbleText}>
                {response.texto_respuesta ?? "Procesado correctamente."}
              </Text>
            </View>
          )}

          {(status === "sending" || status === "processing") && (
            <View style={styles.processingCard}>
              <ActivityIndicator color="#f0a500" style={{ marginBottom: 10 }} />
              <Text style={styles.processingText}>{STATUS_LABEL[status]}</Text>
              {status === "processing" && (
                <Text style={styles.processingHint}>
                  Consultando estado cada 2 seg...
                </Text>
              )}
            </View>
          )}
        </ScrollView>

        {/* ── Status label ── */}
        <Text style={[styles.statusLabel, { color: STATUS_COLOR[status] }]}>
          {STATUS_LABEL[status]}
        </Text>

        {/* ── Botón push-to-talk (90×90, cumple mínimo táctil 44pt) ── */}
        <TouchableOpacity
          style={[
            styles.recordBtn,
            { backgroundColor: STATUS_COLOR[status] },
            status === "recording" && styles.recordBtnActive,
          ]}
          onPressIn={startRecording}
          onPressOut={stopAndSend}
          disabled={isBusy}
          activeOpacity={0.85}
          accessibilityLabel="Botón de grabación de voz"
          accessibilityRole="button"
        >
          <Text style={styles.recordIcon}>{STATUS_ICON[status]}</Text>
        </TouchableOpacity>

        <Text style={styles.hint}>
          {isBusy ? "" : "Mantén presionado · suelta para enviar"}
        </Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#0d0d14" },
  container: {
    flex: 1, paddingHorizontal: 20, paddingTop: 12, paddingBottom: 12,
  },
  header: {
    flexDirection: "row", justifyContent: "space-between",
    alignItems: "center", marginBottom: 20,
  },
  headerTitle: { fontSize: 22, fontWeight: "800", color: "#e0e0ff" },
  headerSub:   { fontSize: 12, color: "#6a6a8a", marginTop: 2 },
  logoutBtn:   { padding: 8 },
  logoutText:  { color: "#6a6a8a", fontSize: 14 },

  responseArea: {
    flex: 1, backgroundColor: "#16161f", borderRadius: 16,
    marginBottom: 18, borderWidth: 1, borderColor: "#2a2a3a",
  },
  responseContent: { padding: 16, flexGrow: 1 },

  placeholder: {
    color: "#3a3a5a", textAlign: "center",
    marginTop: 50, fontSize: 15, lineHeight: 22,
  },

  bubbleAI: {
    backgroundColor: "#1a2a1a", borderRadius: 12, padding: 14,
    marginBottom: 12, borderLeftWidth: 3, borderLeftColor: "#3db87a",
  },
  bubbleLabel: {
    fontSize: 11, fontWeight: "700", color: "#3a7a5a",
    marginBottom: 5, textTransform: "uppercase", letterSpacing: 0.8,
  },
  bubbleText: { color: "#e0e0ff", fontSize: 15, lineHeight: 23 },

  processingCard: {
    backgroundColor: "#1e1a10", borderRadius: 12, padding: 20,
    alignItems: "center", marginTop: 10,
    borderWidth: 1, borderColor: "#f0a50033",
  },
  processingText: { color: "#f0a500", fontSize: 14, textAlign: "center" },
  processingHint: { color: "#8a7a50", fontSize: 12, marginTop: 6 },

  errorCard: {
    backgroundColor: "#2a1a1a", borderRadius: 12, padding: 16,
    borderWidth: 1, borderColor: "#e0525244",
  },
  errorTitle: { color: "#e05252", fontWeight: "700", marginBottom: 6 },
  errorText:  { color: "#c09090", fontSize: 14 },
  retryBtn: {
    marginTop: 12, backgroundColor: "#2a2a3a",
    borderRadius: 8, padding: 10, alignItems: "center",
  },
  retryText: { color: "#e0e0ff", fontWeight: "600" },

  statusLabel: {
    textAlign: "center", fontSize: 13, marginBottom: 14, fontWeight: "500",
  },
  recordBtn: {
    width: 90, height: 90, borderRadius: 45, alignSelf: "center",
    justifyContent: "center", alignItems: "center",
    shadowColor: "#6c63ff", shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.55, shadowRadius: 22, elevation: 12,
  },
  recordBtnActive: { transform: [{ scale: 1.1 }] },
  recordIcon: { fontSize: 34 },
  hint: { textAlign: "center", color: "#3a3a5a", fontSize: 11, marginTop: 10 },
});
