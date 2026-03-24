# TradeSim v3.0 - 株価テクニカル分析・バックテストアプリ

**Flutter 3.x によるネイティブ Android アプリ。Streamlit + Python 版 TradeSim v2.1 の完全移植版です。**

> ⚠️ このアプリは**教育・学習目的のみ**です。実際の投資判断は専門家にご相談ください。

---

## v3.0 について

TradeSim v2.1（Streamlit + Python）をネイティブ Android アプリとして完全移植しました。
v2.1 で Web 版のみ対応していた動的重み付け（適応的AI判定）をネイティブアプリで実現しています。

| | v2.1 (Python) | v3.0 (Flutter) |
|---|---|---|
| 実行環境 | Webブラウザ（Streamlit） | Android ネイティブ |
| オフライン | 不可 | ウォッチリストのみ可 |
| インストール | 不要 | APK / GitHub Releases |
| 重み付けモード | 固定 / 適応 / 手動 | 適応（自動）|

---

## 機能

- **株価データ取得**: Yahoo Finance v8 API
- **テクニカル分析**: SMA / RSI / ボリンジャーバンド / MACD / ATR / 出来高MA
- **適応的シグナル生成**: 市場パターンを自動検出し重み付けを動的に調整
- **市場パターン検出**: 上昇トレンド / 下降トレンド / レンジ / 転換期 / 加速相場
- **シグナル判断理由表示**: 各指標の判断根拠をテキストで表示
- **バックテスト**: リスクベースポジションサイジング / ストップロス / 利確
- **JQuants 銘柄検索**: 日本語・英語・コード検索
- **5画面 UI**: Home / Search / Analysis / Backtest / Portfolio（ウォッチリスト）

---

## 市場パターン検出と動的重み付け

分析時に市場パターンを自動検出し、パターンに最適な重み付けでシグナルを生成します。

| パターン | 重視する指標 | リスク |
|---|---|---|
| 上昇トレンド | MA・MACD 重視 | 中 |
| 下降トレンド | MA・MACD 重視、RSI補助 | 高 |
| レンジ相場 | RSI・ボリンジャーバンド重視 | 低 |
| 転換期 | MACD 最重視 | 高 |
| 加速相場 | 出来高・MACD 重視 | 高 |

分析画面にはパターン名・信頼度・戦略ヒント・重み付けバーが表示されます。

---

## セットアップ

### 必要条件

- Flutter 3.x 以上 / Dart 3.x 以上
- Android SDK (minSdkVersion 21 以上)

### ビルド・実行

```bash
# 依存パッケージのインストール
flutter pub get

# アプリ起動（接続済みデバイス or エミュレーターが必要）
flutter run

# リリースビルド
flutter build apk --release
```

### テスト実行

```bash
# 全ユニットテスト
flutter test
```

---

## 主要依存パッケージ

| パッケージ | 用途 |
|---|---|
| flutter_riverpod | 状態管理 |
| go_router | 画面遷移 |
| candlesticks | ローソク足チャート |
| fl_chart | RSI/MACDチャート |
| http | Yahoo Finance / JQuants API |
| flutter_secure_storage | JQuants 認証情報の安全な保存 |
| intl | 数値・日付フォーマット |

---

## 使い方

1. **銘柄入力**: ホーム画面で銘柄コードを入力（例: `7203.T`, `AAPL`）
2. **期間選択**: 3ヶ月 / 6ヶ月 / 1年 / 2年
3. **分析開始**: チャート・RSI・MACDと最新シグナルが表示される
4. **パターン確認**: 検出された市場パターンと重み付けを確認する
5. **シグナル理由確認**: 各指標がどう判断したかを確認する
6. **バックテスト**: 分析画面右上のボタンから確認
7. **JQuants 検索**: 検索アイコンから日本株の銘柄名・コードで検索

---

## ディレクトリ構成

```
lib/
  main.dart                      # エントリポイント・ルーティング
  models/
    analysis_result.dart         # AnalysisResult / WeightProfile / PatternResult
    stock_candle.dart
    backtest_result.dart
    portfolio_item.dart
  services/
    market_pattern_detector.dart # 市場パターン検出（動的重み付け）
    signal_generator.dart        # シグナル生成（適応モード対応）
    technical_analyzer.dart      # テクニカル指標計算
    backtest_engine.dart         # バックテストエンジン
  repositories/                  # Yahoo Finance / JQuants API
  providers/                     # Riverpod プロバイダー
  screens/                       # 5画面 UI
test/                            # ユニットテスト
docs/
  privacy-policy.md              # プライバシーポリシー
```

---

## プライバシーポリシー

[docs/privacy-policy.md](docs/privacy-policy.md) を参照してください。

---

## 免責事項

このアプリは**教育・学習目的のみ**です。表示される分析結果・シグナルは投資助言ではありません。実際の投資判断は自己責任で行い、必要に応じて専門家にご相談ください。過去の成績は将来の成果を保証するものではありません。
