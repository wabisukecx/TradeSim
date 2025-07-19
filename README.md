# 📱 TradeSim - 株価分析学習アプリ

**🆕 JQuants API対応 | 🏆 品質保証済み | 🌍 グローバル検索対応**
初心者から上級者まで、株価分析とポートフォリオ管理を直感的に学べる教育専用Webアプリです。

## 🌐 ライブデモ

**[📱 今すぐ使ってみる！](https://tradesim-9djzkadr39vp8jt2dxcgud.streamlit.app/)**

## 🆕 v2.1 新機能

### 🔥 JQuants API統合（NEW!）

- **🇯🇵 日本株**: 全上場企業をリアルタイム検索
- **📊 高精度データ**: 市場区分・取引所情報・企業英語名
- **🚀 即座検索**: 会社名入力で瞬時に候補表示

### 🌍 グローバル検索強化

- **Alpha Vantage統合**: 世界中の株式市場対応
- **🔍 統合検索**: JQuants + Alpha Vantage のハイブリッド検索
- **💱 多通貨対応**: USD, JPY, EUR, GBP等自動判定

## 🎯 主な機能

### 🔍 銘柄検索

```bash
🔍 検索例：「トヨタ」
📊 結果：
🇯🇵 7203.T - トヨタ自動車株式会社（東証プライム | JPY | Japan）
🌍 TM - Toyota Motor Corp（NYSE | USD | United States）
```

### 📈 動的重み付け分析

6つのパターンを自動検出し、最適な分析戦略を提案：

| パターン | 説明 | 戦略 | API活用 |
|----------|------|------|---------|
| **上昇トレンド** | 持続的な価格上昇 | 移動平均・MACD重視 | 🇯🇵🌍 |
| **下降トレンド** | 持続的な価格下降 | 反転ポイント重視 | 🇯🇵🌍 |
| **レンジ相場** | 一定範囲内での変動 | RSI・ボリンジャー重視 | 🇯🇵🌍 |
| **転換期** | トレンド変化の可能性 | MACD最重視 | 🇯🇵🌍 |
| **加速相場** | 急激な価格変動 | 出来高重視 | 🇯🇵🌍 |
| **調整局面** | 大きな動きの後の調整 | 安定指標重視 | 🇯🇵🌍 |

### 🛠️ その他の機能

- **📊 テクニカル分析**: 移動平均、RSI、ボリンジャーバンド、MACD
- **💰 投資シミュレーション**: リアルなバックテスト機能
- **💼 ポートフォリオ管理**: 多通貨対応ウォッチリスト
- **📱 レスポンシブUI**: 全デバイス対応

## 🚀 クイックスタート

### 🌟 推奨：オンライン利用

**[📱 ライブデモ](https://tradesim-9djzkadr39vp8jt2dxcgud.streamlit.app/)**をクリックするだけ！

### 🏠 ローカル実行

```bash
git clone https://github.com/your-username/TradeSim.git
cd TradeSim
pip install -r requirements.txt
streamlit run app.py
```

## 📊 使い方

### 🆕 会社検索の使い方

#### 1. 基本的な検索（API設定なし）

```bash
1. 「🔍 会社名で検索」を選択
2. 会社名を入力（例：「トヨタ」「Apple」）
3. 基本検索結果から選択
```

#### 2. 🇯🇵 JQuants API利用（日本株特化）

```bash
1. 「🔧 API設定」を展開
2. 「🇯🇵 JQuants API を使用」をON
3. メールアドレス・パスワードを入力
4. 全上場企業から高精度検索！
```

#### 3. 🌍 Alpha Vantage API利用（世界株対応）

```bash
1. 「🔧 API設定」を展開
2. 「🌍 Alpha Vantage API を使用」をON
3. API Keyを入力
4. 世界中の株式を検索！
```

#### 4. 🚀 ハイブリッド検索（最高精度）

```bash
両方のAPIを有効にすると：
🇯🇵 日本株 → JQuants優先
🌍 海外株 → Alpha Vantage優先
🎯 自動的に最適なAPIを選択
```

### 📈 分析フロー

1. **銘柄選択**: 🆕高精度検索で企業を特定
2. **分析手法選択**: 固定・適応・手動の重み付けモード
3. **分析実行**: 「🚀 分析開始」ボタン
4. **結果確認**: パターン検出結果、チャート、バックテスト
5. **ポートフォリオ管理**: 多通貨対応ウォッチリストに追加

## 🔧 API設定ガイド

### 🇯🇵 JQuants API設定

#### 1. アカウント作成（無料）

1. [JQuants公式サイト](https://jpx-jquants.com/)にアクセス
2. 無料会員登録
3. メールアドレス・パスワードを取得

#### 2. アプリでの設定

```python
# 設定例
JQuantsメールアドレス: your-email@example.com
JQuantsパスワード: your-password
```

#### 3. 利用可能データ

- ✅ 全上場企業（4,000社以上）
- ✅ リアルタイム銘柄マスタ
- ✅ 市場区分（プライム・スタンダード・グロース）
- ✅ 英語企業名
- ✅ 業種分類

### 🌍 Alpha Vantage API設定

#### 1. API Key取得（無料）

1. [Alpha Vantage](https://www.alphavantage.co/support/#api-key)にアクセス
2. 無料API Key取得
3. 1日500リクエスト利用可能

#### 2. アプリでの設定

```python
# 設定例
Alpha Vantage API Key: YOUR_API_KEY_HERE
```

#### 3. 利用可能データ

- ✅ 世界中の株式市場
- ✅ 地域・通貨情報
- ✅ 取引所情報
- ✅ リアルタイム検索

## 🧪 品質保証

### テスト結果

- **総テスト数**: 58個
- **成功率**: 100% ✅
- **実行時間**: 6.76秒

```bash
# テスト実行
pytest tests/
# ============== 58 passed in 6.76s ==============
```

### テスト内容

| カテゴリ | テスト数 | 内容 |
|----------|----------|------|
| **統合テスト** | 14個 | 全体フロー、エラー処理 |
| **シグナル生成** | 24個 | 動的重み付け、個別指標 |
| **テクニカル分析** | 20個 | 指標計算、パフォーマンス |

## 🔧 技術仕様

### 主要技術スタック

- **Streamlit**: Webアプリフレームワーク
- **yfinance**: 株価データ取得
- **🆕 JQuants API**: 日本株検索・企業情報
- **🆕 Alpha Vantage API**: グローバル株式検索
- **Plotly**: インタラクティブチャート
- **TA-Lib**: テクニカル分析
- **Pandas/NumPy**: データ処理

### プロジェクト構造

```bash
TradeSim/
├── app.py                    # メインアプリケーション
├── tests/                    # テストスイート (58個)
├── config/                   # 設定管理
├── core/                     # アプリケーションコア
├── data/                     # データ取得・管理
│   └── stock_fetcher.py     # 🆕 JQuants/Alpha Vantage統合
├── analysis/                 # 分析エンジン
│   └── pattern_detector.py  # パターン検出
├── ui/                       # ユーザーインターフェース
│   ├── components.py        # 🆕 API設定UI
│   └── settings_ui.py       # 🆕 統合検索UI
└── portfolio/                # ポートフォリオ管理
```

### 🆕 API統合アーキテクチャ

```python
# 統合検索フロー
def get_combined_search_results(keyword, jquants_config, alpha_vantage_key):
    results = []
    
    # 日本語検索 → JQuants優先
    if has_japanese_chars(keyword) and jquants_config:
        results.extend(jquants_search(keyword, jquants_config))
    
    # グローバル検索 → Alpha Vantage
    if alpha_vantage_key:
        results.extend(alpha_vantage_search(keyword, alpha_vantage_key))
    
    # 重複除去・優先順位付け
    return deduplicate_and_prioritize(results)
```

## 📈 サポート銘柄

### 🇯🇵 日本株（JQuants API対応）

- **全上場企業**: 4,000社以上
- **市場**: 東証プライム・スタンダード・グロース、名証等
- **例**: トヨタ(7203.T), ソニー(6758.T), 任天堂(7974.T)等

### 🌍 海外株（Alpha Vantage API対応）

- **米国**: Apple(AAPL), Microsoft(MSFT), Google(GOOGL)等
- **欧州**: ASML(ASML.AS), SAP(SAP.DE)等
- **アジア**: Tencent(0700.HK), Samsung等

## 🆕 v2.1 更新内容

### 新機能

- ✅ JQuants API統合（日本株全上場企業検索）
- ✅ Alpha Vantage API統合（グローバル株式検索）
- ✅ 統合検索システム（ハイブリッド検索）
- ✅ 市場情報自動取得（取引所・通貨・地域）
- ✅ 多通貨対応ポートフォリオ

### 改善点

- ✅ 企業データベース削除（約200行のコード削減）
- ✅ リアルタイム企業情報取得
- ✅ 検索精度の大幅向上
- ✅ メンテナンス性向上（自動更新）

### パフォーマンス

- ✅ API認証トークンキャッシュで高速化
- ✅ 重複除去アルゴリズム最適化
- ✅ エラーハンドリング強化

## 📚 教育コンテンツ

### 学習目標

- **株式投資の基本概念**の理解
- **グローバル市場**への理解促進
- **テクニカル分析**の実践的習得
- **リスク管理**の重要性認識
- **🆕 市場構造**の理解（取引所・通貨等）

### 実践的アドバイス

- 💰 余裕資金での投資の重要性
- 🎯 **地域分散投資**によるリスク軽減
- 💱 **通貨リスク**の理解
- 😌 感情的にならない投資判断
- 📈 長期的視点の保持

## 🔐 セキュリティ

### API認証情報の取り扱い

```python
# ✅ セキュア：セッション中のみ保持
jquants_config = {
    "email": "user-input",      # type="default"
    "password": "user-input"    # type="password"
}

# ✅ セキュア：メモリから自動削除
# セッション終了時に認証情報は自動的にクリア
```

### プライバシー保護

- 🔒 認証情報はセッション中のみ保持
- 🗑️ セッション終了時に自動削除
- 🚫 サーバー側での認証情報保存なし
- 🛡️ HTTPS通信によるデータ保護

## ⚡ パフォーマンス最適化

### キャッシュ戦略

```python
# JQuants認証トークンキャッシュ（1時間）
if token_expires > current_time:
    return cached_token
else:
    refresh_token()

# 検索結果キャッシュ
@lru_cache(maxsize=100)
def cached_search(keyword, api_config):
    return api_search(keyword, api_config)
```

### レスポンス時間

- **基本検索**: < 0.1秒
- **JQuants検索**: < 2秒
- **Alpha Vantage検索**: < 3秒
- **統合検索**: < 5秒

## 🐛 トラブルシューティング

### よくある問題と解決方法

#### 1. 🇯🇵 JQuants認証エラー

```bash
❌ エラー: JQuants API認証に失敗しました
✅ 解決: 
- メールアドレス・パスワードの確認
- JQuantsアカウントの有効性確認
- 一時的なサービス停止の可能性
```

#### 2. 🌍 Alpha Vantage制限エラー

```bash
❌ エラー: API制限に達しました
✅ 解決:
- 1日後に再試行
- 有料プランへのアップグレード
- 検索頻度の調整
```

#### 3. 🔍 検索結果が空

```bash
❌ 問題: 検索結果が得られない
✅ 解決:
- API設定を確認
- キーワードを英語/日本語で変更
- 「⌨️ コードを直接入力」を使用
- 銘柄コードでの直接検索
```

## 📄 ライセンス

MIT License - 個人・教育・商用利用自由

## ⚠️ 免責事項

本アプリケーションは**教育・学習目的専用**です。投資助言は行いません。実際の投資判断は自己責任で行い、必要に応じて専門家にご相談ください。

## 🔗 関連リンク

- **[JQuants公式サイト](https://jpx-jquants.com/)** - 日本株データAPI
- **[Alpha Vantage公式サイト](https://www.alphavantage.co/)** - グローバル株式データAPI
- **[Streamlit公式ドキュメント](https://docs.streamlit.io/)** - アプリフレームワーク
