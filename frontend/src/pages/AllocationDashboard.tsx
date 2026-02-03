import { ArcElement, Chart as ChartJS, Legend, Tooltip } from "chart.js";
import { Doughnut } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend);

const AllocationDashboard = () => {
  const data = {
    labels: ["現金", "株式（コア）", "株式（サテライト）", "債券"],
    datasets: [
      {
        data: [15, 45, 20, 20],
        backgroundColor: ["#A0AEC0", "#3182CE", "#63B3ED", "#ED8936"]
      }
    ]
  };

  return (
    <section className="page">
      <h2>配分ダッシュボード</h2>
      <div className="grid">
        <div className="card">
          <h3>現状配分</h3>
          <Doughnut data={data} />
        </div>
        <div className="card">
          <h3>ターゲット比較</h3>
          <table>
            <thead>
              <tr>
                <th>分類</th>
                <th>現状</th>
                <th>ターゲット</th>
                <th>乖離</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>株式（コア）</td>
                <td>45%</td>
                <td>50%</td>
                <td className="negative">-5pp</td>
              </tr>
              <tr>
                <td>株式（サテライト）</td>
                <td>20%</td>
                <td>15%</td>
                <td className="positive">+5pp</td>
              </tr>
              <tr>
                <td>現金</td>
                <td>15%</td>
                <td>15%</td>
                <td>0pp</td>
              </tr>
              <tr>
                <td>債券</td>
                <td>20%</td>
                <td>20%</td>
                <td>0pp</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
};

export default AllocationDashboard;
