from tabulate import tabulate
import numpy as np

class decision_table:
    """
    A generic decision table. There are three prinicple components: 
    1.) a dictionary of N 'conditions' where each key is a code number for a condition and 
        each value is the function that determines that condition; function must 
        return a boolean value
    2.) a dictionary of K 'actions' where each key is a code number for an action and each 
        value is the function that represents that action
    3.) a dictionary of C 'cases' where each member of the list is a dictionary that contains 
        a.) "mask", a dictionary which specifies which conditions to evaluate 
            for this case,
        b.) "result", a dicionary which contains the results after applying the 
            "mask" to the conditions
        c.) "actions", a list of actions listed by their code number; these are the 
            actions that execute when "result" results from applying the "mask" 
            to the "conditions"
            
    The structure:
    ```
    conditions = {
        0: condition_0_function,
        1: condition_1_function,
        .
        .
        .
        N: condition_N_function
    }
    
    actions = {
        0: action_0_function,
        1: action_1_function,
        .
        .
        .
        K: action_K_function
    }
    
    cases = {
        0: {
            "mask": {0: 1, 1: 0, ..., x <- self.conditions.keys(): y <- {1, 0}},
            "result": {0: 1, 1: 0, ..., x <- self.conditions.keys(): y <- {1, -1, 0}},
            "actions": [0,1, ..., x <- self.actions.keys()]
        },
        1: {
            "mask": {0: 1, 1: 0, ..., x <- self.conditions.keys(): y <- {1, 0}},
            "result": {0: 1, 1: 0, ..., x <- self.conditions.keys(): y <- {1, -1, 0}},
            "actions": [0,1, ..., x <- self.actions.keys()]
        },
        
           .
           .
           .
        
        C: {
            "mask": {0: 1, 1: 0, ..., x <- self.conditions.keys(): y <- {1, 0}},
            "result": {0: 1, 1: 0, ..., x <- self.conditions.keys(): y <- {1, -1, 0}},
            "actions": [0, 1, ..., x <- self.actions.keys()]
        }
    }
    ```
    """
    names_list = [] # decision tables should have unique names
    
    def __init__(self, name):
        if name in self.names_list:
            raise ValueError('name of decision table already exists')
        
        self.conditions = {} 
        self.actions = {}
        self.cases = {}
        
    def to_one_neg_one(self, boolean):
        """converts boolean value to 1, -1 for True, False"""
        return (2 * boolean) - 1
    
    def add_condition(self, condition_function):
        """
        Adds a condition to the decision table.
        
        :param condition_function: a condition function; must return a bool
        :type condition_function: callable
        """
        
        if not callable(condition_function):
            raise TypeError('condition_function is not callable.')
            
        if condition_function in [x for x in list(self.conditions.values())]:
            raise ValueError('condition_function already in this decision table\'s conditions')
            
        new_key = len(self.conditions)
        self.conditions[new_key] = condition_function
        
        for case in self.cases:
            case['mask'][new_key] = 0
            case['result'][new_key] = 0
    
    def add_action(self, action_function):
        """
        Adds an action to the decision table.
        
        :param action_function: the function to call for this action
        :type action_function: callable
        """
        
        if not callable(action_function):
            raise TypeError("action_function is not callable")
        
        if action_function in [x for x in list(self.actions.values())]:
            raise ValueError("action_function is already in this decision table's actions")
            
        new_key = len(self.actions)
        self.actions[new_key] = action_function
            
    def add_case(self, mask, result, actions):
        """
        Adds a case to the decision table. A case must have a 'mask' that is unique among all other cases.
        
        :param mask: the boolean mask to apply to the conditions
        :type mask: dict
        
        :param result: the result to get after applying the boolean mask to conditions
        :type result: dict
        
        :param actions: the functions to call when the case is activated
        :type actions: list of callables
        """
        
        # make sure case isn't already in decision table, only if there are cases to check
        if mask in [v['mask'] for k, v in self.cases.items()]:
            raise ValueError("case already exists in this decision table")
            
        if len(mask) != len(self.conditions):
            raise ValueError("not enough entries in 'mask'")
        if len(result) != len(self.conditions):
            raise ValueError("not enough entries in 'result'")
        if not actions:
            raise ValueError("need at least one action per case")
            
        actions_all_callable = all(callable(action) for action in actions)
        actions_all_non_callable = all(not callable(action) for action in actions)
        
        if not (actions_all_callable or actions_all_non_callable):
            raise TypeError("values in actions are either not all callable or not all non-callable")
        
        if actions_all_callable:
            # check to make sure that all given action functions exist in decision table already
            if not set(actions) <= set(list(self.actions.values())):
                raise KeyError('one or more functions given in actions does not exist in self.actions')
            
            coded_actions = []
            
            for k, v in self.actions.items():
                if v in actions:
                    coded_actions.append(k)
                
            actions = coded_actions
        
        mask_all_callable = all(callable(condition) for condition in list(mask.keys()))
        mask_all_non_callable = all(not callable(condition) for condition in list(mask.keys()))
        
        if not (mask_all_callable or mask_all_non_callable):
            raise TypeError("keys in mask are either not all callable or not all non-callable")
        
        if mask_all_callable:
            # check to make sure that all given condition functions exist in decision table already
            if not set(list(self.conditions.values())) <= set(list(mask.keys())):
                raise KeyError('one or more functions given in mask does not exist in self.conditions')
            
            coded_conditions = {}

            for key in self.conditions.keys():
                coded_conditions[key] = mask[self.conditions[key]]
            mask = coded_conditions
        
        result_all_callable = all(callable(condition) for condition in list(result.keys()))
        result_all_non_callable = all(not callable(condition) for condition in list(result.keys()))
        
        if not (result_all_callable or result_all_non_callable):
            raise TypeError("keys in result are either not all callable or not all non-callable")
        
        if result_all_callable:
            # check to make sure that all given condition functions exist in decision table already
            if not set(list(self.conditions.values())) <= set(list(result.keys())):
                raise KeyError('one or more functions given in result does not exist in self.conditions')
            
            coded_conditions = {}
            
            for key in self.conditions.keys():
                coded_conditions[key] = result[self.conditions[key]]
            result = coded_conditions
        
        new_key = len(self.cases)
        self.cases[new_key] = {
            'mask': mask,
            'result': result,
            'actions': actions
        }
            
    def get_actions(self, condition_args):
        """
        Returns the actions to execute given the results of the conditions when given
        the aruments in condition_args. Condition arguments not given in condition_args are
        interpreted as 'don't care' and treated accordingly. All functions and their arguments 
        must be given; which conditions to ignore should be given by the 'mask' for the case 
        for an action. Arguments to condition functions must be given in order!
        
        :param condition_args: a dictionary for which each key is either a code number for a 
            condition function, or a condition function that itself is already a part of 
            self.conditions; each value must be a tuple containing the arguments for the 
            given condition function and must be in order
        :type condition_args: dict
        """
        
        if not isinstance(condition_args, dict):
            raise TypeError('condition_args is not a dictionary')
            
        if len(condition_args) > len(self.conditions):
            raise ValueError('too many conditions given')
            
        if len(condition_args) < len(self.conditions):
            raise ValueError('not all conditions given')
        
        all_callable = all(callable(condition) for condition in list(condition_args.keys()))
        all_non_callable = all(not callable(condition) for condition in list(condition_args.keys()))
        if not (all_callable or all_non_callable):
            raise TypeError("keys in condition_args are either not all callable or not all non-callable")
            
        if all_callable:
            # check to make sure that all given condition functions exist in decision table already
            if not set(list(self.conditions.values())) <= set(list(condition_args.keys())):
                raise KeyError('one or more functions given in condition_args does not exist in self.conditions')
            
            coded_conditions = {}
            # if conditions are given by function,
            # convert to coded value

            for key in self.conditions.keys():
                coded_conditions[key] = condition_args[self.conditions[key]]
            condition_args = coded_conditions
            
        # check to make sure number of arguments given for each function are correct
        '''for key in list(self.conditions.keys()):
            internal_args = self.conditions[key].__code__.co_varnames
            given_args = condition_args[key]
            if len(internal_args) != len(given_args):
                raise ValueError('length of args for ' + str(self.conditions[key].__name__) + ' given as ' 
                                 + str(len(given_args)) + '; should be ' + str(len(internal_args)))'''
            
        requested_actions = []
        
        # for each case
        for case, case_info in self.cases.items():
            conditions = {}
            # for each key (code number) in self.conditions
            for key in list(self.conditions.keys()):
                # execute each condition function using the arguments given and store results
                conditions[key] = self.to_one_neg_one(self.conditions[key](*condition_args[key]))
            
            masked = {}
            for key in list(self.conditions.keys()):
                masked[key] = case_info['mask'][key] * conditions[key]
            
            print('case actions: ', [self.actions[x].__name__  for x in case_info['actions']])
            print('case conditions: ', case_info['result'])
            print('masked conditions: ', masked)
            if masked == case_info['result']:
                actions = []
                for action_code in case_info['actions']:
                    actions.append(self.actions[action_code])
                requested_actions += actions
                
        return requested_actions
    
    def __str__(self):
        cases_row = [[''] + list(self.cases.keys())]
        condition_rows = []
        action_rows = []
        
        for condition_num, condition in self.conditions.items():
            condition_row = [condition.__name__,]
            for case_num, case in self.cases.items():
                if case['result'][condition_num] == 1:
                    condition_row.append('Y')
                elif case['result'][condition_num] == -1:
                    condition_row.append('')
                else:
                    condition_row.append('-')
            condition_rows.append(condition_row)
        
        for action_num, action in self.actions.items():
            action_row = [action.__name__,]
            for case_num, case in self.cases.items():
                if action_num in case['actions']:
                    action_row.append('X')
                else:
                    action_row.append('')
            action_rows.append(action_row)
        
        buffer_row = [len(self.cases) * ['']]
        
        #print(cases_row)
        #print(condition_rows)
        #print(action_rows)
        
        table = cases_row + condition_rows + buffer_row + action_rows
        return tabulate(
            table, 
            headers = 'firstrow', 
            tablefmt = 'grid'
        )