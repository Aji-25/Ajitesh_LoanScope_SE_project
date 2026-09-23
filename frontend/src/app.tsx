import { Navigate, BrowserRouter, Route, Routes } from "react-router-dom";

import { ProjectLayout } from "@/components/project-layout";
import { ProtectedRoute } from "@/components/protected-route";
import { AuthProvider } from "@/contexts/auth-context";
import { ApprovalsPage } from "@/pages/approvals-page";
import { CreateProjectPage } from "@/pages/create-project-page";
import { DashboardPage } from "@/pages/dashboard-page";
import { InterviewPage } from "@/pages/interview-page";
import { LandingPage } from "@/pages/landing-page";
import { LegalPage } from "@/pages/legal-page";
import { LoginPage } from "@/pages/login-page";
import { NotFoundPage } from "@/pages/not-found-page";
import { ProjectOverviewPage } from "@/pages/project-overview-page";
import { ProjectStagePage } from "@/pages/project-stage-page";
import { RequirementsPage } from "@/pages/requirements-page";

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<LandingPage />} path="/" />
          <Route element={<LoginPage />} path="/login" />
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
              <Route element={<ProjectStagePage description="Map approved requirements to retrieved regulatory and policy evidence." eyebrow="Evidence mapping" title="Compliance" />} path="compliance" />
              <Route element={<ProjectStagePage description="Review structured security and privacy findings linked to project requirements." eyebrow="Security review" title="Security" />} path="security" />
              <Route element={<ProjectStagePage description="Track business, technical, security, and compliance risks with clear mitigations." eyebrow="Risk management" title="Risk register" />} path="risks" />
              <Route element={<ProjectStagePage description="Compare deterministic score breakdowns before approving a delivery approach." eyebrow="Delivery planning" title="SDLC recommendation" />} path="sdlc" />
              <Route element={<ApprovalsPage />} path="approvals" />
              <Route element={<ProjectStagePage description="View generated software engineering artefacts built from approved project data." eyebrow="Project artefacts" title="Documents" />} path="documents" />
              <Route element={<ProjectStagePage description="Inspect significant human and system actions across the project lifecycle." eyebrow="Traceability" title="Audit trail" />} path="audit" />
            </Route>
          </Route>
          <Route element={<NotFoundPage />} path="*" />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
