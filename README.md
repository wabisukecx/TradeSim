# TradeSim v3.0 - 株価テクニカル分析・バックテストアプリ

**Flutter 3.x によるネイティブ Android アプリ。Streamlit + Python 版 TradeSim v2.1 の完全移植版です。**

> このアプリは**教育・学習目的のみ**です。実際の投資判断は専門家にご相談ください。

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

- **株価データ取得**: Yahoo Finance v8 API（米国株・日本株対応）
- **テクニカル分析**: SMA / RSI / ボリンジャーバンド / MACD / ATR / 出来高MA
- **適応的シグナル生成**: 市場パターンを自動検出し重み付けを動的に調整
- **市場パターン検出**: 上昇トレンド / 下降トレンド / レンジ / 転換期 / 加速相場
- **シグナル判断理由表示**: 各指標の判断根拠をテキストで表示
- **バックテスト**: リスクベースポジションサイジング / ストップロス / 利確
- **JQuants 銘柄検索**: 日本語・英語・コード検索（要JQuants無料登録）
- **5画面 UI**: Home / Search / Analysis / Backtest / Portfolio（ウォッチリスト）
- **用語集**: 主要テクニカル指標の解説画面

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

## 動作環境

| 項目 | 要件 |
|---|---|
| OS | Android 5.0（API 21）以上 |
| ネットワーク | 株価取得・JQuants検索時にインターネット接続が必要 |
| ストレージ | 約 30MB（インストール時） |

---

## 開発環境の構築

### 1. Flutter SDK のインストール

