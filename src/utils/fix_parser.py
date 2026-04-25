import argparse

def add_minus_separated_flags(parser: argparse.ArgumentParser):
    """
    自动为 argparse.ArgumentParser 中含有下划线的参数添加别名。例如：
    --fix_existing -> 添加别名 --fix-existing
    --augment_OD_num -> 添加别名 --augment-OD-num
    """
    new_option_string_actions = {}
    for group in parser._action_groups:
        for action in group._group_actions:
            # 仅处理可选参数（以 '-' 开头的参数）
            if not action.option_strings:
                continue
            # 找到最长的双减号选项作为主选项，基于它来创建别名
            original_option = ''
            for opt in list(action.option_strings):
                if opt.startswith('--') and '_' in opt and len(opt) > len(original_option):
                    original_option = opt
            # 如果找到了符合条件的原始选项
            if original_option:
                # 将下划线替换为减号
                new_alias_option = original_option.replace('_', '-')
                # 将别名添加到 action 的 option_strings 列表中
                if new_alias_option not in action.option_strings:
                    action.option_strings.append(new_alias_option)
            # 将 action 的所有（新旧）选项添加到新的查找字典中
            for opt in action.option_strings:
                new_option_string_actions[opt] = action
    # 用新构建的字典替换 ArgumentParser 内部的查找字典
    parser._option_string_actions = new_option_string_actions
    return parser

def add_negation_started_flags(parser: argparse.ArgumentParser):
    """
    自动为 parser 中的 store_true 参数添加对应的 --no-xxx 选项。
    """
    for action in parser._actions:
        # 只处理布尔型的 store_true
        if isinstance(action, argparse._StoreTrueAction):
            # 获取参数名，例如 '--flag'
            for option in action.option_strings:
                if not option.startswith('--'): 
                    continue
                neg_option = '--no-' + option.removeprefix('--')
                if any(neg_option in a.option_strings for a in parser._actions):
                    continue # 避免重复添加
                parser.add_argument(
                    neg_option,
                    dest=action.dest,
                    action='store_false',
                    default=action.default,
                    help=f"Disable {option.removeprefix('--')}"
                )
    return parser
