class Scope:

    """Scope - представляет доступ к значениям по именам
    (к функциям и именованным константам).
    Scope может иметь родителя, и если поиск по имени
    в текущем Scope не успешен, то если у Scope есть родитель,
    то поиск делегируется родителю.
    Scope должен поддерживать dict-like интерфейс доступа
    (см. на специальные функции __getitem__ и __setitem__)
    """

    def __init__(self, parent=None):
        self.parent = parent
        self.scope = {}

    def __getitem__(self, key):
        if key in self.scope:
            return self.scope[key]
        elif self.parent is not None:
            return self.parent[key]

    def __setitem__(self, key, value):
        if key in self.scope:
            self.scope[key] = value
        elif self.parent is not None:
            self.parent[key] = value
        else:
            self.scope[key] = value


class Number:

    """Number - представляет число в программе.
    Все числа в нашем языке целые."""

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def __hash__(self):
        return hash(self.value)

    def evaluate(self, scope):
        return self

    def accept(self, visitor):
        visitor.visit_number(self)


class Function:

    """Function - представляет функцию в программе.
    Функция - второй тип поддерживаемый языком.
    Функции можно передавать в другие функции,
    и возвращать из функций.
    Функция состоит из тела и списка имен аргументов.
    Тело функции это список выражений,
    т. е.  у каждого из них есть метод evaluate.
    Список имен аргументов - список имен
    формальных параметров функции.
    Аналогично Number, метод evaluate должен возвращать self.
    """

    def __init__(self, args, body):
        self.args = args
        self.body = body

    def evaluate(self, scope):
        return self


class FunctionDefinition:

    """FunctionDefinition - представляет определение функции,
    т. е. связывает некоторое имя с объектом Function.
    Результатом вычисления FunctionDefinition является
    обновление текущего Scope - в него
    добавляется новое значение типа Function."""

    def __init__(self, name, function):
        self.name = name
        self.function = function

    def evaluate(self, scope):
        scope[self.name] = self.function
        return self.function

    def accept(self, visitor):
        visitor.visit_function_definition(self)


class FunctionCall:

    """
    FunctionCall - представляет вызов функции в программе.
    В результате вызова функции должен создаваться новый объект Scope,
    являющий дочерним для текущего Scope
    (т. е. текущий Scope должен стать для него родителем).
    Новый Scope станет текущим Scope-ом при вычислении тела функции.
    """

    def __init__(self, fun_expr, args):
        self.fun_expr = fun_expr
        self.args = args

    def evaluate(self, scope):
        fun = self.fun_expr.evaluate(scope)
        new_scope = Scope(parent=scope)
        for i in range(len(self.args)):
            scope[fun.args[i]] = self.args[i].evaluate(new_scope)
        for operation in fun.body:
            res = operation.evaluate(new_scope)
        return res

    def accept(self, visitor):
        visitor.visit_function_call(self)


class Conditional:

    """
    Conditional - представляет ветвление в программе, т. е. if.
    """

    def __init__(self, condition, if_true, if_false=None):
        self.condition = condition
        self.if_true = if_true
        self.if_false = if_false

    def evaluate(self, scope):
        if self.condition.evaluate(scope).value != 0:
            for operation in self.if_true:
                current_result = operation.evaluate(scope)
        else:
            for operation in self.if_false:
                current_result = operation.evaluate(scope)
        return current_result

    def accept(self, visitor):
        visitor.visit_conditional(self)


class Reference:

    """Reference - получение объекта
    (функции или переменной) по его имени."""

    def __init__(self, name):
        self.name = name

    def evaluate(self, scope):
        return scope[self.name]

    def accept(self, visitor):
        visitor.visit_reference(self)


