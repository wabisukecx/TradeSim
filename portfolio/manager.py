# portfolio/manager.py - 修正版
"""
ポートフォリオ管理機能
"""

import pandas as pd
import streamlit as st
import yfinance as yf
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime

from data.validators import DataValidator
from data.cache_manager import cache_current_price


class PortfolioManager:
    """ポートフォリオ管理クラス"""
    
    def __init__(self):
        self.validator = DataValidator()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """セッション状態を初期化"""
        if 'portfolio' not in st.session_state:
            st.session_state.portfolio = {}
        
        if 'portfolio_history' not in st.session_state:
            st.session_state.portfolio_history = []
    
    def add_stock(self, symbol: str, shares: int, price: float, long_name: str) -> str:
        """
        ポートフォリオに銘柄を追加
        
        Args:
            symbol: 銘柄コード
            shares: 株数
            price: 価格
            long_name: 会社名
            
        Returns:
            str: 結果メッセージ
        """
        # データ検証
        if not self.validator.validate_symbol_format(symbol):
            return "❌ 銘柄コードが正しくありません"
        
        if shares <= 0 or shares > 1000000:
            return "❌ 株数が正しくありません"
        
        if price <= 0 or price > 1000000:
            return "❌ 価格が正しくありません"
        
        try:
            if symbol in st.session_state.portfolio:
                # 既存銘柄の場合は平均取得価格を更新
                current_data = st.session_state.portfolio[symbol]
                current_shares = current_data['shares']
                current_avg_price = current_data['avg_price']
                
                # 加重平均価格を計算
                total_cost = (current_shares * current_avg_price) + (shares * price)
                total_shares = current_shares + shares
                new_avg_price = total_cost / total_shares
                
                st.session_state.portfolio[symbol].update({
                    'shares': total_shares,
                    'avg_price': new_avg_price,
                    'last_updated': datetime.now()
                })
                
                message = f"✅ ポートフォリオを更新しました: {long_name} - {shares}株追加"
            else:
                # 新規銘柄追加
                st.session_state.portfolio[symbol] = {
                    'shares': shares,
                    'avg_price': price,
                    'longName': long_name,
                    'added_date': datetime.now(),
                    'last_updated': datetime.now()
                }
                
                message = f"✅ ポートフォリオに追加しました: {long_name} - {shares}株"
            
            # 履歴に記録
            self._add_to_history('ADD', symbol, shares, price, long_name)
            
            return message
            
        except Exception as e:
            return f"❌ エラーが発生しました: {e}"
    
    def remove_stock(self, symbol: str) -> str:
        """
        ポートフォリオから銘柄を削除
        
        Args:
            symbol: 銘柄コード
            
        Returns:
            str: 結果メッセージ
        """
        if symbol in st.session_state.portfolio:
            long_name = st.session_state.portfolio[symbol]['longName']
            shares = st.session_state.portfolio[symbol]['shares']
            price = st.session_state.portfolio[symbol]['avg_price']
            
            # 履歴に記録
            self._add_to_history('REMOVE', symbol, shares, price, long_name)
            
            del st.session_state.portfolio[symbol]
            return f"🗑️ ポートフォリオから削除しました: {long_name}"
        else:
            return "ポートフォリオに銘柄がありません。"
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        ポートフォリオサマリーを取得
        
        Returns:
            dict: ポートフォリオサマリー
        """
        if not st.session_state.portfolio:
            return {
                'total_cost': 0,
                'current_value': 0,
                'total_pnl': 0,
                'total_pnl_pct': 0,
                'positions': [],
                'position_count': 0
            }
        
        positions = []
        total_cost = 0
        total_current_value = 0
        
        # 現在価格を一括取得
        symbols = list(st.session_state.portfolio.keys())
        current_prices = self._get_current_prices_batch(symbols)
        
        for symbol, data in st.session_state.portfolio.items():
            shares = data['shares']
            avg_price = data['avg_price']
            long_name = data['longName']
            
            current_price = current_prices.get(symbol, avg_price)
            
            cost_basis = shares * avg_price
            current_value = shares * current_price
            pnl = current_value - cost_basis
            pnl_pct = (pnl / cost_basis) * 100 if cost_basis != 0 else 0
            
            positions.append({
                'symbol': symbol,
                'longName': long_name,
                'shares': shares,
                'avg_price': avg_price,
                'current_price': current_price,
                'cost_basis': cost_basis,
                'current_value': current_value,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'weight': 0  # 後で計算
            })
            
            total_cost += cost_basis
            total_current_value += current_value
        
        # ウェイトを計算
        for position in positions:
            position['weight'] = (position['current_value'] / total_current_value * 100) if total_current_value > 0 else 0
        
        total_pnl = total_current_value - total_cost
        total_pnl_pct = (total_pnl / total_cost) * 100 if total_cost != 0 else 0
        
        return {
            'total_cost': total_cost,
            'current_value': total_current_value,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'positions': positions,
            'position_count': len(positions)
        }
    
    def _get_current_prices_batch(self, symbols: List[str]) -> Dict[str, float]:
        """
        複数銘柄の現在価格を一括取得
        
        Args:
            symbols: 銘柄コードのリスト
            
        Returns:
            dict: {symbol: price}の辞書
        """
        prices = {}
        
        try:
            if len(symbols) == 1:
                # 単一銘柄の場合
                symbol = symbols[0]
                prices[symbol] = cache_current_price(symbol)
            else:
                # 複数銘柄の場合
                for symbol in symbols:
                    try:
                        prices[symbol] = cache_current_price(symbol)
                    except:
                        prices[symbol] = 0.0
        except Exception as e:
            # エラーが発生した場合は個別に取得
            for symbol in symbols:
                try:
                    prices[symbol] = cache_current_price(symbol)
                except:
                    prices[symbol] = 0.0
        
        return prices
    
    def get_portfolio_performance(self, days: int = 30) -> Dict[str, Any]:
        """
        ポートフォリオパフォーマンスを計算
        
        Args:
            days: 分析期間（日数）
            
        Returns:
            dict: パフォーマンス指標
        """
        summary = self.get_portfolio_summary()
        
        if summary['position_count'] == 0:
            return {}
        
        # 基本指標
        performance = {
            'total_return': summary['total_pnl'],
            'total_return_pct': summary['total_pnl_pct'],
            'best_performer': None,
            'worst_performer': None,
            'diversification_score': self._calculate_diversification_score(summary['positions'])
        }
        
        # 最高・最低パフォーマンス銘柄
        if summary['positions']:
            best = max(summary['positions'], key=lambda x: x['pnl_pct'])
            worst = min(summary['positions'], key=lambda x: x['pnl_pct'])
            
            performance['best_performer'] = {
                'symbol': best['symbol'],
                'name': best['longName'],
                'return_pct': best['pnl_pct']
            }
            
            performance['worst_performer'] = {
                'symbol': worst['symbol'],
                'name': worst['longName'],
                'return_pct': worst['pnl_pct']
            }
        
        return performance
    
    def _calculate_diversification_score(self, positions: List[Dict]) -> float:
        """
        分散度スコアを計算（ウェイトの分散度を基準）
        
        Args:
            positions: ポジションリスト
            
        Returns:
            float: 分散度スコア（0-100）
        """
        if len(positions) <= 1:
            return 0.0
        
        weights = [pos['weight'] for pos in positions]
        
        # ウェイトの標準偏差から分散度を計算
        # 均等分散の場合のウェイト
        equal_weight = 100 / len(positions)
        
        # 実際のウェイトと均等ウェイトの差異
        weight_variance = sum((w - equal_weight) ** 2 for w in weights) / len(weights)
        max_variance = (100 - equal_weight) ** 2  # 最大分散（1つに100%集中）
        
        # 分散度スコア（0-100、100が最も分散）
        diversification_score = max(0, (1 - weight_variance / max_variance) * 100)
        
        return diversification_score
    
    def _add_to_history(self, action: str, symbol: str, shares: int, 
                       price: float, long_name: str):
        """
        取引履歴に追加
        
        Args:
            action: 取引種別（ADD, REMOVE, UPDATE）
            symbol: 銘柄コード
            shares: 株数
            price: 価格
            long_name: 会社名
        """
        history_entry = {
            'timestamp': datetime.now(),
            'action': action,
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'longName': long_name
        }
        
        st.session_state.portfolio_history.append(history_entry)
        
        # 履歴は最新100件まで保持
        if len(st.session_state.portfolio_history) > 100:
            st.session_state.portfolio_history = st.session_state.portfolio_history[-100:]
    
    def export_portfolio(self) -> pd.DataFrame:
        """
        ポートフォリオをDataFrameでエクスポート
        
        Returns:
            pd.DataFrame: ポートフォリオデータ
        """
        summary = self.get_portfolio_summary()
        
        if not summary['positions']:
            return pd.DataFrame()
        
        df = pd.DataFrame(summary['positions'])
        df = df[['symbol', 'longName', 'shares', 'avg_price', 'current_price', 
                'cost_basis', 'current_value', 'pnl', 'pnl_pct', 'weight']]
        
        # 列名を日本語に変更
        df.columns = [
            '銘柄コード', '会社名', '株数', '平均取得価格', '現在価格',
            '取得コスト', '現在価値', '損益', '損益率(%)', 'ウェイト(%)'
        ]
        
        return df