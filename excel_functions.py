import math
import random
import platform
import statistics
from datetime import date, datetime

def sum_values(values):
    """
    Calculate the sum of a list of values.
    :param values: List of numbers.
    :return: Sum of the numbers.
    """
    return sum(values)

def average(values):
    """
    Calculate the average of a list of values.
    :param values: List of numbers.
    :return: Average of the numbers. Returns 0 if the list is empty.
    """
    return sum(values) / len(values) if values else 0

def round_value(value, digits):
    """
    Round a value to the specified number of decimal places.
    :param value: The number to round.
    :param digits: Number of decimal places to round to.
    :return: Rounded number.
    """
    return round(value, digits)

def int_value(value):
    """
    Convert a value to an integer by truncating the decimal part.
    :param value: The number to convert.
    :return: Integer part of the number.
    """
    return int(value)

def mod_value(a, b):
    """
    Calculate the remainder when a is divided by b.
    :param a: Dividend.
    :param b: Divisor.
    :return: Remainder of the division.
    """
    return a % b

def rand_value():
    """
    Generate a random floating-point number between 0 and 1.
    :return: Random number between 0 and 1.
    """
    return random.random()

def pi_value():
    """
    Get the value of pi.
    :return: The mathematical constant pi.
    """
    return math.pi

def sin_value(angle):
    """
    Calculate the sine of an angle (in degrees).
    :param angle: Angle in degrees.
    :return: Sine of the angle.
    """
    return math.sin(math.radians(angle))

def cos_value(angle):
    """
    Calculate the cosine of an angle (in degrees).
    :param angle: Angle in degrees.
    :return: Cosine of the angle.
    """
    return math.cos(math.radians(angle))

def tan_value(angle):
    """
    Calculate the tangent of an angle (in degrees).
    :param angle: Angle in degrees.
    :return: Tangent of the angle.
    """
    return math.tan(math.radians(angle))

def count_values(values):
    """
    Count the number of numeric values in a list.
    :param values: List of values.
    :return: Number of numeric values.
    """
    return sum(1 for v in values if isinstance(v, (int, float)))

def counta_values(values):
    """
    Count the number of non-empty values in a list.
    :param values: List of values.
    :return: Number of non-empty values.
    """
    return sum(1 for v in values if v is not None and v != "")

def countif_values(values, condition):
    """
    Count the number of values that satisfy a condition.
    :param values: List of values.
    :param condition: A string representing the condition (e.g., ">10").
    :return: Number of values satisfying the condition.
    """
    operator, threshold = condition[0], float(condition[1:])
    if operator == ">":
        return sum(1 for v in values if v > threshold)
    elif operator == "<":
        return sum(1 for v in values if v < threshold)
    elif operator == "=":
        return sum(1 for v in values if v == threshold)
    else:
        raise ValueError("Unsupported operator")

def max_value(values):
    """
    Get the maximum value in a list.
    :param values: List of values.
    :return: Maximum value.
    """
    return max(values)

def min_value(values):
    """
    Get the minimum value in a list.
    :param values: List of values.
    :return: Minimum value.
    """
    return min(values)

