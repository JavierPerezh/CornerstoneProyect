// app/(main)/ajustes.tsx
// El dispositivo_id vive en usuarios.dispositivo_id (init.sql).
// El demo tiene dispositivo_id = 'device-demo-001'.
// La app lo guarda en SecureStore y lo manda como X-Device-Id en /voz.
import { SafeAreaView } from "react-native-safe-area-context";
import React, { useEffect, useState } from "react";
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  Alert, ActivityIndicator, ScrollView,
} from "react-native";
import { getDeviceId, setDeviceId, getCodigoRegistro } from "../../services/auth";
import { ENDPOINTS } from "../../constants/config";
import { getServerUrl, setServerUrl } from "../../services/config";

export default function AjustesScreen() {
  const [serverUrl, setServerUrlState] = useState("");
  const [deviceId, setDeviceIdState] = useState("");
  const [codigo, setCodigo]          = useState("");
  const [saved, setSaved]            = useState(false);
  const [testing, setTesting]        = useState(false);

  useEffect(() => {
    getDeviceId().then((id)  => { if (id) setDeviceIdState(id); });
    getCodigoRegistro().then((c) => { if (c) setCodigo(c); });
    getServerUrl().then(url => setServerUrlState(url));
  }, []);

  const handleSave = async () => {
    const trimmed = deviceId.trim();
    if (!trimmed) { Alert.alert("Error", "Ingresa un Device ID válido"); return; }
    await setDeviceId(trimmed);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleTest = async () => {
    const trimmed = deviceId.trim();
    if (!trimmed) { Alert.alert("Error", "Guarda un Device ID primero"); return; }
    try {
      setTesting(true);
      // Enviar sin audio → si responde 415/422 el device_id es válido (pasó validate_device)
      // Si responde 401 → device_id rechazado
      const res = await fetch(ENDPOINTS.voz, {
        method: "POST",
        headers: { "X-Device-Id": trimmed },
        body: new FormData(),
      });
      if (res.status === 401) {
        Alert.alert(
          "❌ Device ID inválido",
          "El servidor rechazó este dispositivo_id.\nVerifica que esté registrado en la BD."
        );
      } else {
        Alert.alert(
          "✅ Dispositivo reconocido",
          `El servidor respondió ${res.status} — el dispositivo_id es válido.`
        );
      }
    } catch (e: any) {
      Alert.alert("Error de red", e.message);
    } finally {
      setTesting(false);
    }
  };

    return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#0d0d14" }}>
      <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 40 }}>
        <Text style={styles.title}>Ajustes</Text>

        {/* ── Sesión actual ── */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>👤 Sesión actual</Text>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Código de registro</Text>
            <Text style={styles.infoValue}>{codigo || "—"}</Text>
          </View>
        </View>

        {/* ── Device ID ── */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📡 Device ID</Text>
          <Text style={styles.sectionDesc}>
            El endpoint <Text style={styles.code}>/voz</Text> requiere el campo{" "}
            <Text style={styles.code}>dispositivo_id</Text> registrado en la tabla{" "}
            <Text style={styles.code}>usuarios</Text> de la BD.{"\n\n"}
            Para el entorno demo usa:{" "}
            <Text style={[styles.code, { color: "#6c63ff" }]}>device-demo-001</Text>
          </Text>

          <TextInput
            style={styles.input}
            placeholder="ej: device-demo-001"
            placeholderTextColor="#4a4a6a"
            value={deviceId}
            onChangeText={(t) => { setDeviceIdState(t); setSaved(false); }}
            autoCapitalize="none"
            autoCorrect={false}
          />

          <View style={styles.btnRow}>
            <TouchableOpacity style={styles.btnSave} onPress={handleSave}>
              <Text style={styles.btnText}>{saved ? "✓ Guardado" : "Guardar"}</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.btnTest} onPress={handleTest} disabled={testing}
            >
              {testing
                ? <ActivityIndicator color="#e0e0ff" size="small" />
                : <Text style={styles.btnText}>Probar</Text>
              }
            </TouchableOpacity>
          </View>
        </View>
        
	{/* ── Servidor ── */}
	<View style={styles.section}>
	  <Text style={styles.sectionTitle}>🌐 Servidor</Text>
	  <Text style={styles.sectionDesc}>
	    URL del backend (ej: http://IP:8000)
	  </Text>
	  <TextInput
	    style={styles.input}
	    placeholder="http://192.168.x.x:8000"
	    placeholderTextColor="#4a4a6a"
	    value={serverUrl}
	    onChangeText={setServerUrlState}
	    autoCapitalize="none"
	    autoCorrect={false}
	    keyboardType="url"
	  />
	  <View style={styles.btnRow}>
	    <TouchableOpacity
	      style={styles.btnSave}
	      onPress={async () => {
		await setServerUrl(serverUrl);
		Alert.alert('Guardado', 'URL del servidor actualizada.');
	      }}
	    >
	      <Text style={styles.btnText}>Guardar</Text>
	    </TouchableOpacity>
	    <TouchableOpacity
	      style={styles.btnTest}
	      onPress={async () => {
		try {
		  const testUrl = `${serverUrl.replace(/\/$/, '')}/health`;
		  const res = await fetch(testUrl);
		  if (res.ok) {
		    Alert.alert('✅ Conexión exitosa', `Servidor responde: ${res.status}`);
		  } else {
		    Alert.alert('Error', `El servidor respondió con estado ${res.status}`);
		  }
		} catch (e: any) {
		  Alert.alert('Error de conexión', e.message);
		}
	      }}
	    >
	      <Text style={styles.btnText}>Probar</Text>
	    </TouchableOpacity>
	  </View>
	</View>
	
        {/* ── Cómo registrar un dispositivo nuevo ── */}
        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>⚙️  Registrar un dispositivo nuevo</Text>
          <Text style={styles.infoText}>
            Para registrar la app como dispositivo, el administrador debe ejecutar
            en PostgreSQL:
          </Text>
          <View style={styles.codeBlock}>
            <Text style={styles.codeBlockText}>
              {`UPDATE usuarios\nSET dispositivo_id = 'tu-device-id'\nWHERE codigo_registro = '${codigo || "XXXXXX"}';`}
            </Text>
          </View>
          <Text style={styles.infoText}>
            El <Text style={styles.code}>dispositivo_id</Text> puede ser cualquier
            string único. Se recomienda usar un UUID generado en la app.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1, backgroundColor: "#0d0d14",
    paddingHorizontal: 20, paddingTop: 12,
  },
  title: { fontSize: 22, fontWeight: "800", color: "#e0e0ff", marginBottom: 24 },

  section: {
    backgroundColor: "#16161f", borderRadius: 16, padding: 18,
    borderWidth: 1, borderColor: "#2a2a3a", marginBottom: 16,
  },
  sectionTitle: { fontSize: 15, fontWeight: "700", color: "#e0e0ff", marginBottom: 12 },
  sectionDesc:  { fontSize: 13, color: "#6a6a8a", lineHeight: 20, marginBottom: 14 },

  infoRow: {
    flexDirection: "row", justifyContent: "space-between", alignItems: "center",
  },
  infoLabel: { color: "#6a6a8a", fontSize: 13 },
  infoValue: { color: "#e0e0ff", fontSize: 14, fontWeight: "600", fontFamily: "monospace" },

  code: {
    fontFamily: "monospace", color: "#a0a0d0",
    backgroundColor: "#1e1e2e", borderRadius: 3,
  },

  input: {
    backgroundColor: "#1e1e2e", borderRadius: 10, padding: 12,
    color: "#e0e0ff", fontSize: 14, borderWidth: 1, borderColor: "#2a2a3a",
    marginBottom: 14, fontFamily: "monospace",
  },
  btnRow:   { flexDirection: "row", gap: 10 },
  btnSave:  { flex: 1, backgroundColor: "#6c63ff", borderRadius: 10, padding: 12, alignItems: "center" },
  btnTest:  { flex: 1, backgroundColor: "#2a2a3a", borderRadius: 10, padding: 12, alignItems: "center" },
  btnText:  { color: "#e0e0ff", fontWeight: "600", fontSize: 14 },

  infoCard: {
    backgroundColor: "#16161f", borderRadius: 14, padding: 16,
    borderWidth: 1, borderColor: "#2a2a3a",
  },
  infoTitle: { color: "#a0a0d0", fontWeight: "700", marginBottom: 10, fontSize: 14 },
  infoText:  { color: "#6a6a8a", fontSize: 13, lineHeight: 19, marginBottom: 10 },

  codeBlock: {
    backgroundColor: "#0d0d14", borderRadius: 8, padding: 12,
    marginBottom: 10, borderWidth: 1, borderColor: "#2a2a3a",
  },
  codeBlockText: { color: "#a0c0a0", fontFamily: "monospace", fontSize: 12, lineHeight: 18 },
});
