from new_parser import Parser
from ai_ast import *
from lexer import *
import copy


def flatten_expr_group(program):
    while True:
        modified = False
        for m_id, macro in enumerate(program.macros):
            for e_id, expr in enumerate(macro.body):
                if isinstance(expr, ExprGroup):
                    macro.body = macro.body[:e_id] + expr.exprs + macro.body[e_id + 1:]
                    modified = True
                    break

                    # resolve repeats in movements
        for t_id, track in enumerate(program.tracks):
            for m_id, mov in enumerate(track.movements):
                for e_id, expr in enumerate(mov.expressions):
                    if isinstance(expr, ExprGroup):
                        mov.expressions = mov.expressions[:e_id] + expr.exprs + mov.expressions[e_id + 1:]
                        modified = True
                        break

        if not modified:
            break


def print_list(list, indent):
    for item in list:
        print(traverse_ast(item, indent))
    print()


def resolve_repeats(program):
    # Process macros
    for macro in program.macros:
        macro.body = resolve_in_list(macro.body)

    # Process tracks
    for track in program.tracks:
        for movement in track.movements:
            movement.expressions = resolve_in_list(movement.expressions)


def resolve_in_list(expr_list):
    new_exprs = []
    i = 0
    while i < len(expr_list):
        expr = expr_list[i]

        if isinstance(expr, ExprGroup):
            # Recursively process nested groups
            expr.exprs = resolve_in_list(expr.exprs)
            new_exprs.append(expr)
            i += 1
        elif isinstance(expr, Repetition):
            # Ensure repetition follows an expression
            if not new_exprs:
                raise SyntaxError(f"Invalid repetition at start of expression list: {expr}")

            # Get target expression and repeat count
            target = new_exprs.pop()
            count = expr.times

            expanded = [copy.deepcopy(target) for _ in range(count)]

            new_exprs.extend(expanded)
            i += 1
        else:
            new_exprs.append(expr)
            i += 1

    return new_exprs


def resolve_macros(program):
    # iterate through movements in the ast and find macros
    for t_id, track in enumerate(program.tracks):
        for m_id, mov in enumerate(track.movements):
            while True:  # iterate until no more modifications were made
                mov_body = copy.copy(mov.expressions)  # make a shallow copy of the expr list
                was_modified = False

                for e_id, expr in enumerate(mov_body):
                    if isinstance(expr, Ident):
                        maps = program.ident_dic[expr.source.value]
                        macro = None

                        try:
                            macro = program.macros[maps - 1]
                        except:
                            raise ValueError(f"Unknown idenfitier: {expr}")

                        mov_body = mov_body[:e_id] + inline_macro_body(macro, program) + mov_body[e_id + 1:]
                        was_modified = True
                        break

                    if isinstance(expr, MacroCall):
                        maps = program.ident_dic[expr.name.value]
                        macro = None
                        try:
                            macro = program.macros[maps - 1]
                        except:
                            raise ValueError(f"Unknown macro: {expr}")

                        new_macro = apply_macro(macro, expr.arguments, program)
                        mov_body = mov_body[:e_id] + inline_macro_body(new_macro, program) + mov_body[e_id + 1:]
                        was_modified = True
                        break

                mov.expressions = mov_body
                if not was_modified:
                    break

    pass


def apply_macro(macro, args, program):
    arg_map = {}
    new_macro = copy.deepcopy(macro)

    if len(macro.parameters) != len(args):
        raise ValueError(f"Expected {len(macro.parameters)} arguments, got only {len(args)}")

    for i, param in enumerate(macro.parameters):
        arg_map[param.value] = args[i]

    arg_keys = arg_map.keys()
    for e_id, expr in enumerate(macro.body):
        if expr.source.value in arg_keys:
            new_macro.body = new_macro.body[:e_id] + [arg_map[expr.source.value]] + new_macro.body[e_id + 1:]

    return new_macro


def inline_macro_body(macro, program):
    macro_body = copy.copy(macro.body)

    for e_id, expr in enumerate(macro.body):
        if isinstance(expr, Ident):
            maps = program.ident_dic[expr.source.value]
            new_macro = None

            try:
                new_macro = program.macros[maps - 1]
            except:
                raise ValueError(f"Unknown idenfitier: {expr}")

            macro_body = macro.body[:e_id] + inline_macro_body(new_macro, program) + macro.body[e_id + 1:]
            continue

        if isinstance(expr, MacroCall):
            maps = program.ident_dic[expr.name]
            new_macro = None

            try:
                new_macro = program.macros[maps - 1]
            except:
                raise ValueError(f"Unknown macro: {expr}")

            another_macro = apply_macro(macro, program)
            macro_body = macro.body[:e_id] + inline_macro_body(another_macro, program) + macro.body[e_id + 1:]

    return macro_body
