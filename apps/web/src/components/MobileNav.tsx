import { BookOpen, Brain, MessageSquare, Search, Settings } from "lucide-react";
import { NavLink } from "react-router-dom";

export default function MobileNav() {
  return (
    <nav className="mobile-nav">
      <NavLink to="/"><MessageSquare size={19} /> Talk</NavLink>
      <NavLink to="/sessions"><Search size={19} /> Sessions</NavLink>
      <NavLink to="/atlas"><Brain size={19} /> Atlas</NavLink>
      <NavLink to="/sources"><BookOpen size={19} /> Sources</NavLink>
      <NavLink to="/settings"><Settings size={19} /> Settings</NavLink>
    </nav>
  );
}

