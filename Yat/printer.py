import yat.model as model


class PrettyPrinter:

    def __init__(self):
        self.arithmetic = False
        self.tabs = 0
        self.result_string = ""

    def visit(self, tree):
        self.result_string = ""
        tree.accept(self)
        print(self.result_string, end='')
        return self.result_string

    def custom_print(self, *args, sep='', end=''):
        self.result_string += "".join(map(str, args))

    def visit_conditional(self, tree):
        self.custom_print('\t' * self.tabs, "if (")
        self.arithmetic = True
        tree.condition.accept(self)
        self.arithmetic = False
        self.custom_print(") {", '\n')

        self.tabs += 1
        for operation in tree.if_true:
            operation.accept(self)
        self.tabs -= 1
        self.custom_print('\t' * self.tabs, "}")

        if tree.if_false is not None and len(tree.if_false) > 0:
            self.custom_print(" else {", '\n')
            self.tabs += 1
            for operation in tree.if_false:
                operation.accept(self)
            self.tabs -= 1
            self.custom_print('\t' * self.tabs, "}")
        self.custom_print(";", '\n')

    def visit_function_definition(self, tree):
        self.custom_print('\t' * self.tabs, "def ", tree.name, "(")
        function = tree.function
        if len(function.args) > 0:
            for i in range(len(function.args)):
                self.custom_print(function.args[i])
                if i != len(function.args) - 1:
                    self.custom_print(", ")
        self.custom_print(") {", '\n')

        self.tabs += 1
        for operation in function.body:
            operation.accept(self)
        self.tabs -= 1
        self.custom_print('\t' * self.tabs, "};", '\n')

    def visit_print(self, tree):
        self.custom_print('\t' * self.tabs, "print ")
        old_arithmetic = self.arithmetic
        self.arithmetic = True
        tree.expr.accept(self)
        self.arithmetic = old_arithmetic
        self.custom_print(";", '\n')

    def visit_read(self, tree):
        self.custom_print('\t' * self.tabs, "read ", tree.name)
        self.custom_print(";", '\n')

    def visit_number(self, tree):
        if self.arithmetic:
            self.custom_print(tree.value)
        else:
            self.custom_print('\t' * self.tabs, tree.value)
            self.custom_print(";", '\n')

    def visit_reference(self, tree):
        if self.arithmetic:
            self.custom_print(tree.name)
        else:
            self.custom_print('\t' * self.tabs, tree.name)
            self.custom_print(";", '\n')

    def visit_binary_operation(self, tree):
        if not self.arithmetic:
            self.custom_print('\t' * self.tabs)

        old_arithmetic = self.arithmetic
        self.arithmetic = True
        self.custom_print("(")
        tree.lhs.accept(self)
        self.custom_print(")")
        self.custom_print(" ", tree.op, " ")
        self.custom_print("(")
        tree.rhs.accept(self)
        self.custom_print(")")
        self.arithmetic = old_arithmetic

        if not self.arithmetic:
            self.custom_print(";", '\n')

    def visit_unary_operation(self, tree):
        if not self.arithmetic:
            self.custom_print('\t' * self.tabs)
        self.custom_print(tree.op, "(")

        old_arithmetic = self.arithmetic
        self.arithmetic = True
        tree.expr.accept(self)
        self.arithmetic = old_arithmetic

        self.custom_print(")")
        if not self.arithmetic:
            self.custom_print(";", '\n')

    def visit_function_call(self, tree):
        old_arithmetic = self.arithmetic
        self.arithmetic = True
        tree.fun_expr.accept(self)
        self.custom_print("(")
        for i in range(len(tree.args)):
            tree.args[i].accept(self)
            if i != len(tree.args) - 1:
                self.custom_print(", ")
        self.arithmetic = old_arithmetic
        self.custom_print(");", '\n')

    def visit_assign(self, tree):
        self.custom_print('\t' * self.tabs, tree.name)
        self.custom_print(" = ")
        self.arithmetic = True
        tree.value.accept(self)
        self.arithmetic = False
        self.custom_print(";", '\n')