def median_value(values):
    """
    Calculate the median of a list of values.
    :param values: List of values.
    :return: Median value.
    """
    sorted_values = sorted(values)
    n = len(sorted_values)
    if n % 2 == 0:
        return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
    else:
        return sorted_values[n // 2]

def stdev_p(values):
    """
    Calculate the population standard deviation of a list of values.
    :param values: List of values.
    :return: Population standard deviation.
    """
    return statistics.pstdev(values)

def stdev_s(values):
    """
    Calculate the sample standard deviation of a list of values.
    :param values: List of values.
    :return: Sample standard deviation.
    """
    return statistics.stdev(values)

def var_p(values):
    """
    Calculate the population variance of a list of values.
    :param values: List of values.
    :return: Population variance.
    """
    return statistics.pvariance(values)

def var_s(values):
    """
    Calculate the sample variance of a list of values.
    :param values: List of values.
    :return: Sample variance.
    """
    return statistics.variance(values)

def text_format(value, format_spec):
    """
    Format a value as a string using a specified format.
    :param value: Value to format.
    :param format_spec: Format specification (e.g., ".2f").
    :return: Formatted string.
    """
    return format(value, format_spec)

def left(text, num_chars):
    """
    Extract a specified number of characters from the start of a string.
    :param text: Input string.
    :param num_chars: Number of characters to extract.
    :return: Extracted substring.
    """
    return text[:num_chars]

def right(text, num_chars):
    """
    Extract a specified number of characters from the end of a string.
    :param text: Input string.
    :param num_chars: Number of characters to extract.
    :return: Extracted substring.
    """
    return text[-num_chars:]

def mid(text, start_pos, num_chars):
    """
    Extract a substring from a string, starting at a specified position.
    :param text: Input string.
    :param start_pos: Starting position (1-based).
    :param num_chars: Number of characters to extract.
    :return: Extracted substring.
    """
    return text[start_pos - 1:start_pos - 1 + num_chars]

def length(text):
    """
    Calculate the length of a string.
    :param text: Input string.
    :return: Length of the string.
    """
    return len(text)

def trim(text):
    """
    Remove extra spaces from a string, leaving only single spaces between words.
    :param text: Input string.
    :return: Trimmed string.
    """
    return " ".join(text.split())

def concat(*args):
    """
    Concatenate multiple strings into one.
    :param args: Strings to concatenate.
    :return: Concatenated string.
    """
    return "".join(map(str, args))

def textjoin(separator, *args):
    """
    Join multiple strings using a specified separator.
    :param separator: Separator string.
    :param args: Strings to join.
    :return: Joined string.
    """
    return separator.join(map(str, args))

def search(substring, text):
    """
    Find the position of a substring in a string (case-insensitive).
    :param substring: Substring to find.
    :param text: Input string.
    :return: Position of the substring (1-based) or -1 if not found.
    """
    return text.lower().find(substring.lower()) + 1

def find(substring, text):
    """
    Find the position of a substring in a string (case-sensitive).
    :param substring: Substring to find.
    :param text: Input string.
    :return: Position of the substring (1-based) or -1 if not found.
    """
    try:
        return text.index(substring) + 1
    except ValueError:
        return -1

def today():
    """
    Get the current date.
    :return: Current date as a datetime.date object.
    """
    return date.today()

def now():
    """
    Get the current date and time.
    :return: Current date and time as a datetime.datetime object.
    """
    return datetime.now()

def create_date(year, month, day):
    """
    Create a date object from year, month, and day.
    :param year: Year.
    :param month: Month.
    :param day: Day.
    :return: datetime.date object.
    """
    return date(year, month, day)

def get_year(date_obj):
    """
    Extract the year from a date object.
    :param date_obj: datetime.date object.
    :return: Year as an integer.
    """
    return date_obj.year

def get_month(date_obj):
    """
    Extract the month from a date object.
    :param date_obj: datetime.date object.
    :return: Month as an integer.
    """
    return date_obj.month

def get_day(date_obj):
    """
    Extract the day from a date object.
    :param date_obj: datetime.date object.
    :return: Day as an integer.
    """
    return date_obj.day

def get_hour(datetime_obj):
    """
    Extract the hour from a datetime object.
    :param datetime_obj: datetime.datetime object.
    :return: Hour as an integer.
    """
    return datetime_obj.hour

def get_minute(datetime_obj):
    """
    Extract the minute from a datetime object.
    :param datetime_obj: datetime.datetime object.
    :return: Minute as an integer.
    """
    return datetime_obj.minute

def get_second(datetime_obj):
    """
    Extract the second from a datetime object.
    :param datetime_obj: datetime.datetime object.
    :return: Second as an integer.
    """
    return datetime_obj.second

def datedif(start_date, end_date, unit):
    """
    Calculate the difference between two dates in years, months, or days.
    :param start_date: Start date (datetime.date).
    :param end_date: End date (datetime.date).
    :param unit: Unit of difference ("Y" for years, "M" for months, "D" for days).
    :return: Difference in the specified unit.
    """
    delta = end_date - start_date
    if unit == "Y":
        return end_date.year - start_date.year - ((end_date.month, end_date.day) < (start_date.month, start_date.day))
    elif unit == "M":
        return (end_date.year - start_date.year) * 12 + end_date.month - start_date.month - (end_date.day < start_date.day)
    elif unit == "D":
        return delta.days
    else:
        raise ValueError("Unsupported unit. Use 'Y', 'M', or 'D'.")

def weekday(date_obj):
    """
    Get the day of the week for a date object.
    :param date_obj: datetime.date object.
    :return: Day of the week as an integer (1=Sunday, 7=Saturday).
    """
    return date_obj.isoweekday() % 7 + 1

def vlookup(value, table, col_index):
    """
    Perform a vertical lookup in a table.
    :param value: Value to search for in the first column.
    :param table: List of lists representing the table.
    :param col_index: Column index to return (1-based).
    :return: Value from the specified column or None if not found.
    """
    for row in table:
        if row[0] == value:
            return row[col_index - 1]
    return None

def hlookup(value, table, row_index):
    """
    Perform a horizontal lookup in a table.
    :param value: Value to search for in the first row.
    :param table: List of lists representing the table.
    :param row_index: Row index to return (1-based).
    :return: Value from the specified row or None if not found.
    """
    header = table[0]
    for i, header_value in enumerate(header):
        if header_value == value:
            return table[row_index - 1][i]
    return None

def index(table, row_index, col_index):
    """
    Return the value at a specific row and column in a table.
    :param table: List of lists representing the table.
    :param row_index: Row index (1-based).
    :param col_index: Column index (1-based).
    :return: Value at the specified row and column.
    """
    return table[row_index - 1][col_index - 1]

def match(value, array, match_type=0):
    """
    Find the position of a value in an array.
    :param value: Value to find.
    :param array: List of values.
    :param match_type: Match type (0 for exact match).
    :return: Position of the value (1-based) or None if not found.
    """
    if match_type == 0:
        for i, item in enumerate(array):
            if item == value:
                return i + 1
    return None

def xlookup(value, lookup_array, return_array):
    """
    Perform a flexible lookup in a list.
    :param value: Value to search for.
    :param lookup_array: List of values to search in.
    :param return_array: List of values to return corresponding to the lookup.
    :return: Matched value from the return array or None if not found.
    """
    for i, lookup_value in enumerate(lookup_array):
        if lookup_value == value:
            return return_array[i]
    return None

def offset(table, start_row, start_col, row_offset, col_offset):
    """
    Return the value at a position offset from a starting point in a table.
    :param table: List of lists representing the table.
    :param start_row: Starting row index (1-based).
    :param start_col: Starting column index (1-based).
    :param row_offset: Row offset from the starting point.
    :param col_offset: Column offset from the starting point.
    :return: Value at the calculated position.
    """
    new_row = start_row + row_offset - 1
    new_col = start_col + col_offset - 1
    return table[new_row][new_col]

def conditional_if(condition, value_if_true, value_if_false):
    """
    Return one of two values based on a condition.
    :param condition: Boolean condition.
    :param value_if_true: Value to return if condition is True.
    :param value_if_false: Value to return if condition is False.
    :return: Value based on the condition.
    """
    return value_if_true if condition else value_if_false

def logical_and(*conditions):
    """
    Check if all conditions are True.
    :param conditions: List of conditions.
    :return: True if all conditions are True, otherwise False.
    """
    return all(conditions)

def logical_or(*conditions):
    """
    Check if any condition is True.
    :param conditions: List of conditions.
    :return: True if any condition is True, otherwise False.
    """
    return any(conditions)

def logical_not(condition):
    """
    Negate a boolean condition.
    :param condition: Boolean condition.
    :return: Negated value of the condition.
    """
    return not condition

def is_blank(value):
    """
    Check if the given value is blank (None or empty string).
    :param value: Value to check.
    :return: True if blank, False otherwise.
    """
    return value is None or value == ""

def is_error(expression):
    """
    Check if an expression causes an error.
    :param expression: Expression to evaluate.
    :return: True if there is an error, False otherwise.
    """
    try:
        eval(expression)
        return False
    except Exception:
        return True

def value_type(value):
    """
    Get the type of a value (1 for number, 2 for text, 4 for boolean, 16 for error).
    :param value: Value to check.
    :return: Integer indicating type.
    """
    if isinstance(value, (int, float)):
        return 1  # Number
    elif isinstance(value, str):
        return 2  # Text
    elif isinstance(value, bool):
        return 4  # Boolean
    elif isinstance(value, Exception):
        return 16  # Error
    else:
        return 0  # Unknown

def filter_array(array, condition):
    """
    Filter an array based on a list of boolean conditions.
    :param array: List of values to filter.
    :param condition: List of boolean values.
    :return: Filtered list.
    """
    return [val for val, cond in zip(array, condition) if cond]

def unique(array):
    """
    Get unique values from an array.
    :param array: List of values.
    :return: List of unique values.
    """
    return list(set(array))

def sort_array(array, reverse=False):
    """
    Sort an array in ascending or descending order.
    :param array: List of values to sort.
    :param reverse: If True, sort in descending order.
    :return: Sorted list.
    """
    return sorted(array, reverse=reverse)

def sequence(n, step=1, start=1):
    """
    Generate a sequence of numbers.
    :param n: Number of elements in the sequence.
    :param step: Step size between elements.
    :param start: Starting number of the sequence.
    :return: List of numbers in sequence.
    """
    return list(range(start, start + n * step, step))

def convert(value, from_unit, to_unit):
    """
    Convert a value between units (e.g., meters to centimeters).
    :param value: Value to convert.
    :param from_unit: Source unit.
    :param to_unit: Target unit.
    :return: Converted value.
    """
    conversion_factors = {
        "m": 1,  # Meter
        "cm": 100  # Centimeter
    }
    return value * (conversion_factors[to_unit] / conversion_factors[from_unit])

def dec2bin(value):
    """
    Convert a decimal number to binary.
    :param value: Decimal number.
    :return: Binary representation as a string.
    """
    return bin(value)[2:]

def hex2dec(value):
    """
    Convert a hexadecimal string to decimal.
    :param value: Hexadecimal string.
    :return: Decimal number.
    """
    return int(value, 16)

# Add new implementations to the output examples
def output_examples():
    """
    Demonstrate the usage of various functions by printing example outputs.
    """
    print("--- Basic Math Functions ---")
    print("Sum of [1, 2, 3]:", sum_values([1, 2, 3]))
    print("Average of [1, 2, 3]:", average([1, 2, 3]))
    print("Round 3.14159 to 2 decimal places:", round_value(3.14159, 2))
    print("Integer part of 3.75:", int_value(3.75))
    print("Modulus of 10 % 3:", mod_value(10, 3))
    print("Random value between 0 and 1:", rand_value())
    print("Value of Pi:", pi_value())

    print("\n--- Trigonometric Functions ---")
    print("Sine of 30 degrees:", sin_value(30))
    print("Cosine of 45 degrees:", cos_value(45))
    print("Tangent of 60 degrees:", tan_value(60))

    print("\n--- Text Functions ---")
    print("Left 3 characters of 'HelloWorld':", left("HelloWorld", 3))
    print("Right 5 characters of 'HelloWorld':", right("HelloWorld", 5))
    print("Middle 4 characters starting at position 3 of 'HelloWorld':", mid("HelloWorld", 3, 4))
    print("Length of 'HelloWorld':", length("HelloWorld"))
    print("Trimmed '  Hello   World  ':", trim("  Hello   World  "))
    print("Concatenation of 'Hello' and 'World':", concat("Hello", "World"))
    print("Join 'Hello' and 'World' with '-':", textjoin("-", "Hello", "World"))

    print("\n--- Date and Time Functions ---")
    print("Today's date:", today())
    print("Current datetime:", now())
    print("Create date 2025-01-17:", create_date(2025, 1, 17))
    print("Year of date 2025-01-17:", get_year(create_date(2025, 1, 17)))
    print("Month of date 2025-01-17:", get_month(create_date(2025, 1, 17)))
    print("Day of date 2025-01-17:", get_day(create_date(2025, 1, 17)))
    print("Difference in days between 2025-01-01 and 2025-01-17:", datedif(create_date(2025, 1, 1), create_date(2025, 1, 17), "D"))

    print("\n--- Lookup Functions ---")
    table = [[101, "Apple"], [102, "Banana"], [103, "Cherry"]]
    print("VLOOKUP for ID 102:", vlookup(102, table, 2))
    print("INDEX of row 2, column 2:", index(table, 2, 2))

    print("\n--- Logical Functions ---")
    print("IF condition (10 > 5):", conditional_if(10 > 5, "Yes", "No"))
    print("AND condition (True, True):", logical_and(True, True))
    print("OR condition (True, False):", logical_or(True, False))
    print("NOT condition (True):", logical_not(True))

    print("\n--- Statistical Functions ---")
    print("Maximum of [1, 2, 3]:", max_value([1, 2, 3]))
    print("Minimum of [1, 2, 3]:", min_value([1, 2, 3]))
    print("Median of [1, 2, 3]:", median_value([1, 2, 3]))

    print("\n--- Information Functions ---")
    print("Is blank (None):", is_blank(None))
    print("Is error ('1/0'):", is_error("1/0"))
    print("Value type (123):", value_type(123))

    print("\n--- Array Functions ---")
    print("Filter [1, 2, 3] with condition [True, False, True]:", filter_array([1, 2, 3], [True, False, True]))
    print("Unique values in [1, 2, 2, 3]:", unique([1, 2, 2, 3]))
    print("Sort [3, 1, 2]:", sort_array([3, 1, 2]))
    print("Sequence of 5:", sequence(5))

    print("\n--- Engineering Functions ---")
    print("Convert 1 meter to centimeters:", convert(1, "m", "cm"))
    print("Decimal to binary (10):", dec2bin(10))
    print("Hexadecimal to decimal ('A'):", hex2dec("A"))

if __name__ == "__main__":

    # Call the demonstration function
    output_examples()


