#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版币安活期理财余额查询脚本
"""

import ccxt
import os

def get_flexible_total_balance():
    """获取活期理财总余额（USDT计价）"""
    
    # 从环境变量获取API密钥
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    
    if not api_key or not secret_key:
        print("❌ 请先设置环境变量:")
        print("export BINANCE_API_KEY='your_api_key'")
        print("export BINANCE_SECRET_KEY='your_secret_key'")
        return None
    
    try:
        # 初始化币安交易所
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret_key,
            'options': {'defaultType': 'spot'},
            'enableRateLimit': True,
        })
        
        print("🔍 正在查询活期持仓...")
        
        # 获取活期持仓
        response = exchange.sapiGetSimpleEarnFlexiblePosition({})
        positions = response.get('rows', [])
        
        if not positions:
            print("📊 活期账户余额为 0 USDT")
            return 0
        
        # 获取价格信息
        print("💰 正在获取价格信息...")
        tickers = exchange.fetch_tickers()
        
        total_usdt = 0
        print("\n📋 持仓详情:")
        print("-" * 40)
        
        for position in positions:
            asset = position.get('asset', '')
            amount = float(position.get('totalAmount', 0))
            
            if amount <= 0:
                continue
                
            if asset == 'USDT':
                value_usdt = amount
                print(f"💎 {asset}: {amount:.4f} = ${value_usdt:.2f}")
            else:
                symbol = f"{asset}USDT"
                if symbol in tickers:
                    price = float(tickers[symbol]['last'])
                    value_usdt = amount * price
                    print(f"💎 {asset}: {amount:.4f} × ${price:.4f} = ${value_usdt:.2f}")
                else:
                    print(f"⚠️ {asset}: {amount:.4f} (无法获取价格)")
                    continue
            
            total_usdt += value_usdt
        
        print("-" * 40)
        print(f"📊 总余额: ${total_usdt:.2f} USDT")
        return total_usdt
        
    except ccxt.AuthenticationError:
        print("❌ API密钥验证失败，请检查密钥是否正确")
    except ccxt.PermissionDenied:
        print("❌ API权限不足，请确保已开启现货交易权限")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    return None

if __name__ == "__main__":
    print("🏦 币安活期理财余额查询")
    print("=" * 40)
    get_flexible_total_balance()