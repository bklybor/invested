from table.models import StockTransactRecord, StockInventory, CashTransactionRecord
from home.models import Company


from utils.decision_table import decision_table

import json

class StockTransactRecordDecisionTable:

    # set in apps.py
    company_master_portfolio = None
    stock_management_settings = None
    site_settings = None
    model = None

    def __init__(self):
        self.decision_table = decision_table('StockTransactRecordDecisionTable')

    def __str__(self):
        return str(self.decision_table)

    #---decision table conditions---#
    
    def is_order_status_processing(self, order):
        return (
            order.order_status == order.__class__.STATUS.processing.name
        ) 

    def is_order_status_approved(self, order):
        return (
            order.order_status == order.__class__.STATUS.approved.name
        ) 

    def is_order_status_rejected(self, order):
        return (
            order.order_status == order.__class__.STATUS.rejected.name
        )

    def is_order_status_under_review(self, order):
        return (
            order.order_status == order.__class__.STATUS.under_review
        )
    
    def is_order_type_buy(self, order):
        return (
            order.order_type == order.__class__.TRANSACTION_TYPE.buy.name
        )
    
    def is_order_type_sell(self, order):
        return (
            order.order_type == order.__class__.TRANSACTION_TYPE.sell.name
        )

    def is_broker_review_requested(self, order):
        return (
            order.broker_review_requested
        )
    
    def is_order_class_internal(self, order):
        return (
            order.order_class == order.__class__.TRANSACTION_CLASS.internal.name
        )
    
    def is_order_class_external(self, order):
        return (
            order.order_class == order.__class__.TRANSACTION_CLASS.external.name
        )
    
    def is_order_class_undetermined(self, order):
        return (
            order.order_class == order.__class__.TRANSACTION_CLASS.undetermined.name
        )

    def are_ticker_and_quantity_in_inventory(self, order):
        return (
            (order.ticker in [x[0] for x in self.company_master_portfolio.stockinventory.all().values_list('ticker').distinct()]) and 
            (order.quantity <= self.company_master_portfolio.stockinventory.get(ticker= order.ticker).quantity)
        )

    def does_order_pass_internal_checks(self, order):
        return (
            ((order.quantity / self.company_master_portfolio.stockinventory.get(ticker= order.ticker).quantity) < self.stock_management_settings.internal_share_proportion_threshold) and        
            ((order.price * order.quantity) < self.stock_management_settings.internal_value_threshold)
        )

    def does_order_pass_external_checks(self, order):
        return (
            ((order.quantity/ 10000000) < self.stock_management_settings.external_share_proportion_threshold) and
            ((order.price * order.quantity) < self.stock_management_settings.external_value_threshold)
        )

    def is_value_of_order_leq_than_portfolio_cash(self, order):
        return (
            (order.price * order.quantity) <= order.portfolio.cash
        )

    #---decision table actions---#

    def save_order_class_as_internal(self, order):
        order.order_class = StockTransactRecord.TRANSACTION_CLASS.internal.name
        order.save()

    def save_order_class_as_external(self, order):
        order.order_class = StockTransactRecord.TRANSACTION_CLASS.external.name
        order.save()

    def save_order_status_as_approved(self, order):
        order.order_status = StockTransactRecord.STATUS.approved.name
        order.save()

    def save_order_status_as_rejected(self, order):
        order.order_status = StockTransactRecord.STATUS.rejected.name
        order.save()

    def remove_value_of_order_from_portfolio_cash(self, order):
        '''Removes value of order from client's portfolio and adds stock quantity to the StockInventory of this order's portfolio.'''
        order.portfolio.cash -= (order.price * order.quantity)
        order.order_status = StockTransactRecord.STATUS.completed.name
        order.portfolio.save()

        sti, created = StockInventory.objects.get_or_create(
            portfolio= order.portfolio,
            exchange_abbr= order.exchange_abbr,
            ticker= order.ticker,
        )
        sti.quantity += order.quantity
        sti.save()

        if order.order_class == StockTransactRecord.TRANSACTION_CLASS.internal.name:
            stock = self.company_master_portfolio.stockinventory.all().get(ticker= order.ticker)
            stock.quantity -= order.quantity
            stock.save()
            print(str(order.quantity) + " shares of " + order.ticker + " removed from company portfolio.")


    #---decision table setup---#
    def setup_decision_table(self):
        self.decision_table.add_condition(self.is_order_status_processing)
        self.decision_table.add_condition(self.is_order_status_approved)
        self.decision_table.add_condition(self.is_order_status_rejected)
        self.decision_table.add_condition(self.is_order_type_buy)
        self.decision_table.add_condition(self.is_order_type_sell)
        self.decision_table.add_condition(self.is_broker_review_requested)
        self.decision_table.add_condition(self.is_order_class_internal)
        self.decision_table.add_condition(self.is_order_class_external)
        self.decision_table.add_condition(self.is_order_class_undetermined)
        self.decision_table.add_condition(self.are_ticker_and_quantity_in_inventory)
        self.decision_table.add_condition(self.does_order_pass_internal_checks)
        self.decision_table.add_condition(self.does_order_pass_external_checks)
        self.decision_table.add_condition(self.is_value_of_order_leq_than_portfolio_cash)

        self.decision_table.add_action(self.save_order_class_as_internal)
        self.decision_table.add_action(self.save_order_status_as_approved)
        self.decision_table.add_action(self.save_order_class_as_external)
        self.decision_table.add_action(self.remove_value_of_order_from_portfolio_cash)
        self.decision_table.add_action(self.save_order_status_as_rejected)

        self.decision_table.add_case(
            result = {
                self.is_order_status_processing: 1,
                self.is_order_type_buy: 1,
                self.is_broker_review_requested: -1,
                self.is_order_class_undetermined: 1,
                self.are_ticker_and_quantity_in_inventory: 1,
            },
            actions = [self.save_order_class_as_internal]
        )

        self.decision_table.add_case(
            result = {
                self.is_order_status_processing: 1,
                self.is_order_type_buy: 1,
                self.is_broker_review_requested: -1,
                self.is_order_class_internal: 1,
                self.does_order_pass_internal_checks: 1,
            },
            actions = [self.save_order_status_as_approved]
        )

        self.decision_table.add_case(
            result = {
                self.is_order_status_processing: 1,
                self.is_order_type_buy: 1,
                self.is_broker_review_requested: -1,
                self.is_order_class_internal: 1,
                self.does_order_pass_internal_checks: -1,
            },
            actions = [self.save_order_status_as_rejected]
        )

        self.decision_table.add_case(
            result = {
                self.is_order_status_processing: 1,
                self.is_order_type_buy: 1,
                self.is_broker_review_requested: -1,
                self.is_order_class_undetermined: 1,
                self.are_ticker_and_quantity_in_inventory: -1,
            },
            actions = [self.save_order_class_as_external]
        )

        self.decision_table.add_case(
            result = {
                self.is_order_status_processing: 1,
                self.is_order_type_buy: 1,
                self.is_broker_review_requested: -1,
                self.is_order_class_external: 1,
                self.does_order_pass_external_checks: 1,
            },
            actions = [self.save_order_status_as_approved]
        )

        self.decision_table.add_case(
            result = {
                self.is_order_status_approved: 1,
                self.is_order_type_buy: 1,
                self.is_broker_review_requested: -1,
                self.is_order_class_undetermined: -1,
                self.is_value_of_order_leq_than_portfolio_cash: 1
            },
            actions = [self.remove_value_of_order_from_portfolio_cash]
        )

        self.decision_table.add_case(
            result = {
                self.is_order_status_approved: 1,
                self.is_order_type_buy: 1,
                self.is_broker_review_requested: -1,
                self.is_order_class_undetermined: -1,
                self.is_value_of_order_leq_than_portfolio_cash: -1
            },
            actions = [self.save_order_status_as_rejected]
        )

    def process_order(self, order):
        conditions = self.decision_table.conditions

        terminal_conditions = [
            StockTransactRecord.STATUS.rejected.name,
            StockTransactRecord.STATUS.completed.name
        ]
        while order.order_status not in terminal_conditions:
            condition_args = dict(
                zip(
                    list(conditions.keys()), len(conditions) * [(order,)]
                )
            )
            actions = self.decision_table.get_actions(condition_args)
            for action in actions:
                print(action.__name__)
                action(order)


