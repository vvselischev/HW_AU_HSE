import yat.model as model


class ConstantFolder:

    def __init__(self):
        pass

    def visit(self, tree):
        tree.accept(self)
        tree = self.get_constant_value(tree)
        return tree

    def check_num_num(self, tree):
        return isinstance(tree.lhs, model.Number) and \
               isinstance(tree.rhs, model.Number)

    def check_num_ref(self, tree):
        return isinstance(tree.lhs, model.Number) and \
               isinstance(tree.rhs, model.Reference) and \
               tree.lhs.value == 0 and tree.op == "*"

    def check_ref_num(self, tree):
        return isinstance(tree.lhs, model.Reference) and \
               isinstance(tree.rhs, model.Number) and \
               tree.rhs.value == 0 and tree.op == "*"

    def check_ref_ref(self, tree):
        return isinstance(tree.lhs, model.Reference) and \
               isinstance(tree.rhs, model.Reference) and \
               tree.lhs.name == tree.rhs.name and tree.op == "-"

    def get_constant_value(self, tree):
        if isinstance(tree, model.BinaryOperation):
            if self.check_num_num(tree):
                return tree.evaluate(model.Scope())
            if self.check_num_ref(tree) or self.check_ref_num(tree) or \
               self.check_ref_ref(tree):
                return model.Number(0)

        if isinstance(tree, model.UnaryOperation):
            if isinstance(tree.expr, model.Number):
                return tree.evaluate(model.Scope())

        return tree

    def visit_conditional(self, tree):
        tree.condition.accept(self)
        tree.condition = self.get_constant_value(tree.condition)

        for operation in tree.if_true:
            operation.accept(self)
            operation = self.get_constant_value(operation)

        if tree.if_false is not None:
            for operation in tree.if_false:
                operation.accept(self)
                operation = self.get_constant_value(operation)

    def visit_function_definition(self, tree):
        for operation in tree.function.body:
            operation.accept(self)
            operation = self.get_constant_value(operation)

    def visit_print(self, tree):
        tree.expr.accept(self)
        tree.expr = self.get_constant_value(tree.expr)

    def visit_read(self, tree):
        pass

    def visit_number(self, tree):
        pass

    def visit_reference(self, tree):
        pass

    def visit_binary_operation(self, tree):
        tree.lhs.accept(self)
        tree.rhs.accept(self)

        tree.lhs = self.get_constant_value(tree.lhs)
        tree.rhs = self.get_constant_value(tree.rhs)

    def visit_unary_operation(self, tree):
        tree.expr.accept(self)
        tree.expr = self.get_constant_value(tree.expr)

    def visit_function_call(self, tree):
        tree.fun_expr.accept(self)
        tree.fun_expr = self.get_constant_value(tree.fun_expr)

        for i in range(len(tree.args)):
            tree.args[i].accept(self)
            tree.args[i] = self.get_constant_value(tree.args[i])

    def visit_assign(self, tree):
        tree.value.accept(self)
        tree.value = self.get_constant_value(tree.value)


