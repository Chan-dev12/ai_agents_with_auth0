import { useState } from "react";
import useAuth, { getLoginUrl, getLogoutUrl } from "@/lib/use-auth";
import { apiClient } from "@/lib/api-client";

type EndpointResult = {
  status: number | null;
  data: unknown;
  error: string | null;
};

const ENDPOINTS = [
  { label: "All Salaries (Admin only)", path: "/salary/all" },
  { label: "Team Salaries (Admin/Manager)", path: "/salary/team" },
  { label: "My Info (Any logged-in user)", path: "/salary/me" },
];

export default function RBACTest() {
  const { user, isLoading } = useAuth();
  const [results, setResults] = useState<Record<string, EndpointResult>>({});

  const testEndpoint = async (path: string) => {
    try {
      const res = await apiClient.get(path);
      setResults((prev) => ({
        ...prev,
        [path]: { status: res.status, data: res.data, error: null },
      }));
    } catch (err: any) {
      setResults((prev) => ({
        ...prev,
        [path]: {
          status: err?.response?.status ?? null,
          data: err?.response?.data ?? null,
          error: err?.message ?? "Unknown error",
        },
      }));
    }
  };

  if (isLoading) return <div>Loading...</div>;

  if (!user) {
    return (
      <div className="p-4">
        <p>You are not logged in.</p>
        <a href={getLoginUrl()} className="text-blue-600 underline">
          Log in
        </a>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      <div className="border-b pb-2">
        <p><strong>Logged in as:</strong> {user.email}</p>
        <p><strong>Roles:</strong> {JSON.stringify(user["https://yourapp.com/roles"])}</p>
        <a href={getLogoutUrl()} className="text-red-600 underline">
          Log out
        </a>
      </div>

      <div className="space-y-3">
        {ENDPOINTS.map(({ label, path }) => (
          <div key={path} className="border p-3 rounded">
            <div className="flex justify-between items-center">
              <span>{label}</span>
              <button
                onClick={() => testEndpoint(path)}
                className="bg-blue-600 text-white px-3 py-1 rounded"
              >
                Test
              </button>
            </div>
            {results[path] && (
              <pre className="text-xs mt-2 bg-gray-100 p-2 rounded overflow-x-auto">
                Status: {results[path].status}
                {"\n"}
                {JSON.stringify(results[path].data, null, 2)}
              </pre>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}