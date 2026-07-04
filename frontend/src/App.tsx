import { Route, Routes } from "react-router-dom";
import { NavBar } from "./components/NavBar";
import { ArchitecturePage } from "./pages/ArchitecturePage";
import { AskPage } from "./pages/AskPage";
import { AuditLogPage } from "./pages/AuditLogPage";
import { UserPickerPage } from "./pages/UserPickerPage";

function App() {
  return (
    <div className="min-h-screen bg-slate-50">
      <NavBar />
      <Routes>
        <Route path="/" element={<UserPickerPage />} />
        <Route path="/ask" element={<AskPage />} />
        <Route path="/audit" element={<AuditLogPage />} />
        <Route path="/architecture" element={<ArchitecturePage />} />
      </Routes>
    </div>
  );
}

export default App;
