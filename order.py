#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import robin_stocks.robinhood as rh

class Order():
    def __init__(self, order_info=None):
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
        
        if order_info != None:
            self.is_initialized = True
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
        else:
            self.is_initialized = False
    
    def __repr__(self):
        if self.is_initialized:
            return 'order_id:' + str(self.id)
        else:
            return 'Order class'
    
    def set_id(self, id):
        """
        Sets Order.id = id, then updates the order with the id
        """
        self.id = id
        
        self.is_initialized = True
        
        update()
    
    def is_filled(self):
        if self.is_initialized:
            if self.state == "filled":
                return True
            else:
                return False
        else:
            return -1
    
    def update(self, new_order_info=None):
        if is_initialized:
            if new_order_info == None:
                new_order_info = rh.orders.get_crypto_order_info(self.id)

            self.account_id = new_order_info['account_id']
            self.average_price = new_order_info['average_price']
            self.cancel_url = new_order_info['cancel_url']
            self.created_at = new_order_info['created_at']
            self.cumulative_quantity = new_order_info['cumulative_quantity']
            self.currency_pair_id = new_order_info['currency_pair_id']
            self.entered_price = new_order_info['entered_price']
            self.executions = new_order_info['executions']
            self.funding_source_id = new_order_info['funding_source_id']
            self.initiator_id = new_order_info['initiator_id']
            self.initiator_type = new_order_info['initiator_type']
            self.is_visible_to_user = new_order_info['is_visible_to_user']
            self.last_transaction_at = new_order_info['last_transaction_at']
            self.price = new_order_info['price']
            self.quantity = new_order_info['quantity']
            self.ref_id = new_order_info['ref_id']
            self.rounded_executed_notional = new_order_info['rounded_executed_notional']
            self.side = new_order_info['side']
            self.state = new_order_info['state']
            self.time_in_force = new_order_info['time_in_force']
            self.type = new_order_info['type']
            self.updated_at = new_order_info['updated_at']
        else:
            return -1
    
    def cancel(self):
        """
        Cancels the order and then updates the order
        """
        if self.is_initialized:
            updated_order_info = rh.orders.cancel_crypto_order(self.id)

            self.update(updated_order_info)
        else:
            return -1
    
    def cancel_all_orders(self):
        """
        Cancels all open crypto orders
        """
        rh.orders.cancel_all_crypto_orders()
    
    def get_all_orders(self):
        """
        Returns a list of orders (Order class) of all orders that have been processed for the account
        """
        completed_orders = rh.orders.get_all_crypto_orders()
        
        for i in range(len(completed_orders)):
            completed_orders[i] = Order(completed_orders[i])
        
        return completed_orders
    
    def get_all_open_orders(self):
        """
        Returns a list of orders (Order class) of all orders that are still open
        """
        open_orders = rh.orders.get_all_open_crypto_orders()
        
        for i in range(len(open_orders)):
            open_orders[i] = Order(open_orders[i])
        
        return open_orders
