import React from 'react';
import Head from 'next/head';
import SubscriptionDashboard from '../components/SubscriptionDashboard';
import ProtectedRoute from '../components/ProtectedRoute';

const SubscriptionPage = () => {
  return (
    <ProtectedRoute>
      <Head>
        <title>Subscription Dashboard - ApplyAI</title>
        <meta name="description" content="Manage your ApplyAI subscription, billing, and account settings" />
      </Head>
      <SubscriptionDashboard />
    </ProtectedRoute>
  );
};

export default SubscriptionPage;