import AsyncStorage from '@react-native-async-storage/async-storage';

const SERVER_URL_KEY = 'cornerst_server_url';
const DEFAULT_URL = 'http://192.168.80.23:8000'; // Tu IP actual

export async function getServerUrl(): Promise<string> {
  try {
    const saved = await AsyncStorage.getItem(SERVER_URL_KEY);
    if (saved && saved.trim().length > 0) {
      return saved.trim().replace(/\/$/, '');
    }
  } catch (e) {
    // ignorar
  }
  return DEFAULT_URL;
}

export async function setServerUrl(url: string): Promise<void> {
  const cleanUrl = url.trim().replace(/\/$/, '');
  await AsyncStorage.setItem(SERVER_URL_KEY, cleanUrl);
}