class CashTransactionRecordDecisionTable:

    # set in apps.py
    site_settings = None
    cash_management_settings = None

    def __init__(self):
        self.decision_table = decision_table('CashTransactionRecordDecisionTable')

    def __str__(self):
        return str(self.decision_table)

    #---condition functions---#

    def is_type_external_deposit(self, transaction):
        return (
            transaction.transaction_type == CashTransactionRecord.TRANSACTION_TYPE.external_deposit.name
        )

    def is_type_external_withdrawal(self, transaction):
        return (
            transaction.transaction_type ==  CashTransactionRecord.TRANSACTION_TYPE.external_withdrawal.name
        )

    def is_type_stock_buy_cover(self, transaction):
        return transaction.transaction_type == CashTransactionRecord.TRANSACTION_TYPE.stock_buy_cover.name

    def is_type_stock_sell_proceeds(self, transaction):
        return transaction.transaction_type == CashTransactionRecord.TRANSACTION_TYPE.stock_sell_proceeds.name

    def is_client(self, transaction):
        return transaction.portfolio.owner.is_client

    def is_broker(self, transaction):
        return transaction.portfolio.owner.is_broker

    def is_company(self, transaction):
        return transaction.portfolio.owner.is_company

    def is_under_client_one_external_deposit_max(self, transaction):
        return (
            transaction.amount_in_USD <= self.cash_management_settings.client_one_external_deposit_max
        )

    def is_over_client_one_external_deposit_min(self, transaction):
        return (
            transaction.amount_in_USD >= self.cash_management_settings.client_one_external_deposit_min
        )

    def is_already_at_client_total_deposit_max(self, transaction):
        return (
            transaction.portfolio.cash == self.cash_management_settings.client_total_deposit_max
        )

    def would_deposit_be_over_client_total_deposit_max(self, transaction):
        return (
            (transaction.amount_in_USD + transaction.portfolio.cash) > self.cash_management_settings.client_total_deposit_max
        )

    def is_already_at_client_total_deposit_min(self, transaction):
        return (
            transaction.portfolio.cash == self.cash_management_settings.client_total_deposit_min
        )

    def would_withdrawal_be_under_client_total_deposit_min(self, transaction):
        return (
            (transaction.portfolio.cash - transaction.amount_in_USD) < self.cash_management_settings.client_total_deposit_min
        )

    def is_over_client_external_withdrawal_max(self, transaction):
        return (
            transaction.amount_in_USD > self.cash_management_settings.client_external_withdrawal_max
        )

    def is_status_approved(self, transaction):
        return transaction.status == CashTransactionRecord.STATUS.approved.name

    def is_status_rejected(self, transaction):
        return transaction.status == CashTransactionRecord.STATUS.rejected.name

    def is_status_processing(self, transaction):
        return transaction.status == CashTransactionRecord.STATUS.processing.name

    def is_status_under_review(self, transaction):
        return transaction.status == CashTransactionRecord.STATUS.under_review.name

    def is_status_completed(self, transaction):
        return transaction.status == CashTransactionRecord.STATUS.completed.name


    #---action functions---#

    def withdraw_cash_from_portfolio(self, transaction):
        transaction.portfolio.cash -= transaction.amount_in_USD
        transaction.status = CashTransactionRecord.STATUS.completed.name
        transaction.portfolio.save()

    def deposit_cash_into_portfolio(self, transaction):
        transaction.portfolio.cash += transaction.amount_in_USD
        transaction.status = CashTransactionRecord.STATUS.completed.name
        transaction.portfolio.save()

    def save_transaction_as_approved(self, transaction):
        transaction.status = CashTransactionRecord.STATUS.approved.name
        transaction.save()

    def save_transaction_as_rejected(self, transaction):
        transaction.status = CashTransactionRecord.STATUS.rejected.name
        transaction.save()

    def get_transaction_conditions(self, transaction):
        json_message = dict()

        for condition, condition_function in self.decision_table.conditions.items():
            print(condition_function.__name__ + ': ', condition_function(transaction))
            json_message[condition_function.__name__] = condition_function(transaction)

        print('')

        return json.dumps(json_message)

    #---decision table setup---#
    def setup_decision_table(self):
        self.decision_table.add_condition(self.is_type_external_deposit) # 0
        self.decision_table.add_condition(self.is_type_external_withdrawal) # 1
        self.decision_table.add_condition(self.is_client) # 2
        self.decision_table.add_condition(self.is_broker) # 3
        self.decision_table.add_condition(self.is_company) # 4
        self.decision_table.add_condition(self.is_under_client_one_external_deposit_max) # 5
        self.decision_table.add_condition(self.is_over_client_one_external_deposit_min) # 6
        self.decision_table.add_condition(self.is_already_at_client_total_deposit_max) # 7
        self.decision_table.add_condition(self.would_deposit_be_over_client_total_deposit_max) # 8
        self.decision_table.add_condition(self.is_already_at_client_total_deposit_min) # 9
        self.decision_table.add_condition(self.would_withdrawal_be_under_client_total_deposit_min) # 10
        self.decision_table.add_condition(self.is_over_client_external_withdrawal_max) # 11
        self.decision_table.add_condition(self.is_status_approved) # 12
        self.decision_table.add_condition(self.is_status_rejected) # 13
        self.decision_table.add_condition(self.is_status_processing) # 14
        self.decision_table.add_condition(self.is_status_under_review) # 15
        self.decision_table.add_condition(self.is_status_completed) # 16
        self.decision_table.add_condition(self.is_type_stock_buy_cover) # 17
        self.decision_table.add_condition(self.is_type_stock_sell_proceeds) # 18

        self.decision_table.add_action(self.withdraw_cash_from_portfolio)
        self.decision_table.add_action(self.deposit_cash_into_portfolio)
        self.decision_table.add_action(self.save_transaction_as_approved)
        self.decision_table.add_action(self.save_transaction_as_rejected)
        self.decision_table.add_action(self.get_transaction_conditions)
        
        # withdraw cash from client portfolio to external source
        self.decision_table.add_case(
            result= {
                self.is_type_external_withdrawal: 1,
                self.is_client: 1,
                self.is_status_approved: 1,
            },
            actions= [self.withdraw_cash_from_portfolio],
            name= "withdraw_cash_from_client_portfolio_to_external_source"
        )

        # deposit cash into client portfolio from external source
        self.decision_table.add_case(
            result= {
                self.is_type_external_deposit: 1,
                self.is_client: 1,
                self.is_status_approved: 1,
            },
            actions= [self.deposit_cash_into_portfolio],
            name= "deposit_cash_into_client_portfolio_from_external_source"
        )

        # approved for external deposit into client portfolio
        self.decision_table.add_case(
            result= {
                self.is_type_external_deposit: 1,
                self.is_client: 1,
                self.is_under_client_one_external_deposit_max: 1,
                self.is_over_client_one_external_deposit_min: 1,
                self.is_already_at_client_total_deposit_max: -1,
                self.would_deposit_be_over_client_total_deposit_max: -1,
                self.is_status_processing: 1,
            },
            actions= [self.save_transaction_as_approved],
            name= "approved_for_external_deposit_into_client_portfolio"
        )

        # approved for external withdrawal from client portfolio
        self.decision_table.add_case(
            result= {
                self.is_type_external_withdrawal: 1,
                self.is_client: 1,
                self.is_already_at_client_total_deposit_min: -1,
                self.would_withdrawal_be_under_client_total_deposit_min: -1,
                self.is_over_client_external_withdrawal_max: -1,
                self.is_status_processing: 1,
            },
            actions= [self.save_transaction_as_approved],
            name= "approved_for_external_withdrawal_from_client portfolio"
        )
        
        # approved for withdrawal from client portfolio to cover stock buy order
        self.decision_table.add_case(
            result= {
                self.is_type_stock_buy_cover: 1,
                self.is_client: 1,
                self.is_already_at_client_total_deposit_min: -1,
                self.would_withdrawal_be_under_client_total_deposit_min: -1,
                self.is_status_processing: 1,
            },
            actions= [self.save_transaction_as_approved],
            name= "approved_for_withdrawal_from_client_portfolio_to_cover_stock_buy_order"
        )

        # withdraw cash from client portfolio to cover stock buy order
        self.decision_table.add_case(
            result= {
                self.is_type_stock_buy_cover: 1,
                self.is_client: 1,
                self.is_status_approved: 1,
            },
            actions= [self.withdraw_cash_from_portfolio],
            name= "withdraw_cash_from_client_portfolio_cover_stock_buy_order"
        )
    
    def process_transaction(self, transaction):
        conditions = self.decision_table.conditions

        terminal_conditions = [
            CashTransactionRecord.STATUS.rejected.name,
            CashTransactionRecord.STATUS.completed.name
        ]

        while (transaction.status not in terminal_conditions):
            condition_args = dict(
                zip(
                    list(conditions.keys()), len(conditions) * [(transaction,)]
                )
            )
            #self.get_transaction_conditions(transaction)
            actions = self.decision_table.get_actions(condition_args)
            if actions:
                for action in actions:
                    print(action.__name__)
                    action(transaction)
            else: # catch all for conditions that yield no action
                #transaction.transaction_conditions = self.get_transaction_conditions(transaction)
                self.save_transaction_as_rejected(transaction)

        