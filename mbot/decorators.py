
import functools


def save_command(func):

    @functools.wraps(func)
    def dec(middleware, msg, *args, **kwargs):

        msg.bot.state.save_command(msg.user, func,
                                   (middleware, msg,))

        return func(middleware, msg, *args, **kwargs)

    return dec
