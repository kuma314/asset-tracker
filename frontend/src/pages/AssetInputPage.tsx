const AssetInputPage = () => {
  return (
    <section className="page">
      <h2>資産入力</h2>
      <p>口座・銘柄・分類・評価額を登録します。</p>
      <div className="card">
        <div className="form-grid">
          <label>
            口座
            <input placeholder="例: 証券口座" />
          </label>
          <label>
            銘柄/資産
            <input placeholder="例: 全世界株式" />
          </label>
          <label>
            分類
            <select>
              <option>現金</option>
              <option>株式（コア）</option>
              <option>株式（サテライト）</option>
              <option>債券</option>
            </select>
          </label>
          <label>
            評価額 (JPY)
            <input type="number" placeholder="1000000" />
          </label>
        </div>
        <button className="primary">保存</button>
      </div>
    </section>
  );
};

export default AssetInputPage;
