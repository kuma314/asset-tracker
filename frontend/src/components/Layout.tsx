import { NavLink } from "react-router-dom";

import Disclaimer from "./Disclaimer";

const Layout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Asset Tracker</h1>
        <nav>
          <NavLink to="/">資産入力</NavLink>
          <NavLink to="/allocation">配分ダッシュボード</NavLink>
          <NavLink to="/trend">推移</NavLink>
          <NavLink to="/simulation">シミュレーション</NavLink>
          <NavLink to="/import-export">インポート/エクスポート</NavLink>
        </nav>
      </header>
      <main className="app-main">{children}</main>
      <Disclaimer />
    </div>
  );
};

export default Layout;
