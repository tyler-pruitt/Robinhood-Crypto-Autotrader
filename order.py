#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import robin_stocks.robinhood as rh

class Order():
    def __init__(self, order_info):
        """
        order_info = {
        'account_id': 'some_id',
        'average_price': 'some_float',
        'cancel_url': 'some_url',
        'created_at': 'some_time',
        'cumulative_quantity': 'some_float',
        'currency_pair_id': 'some_id',
        'entered_price': 'amount_in_dollars_spent',
        'executions': [],
        'funding_source_id': None,
        'id': 'some_order_id',
        'initiator_id': None,
        'initiator_type': None,
        'is_visible_to_user': True,
        'last_transaction_at': None,
        'price': 'some_price',
        'quantity': 'some_quantity',
        'ref_id': 'some_id',
        'rounded_executed_notional': 'some_float',
        'side': 'buy_or_sell',
        'state': 'unconfirmed',
        'time_in_force': 'gtc',
        'type': 'market',
        'updated_at': 'some_time'
        }
        """
        
        self.account_id = order_info['account_id']
        self.average_price = order_info['average_price']
        self.cancel_url = order_info['cancel_url']
        self.created_at = order_info['created_at']
        self.cumulative_quantity = order_info['cumulative_quantity']
        self.currency_pair_id = order_info['currency_pair_id']
        self.entered_price = order_info['entered_price']
        self.executions = order_info['executions']
        self.funding_source_id = order_info['funding_source_id']
        self.id = order_info['id']
        self.initiator_id = order_info['initiator_id']
        self.initiator_type = order_info['initiator_type']
        self.is_visible_to_user = order_info['is_visible_to_user']
        self.last_transaction_at = order_info['last_transaction_at']
        self.price = order_info['price']
        self.quantity = order_info['quantity']
        self.ref_id = order_info['ref_id']
        self.rounded_executed_notional = order_info['rounded_executed_notional']
        self.side = order_info['side']
        self.state = order_info['state']
        self.time_in_force = order_info['time_in_force']
        self.type = order_info['type']
        self.updated_at = order_info['updated_at']
    
    def update(new_order_info):
        self.account_id = order_info['account_id']
        self.average_price = order_info['average_price']
        self.cancel_url = order_info['cancel_url']
        self.created_at = order_info['created_at']
        self.cumulative_quantity = order_info['cumulative_quantity']
        self.currency_pair_id = order_info['currency_pair_id']
        self.entered_price = order_info['entered_price']
        self.executions = order_info['executions']
        self.funding_source_id = order_info['funding_source_id']
        self.id = order_info['id']
        self.initiator_id = order_info['initiator_id']
        self.initiator_type = order_info['initiator_type']
        self.is_visible_to_user = order_info['is_visible_to_user']
        self.last_transaction_at = order_info['last_transaction_at']
        self.price = order_info['price']
        self.quantity = order_info['quantity']
        self.ref_id = order_info['ref_id']
        self.rounded_executed_notional = order_info['rounded_executed_notional']
        self.side = order_info['side']
        self.state = order_info['state']
        self.time_in_force = order_info['time_in_force']
        self.type = order_info['type']
        self.updated_at = order_info['updated_at']
    
    def cancel():
        updated_order_info = rh.cancel_crypto_order(self.id)
        
        self.update(updated_order_info)
