/**
 * Competitors Screen
 * List and manage all competitors
 */
import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    FlatList,
    TouchableOpacity,
    RefreshControl,
    TextInput,
} from 'react-native';
import { getCompetitors } from '../api/client';

export default function CompetitorsScreen({ navigation }) {
    const [competitors, setCompetitors] = useState([]);
    const [filtered, setFiltered] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');

    useEffect(() => {
        loadCompetitors();
    }, []);

    useEffect(() => {
        if (search) {
            setFiltered(competitors.filter(c =>
                c.name.toLowerCase().includes(search.toLowerCase())
            ));
        } else {
            setFiltered(competitors);
        }
    }, [search, competitors]);

    const loadCompetitors = async () => {
        try {
            const res = await getCompetitors();
            setCompetitors(res.data);
            setFiltered(res.data);
        } catch (error) {
            console.error('Error loading competitors:', error);
        } finally {
            setLoading(false);
        }
    };

    const renderCompetitor = ({ item }) => (
        <TouchableOpacity style={styles.card}>
            <View style={styles.cardHeader}>
                <Text style={styles.name}>{item.name}</Text>
                <View style={[styles.badge, styles[`badge${item.threat_level}`]]}>
                    <Text style={[styles.badgeText, styles[`badgeText${item.threat_level}`]]}>
                        {item.threat_level}
                    </Text>
                </View>
            </View>
            <Text style={styles.website}>{item.website}</Text>
            <View style={styles.details}>
                <View style={styles.detailItem}>
                    <Text style={styles.detailLabel}>Customers</Text>
                    <Text style={styles.detailValue}>{item.customer_count || 'Unknown'}</Text>
                </View>
                <View style={styles.detailItem}>
                    <Text style={styles.detailLabel}>Pricing</Text>
                    <Text style={styles.detailValue}>{item.base_price || 'N/A'}</Text>
                </View>
                <View style={styles.detailItem}>
                    <Text style={styles.detailLabel}>G2 Rating</Text>
                    <Text style={styles.detailValue}>{item.g2_rating || 'N/A'} ⭐</Text>
                </View>
            </View>
        </TouchableOpacity>
    );

    return (
        <View style={styles.container}>
            <TextInput
                style={styles.searchInput}
                placeholder="Search competitors..."
                value={search}
                onChangeText={setSearch}
            />
            <FlatList
                data={filtered}
                keyExtractor={(item) => item.id.toString()}
                renderItem={renderCompetitor}
                refreshControl={
                    <RefreshControl refreshing={loading} onRefresh={loadCompetitors} />
                }
                contentContainerStyle={styles.list}
            />
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#F8FAFC' },
    searchInput: {
        margin: 16,
        padding: 12,
        backgroundColor: '#FFF',
        borderRadius: 10,
        borderWidth: 1,
        borderColor: '#E2E8F0',
        fontSize: 16,
    },
    list: { padding: 16, paddingTop: 0 },
    card: {
        backgroundColor: '#FFF',
        borderRadius: 12,
        padding: 16,
        marginBottom: 12,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 2,
    },
    cardHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 4,
    },
    name: { fontSize: 18, fontWeight: '600', color: '#1A1A2E' },
    website: { fontSize: 13, color: '#2F5496', marginBottom: 12 },
    badge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
    badgeHigh: { backgroundColor: 'rgba(220, 53, 69, 0.1)' },
    badgeMedium: { backgroundColor: 'rgba(255, 193, 7, 0.1)' },
    badgeLow: { backgroundColor: 'rgba(40, 167, 69, 0.1)' },
    badgeText: { fontSize: 12, fontWeight: '600' },
    badgeTextHigh: { color: '#DC3545' },
    badgeTextMedium: { color: '#B8860B' },
    badgeTextLow: { color: '#28A745' },
    details: { flexDirection: 'row', justifyContent: 'space-between' },
    detailItem: { flex: 1 },
    detailLabel: { fontSize: 11, color: '#6C757D', textTransform: 'uppercase' },
    detailValue: { fontSize: 14, fontWeight: '500', color: '#1A1A2E', marginTop: 2 },
});
