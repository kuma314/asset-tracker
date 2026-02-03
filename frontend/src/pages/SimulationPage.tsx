import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

const SimulationPage = () => {
  const data = {
    labels: ["0", "6", "12", "18", "24"],
    datasets: [
      {
        label: "ベース",
        data: [0, 800, 1700, 2700, 3800],
        borderColor: "#2F855A"
      },
      {
        label: "楽観",
        data: [0, 900, 1900, 3100, 4500],
        borderColor: "#38A169"
      },
      {
        label: "悲観",
        data: [0, 700, 1500, 2300, 3100],
        borderColor: "#C53030"
      }
    ]
  };

  return (
    <section className="page">
      <h2>将来推計シミュレーション</h2>
      <div className="grid">
        <div className="card">
          <h3>入力条件</h3>
          <div className="form-grid">
            <label>
              期間 (月)
              <input type="number" defaultValue={24} />
            </label>
            <label>
              年率リターン
              <input type="number" step="0.01" defaultValue={0.05} />
            </label>
            <label>
              毎月積立額
              <input type="number" defaultValue={80000} />
            </label>
            <label>
              配賦ルール
              <select>
                <option>ターゲット配分</option>
                <option>固定ルール</option>
              </select>
            </label>
          </div>
          <button className="primary">シミュレーション実行</button>
        </div>
        <div className="card">
          <h3>推計結果</h3>
          <Line data={data} />
        </div>
      </div>
    </section>
  );
};

export default SimulationPage;
