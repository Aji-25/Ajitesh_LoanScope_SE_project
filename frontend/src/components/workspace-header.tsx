import { SignOut, UserCircle } from "@phosphor-icons/react";
import { Link, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/auth-store";

export function WorkspaceHeader() {
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  function signOut() {
    logout();
    navigate("/login");
  }

  return (
    <header className="border-b border-white/10 bg-[#181818] px-4 py-3 sm:px-6">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
        <Link className="flex items-center gap-2 rounded-full font-semibold" to="/dashboard">
          <span className="grid size-8 place-items-center rounded-full bg-[#d9ff76] text-sm font-bold text-[#131209]">
            C
          </span>
          Clarifi
        </Link>
        <div className="flex items-center gap-3">
          <div className="hidden text-right sm:block">
            <p className="text-sm font-semibold">{user?.full_name}</p>
            <p className="text-xs text-[#8f8f8f]">{user?.role}</p>
          </div>
          <UserCircle aria-hidden="true" className="text-[#b6b6b6]" size={28} />
          <Button aria-label="Sign out" onClick={signOut} size="small" variant="ghost">
            <SignOut aria-hidden="true" size={18} />
            <span className="hidden sm:inline">Sign out</span>
          </Button>
        </div>
      </div>
    </header>
  );
}
