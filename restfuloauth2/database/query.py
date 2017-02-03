import json
from flask_restful import abort


class Query(object):
    """Database query helper."""

    INVALID_OPERATOR = 'Invalid operator'
    ITEM_NOT_FOUND = 'Item not found'
    ETAG_NOT_MATCHING = 'Etags do not match'
    VALID_CONDITION_OPERATORS = ['and', 'or']
    VALID_COLUMN_OPERATORS = ['=', '!=', '<', '<=', '>', '>=', 'like']
    COLUMN_REFERENCE = 'column'
    OPERATOR_REFERENCE = 'operator'
    VALUE_REFERENCE = 'value'
    CONDITIONS_REFERENCE = 'conditions'
    DEFAULT_PAGE = 1
    DEFAULT_MAX_RESULTS = 10
    DEFAULT_SORT = 'id-asc'
    DEFAULT_SEARCH = None

    @classmethod
    def valid_condition_operator(cls, operator):
        """Checks if the provided condition operator is valid."""
        return operator in cls.VALID_CONDITION_OPERATORS

    @classmethod
    def valid_column_operator(cls, operator):
        """Checks if the provided column operator is valid."""
        return operator in cls.VALID_COLUMN_OPERATORS

    @classmethod
    def from_json_or_abort(cls, data):
        """Recursive function that generates a text query from JSON data."""
        if isinstance(data, basestring):
            # If data is still a string load it as JSON.
            data = json.loads(data)
        # If column, operator and value are present we have a condition.
        if (cls.COLUMN_REFERENCE in data and cls.OPERATOR_REFERENCE in data and
                cls.VALUE_REFERENCE in data):
            # Abort if the operator is invalid.
            if not cls.valid_column_operator(data[cls.OPERATOR_REFERENCE]):
                abort(401, message=cls.INVALID_OPERATOR)
            # If the value is a string concat and return a quoted text query.
            if isinstance(data[cls.VALUE_REFERENCE], basestring):
                return (
                    data[cls.COLUMN_REFERENCE] +
                    data[cls.OPERATOR_REFERENCE] + '"' +
                    str(data[cls.VALUE_REFERENCE]) + '"'
                )
            # Concat and return a text query.
            return (
                data[cls.COLUMN_REFERENCE] +
                data[cls.OPERATOR_REFERENCE] +
                str(data[cls.VALUE_REFERENCE])
            )
        # If conditions and an operator are found we have a conditional.
        elif (cls.CONDITIONS_REFERENCE in data and cls.OPERATOR_REFERENCE in
                data):
            # Abort if the operator is invalid.
            if not cls.valid_condition_operator(data[cls.OPERATOR_REFERENCE]):
                abort(401, message=cls.INVALID_OPERATOR)
            # If there is a list of conditions send them to this same function.
            if isinstance(data[cls.CONDITIONS_REFERENCE], list):
                # Open group parenthesis.
                query = '('
                # Make recursive calls, resolve and concat childs.
                for i, condition in enumerate(data[cls.CONDITIONS_REFERENCE]):
                    query += cls.from_json_or_abort(condition)
                    if (len(data[cls.CONDITIONS_REFERENCE]) > 1 and
                            i != len(data[cls.CONDITIONS_REFERENCE])-1):
                        query += ' ' + data[cls.OPERATOR_REFERENCE] + ' '
                # Close group parenthesis and return the result.
                query += ')'
                return query

    @classmethod
    def get_item_or_abort(cls, item_cls, item_id, user):
        """Gets an item, if permitted, given the model and user's id."""
        model = item_cls.get_permitted(item_id, user)
        if not model:
            abort(404, message=cls.ITEM_NOT_FOUND)
        return model

    @classmethod
    def get_sort_attribute(cls, item_cls, sort):
        """Returns a model column to sort."""
        sort_column = sort.split('-')[0]
        sort_direction = sort.split('-')[1]
        sort_attribute = getattr(item_cls, sort_column)
        return getattr(sort_attribute, sort_direction)()
