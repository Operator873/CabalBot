import cabalutil
from sopel import formatting


def check_for_log_reporter(change):
    log_check = f"""SELECT * FROM log_feed WHERE project="{change}";"""
    return len(cabalutil.do_sqlite(log_check, 'all')) > 0


def log_report(bot, change):
    chan_query = f"""SELECT * FROM log_feed WHERE project='{change["wiki"]}';"""
    data = cabalutil.do_sqlite(chan_query, 'all')
    
    container = {}
    for item in data:
        project, channel, action = item
        if channel in container:
            container[channel].append(action.upper())
        else:
            container[channel] = [action.upper()]
    
    for chan in container:
        if change["log_type"].upper() not in container[chan]:
            continue

        if change["log_type"].upper() == "BLOCK":
            report = (
                    "Log action by "
                    + formatting.color(editor, formatting.colors.GREEN)
                    + ": "
                    + formatting.color(formatting.bold(change['log_type'].upper()), formatting.colors.RED)
                    + " || "
                    + pageLink
                    + " was "
                    + change["log_action"]
                    + "ed || Flags: "
                    + change["log_params"]["flags"]
                    + " || Duration: "
                    + change["log_params"]["duration"]
                    + " || Comment: "
                    + comment[:200]
            )
        elif change["log_type"].upper() == "MOVE":
            report = (
                    "Log action by "
                    + formatting.color(editor, formatting.colors.GREEN)
                    + ": "
                    + formatting.color(formatting.bold(change['log_type'].upper()), formatting.colors.RED)
                    + " || "
                    + editor
                    + " moved "
                    + pageLink
                    + " "
                    + comment[:200]
            )
        else:
            report = (
                    "Log action by "
                    + formatting.color(editor, formatting.colors.GREEN)
                    + ": "
                    + formatting.color(formatting.bold(change['log_type'].upper()), formatting.colors.RED)
                    + " || "
                    + pageLink
                    + " "
                    + comment[:200]
            )

        if not cabalutil.check_hush(chan):
            bot.say(report, chan)


def log_reporter_check_channel(project, channel):
    query = f"""SELECT channel FROM log_feed WHERE project='{project}' and channel='{channel}';"""
    return len(cabalutil.do_sqlite(query, 'all')) > 0


def log_reporter_channel(project, channel, operation):
    if operation == "add":
        query = f"""INSERT INTO log_feed VALUES("{project}", "{channel}", "BLOCK");"""
    else:
        query = f"""DELETE FROM log_feed WHERE project="{project}" and channel="{channel}";"""
        
    return cabalutil.do_sqlite(query, 'act')


def log_reporter_action(trigger, operation):
    if not cabalutil.check_feedadmin(trigger.account, trigger.sender):
        return "You are not a feed admin!"

    if not log_reporter_check_channel(trigger.group(4), trigger.sender):
        return f"I'm not reporting log actions for {trigger.group(4)} in this channel."
    
    if operation.lower() in ['del', 'delete', 'rm', 'remove', '-']:
        query = f"""DELETE FROM log_feed WHERE project="{trigger.group(4)}" and channel="{trigger.sender}" and action="{trigger.group(5)}";"""
    elif operation.lower() in ['add', '+']:
        query = f"""INSERT INTO log_feed VALUES("{trigger.group(4)}", "{trigger.sender}", "{trigger.group(5)}");"""
    else:
        return "Command seems malformed. Options are like add, del, -, +"

    if cabalutil.do_sqlite(query, 'act'):
        if operation.lower() in ['add', '+']:
            return f"{trigger.group(5)} added as reportable action for {trigger.group(4)}."
        else:
            return f"{trigger.group(5)} removed from reportable action on {trigger.group(4)}."
    else:
        return "An unknown error occurred while writing to the database."
        

def start_log_reporter(trigger):
    if not cabalutil.check_feedadmin(trigger.account, trigger.sender):
        return "You are not a feed admin!"

    if log_reporter_check_channel(trigger.group(4), trigger.sender):
        response = (
            f"I'm already reporting log events for {trigger.group(4)}."
            + " Were you looking for !logreporter add <project> <LOG TYPE> perhaps?"
        )
        return response

    if log_reporter_channel(trigger.group(4), trigger.sender, "add"):
        response = (
            f"Log reporter activated for {trigger.group(4)} in this channel."
            + "BLOCK events have been added by default."
            + " Please use !logreporter add <project> <LOG EVENT TYPE> to add others."
            + " Example: !logreporter add MOVE"
        )
        return response
    else:
        return "An unknown error occurred during addition to database."


def stop_log_reporter(trigger):
    if not cabalutil.check_feedadmin(trigger.account, trigger.sender):
        return "You are not a feed admin!"

    if not log_reporter_check_channel(trigger.group(4), trigger.sender):
        return f"I'm not reporting log actions on {trigger.group(4)} in this channel."

    if log_reporter_channel(trigger.group(4), trigger.sender, 'del'):
        return "Log reporter stopped in this channel."
    else:
        return "An unknown error occurred while writing to the database."
