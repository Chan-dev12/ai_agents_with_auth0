import { Routes, Route } from "react-router";
import { Github } from "lucide-react";
import { Button } from "@/components/ui/button";
import UserButton from "@/components/auth0/user-button";
import { ActiveLink } from "@/components/navbar";

import ChatPage from "@/pages/ChatPage";
import useAuth, { getLogoutUrl, getLoginUrl, getSignupUrl } from "@/lib/use-auth";
import ClosePage from "@/pages/ClosePage";
import DocumentsPage from "@/pages/DocumentsPage";

export default function Layout() {
  const { user, isLoading } = useAuth();

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="bg-secondary grid grid-rows-[auto_1fr] h-[100dvh]">
        <div className="grid grid-cols-[1fr_auto] gap-2 p-4 bg-black/25">
          <div className="flex gap-4 flex-col md:flex-row md:items-center">
            <a
              href="https://a0.to/ai-event"
              rel="noopener noreferrer"
              target="_blank"
              className="flex items-center gap-2 px-4"
            >
              <img
                src="/images/auth0-logo.svg"
                alt="Auth0 AI Logo"
                className="h-8"
                width={143}
                height={32}
              />
            </a>
            <span className="text-white text-2xl">Assistant0</span>
          </div>
        </div>
        <div className="gradient-up bg-gradient-to-b from-white/10 to-white/0 relative grid border-input border-b-0 flex items-center justify-center">
          <div className="text-white text-lg">Loading...</div>
        </div>
      </div>
    );
  }

  // If not authenticated, show login/signup page
  if (!user) {
    return (
      <div className="bg-secondary grid grid-rows-[auto_1fr] h-[100dvh]">
        <div className="grid grid-cols-[1fr_auto] gap-2 p-4 bg-black/25">
          <div className="flex gap-4 flex-col md:flex-row md:items-center">
            <a
              href="https://a0.to/ai-event"
              rel="noopener noreferrer"
              target="_blank"
              className="flex items-center gap-2 px-4"
            >
              <img
                src="/images/auth0-logo.svg"
                alt="Auth0 AI Logo"
                className="h-8"
                width={143}
                height={32}
              />
            </a>
            <span className="text-white text-2xl">Assistant0</span>
          </div>
          <Button asChild variant="header" size="default">
            <a
              href="https://github.com/auth0-samples/auth0-assistant0-python"
              target="_blank"
            >
              <Github className="size-3" />
              <span>Open in GitHub</span>
            </a>
          </Button>
        </div>
        <div className="gradient-up bg-gradient-to-b from-white/10 to-white/0 relative grid border-input border-b-0 flex items-center justify-center">
          <div className="flex flex-col gap-6 items-center justify-center">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-white mb-2">Welcome to Assistant0</h1>
              <p className="text-white/80 text-lg">Your personal AI assistant powered by LangGraph</p>
            </div>
            <div className="flex gap-4">
              <Button asChild size="lg" className="px-8">
                <a href={getLoginUrl()}>
                  Login
                </a>
              </Button>
              <Button asChild size="lg" variant="outline" className="px-8">
                <a href={getSignupUrl()}>
                  Sign Up
                </a>
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // User is authenticated - show the app
  return (
    <div className="bg-secondary grid grid-rows-[auto_1fr] h-[100dvh]">
      <div className="grid grid-cols-[1fr_auto] gap-2 p-4 bg-black/25">
        <div className="flex gap-4 flex-col md:flex-row md:items-center">
          <a
            href="https://a0.to/ai-event"
            rel="noopener noreferrer"
            target="_blank"
            className="flex items-center gap-2 px-4"
          >
            <img
              src="/images/auth0-logo.svg"
              alt="Auth0 AI Logo"
              className="h-8"
              width={143}
              height={32}
            />
          </a>
          <span className="text-white text-2xl">Assistant0</span>
          <nav className="flex gap-1 flex-col md:flex-row">
            <ActiveLink href="/">Chat</ActiveLink>
            <ActiveLink href="/documents">Documents</ActiveLink>
          </nav>
        </div>
        <div className="flex justify-center">
          {user && (
            <div className="flex items-center gap-2 px-4 text-white">
              <UserButton user={user} logoutUrl={getLogoutUrl()} />
            </div>
          )}
          <Button asChild variant="header" size="default">
            <a
              href="https://github.com/auth0-samples/auth0-assistant0-python"
              target="_blank"
            >
              <Github className="size-3" />
              <span>Open in GitHub</span>
            </a>
          </Button>
        </div>
      </div>
      <div className="gradient-up bg-gradient-to-b from-white/10 to-white/0 relative grid border-input border-b-0">
        <div className="absolute inset-0">
          <Routes>
            <Route path="/" element={<ChatPage />} />
            <Route path="/close" element={<ClosePage />} />
            <Route path="/documents" element={<DocumentsPage />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}
