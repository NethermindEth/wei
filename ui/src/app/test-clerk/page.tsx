"use client";

import { useAuth, useUser } from "@clerk/nextjs";
import { useState } from "react";

export default function TestClerkPage() {
  const { getToken } = useAuth();
  const { user, isLoaded } = useUser();
  const [apiResponse, setApiResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testBackendAPI = async () => {
    setLoading(true);
    setError(null);
    setApiResponse(null);

    try {
      // Get the JWT token
      const token = await getToken();
      
      if (!token) {
        throw new Error("No JWT token available");
      }

      // Call your backend API
      const response = await fetch("http://localhost:3001/user/me", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "x-api-key": "test-key-123", // Use your actual API key
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`API call failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setApiResponse(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isLoaded) {
    return <div className="p-8">Loading...</div>;
  }

  if (!user) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Clerk Integration Test</h1>
        <p>Please sign in to test the integration.</p>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-white">Clerk Integration Test</h1>
      
      {/* Frontend User Info */}
      <div className="bg-gray-800 p-6 rounded-lg mb-6">
        <h2 className="text-xl font-semibold mb-4 text-white">Frontend User Info (from Clerk)</h2>
        <div className="space-y-2 text-gray-300">
          <p><strong>ID:</strong> {user.id}</p>
          <p><strong>Email:</strong> {user.primaryEmailAddress?.emailAddress}</p>
          <p><strong>Name:</strong> {user.firstName} {user.lastName}</p>
          <p><strong>Username:</strong> {user.username}</p>
          <p><strong>Email Verified:</strong> {user.primaryEmailAddress?.verification.status}</p>
          <p><strong>Created:</strong> {user.createdAt?.toISOString()}</p>
        </div>
      </div>

      {/* Test Backend API */}
      <div className="bg-gray-800 p-6 rounded-lg mb-6">
        <h2 className="text-xl font-semibold mb-4 text-white">Backend API Test</h2>
        <button
          onClick={testBackendAPI}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg disabled:opacity-50"
        >
          {loading ? "Testing..." : "Test Backend API"}
        </button>
      </div>

      {/* API Response */}
      {error && (
        <div className="bg-red-900 border border-red-600 p-4 rounded-lg mb-6">
          <h3 className="text-lg font-semibold text-red-200 mb-2">Error</h3>
          <p className="text-red-300">{error}</p>
        </div>
      )}

      {apiResponse && (
        <div className="bg-green-900 border border-green-600 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-green-200 mb-2">Backend Response</h3>
          <pre className="text-green-300 text-sm overflow-auto">
            {JSON.stringify(apiResponse, null, 2)}
          </pre>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-gray-800 p-6 rounded-lg mt-6">
        <h3 className="text-lg font-semibold text-white mb-2">Testing Instructions</h3>
        <ol className="list-decimal list-inside space-y-2 text-gray-300">
          <li>Make sure your backend is running: <code>cd crates/agent && cargo run</code></li>
          <li>Ensure your environment variables are set correctly</li>
          <li>Click "Test Backend API" to verify the integration</li>
          <li>Check that the response matches your frontend user data</li>
        </ol>
      </div>
    </div>
  );
}
