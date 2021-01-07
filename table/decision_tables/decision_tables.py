from table.models import StockTransactRecord, StockInventory
from home.models import Company


from utils.decision_table import decision_table

class StockTransactRecordDecisionTable:

    # set in apps.py
    company_master_portfolio = None
    stock_management_settings = None
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
        sti = StockInventory(
            portfolio = order.portfolio, 
            exchange_abbr = order.exchange_abbr,
            ticker = order.ticker,
            quantity= order.quantity
        )
        sti.save()
        order.portfolio.save()

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
            mask = {
                self.is_order_status_processing: 1,
                self.is_order_status_approved: 1,
                self.is_order_status_rejected: 1,
                self.is_order_type_buy: 1,
                self.is_order_type_sell: 1,
                self.is_broker_review_requested: 1,
                self.is_order_class_internal: 1,
                self.is_order_class_external: 1,
                self.is_order_class_undetermined: 1,
                self.are_ticker_and_quantity_in_inventory: 1,
                self.does_order_pass_internal_checks: 0,
                self.does_order_pass_external_checks: 0,
                self.is_value_of_order_leq_than_portfolio_cash: 0
            },
            result = {
                self.is_order_status_processing: 1,
                self.is_order_status_approved: -1,
                self.is_order_status_rejected: -1,
                self.is_order_type_buy: 1,
                self.is_order_type_sell: -1,
                self.is_broker_review_requested: -1,
                self.is_order_class_internal: -1,
                self.is_order_class_external: -1,
                self.is_order_class_undetermined: 1,
                self.are_ticker_and_quantity_in_inventory: 1,
                self.does_order_pass_internal_checks: 0,
                self.does_order_pass_external_checks: 0,
                self.is_value_of_order_leq_than_portfolio_cash: 0
            },
            actions = [self.save_order_class_as_internal]
        )

        self.decision_table.add_case(
            mask = {
                self.is_order_status_processing: 1,
                self.is_order_status_approved: 1,
                self.is_order_status_rejected: 1,
                self.is_order_type_buy: 1,
                self.is_order_type_sell: 1,
                self.is_broker_review_requested: 1,
                self.is_order_class_internal: 1,
                self.is_order_class_external: 1,
                self.is_order_class_undetermined: 1,
                self.are_ticker_and_quantity_in_inventory: 0,
                self.does_order_pass_internal_checks: 1,
                self.does_order_pass_external_checks: 0,
                self.is_value_of_order_leq_than_portfolio_cash: 0
            },
            result = {
                self.is_order_status_processing: 1,
                self.is_order_status_approved: -1,
                self.is_order_status_rejected: -1,
                self.is_order_type_buy: 1,
                self.is_order_type_sell: -1,
                self.is_broker_review_requested: -1,
                self.is_order_class_internal: 1,
                self.is_order_class_external: -1,
                self.is_order_class_undetermined: -1,
                self.are_ticker_and_quantity_in_inventory: 0,
                self.does_order_pass_internal_checks: 1,
                self.does_order_pass_external_checks: 0,
                self.is_value_of_order_leq_than_portfolio_cash: 0
            },
            actions = [self.save_order_status_as_approved]
        )

        self.decision_table.add_case(
            mask = {
                self.is_order_status_processing: 1,
                self.is_order_status_approved: 1,
                self.is_order_status_rejected: 1,
                self.is_order_type_buy: 1,
                self.is_order_type_sell: 1,
                self.is_broker_review_requested: 1,
                self.is_order_class_internal: 1,
                self.is_order_class_external: 1,
                self.is_order_class_undetermined: 1,
                self.are_ticker_and_quantity_in_inventory: 1,
                self.does_order_pass_internal_checks: 0,
                self.does_order_pass_external_checks: 0,
                self.is_value_of_order_leq_than_portfolio_cash: 0
            },
            result = {
                self.is_order_status_processing: 1,
                self.is_order_status_approved: -1,
                self.is_order_status_rejected: -1,
                self.is_order_type_buy: 1,
                self.is_order_type_sell: -1,
                self.is_broker_review_requested: -1,
                self.is_order_class_internal: -1,
                self.is_order_class_external: -1,
                self.is_order_class_undetermined: 1,
                self.are_ticker_and_quantity_in_inventory: -1,
                self.does_order_pass_internal_checks: 0,
                self.does_order_pass_external_checks: 0,
                self.is_value_of_order_leq_than_portfolio_cash: 0
            },
            actions = [self.save_order_class_as_external]
        )

        self.decision_table.add_case(
            mask = {
                self.is_order_status_processing: 1,
                self.is_order_status_approved: 1,
                self.is_order_status_rejected: 1,
                self.is_order_type_buy: 1,
                self.is_order_type_sell: 1,
                self.is_broker_review_requested: 1,
                self.is_order_class_internal: 1,
                self.is_order_class_external: 1,
                self.is_order_class_undetermined: 1,
                self.are_ticker_and_quantity_in_inventory: 0,
                self.does_order_pass_internal_checks: 0,
                self.does_order_pass_external_checks: 1,
                self.is_value_of_order_leq_than_portfolio_cash: 0
            },
            result = {
                self.is_order_status_processing: 1,
                self.is_order_status_approved: -1,
                self.is_order_status_rejected: -1,
                self.is_order_type_buy: 1,
                self.is_order_type_sell: -1,
                self.is_broker_review_requested: -1,
                self.is_order_class_internal: -1,
                self.is_order_class_external: 1,
                self.is_order_class_undetermined: -1,
                self.are_ticker_and_quantity_in_inventory: 0,
                self.does_order_pass_internal_checks: 0,
                self.does_order_pass_external_checks: 1,
                self.is_value_of_order_leq_than_portfolio_cash: 0
            },
            actions = [self.save_order_status_as_approved]
        )

        self.decision_table.add_case(
            mask = {
                self.is_order_status_processing: 1,
                self.is_order_status_approved: 1,
                self.is_order_status_rejected: 1,
                self.is_order_type_buy: 1,
                self.is_order_type_sell: 1,
                self.is_broker_review_requested: 1,
                self.is_order_class_internal: 0,
                self.is_order_class_external: 0,
                self.is_order_class_undetermined: 1,
                self.are_ticker_and_quantity_in_inventory: 0,
                self.does_order_pass_internal_checks: 0,
                self.does_order_pass_external_checks: 0,
                self.is_value_of_order_leq_than_portfolio_cash: 1
            },
            result = {
                self.is_order_status_processing: -1,
                self.is_order_status_approved: 1,
                self.is_order_status_rejected: -1,
                self.is_order_type_buy: 1,
                self.is_order_type_sell: -1,
                self.is_broker_review_requested: -1,
                self.is_order_class_internal: 0,
                self.is_order_class_external: 0,
                self.is_order_class_undetermined: -1,
                self.are_ticker_and_quantity_in_inventory: 0,
                self.does_order_pass_internal_checks: 0,
                self.does_order_pass_external_checks: 0,
                self.is_value_of_order_leq_than_portfolio_cash: 1
            },
            actions = [self.remove_value_of_order_from_portfolio_cash]
        )

        self.decision_table.add_case(
            mask = {
                self.is_order_status_processing: 1,
                self.is_order_status_approved: 1,
                self.is_order_status_rejected: 1,
                self.is_order_type_buy: 1,
                self.is_order_type_sell: 1,
                self.is_broker_review_requested: 1,
                self.is_order_class_internal: 0,
                self.is_order_class_external: 0,
                self.is_order_class_undetermined: 1,
                self.are_ticker_and_quantity_in_inventory: 0,
                self.does_order_pass_internal_checks: 0,
                self.does_order_pass_external_checks: 0,
                self.is_value_of_order_leq_than_portfolio_cash: 1
            },
            result = {
                self.is_order_status_processing: -1,
                self.is_order_status_approved: 1,
                self.is_order_status_rejected: -1,
                self.is_order_type_buy: 1,
                self.is_order_type_sell: -1,
                self.is_broker_review_requested: -1,
                self.is_order_class_internal: 0,
                self.is_order_class_external: 0,
                self.is_order_class_undetermined: -1,
                self.are_ticker_and_quantity_in_inventory: 0,
                self.does_order_pass_internal_checks: 0,
                self.does_order_pass_external_checks: 0,
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
            '''print('order_status: ', order.order_status)
            print('order_value: ', (order.price * order.quantity))
            print('portfolio_cash: ', order.portfolio.cash)'''
            condition_args = dict(
                zip(
                    list(conditions.keys()), len(conditions) * [(order,)]
                )
            )
            actions = self.decision_table.get_actions(condition_args)
            for action in actions:
                print(action.__name__)
                action(order)

# from table.decision_tables.decision_tables import StockTransactRecordDecisionTable
# stdt = StockTransactRecordDecisionTable()
# stdt.setup_decision_table()
# stdt.decision_table.get_actions(dict(zip(list(stdt.decision_table.conditions.keys()), len(stdt.decision_table.conditions) * [(st,)])))