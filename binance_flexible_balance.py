#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
币安理财活期账户总余额查询脚本
功能：获取所有活期赚币资产的总余额（以USDT计价）
"""

import ccxt
import os
import sys
from typing import Optional, Dict, List
from decimal import Decimal, ROUND_HALF_UP

class BinanceFlexibleBalanceTracker:
    """币安活期理财余额追踪器"""
    
    def __init__(self, api_key: str = None, secret_key: str = None):
        """
        初始化追踪器
        
        Args:
            api_key: 币安API密钥，如果为None则从环境变量读取
            secret_key: 币安密钥，如果为None则从环境变量读取
        """
        self.api_key = api_key or os.getenv('BINANCE_API_KEY')
        self.secret_key = secret_key or os.getenv('BINANCE_SECRET_KEY')
        
        if not self.api_key or not self.secret_key:
            raise ValueError("请设置BINANCE_API_KEY和BINANCE_SECRET_KEY环境变量，或直接传入参数")
        
        # 初始化交易所对象
        self.exchange = ccxt.binance({
            'apiKey': self.api_key,
            'secret': self.secret_key,
            'options': {
                'defaultType': 'spot',
            },
            'enableRateLimit': True,  # 启用频率限制
        })
        
    def get_flexible_positions(self) -> Optional[List[Dict]]:
        """
        获取所有活期赚币持仓信息
        
        Returns:
            包含持仓信息的列表，失败返回None
        """
        try:
            print("🔍 正在查询活期赚币持仓...")
            
            # 调用币安API获取活期持仓
            response = self.exchange.sapiGetSimpleEarnFlexiblePosition({})
            
            if response and 'rows' in response:
                positions = response['rows']
                print(f"✅ 成功获取 {len(positions)} 个活期持仓")
                return positions
            else:
                print("ℹ️ 未查询到任何活期持仓")
                return []
                
        except ccxt.AuthenticationError as e:
            print(f"❌ 身份验证失败，请检查API密钥: {e}")
        except ccxt.PermissionDenied as e:
            print(f"❌ 权限不足，请检查API权限设置: {e}")
        except ccxt.NetworkError as e:
            print(f"❌ 网络错误: {e}")
        except ccxt.ExchangeError as e:
            print(f"❌ 交易所错误: {e}")
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            
        return None
    
    def get_ticker_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        获取指定交易对的价格
        
        Args:
            symbols: 交易对列表，如 ['BTCUSDT', 'ETHUSDT']
            
        Returns:
            价格字典 {symbol: price}
        """
        prices = {}
        try:
            print("💰 正在获取价格信息...")
            
            # 获取所有ticker价格
            tickers = self.exchange.fetch_tickers()
            
            for symbol in symbols:
                if symbol in tickers:
                    prices[symbol] = float(tickers[symbol]['last'])
                else:
                    print(f"⚠️ 无法获取 {symbol} 的价格")
                    
        except Exception as e:
            print(f"❌ 获取价格信息失败: {e}")
            
        return prices
    
    def calculate_total_balance_usdt(self) -> Optional[Decimal]:
        """
        计算活期账户总余额（USDT计价）
        
        Returns:
            总余额（USDT），失败返回None
        """
        positions = self.get_flexible_positions()
        if positions is None:
            return None
            
        if not positions:
            print("📊 活期账户余额为 0")
            return Decimal('0')
        
        # 收集需要获取价格的资产
        assets_need_price = []
        usdt_balance = Decimal('0')
        
        print("\n📋 活期持仓详情:")
        print("-" * 50)
        
        for position in positions:
            asset = position.get('asset', 'UNKNOWN')
            total_amount = Decimal(str(position.get('totalAmount', '0')))
            
            print(f"💎 {asset}: {total_amount}")
            
            if asset == 'USDT':
                usdt_balance += total_amount
            elif total_amount > 0:
                # 需要获取价格的非USDT资产
                symbol = f"{asset}USDT"
                assets_need_price.append(symbol)
        
        # 获取价格信息
        if assets_need_price:
            prices = self.get_ticker_prices(assets_need_price)
        else:
            prices = {}
        
        # 计算总价值
        total_value_usdt = usdt_balance
        
        print("\n💰 价值计算:")
        print("-" * 50)
        
        if usdt_balance > 0:
            print(f"USDT: {usdt_balance} USDT")
        
        for position in positions:
            asset = position.get('asset', 'UNKNOWN')
            total_amount = Decimal(str(position.get('totalAmount', '0')))
            
            if asset != 'USDT' and total_amount > 0:
                symbol = f"{asset}USDT"
                if symbol in prices:
                    price = Decimal(str(prices[symbol]))
                    value_usdt = total_amount * price
                    total_value_usdt += value_usdt
                    print(f"{asset}: {total_amount} × ${price} = ${value_usdt.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)} USDT")
                else:
                    print(f"⚠️ {asset}: {total_amount} (无法获取价格)")
        
        return total_value_usdt
    
    def display_summary(self):
        """显示活期账户余额汇总"""
        print("="*60)
        print("🏦 币安理财活期账户余额查询")
        print("="*60)
        
        total_balance = self.calculate_total_balance_usdt()
        
        if total_balance is not None:
            print("\n" + "="*60)
            print(f"📊 活期账户总余额: ${total_balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)} USDT")
            print("="*60)
        else:
            print("\n❌ 查询失败，请检查网络连接和API配置")

def main():
    """主函数"""
    try:
        # 创建余额追踪器
        tracker = BinanceFlexibleBalanceTracker()
        
        # 显示余额汇总
        tracker.display_summary()
        
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("\n💡 使用方法:")
        print("1. 设置环境变量:")
        print("   export BINANCE_API_KEY='your_api_key'")
        print("   export BINANCE_SECRET_KEY='your_secret_key'")
        print("2. 或者直接在代码中传入API密钥")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 用户取消操作")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()