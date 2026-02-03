const ImportExportPage = () => {
  return (
    <section className="page">
      <h2>インポート / エクスポート</h2>
      <div className="grid">
        <div className="card">
          <h3>インポート</h3>
          <p>CSV/Excel を使って初期データを取り込みます。</p>
          <input type="file" />
          <button className="primary">インポート開始</button>
        </div>
        <div className="card">
          <h3>エクスポート</h3>
          <p>CSV/JSON としてデータを保存します。</p>
          <button>CSV エクスポート</button>
          <button>JSON エクスポート</button>
        </div>
      </div>
    </section>
  );
};

export default ImportExportPage;
