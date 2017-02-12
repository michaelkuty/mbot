
import logging

LOG = logging.getLogger(__name__)


def history(msg):
    """
    `save my last command name: test`\n
    `run: test`\n
    `history`\n
    `list`\n
    `save my command name: echo index: 0`
    """

    if msg.user and msg.text:

        if "save" in msg.text and "command" in msg.text:
            # store command
            name, new_text = msg._extract_from_text(
                "name", msg.text,
                r":\s?(\S*['-]*|\w*.+|'[^']+')")
            print(name)
            if "last" in msg.text:
                cmd = msg.bot.state.get_last_command(msg.user)
            else:
                index, new_text = msg._extract_from_text(
                    "index", msg.text,
                    r':\s?(\w*.+|"[^"]+")')

                try:
                    cmd = msg.bot.state.command_history[msg.user][int(index)]
                except:
                    cmd = None

            if not cmd:
                msg.reply("No commands found for you.")
                return

            if "last" in msg.text:
                msg.bot.state.save_last_command(msg.user, name)
            else:
                msg.bot.state.save_command_from_history(
                    msg.user, int(index), name)

            msg.reply(
                "Your command %s was saved and is available under %s." % (
                    cmd, name))

        elif "run" in msg.text:
            # find command
            name, new_text = msg._extract_from_text("run", msg.text)

            if name:
                msg.bot.state.run_command(name, msg=msg)

        elif "list" in msg.text:

            if msg.user in msg.bot.state.commands:
                msg.reply(
                    "List of your commands \n %s." % '\n'.join(
                        msg.bot.state.commands[msg.user].keys()))

        elif "history" in msg.text:

            if msg.user in msg.bot.state.command_history:
                msg.reply(
                    "History of your commands \n %s." % '\n'.join(
                        [str((i, cmd[0].__name__, cmd[1], cmd[2],))
                         for i, cmd in enumerate(
                            msg.bot.state.command_history[msg.user])]))
