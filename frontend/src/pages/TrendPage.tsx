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

const TrendPage = () => {
  const data = {
    labels: ["1月", "2月", "3月", "4月", "5月", "6月"],
    datasets: [
      {
        label: "総資産",
        data: [520, 560, 610, 640, 700, 750],
        borderColor: "#3182CE",
        backgroundColor: "rgba(49, 130, 206, 0.2)"
      }
    ]
  };

  return (
    <section className="page">
      <h2>資産推移</h2>
      <div className="card">
        <Line data={data} />
      </div>
    </section>
  );
};

export default TrendPage;
