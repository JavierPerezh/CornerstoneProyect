// app/(main)/historial.tsx
// Muestra la tabla `interacciones` con todos sus campos relevantes
import React, { useEffect, useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import {
  View, Text, FlatList, StyleSheet,
  ActivityIndicator, TouchableOpacity,
} from "react-native";
import { obtenerHistorial, Interaccion } from "../../services/api";

const NIVEL_COLOR: Record<string, string> = {
  verde:    "#3db87a",
  amarillo: "#f0a500",
  rojo:     "#e05252",
};
const NIVEL_EMOJI: Record<string, string> = {
  verde: "✅", amarillo: "⚠️", rojo: "🚨",
};

export default function HistorialScreen() {
  const [items, setItems]   = useState<Interaccion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState<string | null>(null);

  const cargar = async () => {
    try {
      setLoading(true);
      setError(null);
      setItems(await obtenerHistorial());
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { cargar(); }, []);

  const formatFecha = (iso: string) =>
    new Date(iso).toLocaleDateString("es-CO", {
      day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit",
    });

  if (loading) return (
    <View style={styles.center}>
      <ActivityIndicator color="#6c63ff" size="large" />
    </View>
  );

  if (error) return (
    <View style={styles.center}>
      <Text style={styles.errorText}>{error}</Text>
      <TouchableOpacity onPress={cargar} style={styles.retryBtn}>
        <Text style={styles.retryText}>Reintentar</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#0d0d14' }}>
    <View style={styles.container}>
      <Text style={styles.title}>Historial</Text>

      {items.length === 0
        ? <Text style={styles.empty}>No hay interacciones registradas aún.</Text>
        : (
          <FlatList
            data={items}
            keyExtractor={(item) => String(item.id)}
            contentContainerStyle={{ paddingBottom: 30 }}
            renderItem={({ item }) => {
              const nivel  = item.nivel_alerta ?? "verde";
              const color  = NIVEL_COLOR[nivel] ?? "#6c63ff";
              const urgente = item.requiere_accion_inmediata;

              return (
                <View style={[styles.card, urgente && styles.cardUrgente]}>
                  {/* Header: fecha + nivel + urgencia */}
                  <View style={styles.cardHeader}>
                    <Text style={styles.fecha}>{formatFecha(item.fecha)}</Text>
                    <View style={{ flexDirection: "row", gap: 6, alignItems: "center" }}>
                      {urgente && (
                        <View style={styles.urgenteBadge}>
                          <Text style={styles.urgenteText}>URGENTE</Text>
                        </View>
                      )}
                      <View style={[styles.nivelBadge, { borderColor: color }]}>
                        <Text style={[styles.nivelText, { color }]}>
                          {NIVEL_EMOJI[nivel]} {nivel}
                        </Text>
                      </View>
                    </View>
                  </View>

                  {/* Texto paciente */}
                  <Text style={styles.labelUser}>Tú dijiste</Text>
                  <Text style={styles.textUser} numberOfLines={2}>
                    {item.texto_usuario}
                  </Text>

                  {/* Texto IA */}
                  <Text style={styles.labelAI}>Cornerst respondió</Text>
                  <Text style={styles.textAI} numberOfLines={3}>
                    {item.texto_respuesta}
                  </Text>

                  {/* Síntomas detectados */}
                  {(item.sintomas_madre.length > 0 || item.sintomas_bebe.length > 0) && (
                    <View style={styles.sintomasRow}>
                      {item.sintomas_madre.length > 0 && (
                        <View style={styles.sintomaGroup}>
                          <Text style={styles.sintomaLabel}>Mamá</Text>
                          <Text style={styles.sintomaText}>
                            {item.sintomas_madre.join(", ")}
                          </Text>
                        </View>
                      )}
                      {item.sintomas_bebe.length > 0 && (
                        <View style={styles.sintomaGroup}>
                          <Text style={styles.sintomaLabel}>Bebé</Text>
                          <Text style={styles.sintomaText}>
                            {item.sintomas_bebe.join(", ")}
                          </Text>
                        </View>
                      )}
                    </View>
                  )}

                  {/* Score ML */}
                  {item.puntuacion_riesgo !== null && (
                    <Text style={styles.score}>
                      Score ML: {(item.puntuacion_riesgo * 100).toFixed(1)}%
                    </Text>
                  )}
                </View>
              );
            }}
          />
        )
      }
    </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1, backgroundColor: "#0d0d14",
    paddingHorizontal: 20, paddingTop: 12,
  },
  center: {
    flex: 1, backgroundColor: "#0d0d14",
    justifyContent: "center", alignItems: "center", padding: 24,
  },
  title: { fontSize: 22, fontWeight: "800", color: "#e0e0ff", marginBottom: 20 },
  empty: { color: "#3a3a5a", textAlign: "center", marginTop: 60, fontSize: 15 },

  card: {
    backgroundColor: "#16161f", borderRadius: 14, padding: 14,
    marginBottom: 12, borderWidth: 1, borderColor: "#2a2a3a",
  },
  cardUrgente: { borderColor: "#e0525288", backgroundColor: "#1e1010" },

  cardHeader: {
    flexDirection: "row", justifyContent: "space-between",
    alignItems: "center", marginBottom: 10,
  },
  fecha: { color: "#5a5a7a", fontSize: 12 },

  nivelBadge: {
    borderWidth: 1, borderRadius: 12,
    paddingHorizontal: 8, paddingVertical: 2,
  },
  nivelText: { fontSize: 11, fontWeight: "600" },

  urgenteBadge: {
    backgroundColor: "#e05252", borderRadius: 8,
    paddingHorizontal: 6, paddingVertical: 2,
  },
  urgenteText: { color: "#fff", fontSize: 10, fontWeight: "800" },

  labelUser: {
    color: "#5a5a9a", fontSize: 11, fontWeight: "700",
    marginBottom: 3, textTransform: "uppercase", letterSpacing: 0.7,
  },
  textUser: { color: "#b0b0d0", fontSize: 14, marginBottom: 10 },

  labelAI: {
    color: "#3a7a5a", fontSize: 11, fontWeight: "700",
    marginBottom: 3, textTransform: "uppercase", letterSpacing: 0.7,
  },
  textAI: { color: "#90c0a0", fontSize: 14, marginBottom: 10 },

  sintomasRow: {
    flexDirection: "row", gap: 12,
    backgroundColor: "#1e1e2e", borderRadius: 8,
    padding: 10, marginBottom: 8,
  },
  sintomaGroup: { flex: 1 },
  sintomaLabel: { color: "#6a6a8a", fontSize: 11, fontWeight: "700", marginBottom: 3 },
  sintomaText:  { color: "#a0a0c0", fontSize: 12 },

  score: { color: "#4a4a6a", fontSize: 11, marginTop: 4 },

  errorText: { color: "#e05252", textAlign: "center", marginBottom: 16 },
  retryBtn:  { backgroundColor: "#2a2a3a", borderRadius: 8, padding: 12 },
  retryText: { color: "#e0e0ff", fontWeight: "600" },
});
