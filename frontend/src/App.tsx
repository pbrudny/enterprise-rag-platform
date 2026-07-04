import { Route, Routes } from "react-router-dom";
import { NavBar } from "./components/NavBar";
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
      </Routes>
    </div>
  );
}

export default App;