class BinaryOperation:

    """BinaryOperation - представляет бинарную операцию над двумя выражениями.
    Результатом вычисления бинарной операции является объект Number.
    Поддерживаемые операции:
    “+”, “-”, “*”, “/”, “%”, “==”, “!=”,
    “<”, “>”, “<=”, “>=”, “&&”, “||”."""

    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def evaluate(self, scope):
        evaluated_left = self.lhs.evaluate(scope).value
        evaluated_right = self.rhs.evaluate(scope).value
        op = self.op
        if op == '+':
            return Number(evaluated_left + evaluated_right)
        if op == '-':
            return Number(evaluated_left - evaluated_right)
        if op == '*':
            return Number(evaluated_left * evaluated_right)
        if op == '/':
            return Number(evaluated_left // evaluated_right)
        if op == '%':
            return Number(evaluated_left % evaluated_right)
        if op == '==':
            return Number(evaluated_left == evaluated_right)
        if op == '!=':
            return Number(evaluated_left != evaluated_right)
        if op == '<':
            return Number(evaluated_left < evaluated_right)
        if op == '>':
            return Number(evaluated_left > evaluated_right)
        if op == '<=':
            return Number(evaluated_left <= evaluated_right)
        if op == '>=':
            return Number(evaluated_left >= evaluated_right)
        if op == '&&':
            return Number(evaluated_left and evaluated_right)
        if op == '||':
            return Number(evaluated_left or evaluated_right)

    def accept(self, visitor):
        visitor.visit_binary_operation(self)


class UnaryOperation:

    """UnaryOperation - представляет унарную операцию над выражением.
    Результатом вычисления унарной операции является объект Number.
    Поддерживаемые операции: “-”, “!”."""

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def evaluate(self, scope):
        if self.op == '-':
            return Number(-self.expr.evaluate(scope).value)
        if self.op == '!':
            return Number(not self.expr.evaluate(scope).value)

    def accept(self, visitor):
        visitor.visit_unary_operation(self)


class Assign:

    """Assign - присваиваивание значения по имени"""

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def evaluate(self, scope):
        scope[self.name] = self.value.evaluate(scope)

    def accept(self, visitor):
        visitor.visit_assign(self)


class Print:

    """Print - печатает значение выражения на отдельной строке."""

    def __init__(self, expr):
        self.expr = expr

    def evaluate(self, scope):
        print(self.expr.evaluate(scope).value)
        return self.expr.evaluate(scope)

    def accept(self, visitor):
        visitor.visit_print(self)


class Read:

    """Read - читает число из стандартного потока ввода
     и обновляет текущий Scope.
     Каждое входное число располагается на отдельной строке
     (никаких пустых строк и лишних символов не будет).
     """

    def __init__(self, name):
        self.name = name

    def evaluate(self, scope):
        value = int(input())
        scope[self.name] = Number(value)

    def accept(self, visitor):
        visitor.visit_read(self)


class Tests:

    def test_number(self):
        scope = Scope()
        assert Number(10).evaluate(scope).value == 10

    def test_scope(self):
        scope = Scope()
        scope["a"] = Number(10)
        assert scope["a"].value == Number(10).value

    def test_print(self):
        scope = Scope()
        scope["a"] = Number(10)
        printed = Print(scope["a"]).evaluate(scope)
        assert printed.value == scope["a"].value

    def test_reference(self):
        scope = Scope()
        scope["a"] = Number(10)
        var = Reference("a").evaluate(scope)
        assert var.value == scope["a"].value

    def test_reference_parent(self):
        scope = Scope()
        scope["a"] = Number(10)
        child_scope = Scope(scope)
        var = Reference("a").evaluate(child_scope)
        assert var.value == scope["a"].value

    def test_assign(self):
        scope = Scope()
        scope["a"] = Number(10)
        Assign("b", scope["a"]).evaluate(scope)
        assert scope["b"].value == scope["a"].value

    def test_unary_operation(self):
        scope = Scope()
        scope["a"] = Number(10)
        result = UnaryOperation("-", scope["a"]).evaluate(scope)
        assert result.value == -scope["a"].value

        result = UnaryOperation("!", scope["a"]).evaluate(scope)
        assert result.value == (not scope["a"].value)

    def test_binary_operation(self):
        scope = Scope()
        scope["a"] = Number(10)
        scope["b"] = Number(20)
        result = BinaryOperation(scope["a"], "+", scope["b"]).evaluate(scope)
        assert result.value == scope["a"].value + scope["b"].value

        result = BinaryOperation(scope["a"], "-", scope["b"]).evaluate(scope)
        assert result.value == scope["a"].value - scope["b"].value

        result = BinaryOperation(scope["a"], "*", scope["b"]).evaluate(scope)
        assert result.value == scope["a"].value * scope["b"].value

        result = BinaryOperation(scope["a"], "/", scope["b"]).evaluate(scope)
        assert result.value == scope["a"].value // scope["b"].value

        result = BinaryOperation(scope["a"], "%", scope["b"]).evaluate(scope)
        assert result.value == scope["a"].value % scope["b"].value

        result = BinaryOperation(scope["a"], "==", scope["b"]).evaluate(scope)
        assert result.value == (scope["a"].value == scope["b"].value)

        result = BinaryOperation(scope["a"], "!=", scope["b"]).evaluate(scope)
        assert result.value == (scope["a"].value != scope["b"].value)

        result = BinaryOperation(scope["a"], "<", scope["b"]).evaluate(scope)
        assert result.value == (scope["a"].value < scope["b"].value)

        result = BinaryOperation(scope["a"], ">", scope["b"]).evaluate(scope)
        assert result.value == (scope["a"].value > scope["b"].value)

        result = BinaryOperation(scope["a"], "<=", scope["b"]).evaluate(scope)
        assert result.value == (scope["a"].value <= scope["b"].value)

        result = BinaryOperation(scope["a"], ">=", scope["b"]).evaluate(scope)
        assert result.value == (scope["a"].value >= scope["b"].value)

        result = BinaryOperation(scope["a"], "&&", scope["b"]).evaluate(scope)
        assert result.value == (scope["a"].value and scope["b"].value)

        result = BinaryOperation(scope["a"], "||", scope["b"]).evaluate(scope)
        assert result.value == (scope["a"].value or scope["b"].value)

    def test_conditional(self):
        scope = Scope()
        scope["a"] = Number(10)
        scope["b"] = Number(20)
        Conditional(BinaryOperation(Reference("a"), ">", Reference("b")),
                    [Assign("res", Reference("a"))],
                    [Assign("res", Reference("b"))]).evaluate(scope)
        assert scope["res"].value == scope["b"].value

    def test_mixed_conditional(self):
        scope = Scope()
        scope["a"] = Number(-10)
        scope["b"] = Number(5)
        scope["c"] = Number(10)

        """ if not (a == c) and b < c:
                print(a) """
        Conditional(BinaryOperation(UnaryOperation(
            "!", BinaryOperation(Reference("a"), "==", Reference("c"))),
                                    "&&", BinaryOperation(
                                        Reference("b"), "<", Reference("c"))),
                    [Assign("res", Reference("a"))]).evaluate(scope)
        assert scope["res"].value == scope["a"].value

    def test_function(self):
        scope = Scope()
        scope["a"] = Number(10)

        function = Function((), [Assign("a", BinaryOperation(
            Reference("a"), "*", Number(2))), Assign("res", Reference("a"))])
        FunctionDefinition("get__double_a", function).evaluate(scope)
        FunctionCall(Reference("get__double_a"), []).evaluate(scope)
        assert scope["res"].value == 20

    def my_tests(self):
        print("Running tests...")
        self.test_number()
        self.test_scope()
        self.test_print()
        self.test_reference()
        self.test_reference_parent()
        self.test_assign()
        self.test_unary_operation()
        self.test_binary_operation()
        self.test_conditional()
        self.test_mixed_conditional()
        self.test_function()
        print("Passes all tests")


if __name__ == "__main__":
    tests = Tests()
    tests.my_tests()