[flutter.dev](https://docs.flutter.dev/get-started/install) から OS に合わせたインストール手順を確認してください。

**Windows（winget）**

```bash
winget install --id=Google.Flutter
```

**macOS（Homebrew）**

```bash
brew install --cask flutter
```

**手動インストール共通手順**

1. Flutter SDK を任意のディレクトリに展開（例: `C:\flutter` または `~/flutter`）
2. `bin` ディレクトリを PATH に追加
3. インストール確認

```bash
flutter --version
```

### 2. Android SDK の準備

Android Studio は**必須ではありません**が、SDK の管理が容易なため推奨です。

#### 方法A：Android Studio 経由（推奨）

[developer.android.com](https://developer.android.com/studio) から Android Studio をインストールし、SDK Manager で以下を導入します。

- **Android SDK**
- **Android SDK Command-line Tools**
- **Android Emulator**（実機がない場合）

JDK は Android Studio に同梱されているものをそのまま使用できます。

#### 方法B：Command-line Tools のみ（Android Studio 不要）

Android Studio を使わない場合は [sdkmanager](https://developer.android.com/tools/sdkmanager) を単体でインストールし、以下を実行します。

```bash
sdkmanager "platform-tools" "platforms;android-36" "build-tools;36.0.0" "cmdline-tools;latest"
```

JDK は別途インストールが必要です。

**Windows（winget）**

```bash
winget install --id=EclipseAdoptium.Temurin.17.JDK
```

**macOS（Homebrew）**

```bash
brew install --cask temurin@17
```

### 3. Flutter の Android ライセンス承認

```bash
flutter doctor --android-licenses
```

すべての質問に `y` で回答します。

### 4. VS Code を使う場合（任意）

VS Code に以下の拡張機能を追加します。

- [Flutter](https://marketplace.visualstudio.com/items?itemName=Dart-Code.flutter)
- [Dart](https://marketplace.visualstudio.com/items?itemName=Dart-Code.dart-code)

### 5. 環境確認

```bash
flutter doctor
```

最低限以下にチェックが入れば準備完了です（Android Studio は方法B の場合は不要）。

```
[✓] Flutter
[✓] Android toolchain
[✓] Connected device
```

---

## セットアップ（開発者向け）

### 必要条件

- Flutter 3.x 以上 / Dart 3.11.3 以上
- Android SDK（compileSdk 36 / minSdk 21）
- JDK 17 以上
- Android Studio（推奨）または Android SDK Command-line Tools のみでも可

### リポジトリのクローン

```bash
git clone https://github.com/wabisukecx/Tradesim.git
cd Tradesim
```

### 依存パッケージのインストール

```bash
flutter pub get
```

### アプリ起動（開発用）

Android デバイスまたはエミュレーターを接続した状態で実行します。

```bash
# 接続デバイスの確認
flutter devices

# デバッグモードで起動
flutter run

# 特定デバイスを指定して起動
flutter run -d <device_id>
```

### テスト実行

```bash
# 全ユニットテスト
flutter test

# 詳細ログ付きで実行
flutter test --verbose
```

---

## APK のビルドと配布

### リリース APK のビルド（fat APK・全アーキテクチャ対応）

デフォルトでは全アーキテクチャを含む fat APK が生成されます。ファイルサイズは大きくなりますが、どのデバイスでも動作します。

```bash
flutter build apk --release
```

ビルド成功後、以下のパスに APK が生成されます。

```
build/app/outputs/flutter-apk/app-release.apk
```

## Android デバイスへの APK インストール（サイドロード）

### デバイス側の設定

1. **設定 > セキュリティ**（または「プライバシー」）を開く
2. **「不明なアプリのインストール」** を許可する（Android 8.0 以降はアプリ単位で設定）

### ADB を使ったインストール

```bash
adb install build/app/outputs/flutter-apk/app-release.apk
```

### ファイル転送でインストール

APK ファイルをデバイスに転送し、ファイルマネージャーからタップしてインストールします。

---

## 主要依存パッケージ

| パッケージ | バージョン | 用途 |
|---|---|---|
| flutter_riverpod | ^2.5.0 | 状態管理 |
| go_router | ^13.0.0 | 画面遷移 |
| candlesticks | ^2.1.0 | ローソク足チャート |
| fl_chart | ^0.68.0 | RSI / MACD チャート |
| http | ^1.2.0 | Yahoo Finance / JQuants API 通信 |
| flutter_secure_storage | ^9.0.0 | JQuants 認証情報の安全な保存 |
| shared_preferences | ^2.2.0 | ウォッチリスト等の永続化 |
| intl | ^0.19.0 | 数値・日付フォーマット |
| url_launcher | ^6.3.0 | 外部リンク起動 |

---

## 使い方

1. **銘柄入力**: ホーム画面で銘柄コードを入力
   - 日本株: `7203.T`（末尾に `.T`）
   - 米国株: `AAPL`（ティッカーシンボル）
2. **期間選択**: 3ヶ月 / 6ヶ月 / 1年 / 2年
3. **分析開始**: チャート・RSI・MACDと最新シグナルが表示される
4. **パターン確認**: 検出された市場パターンと重み付けを確認する
5. **シグナル理由確認**: 各指標がどう判断したかを確認する
6. **バックテスト**: 分析画面右上のボタンから確認
7. **JQuants 検索**: 検索アイコンから日本株の銘柄名・コードで検索
   - 事前に [JQuants](https://www.jquants.com/) への無料登録とメール認証が必要
   - 設定画面でメールアドレス・パスワードを入力すると認証情報が安全に保存されます

---

## ディレクトリ構成

```
Tradesim/
├── android/                        # Android ネイティブ設定
│   └── app/
│       └── build.gradle.kts        # applicationId / minSdk / targetSdk 設定
├── assets/
│   └── icon/
│       └── app_icon.png            # アプリアイコン
├── lib/
│   ├── main.dart                   # エントリポイント・ルーティング（go_router）
│   ├── models/
│   │   ├── analysis_result.dart    # AnalysisResult / WeightProfile / PatternResult
│   │   ├── backtest_result.dart    # バックテスト結果モデル
│   │   ├── performance_metrics.dart # パフォーマンス指標
│   │   ├── portfolio_item.dart     # ウォッチリスト銘柄モデル
│   │   ├── portfolio_value.dart    # ポートフォリオ評価額モデル
│   │   ├── stock_candle.dart       # ローソク足データモデル
│   │   └── trade_record.dart       # トレード履歴モデル
│   ├── services/
│   │   ├── market_pattern_detector.dart  # 市場パターン検出（動的重み付け）
│   │   ├── signal_generator.dart         # シグナル生成（適応モード対応）
│   │   ├── technical_analyzer.dart       # テクニカル指標計算
│   │   └── backtest_engine.dart          # バックテストエンジン
│   ├── repositories/
│   │   ├── stock_repository.dart         # Yahoo Finance v8 API
│   │   └── jquants_repository.dart       # JQuants API（銘柄検索・認証）
│   ├── providers/
│   │   └── providers.dart               # Riverpod プロバイダー定義
│   └── screens/
│       ├── home_screen.dart             # ホーム（銘柄入力・期間選択）
│       ├── search_screen.dart           # JQuants 銘柄検索
│       ├── analysis_screen.dart         # チャート・シグナル・パターン表示
│       ├── backtest_screen.dart         # バックテスト結果
│       ├── portfolio_screen.dart        # ウォッチリスト管理
│       └── glossary_screen.dart         # テクニカル指標用語集
├── test/                           # ユニットテスト
├── docs/
│   └── privacy-policy.md           # プライバシーポリシー
└── pubspec.yaml                    # パッケージ依存関係
```

---

## 免責事項

このアプリは**教育・学習目的のみ**です。表示される分析結果・シグナルは投資助言ではありません。実際の投資判断は自己責任で行い、必要に応じて専門家にご相談ください。過去の成績は将来の成果を保証するものではありません。
