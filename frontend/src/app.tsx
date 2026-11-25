import { Navigate, BrowserRouter, Route, Routes } from "react-router-dom";

import { ProjectLayout } from "@/components/project-layout";
import { ProtectedRoute } from "@/components/protected-route";
import { AuthProvider } from "@/contexts/auth-context";
import { ApprovalsPage } from "@/pages/approvals-page";
import { AuditPage } from "@/pages/audit-page";
import { CreateProjectPage } from "@/pages/create-project-page";
import { DashboardPage } from "@/pages/dashboard-page";
import { DocumentsPage } from "@/pages/documents-page";
import { InterviewPage } from "@/pages/interview-page";
import { LandingPage } from "@/pages/landing-page";
import { KnowledgePage } from "@/pages/knowledge-page";
import { LegalPage } from "@/pages/legal-page";
import { LoginPage } from "@/pages/login-page";
import { NotFoundPage } from "@/pages/not-found-page";
import { ProjectOverviewPage } from "@/pages/project-overview-page";
import { RequirementsPage } from "@/pages/requirements-page";
import { RegisterPage } from "@/pages/register-page";
import { SecurityRiskPage } from "@/pages/security-risk-page";
import { SDLCPage } from "@/pages/sdlc-page";

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<LandingPage />} path="/" />
          <Route element={<LoginPage />} path="/login" />
          <Route element={<RegisterPage />} path="/register" />
          <Route element={<LegalPage title="Privacy" />} path="/privacy" />
          <Route element={<LegalPage title="Terms" />} path="/terms" />
          <Route element={<ProtectedRoute />}>
            <Route element={<DashboardPage />} path="/dashboard" />
            <Route element={<CreateProjectPage />} path="/projects/new" />
            <Route element={<ProjectLayout />} path="/projects/:projectId">
              <Route element={<Navigate replace to="overview" />} index />
              <Route element={<ProjectOverviewPage />} path="overview" />
              <Route element={<InterviewPage />} path="interview" />
              <Route element={<RequirementsPage />} path="requirements" />
              <Route element={<KnowledgePage />} path="compliance" />
              <Route element={<SecurityRiskPage view="security" />} path="security" />
              <Route element={<SecurityRiskPage view="risks" />} path="risks" />
              <Route element={<SDLCPage />} path="sdlc" />
              <Route element={<ApprovalsPage />} path="approvals" />
              <Route element={<DocumentsPage />} path="documents" />
              <Route element={<AuditPage />} path="audit" />
            </Route>
          </Route>
          <Route element={<NotFoundPage />} path="*" />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
