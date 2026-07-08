import { useQuery } from "@tanstack/react-query";
import { apiClient } from "./api-client";

export default function useAuth() {
  const { data: user, isLoading } = useQuery({
    queryKey: ["user"],
    queryFn: async () => {
      return (await apiClient.get("/auth/profile")).data?.user;
    },
  });

  return {
    user,
    isLoading,
  };
}

export const getLoginUrl = () => {
  return `${import.meta.env.VITE_API_HOST}/auth/login?returnTo=${window.location.origin}/`;
};

export const getSignupUrl = () => {
  return `${import.meta.env.VITE_API_HOST}/auth/login?screen_hint=signup&returnTo=${window.location.origin}/`;
};

export const getLogoutUrl = () => {
  return `${import.meta.env.VITE_API_HOST}/auth/logout?returnTo=${window.location.origin}/`;
};