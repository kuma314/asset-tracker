import { Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import AllocationDashboard from "./pages/AllocationDashboard";
import AssetInputPage from "./pages/AssetInputPage";
import ImportExportPage from "./pages/ImportExportPage";
import SimulationPage from "./pages/SimulationPage";
import TrendPage from "./pages/TrendPage";

const App = () => {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<AssetInputPage />} />
        <Route path="/allocation" element={<AllocationDashboard />} />
        <Route path="/trend" element={<TrendPage />} />
        <Route path="/simulation" element={<SimulationPage />} />
        <Route path="/import-export" element={<ImportExportPage />} />
      </Routes>
    </Layout>
  );
};

export default App;
