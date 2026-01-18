/**
 * Alerts Screen
 * View recent changes and manage alerts
 */
import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    FlatList,
    RefreshControl,
    TouchableOpacity,
} from 'react-native';
import { getChanges } from '../api/client';

export default function AlertsScreen() {
    const [changes, setChanges] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');

    useEffect(() => {
        loadChanges();
    }, []);

    const loadChanges = async () => {
        try {
            const res = await getChanges(30);
            setChanges(res.data.changes || []);
        } catch (error) {
            console.error('Error loading changes:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredChanges = filter === 'all'
        ? changes
        : changes.filter(c => c.severity === filter);

    const renderChange = ({ item }) => (
        <View style={styles.changeCard}>
            <View style={[styles.icon, styles[`icon${item.severity}`]]}>
                <Text style={styles.iconText}>
                    {item.severity === 'High' ? '🔴' : item.severity === 'Medium' ? '🟡' : '🔵'}
                </Text>
            </View>
            <View style={styles.content}>
                <Text style={styles.title}>{item.competitor_name}</Text>
                <Text style={styles.type}>{item.change_type}</Text>
                <Text style={styles.details}>
                    {item.previous_value ? `"${item.previous_value}" → ` : ''}"
                    {item.new_value}"
                </Text>
                <Text style={styles.date}>{new Date(item.detected_at).toLocaleDateString()}</Text>
            </View>
        </View>
    );

    return (
        <View style={styles.container}>
            <View style={styles.filters}>
                {['all', 'High', 'Medium', 'Low'].map((f) => (
                    <TouchableOpacity
                        key={f}
                        style={[styles.filterBtn, filter === f && styles.filterActive]}
                        onPress={() => setFilter(f)}
                    >
                        <Text style={[styles.filterText, filter === f && styles.filterTextActive]}>
                            {f === 'all' ? 'All' : f}
                        </Text>
                    </TouchableOpacity>
                ))}
            </View>
            <FlatList
                data={filteredChanges}
                keyExtractor={(_, index) => index.toString()}
                renderItem={renderChange}
                refreshControl={
                    <RefreshControl refreshing={loading} onRefresh={loadChanges} />
                }
                contentContainerStyle={styles.list}
                ListEmptyComponent={
                    <Text style={styles.empty}>No changes found</Text>
                }
            />
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#F8FAFC' },
    filters: {
        flexDirection: 'row',
        padding: 16,
        gap: 8,
    },
    filterBtn: {
        paddingHorizontal: 16,
        paddingVertical: 8,
        borderRadius: 20,
        backgroundColor: '#E8EEF4',
    },
    filterActive: { backgroundColor: '#2F5496' },
    filterText: { color: '#6C757D', fontWeight: '500' },
    filterTextActive: { color: '#FFF' },
    list: { padding: 16, paddingTop: 0 },
    changeCard: {
        flexDirection: 'row',
        backgroundColor: '#FFF',
        borderRadius: 12,
        padding: 12,
        marginBottom: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.08,
        shadowRadius: 3,
        elevation: 1,
    },
    icon: {
        width: 44,
        height: 44,
        borderRadius: 22,
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 12,
    },
    iconHigh: { backgroundColor: 'rgba(220, 53, 69, 0.1)' },
    iconMedium: { backgroundColor: 'rgba(255, 193, 7, 0.1)' },
    iconLow: { backgroundColor: 'rgba(40, 167, 69, 0.1)' },
    iconText: { fontSize: 20 },
    content: { flex: 1 },
    title: { fontSize: 16, fontWeight: '600', color: '#1A1A2E' },
    type: { fontSize: 14, color: '#2F5496', marginTop: 2 },
    details: { fontSize: 13, color: '#6C757D', marginTop: 4 },
    date: { fontSize: 12, color: '#999', marginTop: 4 },
    empty: { textAlign: 'center', color: '#6C757D', marginTop: 40, fontStyle: 'italic' },
});
