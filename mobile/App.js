/**
 * Certify Intel Mobile App
 * React Native / Expo entry point
 */
import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { SafeAreaProvider } from 'react-native-safe-area-context';

// Import screens
import DashboardScreen from './src/screens/DashboardScreen';
import CompetitorsScreen from './src/screens/CompetitorsScreen';
import AlertsScreen from './src/screens/AlertsScreen';
import SettingsScreen from './src/screens/SettingsScreen';

const Tab = createBottomTabNavigator();

export default function App() {
    return (
        <SafeAreaProvider>
            <NavigationContainer>
                <Tab.Navigator
                    screenOptions={{
                        tabBarActiveTintColor: '#2F5496',
                        tabBarInactiveTintColor: '#6C757D',
                        tabBarStyle: {
                            paddingBottom: 5,
                            paddingTop: 5,
                            height: 60,
                        },
                        headerStyle: {
                            backgroundColor: '#2F5496',
                        },
                        headerTintColor: '#fff',
                        headerTitleStyle: {
                            fontWeight: 'bold',
                        },
                    }}
                >
                    <Tab.Screen
                        name="Dashboard"
                        component={DashboardScreen}
                        options={{
                            tabBarIcon: ({ color, size }) => (
                                <TabIcon name="dashboard" color={color} size={size} />
                            ),
                        }}
                    />
                    <Tab.Screen
                        name="Competitors"
                        component={CompetitorsScreen}
                        options={{
                            tabBarIcon: ({ color, size }) => (
                                <TabIcon name="competitors" color={color} size={size} />
                            ),
                        }}
                    />
                    <Tab.Screen
                        name="Alerts"
                        component={AlertsScreen}
                        options={{
                            tabBarIcon: ({ color, size }) => (
                                <TabIcon name="alerts" color={color} size={size} />
                            ),
                        }}
                    />
                    <Tab.Screen
                        name="Settings"
                        component={SettingsScreen}
                        options={{
                            tabBarIcon: ({ color, size }) => (
                                <TabIcon name="settings" color={color} size={size} />
                            ),
                        }}
                    />
                </Tab.Navigator>
            </NavigationContainer>
            <StatusBar style="light" />
        </SafeAreaProvider>
    );
}

// Simple tab icon component using emoji (replace with proper icons in production)
function TabIcon({ name, color, size }) {
    const icons = {
        dashboard: '📊',
        competitors: '🏢',
        alerts: '🔔',
        settings: '⚙️',
    };

    return (
        <React.Text style={{ fontSize: size * 0.9 }}>
            {icons[name] || '•'}
        </React.Text>
    );
}
