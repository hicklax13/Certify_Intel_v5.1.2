/**
 * Dashboard Screen
 * Main overview of competitive intelligence
 */
import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    RefreshControl,
    TouchableOpacity,
    ActivityIndicator,
} from 'react-native';
import { getDashboardStats, getCompetitors, getChanges } from '../api/client';

export default function DashboardScreen({ navigation }) {
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [stats, setStats] = useState({});
    const [topThreats, setTopThreats] = useState([]);
    const [recentChanges, setRecentChanges] = useState([]);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);

            const [statsRes, compsRes, changesRes] = await Promise.all([
                getDashboardStats(),
                getCompetitors(),
                getChanges(7),
            ]);

            setStats(statsRes.data);
            setTopThreats(compsRes.data.filter(c => c.threat_level === 'High').slice(0, 5));
            setRecentChanges(changesRes.data.changes?.slice(0, 5) || []);
        } catch (error) {
            console.error('Error loading dashboard:', error);
        } finally {
            setLoading(false);
        }
    };

    const onRefresh = async () => {
        setRefreshing(true);
        await loadData();
        setRefreshing(false);
    };

    if (loading) {
        return (
            <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#2F5496" />
                <Text style={styles.loadingText}>Loading dashboard...</Text>
            </View>
        );
    }

    return (
        <ScrollView
            style={styles.container}
            refreshControl={
                <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
            }
        >
            {/* Stats Cards */}
            <View style={styles.statsGrid}>
                <StatCard
                    icon="🏢"
                    value={stats.total_competitors || 0}
                    label="Total"
                    color="#2F5496"
                />
                <StatCard
                    icon="🔴"
                    value={stats.high_threat || 0}
                    label="High Threat"
                    color="#DC3545"
                />
                <StatCard
                    icon="🟡"
                    value={stats.medium_threat || 0}
                    label="Medium"
                    color="#FFC107"
                />
                <StatCard
                    icon="🟢"
                    value={stats.low_threat || 0}
                    label="Low"
                    color="#28A745"
                />
            </View>

            {/* Top Threats */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Top Threats</Text>
                {topThreats.map((comp) => (
                    <TouchableOpacity
                        key={comp.id}
                        style={styles.threatCard}
                        onPress={() => navigation.navigate('Competitors', {
                            screen: 'CompetitorDetail',
                            params: { competitor: comp }
                        })}
                    >
                        <View style={styles.threatHeader}>
                            <Text style={styles.threatName}>{comp.name}</Text>
                            <View style={[styles.badge, styles.badgeHigh]}>
                                <Text style={styles.badgeText}>High</Text>
                            </View>
                        </View>
                        <Text style={styles.threatDetails}>
                            {comp.customer_count || 'Unknown'} customers • {comp.base_price || 'N/A'}
                        </Text>
                    </TouchableOpacity>
                ))}
            </View>

            {/* Recent Changes */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Recent Changes</Text>
                {recentChanges.length > 0 ? (
                    recentChanges.map((change, index) => (
                        <View key={index} style={styles.changeCard}>
                            <View style={styles.changeIcon}>
                                <Text style={styles.changeEmoji}>
                                    {change.severity === 'High' ? '🔴' : change.severity === 'Medium' ? '🟡' : '🔵'}
                                </Text>
                            </View>
                            <View style={styles.changeContent}>
                                <Text style={styles.changeTitle}>
                                    {change.competitor_name}: {change.change_type}
                                </Text>
                                <Text style={styles.changeDetails}>
                                    {change.previous_value ? `"${change.previous_value}" → ` : ''}
                                    "{change.new_value}"
                                </Text>
                            </View>
                        </View>
                    ))
                ) : (
                    <Text style={styles.emptyText}>No recent changes</Text>
                )}
            </View>
        </ScrollView>
    );
}

// Stat Card Component
function StatCard({ icon, value, label, color }) {
    return (
        <View style={[styles.statCard, { borderLeftColor: color }]}>
            <Text style={styles.statIcon}>{icon}</Text>
            <Text style={styles.statValue}>{value}</Text>
            <Text style={styles.statLabel}>{label}</Text>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F8FAFC',
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    loadingText: {
        marginTop: 10,
        color: '#6C757D',
    },
    statsGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        padding: 16,
        gap: 12,
    },
    statCard: {
        flex: 1,
        minWidth: '45%',
        backgroundColor: '#FFFFFF',
        padding: 16,
        borderRadius: 12,
        borderLeftWidth: 4,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 2,
    },
    statIcon: {
        fontSize: 24,
        marginBottom: 8,
    },
    statValue: {
        fontSize: 28,
        fontWeight: '700',
        color: '#1A1A2E',
    },
    statLabel: {
        fontSize: 12,
        color: '#6C757D',
        marginTop: 4,
    },
    section: {
        padding: 16,
        paddingTop: 0,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: '600',
        color: '#1A1A2E',
        marginBottom: 12,
    },
    threatCard: {
        backgroundColor: '#FFFFFF',
        padding: 16,
        borderRadius: 12,
        marginBottom: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.08,
        shadowRadius: 3,
        elevation: 1,
    },
    threatHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 8,
    },
    threatName: {
        fontSize: 16,
        fontWeight: '600',
        color: '#1A1A2E',
    },
    badge: {
        paddingHorizontal: 10,
        paddingVertical: 4,
        borderRadius: 12,
    },
    badgeHigh: {
        backgroundColor: 'rgba(220, 53, 69, 0.1)',
    },
    badgeText: {
        fontSize: 12,
        fontWeight: '600',
        color: '#DC3545',
    },
    threatDetails: {
        fontSize: 14,
        color: '#6C757D',
    },
    changeCard: {
        flexDirection: 'row',
        backgroundColor: '#FFFFFF',
        padding: 12,
        borderRadius: 12,
        marginBottom: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.08,
        shadowRadius: 3,
        elevation: 1,
    },
    changeIcon: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: '#F8FAFC',
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 12,
    },
    changeEmoji: {
        fontSize: 18,
    },
    changeContent: {
        flex: 1,
    },
    changeTitle: {
        fontSize: 14,
        fontWeight: '600',
        color: '#1A1A2E',
        marginBottom: 4,
    },
    changeDetails: {
        fontSize: 13,
        color: '#6C757D',
    },
    emptyText: {
        color: '#6C757D',
        fontStyle: 'italic',
        textAlign: 'center',
        padding: 20,
    },
});
