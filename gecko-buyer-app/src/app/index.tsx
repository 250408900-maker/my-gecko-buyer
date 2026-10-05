import { useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

const API_URL = 'https://my-gecko-buyer-o2p9.onrender.com';

export default function HomeScreen() {
  const [ask, setAsk] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  async function checkPurchase() {
    if (!ask.trim()) {
      setError('Enter something you want to buy.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ask: ask.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Purchase check failed.');
      }

      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Could not connect to Gecko Buyer.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.gecko}>🦎</Text>

        <Text style={styles.title}>Gecko Buyer</Text>

        <Text style={styles.subtitle}>
          Safe AI-powered purchasing
        </Text>

        <View style={styles.card}>
          <Text style={styles.label}>
            What do you want to buy?
          </Text>

          <TextInput
            style={styles.input}
            placeholder="e.g. one espresso"
            placeholderTextColor="#777"
            multiline
            value={ask}
            onChangeText={setAsk}
          />

          <Pressable
            style={[
              styles.button,
              loading && styles.buttonDisabled,
            ]}
            onPress={checkPurchase}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#071109" />
            ) : (
              <Text style={styles.buttonText}>
                Check Purchase
              </Text>
            )}
          </Pressable>
        </View>

        {error ? (
          <View style={styles.errorCard}>
            <Text style={styles.errorTitle}>
              Purchase rejected
            </Text>

            <Text style={styles.errorText}>
              {error}
            </Text>
          </View>
        ) : null}

        {result ? (
          <View style={styles.resultCard}>
            <Text style={styles.resultTitle}>
              ✓ Purchase checked
            </Text>

            <Text style={styles.resultText}>
              Ask: {result.ask}
            </Text>

            <Text style={styles.resultText}>
              Status: {result.outcome?.kind ?? 'unknown'}
            </Text>

            <Text style={styles.resultText}>
              Step: {result.outcome?.step ?? 'unknown'}
            </Text>

            <Text style={styles.resultText}>
              Source: {result.source}
            </Text>
          </View>
        ) : null}

        <Text style={styles.footer}>
          Powered by Gecko Buyer 🦎
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#090b0a',
  },

  content: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: 24,
    paddingVertical: 30,
  },

  gecko: {
    fontSize: 70,
    textAlign: 'center',
    marginBottom: 12,
  },

  title: {
    color: '#ffffff',
    fontSize: 38,
    fontWeight: '800',
    textAlign: 'center',
  },

  subtitle: {
    color: '#9ca3af',
    fontSize: 16,
    textAlign: 'center',
    marginTop: 8,
    marginBottom: 40,
  },

  card: {
    backgroundColor: '#151816',
    borderWidth: 1,
    borderColor: '#292d2a',
    borderRadius: 22,
    padding: 20,
  },

  label: {
    color: '#ffffff',
    fontSize: 17,
    fontWeight: '600',
    marginBottom: 12,
  },

  input: {
    backgroundColor: '#0c0e0d',
    color: '#ffffff',
    minHeight: 110,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#303531',
    padding: 15,
    fontSize: 16,
    textAlignVertical: 'top',
  },

  button: {
    backgroundColor: '#5ee38c',
    paddingVertical: 16,
    borderRadius: 14,
    alignItems: 'center',
    marginTop: 16,
  },

  buttonDisabled: {
    opacity: 0.6,
  },

  buttonText: {
    color: '#071109',
    fontSize: 16,
    fontWeight: '800',
  },

  resultCard: {
    backgroundColor: '#102418',
    borderColor: '#5ee38c',
    borderWidth: 1,
    borderRadius: 18,
    padding: 18,
    marginTop: 20,
  },

  resultTitle: {
    color: '#5ee38c',
    fontSize: 18,
    fontWeight: '800',
    marginBottom: 10,
  },

  resultText: {
    color: '#ffffff',
    fontSize: 15,
    marginTop: 4,
  },

  errorCard: {
    backgroundColor: '#291414',
    borderColor: '#ff6b6b',
    borderWidth: 1,
    borderRadius: 18,
    padding: 18,
    marginTop: 20,
  },

  errorTitle: {
    color: '#ff7b7b',
    fontSize: 18,
    fontWeight: '800',
    marginBottom: 8,
  },

  errorText: {
    color: '#ffffff',
    fontSize: 14,
  },

  footer: {
    color: '#626862',
    textAlign: 'center',
    marginTop: 28,
    fontSize: 13,
  },
});