class Tests:

    def test_num_num(self):
        n0, n1, n2 = model.Number(4), model.Number(2), model.Number(3)
        mul = model.BinaryOperation(n0, "*", model.BinaryOperation(n1, "+",
                                                                   n2))
        folder = ConstantFolder()
        tree = folder.visit(mul)
        assert isinstance(tree, model.Number) and tree.value == 20

    def test_num_ref(self):
        scope = model.Scope()
        scope["a"] = model.Number(10)
        op = model.BinaryOperation(model.Number(0), "*",
                                   model.Reference("a"))
        folder = ConstantFolder()
        tree = folder.visit(op)
        assert isinstance(tree, model.Number) and tree.value == 0

    def test_num_ref_var(self):
        op = model.BinaryOperation(model.Number(0), "/", model.Reference("a"))
        folder = ConstantFolder()
        tree = folder.visit(op)
        return (isinstance(tree, model.BinaryOperation) and
                tree.op == "/" and tree.lhs.value == 0 and
                isinstance(tree.rhs, model.Reference) and tree.rhs.name == "a")

    def test_ref_num(self):
        scope = model.Scope()
        scope["a"] = model.Number(10)
        op = model.BinaryOperation(model.Reference("a"), "*", model.Number(0))
        folder = ConstantFolder()
        tree = folder.visit(op)
        assert isinstance(tree, model.Number) and tree.value == 0

    def test_ref_num_var(self):
        op = model.BinaryOperation(model.Reference("a"), "+", model.Number(0))
        folder = ConstantFolder()
        tree = folder.visit(op)
        assert (isinstance(tree, model.BinaryOperation) and tree.op == "+" and
                isinstance(tree.rhs, model.Number) and tree.rhs.value == 0 and
                isinstance(tree.lhs, model.Reference) and tree.lhs.name == "a")

    def test_ref_ref(self):
        scope = model.Scope()
        scope["a"] = model.Number(10)
        op = model.BinaryOperation(model.Reference("a"), "-",
                                   model.Reference("a"))
        folder = ConstantFolder()
        tree = folder.visit(op)
        assert isinstance(tree, model.Number) and tree.value == 0

    def test_ref_ref_var(self):
        op = model.BinaryOperation(model.Reference("a"), "+",
                                   model.Reference("a"))
        folder = ConstantFolder()
        tree = folder.visit(op)
        assert (isinstance(tree, model.BinaryOperation) and tree.op == "+" and
                isinstance(tree.lhs, model.Reference) and
                tree.lhs.name == "a" and
                isinstance(tree.rhs, model.Reference) and
                tree.rhs.name == "a")

    def test_unary_operation(self):
        op = model.UnaryOperation("-", model.BinaryOperation(model.Number(1),
                                                             "+",
                                                             model.Number(2)))
        folder = ConstantFolder()
        tree = folder.visit(op)
        assert isinstance(tree, model.Number) and tree.value == -3

    def test_assign(self):
        n1, n2 = model.Number(2), model.Number(3)
        assign = model.Assign("x", model.BinaryOperation(n1, "+", n2))
        folder = ConstantFolder()
        tree = folder.visit(assign)
        assert isinstance(tree.value, model.Number)
        assert tree.value.value == 5

    def test_assign_var(self):
        scope = model.Scope()
        scope["a"] = model.Number(0)
        assign = model.Assign("x", model.Reference("a"))
        folder = ConstantFolder()
        tree = folder.visit(assign)
        assert (isinstance(tree, model.Assign) and tree.name == "x" and
                isinstance(tree.value, model.Reference) and
                tree.value.name == "a")

    def test_conditional(self):
        scope = model.Scope()
        scope["a"] = model.Number(10)
        cond = model.Conditional(model.BinaryOperation(model.Number(4), ">",
                                                       model.Number(3)),
                                 [model.Assign("x", model.BinaryOperation(
                                     model.Number(3), "-", model.Number(5))),
                                  model.Assign("y", model.BinaryOperation(
                                      model.Number(5), "*", model.Number(5)))],
                                 [model.Assign("x", model.BinaryOperation(
                                     model.Reference("a"), "*",
                                     model.Number(0)))])
        folder = ConstantFolder()
        tree = folder.visit(cond)
        assert (isinstance(tree, model.Conditional) and
                tree.condition.value > 0 and
                isinstance(tree.if_true[0], model.Assign) and
                tree.if_true[0].value.value == -2 and
                isinstance(tree.if_true[1], model.Assign) and
                tree.if_true[1].value.value == 25 and
                len(tree.if_true) == 2 and len(tree.if_false) == 1 and
                isinstance(tree.if_false[0], model.Assign) and
                tree.if_false[0].value.value == 0)

    def test_print(self):
        n1, n2 = model.Number(2), model.Number(3)
        pr = model.Print(model.BinaryOperation(n1, "+", n2))
        folder = ConstantFolder()
        tree = folder.visit(pr)
        assert isinstance(tree, model.Print) and tree.expr.value == 5

    def test_function_definition(self):
        scope = model.Scope()
        function = model.Function(["a"], [model.Print(model.BinaryOperation(
            model.Reference('a'), '-', model.Reference("a")))])
        definition = model.FunctionDefinition("f", function)
        folder = ConstantFolder()
        tree = folder.visit(definition)
        assert (isinstance(tree, model.FunctionDefinition) and
                tree.name == "f" and len(tree.function.args) == 1 and
                len(tree.function.body) == 1 and
                isinstance(tree.function.body[0], model.Print) and
                isinstance(tree.function.body[0].expr, model.Number) and
                tree.function.body[0].expr.value == 0)

    def test_function_call(self):
        scope = model.Scope()
        scope["x"] = model.Number(10)
        function = model.Function(["a", "b", "c"], [])
        model.FunctionDefinition("f", function).evaluate(scope)

        call = model.FunctionCall(model.Reference("f"), [model.BinaryOperation(
            model.Number(2), "*", model.Number(3)), model.BinaryOperation(
                model.Number(0), "*", model.Reference("x")),
                                                   model.Reference("x")])
        folder = ConstantFolder()
        tree = folder.visit(call)
        assert (isinstance(tree, model.FunctionCall) and
                isinstance(tree.fun_expr, model.Reference) and
                tree.fun_expr.name == "f" and len(tree.args) == 3 and
                isinstance(tree.args[0], model.Number) and
                tree.args[0].value == 6 and
                isinstance(tree.args[1], model.Number) and
                tree.args[1].value == 0 and
                isinstance(tree.args[2], model.Reference) and
                tree.args[2].name == "x")

    def my_tests(self):
        tests = []
        tests.append(self.test_num_num)
        tests.append(self.test_num_ref)
        tests.append(self.test_num_ref_var)
        tests.append(self.test_ref_num)
        tests.append(self.test_ref_num_var)
        tests.append(self.test_ref_ref)
        tests.append(self.test_ref_ref_var)
        tests.append(self.test_unary_operation)
        tests.append(self.test_assign)
        tests.append(self.test_assign_var)
        tests.append(self.test_conditional)
        tests.append(self.test_print)
        tests.append(self.test_function_definition)
        tests.append(self.test_function_call)

        print("Runnig tests...")
        for test in tests:
            test()
        print("Passes all tests.")


if __name__ == "__main__":
    tests = Tests()
    tests.my_tests()
