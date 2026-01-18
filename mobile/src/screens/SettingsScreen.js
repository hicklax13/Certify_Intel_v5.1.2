/**
 * Settings Screen
 * App configuration and actions
 */
import React from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    TouchableOpacity,
    Linking,
    Alert,
} from 'react-native';
import { triggerScrapeAll, sendDailyDigest, sendWeeklySummary, exportExcel } from '../api/client';

export default function SettingsScreen() {
    const handleScrapeAll = async () => {
        try {
            await triggerScrapeAll();
            Alert.alert('Success', 'Data refresh started in background');
        } catch (error) {
            Alert.alert('Error', 'Failed to start refresh');
        }
    };

    const handleSendDigest = async () => {
        try {
            await sendDailyDigest();
            Alert.alert('Success', 'Daily digest sent');
        } catch (error) {
            Alert.alert('Error', 'Failed to send digest');
        }
    };

    const handleExport = () => {
        Linking.openURL(exportExcel());
    };

    return (
        <ScrollView style={styles.container}>
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Data Management</Text>
                <TouchableOpacity style={styles.item} onPress={handleScrapeAll}>
                    <Text style={styles.itemIcon}>🔄</Text>
                    <View style={styles.itemContent}>
                        <Text style={styles.itemTitle}>Refresh All Data</Text>
                        <Text style={styles.itemDesc}>Scrape and update all competitors</Text>
                    </View>
                </TouchableOpacity>
                <TouchableOpacity style={styles.item} onPress={handleExport}>
                    <Text style={styles.itemIcon}>📥</Text>
                    <View style={styles.itemContent}>
                        <Text style={styles.itemTitle}>Export to Excel</Text>
                        <Text style={styles.itemDesc}>Download full competitor data</Text>
                    </View>
                </TouchableOpacity>
            </View>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Notifications</Text>
                <TouchableOpacity style={styles.item} onPress={handleSendDigest}>
                    <Text style={styles.itemIcon}>📧</Text>
                    <View style={styles.itemContent}>
                        <Text style={styles.itemTitle}>Send Daily Digest</Text>
                        <Text style={styles.itemDesc}>Email summary of recent changes</Text>
                    </View>
                </TouchableOpacity>
                <TouchableOpacity style={styles.item} onPress={() => sendWeeklySummary()}>
                    <Text style={styles.itemIcon}>📊</Text>
                    <View style={styles.itemContent}>
                        <Text style={styles.itemTitle}>Send Weekly Summary</Text>
                        <Text style={styles.itemDesc}>Full weekly intelligence report</Text>
                    </View>
                </TouchableOpacity>
            </View>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Schedule</Text>
                <View style={styles.scheduleItem}>
                    <Text style={styles.scheduleLabel}>Weekly Full Refresh</Text>
                    <Text style={styles.scheduleValue}>Sundays 2:00 AM</Text>
                </View>
                <View style={styles.scheduleItem}>
                    <Text style={styles.scheduleLabel}>Daily High-Priority</Text>
                    <Text style={styles.scheduleValue}>Daily 6:00 AM</Text>
                </View>
            </View>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>About</Text>
                <Text style={styles.aboutText}>Certify Intel v1.0.0</Text>
                <Text style={styles.aboutText}>Competitive Intelligence Platform</Text>
            </View>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#F8FAFC' },
    section: {
        backgroundColor: '#FFF',
        marginTop: 24,
        marginHorizontal: 16,
        borderRadius: 12,
        padding: 16,
    },
    sectionTitle: {
        fontSize: 14,
        fontWeight: '600',
        color: '#6C757D',
        textTransform: 'uppercase',
        marginBottom: 12,
    },
    item: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#E8EEF4',
    },
    itemIcon: { fontSize: 24, marginRight: 12 },
    itemContent: { flex: 1 },
    itemTitle: { fontSize: 16, fontWeight: '500', color: '#1A1A2E' },
    itemDesc: { fontSize: 13, color: '#6C757D', marginTop: 2 },
    scheduleItem: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        paddingVertical: 10,
        borderBottomWidth: 1,
        borderBottomColor: '#E8EEF4',
    },
    scheduleLabel: { fontSize: 15, color: '#1A1A2E' },
    scheduleValue: { fontSize: 15, color: '#2F5496', fontWeight: '500' },
    aboutText: { fontSize: 14, color: '#6C757D', marginBottom: 4 },
});
