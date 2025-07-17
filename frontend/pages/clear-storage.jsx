import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

export default function ClearStorage() {
  const router = useRouter();
  const [message, setMessage] = useState('Clearing browser storage...');
  
  useEffect(() => {
    try {
      // Clear localStorage
      localStorage.clear();
      
      // Clear sessionStorage
      sessionStorage.clear();
      
      setMessage('Storage cleared successfully! Redirecting to login page...');
      
      // Redirect to login page after a short delay
      setTimeout(() => {
        router.push('/login');
      }, 2000);
    } catch (error) {
      setMessage(`Error clearing storage: ${error.message}`);
    }
  }, [router]);
  
  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center', 
      minHeight: '100vh',
      padding: '20px',
      textAlign: 'center'
    }}>
      <h1 style={{ marginBottom: '20px' }}>Storage Cleanup</h1>
      <div style={{ 
        padding: '20px', 
        backgroundColor: '#e8f5e9', 
        borderRadius: '8px',
        maxWidth: '500px'
      }}>
        <p>{message}</p>
      </div>
      <button 
        onClick={() => router.push('/login')}
        style={{
          marginTop: '20px',
          padding: '10px 20px',
          backgroundColor: '#4CAF50',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        Go to Login Page
      </button>
    </div>
  );
}