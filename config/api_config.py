# config/api_config.py
"""
API設定管理モジュール
JQuants、Alpha Vantage等のAPI認証情報を管理
"""

import json
import os
from typing import Optional, Dict, Any
from pathlib import Path

# python-dotenvライブラリの使用
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class APIConfigManager:
    """API設定管理クラス"""
    
    def __init__(self):
        self.config_file = "api_config.json"
        self.env_file = ".env"
        self._config_cache = None
        
        # .envファイルを環境変数に読み込み（python-dotenv使用）
        if DOTENV_AVAILABLE and os.path.exists(self.env_file):
            load_dotenv(self.env_file)
    
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        if self._config_cache is not None:
            return self._config_cache
        
        config = {}
        
        # 1. api_config.jsonから読み込み
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # 2. .envファイルから読み込み（手動解析版 - バックアップ）
        if not DOTENV_AVAILABLE and os.path.exists(self.env_file):
            self._load_env_manually(config)
        
        # 3. 環境変数から読み込み（最優先）
        self._load_from_environment_variables(config)
        
        self._config_cache = config
        return config
    
    def _load_env_manually(self, config: Dict[str, Any]):
        """手動で.envファイルを読み込み（dotenvが利用できない場合）"""
        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # 空行やコメント行をスキップ
                    if not line or line.startswith('#'):
                        continue
                    
                    # =が含まれていない行はスキップ
                    if '=' not in line:
                        print(f"Warning: .env line {line_num} invalid format: {line}")
                        continue
                    
                    # 最初の=で分割（値に=が含まれる場合を考慮）
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # クォートを除去
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # 環境変数をネストした辞書に変換
                    if key.startswith('JQUANTS_'):
                        if 'jquants' not in config:
                            config['jquants'] = {}
                        sub_key = key.replace('JQUANTS_', '').lower()
                        config['jquants'][sub_key] = value
                        print(f"Loaded from .env: {key} -> jquants.{sub_key}")
                    elif key.startswith('ALPHA_VANTAGE_'):
                        if 'alpha_vantage' not in config:
                            config['alpha_vantage'] = {}
                        sub_key = key.replace('ALPHA_VANTAGE_', '').lower()
                        config['alpha_vantage'][sub_key] = value
                        print(f"Loaded from .env: {key} -> alpha_vantage.{sub_key}")
        except FileNotFoundError:
            print(f"Warning: .env file not found: {self.env_file}")
        except Exception as e:
            print(f"Error reading .env file: {e}")
    
    def _load_from_environment_variables(self, config: Dict[str, Any]):
        """システム環境変数から読み込み"""
        # JQuants設定
        jquants_email = os.environ.get('JQUANTS_EMAIL')
        jquants_password = os.environ.get('JQUANTS_PASSWORD')
        
        if jquants_email or jquants_password:
            if 'jquants' not in config:
                config['jquants'] = {}
            if jquants_email:
                config['jquants']['email'] = jquants_email
                print("Loaded JQUANTS_EMAIL from environment")
            if jquants_password:
                config['jquants']['password'] = jquants_password
                print("Loaded JQUANTS_PASSWORD from environment")
        
        # Alpha Vantage設定
        alpha_vantage_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
        if alpha_vantage_key:
            if 'alpha_vantage' not in config:
                config['alpha_vantage'] = {}
            config['alpha_vantage']['api_key'] = alpha_vantage_key
            print("Loaded ALPHA_VANTAGE_API_KEY from environment")
    
    def get_jquants_config(self) -> Optional[Dict[str, str]]:
        """JQuants API設定を取得"""
        config = self._load_config()
        jquants_config = config.get('jquants', {})
        
        email = jquants_config.get('email')
        password = jquants_config.get('password')
        
        if email and password:
            return {
                'email': email,
                'password': password
            }
        return None
    
    def get_alpha_vantage_key(self) -> Optional[str]:
        """Alpha Vantage API Keyを取得"""
        config = self._load_config()
        alpha_vantage_config = config.get('alpha_vantage', {})
        return alpha_vantage_config.get('api_key')
    
    def is_configured(self) -> bool:
        """API設定が存在するかチェック"""
        return (self.get_jquants_config() is not None or 
                self.get_alpha_vantage_key() is not None)
    
    def get_config_status(self) -> Dict[str, bool]:
        """設定状況を取得"""
        return {
            'jquants': self.get_jquants_config() is not None,
            'alpha_vantage': self.get_alpha_vantage_key() is not None
        }
    
    def clear_cache(self):
        """キャッシュをクリア"""
        self._config_cache = None
    
    def debug_config(self):
        """デバッグ用設定確認"""
        print("🔧 API設定デバッグ開始...")
        print(f"📁 python-dotenv available: {DOTENV_AVAILABLE}")
        print(f"📁 設定ファイル存在: {os.path.exists(self.config_file)}")
        print(f"📁 .env存在: {os.path.exists(self.env_file)}")
        
        # 環境変数の確認
        print("\n🌍 環境変数:")
        for key in ['JQUANTS_EMAIL', 'JQUANTS_PASSWORD', 'ALPHA_VANTAGE_API_KEY']:
            value = os.environ.get(key)
            if value:
                print(f"   {key}: {value[:10]}...")
            else:
                print(f"   {key}: 未設定")
        
        # 設定の確認
        config = self._load_config()
        print(f"\n📊 読み込み済み設定:")
        print(f"   JQuants: {config.get('jquants', {})}")
        print(f"   Alpha Vantage: {config.get('alpha_vantage', {})}")
        
        jquants_config = self.get_jquants_config()
        alpha_vantage_key = self.get_alpha_vantage_key()
        
        print(f"\n🎯 最終結果:")
        print(f"🇯🇵 JQuants設定: {'✅' if jquants_config else '❌'}")
        if jquants_config:
            print(f"   Email: {jquants_config['email'][:20]}...")
        
        print(f"🌍 Alpha Vantage設定: {'✅' if alpha_vantage_key else '❌'}")
        if alpha_vantage_key:
            print(f"   API Key: {alpha_vantage_key[:10]}...")
        
        print("🎯 API設定デバッグ完了")
    
    def render_config_management_ui(self):
        """設定管理UIを表示"""
        import streamlit as st
        
        st.markdown("#### 📁 設定ファイル管理")
        
        # 設定ファイルの状況表示
        config_status = self.get_config_status()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 設定状況**")
            if config_status['jquants']:
                st.success("🇯🇵 JQuants: 設定済み")
            else:
                st.warning("🇯🇵 JQuants: 未設定")
            
            if config_status['alpha_vantage']:
                st.success("🌍 Alpha Vantage: 設定済み")
            else:
                st.warning("🌍 Alpha Vantage: 未設定")
        
        with col2:
            st.markdown("**📝 設定ファイル**")
            if os.path.exists(self.config_file):
                st.info(f"📄 {self.config_file}: 存在")
            else:
                st.warning(f"📄 {self.config_file}: なし")
            
            if os.path.exists(self.env_file):
                st.info(f"📄 {self.env_file}: 存在")
            else:
                st.warning(f"📄 {self.env_file}: なし")
            
            # python-dotenvの状況表示
            if DOTENV_AVAILABLE:
                st.success("✅ python-dotenv: 利用可能")
            else:
                st.warning("⚠️ python-dotenv: 未インストール")
        
        # デバッグ機能
        if st.button("🐛 設定デバッグ実行", key="debug_api_config"):
            self.debug_config()
            st.success("✅ デバッグ情報をコンソールに出力しました")
        
        # 設定保存機能
        if st.button("💾 現在の手動設定をファイルに保存", key="save_api_config"):
            self._save_manual_config_to_file()
        
        # リロード機能
        if st.button("🔄 設定ファイルを再読み込み", key="reload_api_config"):
            self.clear_cache()
            # .envファイルの再読み込み
            if DOTENV_AVAILABLE and os.path.exists(self.env_file):
                load_dotenv(self.env_file, override=True)
            st.success("✅ 設定をリロードしました")
            st.rerun()
    
    def _save_manual_config_to_file(self):
        """手動設定をファイルに保存"""
        import streamlit as st
        
        config = {}
        
        # セッション状態から手動設定を取得
        if 'manual_jquants_config' in st.session_state:
            config['jquants'] = st.session_state['manual_jquants_config']
        
        if 'manual_alpha_vantage_key' in st.session_state:
            config['alpha_vantage'] = {'api_key': st.session_state['manual_alpha_vantage_key']}
        
        if config:
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                st.success(f"✅ 設定を {self.config_file} に保存しました")
                self.clear_cache()  # キャッシュをクリア
            except Exception as e:
                st.error(f"❌ 設定保存エラー: {str(e)}")
        else:
            st.warning("⚠️ 保存する手動設定がありません")


# グローバルインスタンス
_api_config_manager = None


def get_api_config_manager() -> APIConfigManager:
    """APIConfigManagerのシングルトンインスタンスを取得"""
    global _api_config_manager
    if _api_config_manager is None:
        _api_config_manager = APIConfigManager()
    return _api_config_manager


# デバッグ用関数
def test_api_config():
    """API設定のテスト"""
    manager = get_api_config_manager()
    manager.debug_config()


if __name__ == "__main__":
    test_api_config()