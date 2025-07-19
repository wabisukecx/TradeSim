# config/api_config.py
"""
API設定管理モジュール
JQuants、Alpha Vantage等のAPI認証情報を管理
"""

import json
import os
from typing import Optional, Dict, Any
from pathlib import Path


class APIConfigManager:
    """API設定管理クラス"""
    
    def __init__(self):
        self.config_file = "api_config.json"
        self.env_file = ".env"
        self._config_cache = None
    
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
        
        # 2. .envファイルから読み込み（上書き）
        if os.path.exists(self.env_file):
            try:
                with open(self.env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            
                            # 環境変数をネストした辞書に変換
                            if key.startswith('JQUANTS_'):
                                if 'jquants' not in config:
                                    config['jquants'] = {}
                                sub_key = key.replace('JQUANTS_', '').lower()
                                config['jquants'][sub_key] = value
                            elif key.startswith('ALPHA_VANTAGE_'):
                                if 'alpha_vantage' not in config:
                                    config['alpha_vantage'] = {}
                                sub_key = key.replace('ALPHA_VANTAGE_', '').lower()
                                config['alpha_vantage'][sub_key] = value
            except FileNotFoundError:
                pass
        
        # 3. 環境変数から読み込み（最優先）
        jquants_email = os.environ.get('JQUANTS_EMAIL')
        jquants_password = os.environ.get('JQUANTS_PASSWORD')
        alpha_vantage_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
        
        if jquants_email or jquants_password:
            if 'jquants' not in config:
                config['jquants'] = {}
            if jquants_email:
                config['jquants']['email'] = jquants_email
            if jquants_password:
                config['jquants']['password'] = jquants_password
        
        if alpha_vantage_key:
            if 'alpha_vantage' not in config:
                config['alpha_vantage'] = {}
            config['alpha_vantage']['api_key'] = alpha_vantage_key
        
        self._config_cache = config
        return config
    
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
        
        # 設定保存機能
        if st.button("💾 現在の手動設定をファイルに保存", key="save_api_config"):
            self._save_manual_config_to_file()
        
        # リロード機能
        if st.button("🔄 設定ファイルを再読み込み", key="reload_api_config"):
            self.clear_cache()
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
    
    print("🔧 API設定テスト開始...")
    print(f"📁 設定ファイル存在: {os.path.exists(manager.config_file)}")
    print(f"📁 .env存在: {os.path.exists(manager.env_file)}")
    
    jquants_config = manager.get_jquants_config()
    alpha_vantage_key = manager.get_alpha_vantage_key()
    
    print(f"🇯🇵 JQuants設定: {'✅' if jquants_config else '❌'}")
    if jquants_config:
        print(f"   Email: {jquants_config['email'][:20]}...")
    
    print(f"🌍 Alpha Vantage設定: {'✅' if alpha_vantage_key else '❌'}")
    if alpha_vantage_key:
        print(f"   API Key: {alpha_vantage_key[:10]}...")
    
    print("🎯 API設定テスト完了")


if __name__ == "__main__":
    test_api_config()