class Tests:

    def test_number(self):
        ten = model.Number(10)
        printer = PrettyPrinter()
        result = printer.visit(ten)
        assert result == "10;\n"

    def test_empty_conditional(self):
        number = model.Number(42)
        conditional = model.Conditional(number, [], [])
        printer = PrettyPrinter()
        result = printer.visit(conditional)
        assert result == "if (42) {\n};\n"

    def test_empty_function_definition(self):
        function = model.Function([], [])
        definition = model.FunctionDefinition("foo", function)
        printer = PrettyPrinter()
        result = printer.visit(definition)
        assert result == "def foo() {\n};\n"

    def test_read(self):
        read = model.Read("x")
        printer = PrettyPrinter()
        result = printer.visit(read)
        assert result == "read x;\n"

    def test_print(self):
        number = model.Number(42)
        my_print = model.Print(number)
        printer = PrettyPrinter()
        result = printer.visit(my_print)
        assert result == "print 42;\n"

    def test_arithmetic_print(self):
        my_print = model.Print(model.BinaryOperation(model.Number(0), "+",
                                                     model.Number(1)))
        printer = PrettyPrinter()
        result = printer.visit(my_print)
        assert result == "print (0) + (1);\n"

    def test_reference(self):
        reference = model.Reference("x")
        printer = PrettyPrinter()
        result = printer.visit(reference)
        assert result == "x;\n"

    def test_assign(self):
        assign = model.Assign("x", model.Number(2))
        printer = PrettyPrinter()
        result = printer.visit(assign)
        assert result == "x = 2;\n"

    def test_unary_operation(self):
        number = model.Number(42)
        unary = model.UnaryOperation("-", number)
        printer = PrettyPrinter()
        result = printer.visit(unary)
        assert result == "-(42);\n"

    def test_function_call(self):
        reference = model.Reference("foo")
        call = model.FunctionCall(reference, [model.Number(1),
                                              model.Number(2),
                                              model.Number(3)])
        printer = PrettyPrinter()
        result = printer.visit(call)
        assert result == "foo(1, 2, 3);\n"

    def test_mixed_arithmetic(self):
        n0, n1, n2 = model.Number(1), model.Number(2), model.Number(3)
        add = model.BinaryOperation(n1, "+", n2)
        mul = model.BinaryOperation(n0, "*", add)
        printer = PrettyPrinter()
        result = printer.visit(mul)
        assert result == "(1) * ((2) + (3));\n"

    def test_mixed_conditional(self):
        scope = model.Scope()
        scope["a"] = model.Number(-10)
        scope["b"] = model.Number(5)
        scope["c"] = model.Number(10)

        """ if not (a == c) and b < c:
                print(a) """
        conditional = model.Conditional(model.BinaryOperation(
            model.UnaryOperation("!", model.BinaryOperation(
                model.Reference("a"), "==", model.Reference("c"))),
            "&&", model.BinaryOperation(
                model.Reference("b"), "<",
                model.Number(42))), [model.Assign("res",
                                                  model.Reference("a"))])
        printer = PrettyPrinter()
        result = printer.visit(conditional)
        assert (result == "if ((!((a) == (c))) && ((b) < (42))) {\n\tres =" +
                " a;\n};\n")

    def test_function_with_body_args(self):
        parent = model.Scope()
        parent["f"] = model.Function(("a", "b"),
                                     [model.Print(model.BinaryOperation(
                                         model.Reference("a"), "+",
                                         model.Reference("b")))])
        parent["x"] = model.Number(10)
        scope = model.Scope(parent)
        scope["y"] = model.Number(20)
        definition = model.FunctionDefinition("f", parent["f"])
        printer = PrettyPrinter()
        result = printer.visit(definition)
        assert result == "def f(a, b) {\n\tprint (a) + (b);\n};\n"

        definition.evaluate(scope)
        call = model.FunctionCall(model.Reference("f"),
                                  [model.Number(5),
                                   model.UnaryOperation("-", model.Number(3))])
        result = printer.visit(call)
        assert result == "f(5, -(3));\n"

    def my_tests(self):
        tests = []
        tests.append(self.test_number)
        tests.append(self.test_empty_conditional)
        tests.append(self.test_empty_function_definition)
        tests.append(self.test_read)
        tests.append(self.test_print)
        tests.append(self.test_arithmetic_print)
        tests.append(self.test_reference)
        tests.append(self.test_assign)
        tests.append(self.test_unary_operation)
        tests.append(self.test_function_call)
        tests.append(self.test_mixed_arithmetic)
        tests.append(self.test_mixed_conditional)
        tests.append(self.test_function_with_body_args)

        print("Running tests...")
        print("=" * 30)
        for test in tests:
            test()
            print("=" * 30)
        print("Passes all tests.")


if __name__ == "__main__":
    tests = Tests()
    tests.my_tests()
