

class Dialog:

    """

    .. code-block: python

        def step1(dialog, msg, params):
            msg.reply("Check your params: %s and say Yes!" % ','.join([
                str(h) for h in params.items()]))
            return params

        def step2(dialog, msg, params):
            msg.reply("I store your connection "
                      "with params: %s" % dialog.get_step_data(0))
            return True

        dialog = Dialog(msg, "connection",
                        actions=[(step1, self.parameters),
                                 (step2, ['conn'])])

        dialog.process()
    """

    def __init__(self, msg, name, actions):
        self.msg = msg
        self.name = name
        self.actions = actions

    def extract_parameters(self, msg, parameters=None):
        return self.msg.extract_parameters(parameters)

    def get_steps_data(self):
        data = {}
        for i, action in enumerate(self.actions):
            data[i] = self.msg.bot.state.dialogs.get(
                self.get_step_key(i), user=self.msg.user)
        return data

    def get_info(self):
        return {
            'data': self.get_steps_data(),
            'current_step': self.get_current_step()[0]
        }

    def get_step_data(self, index):
        return self.msg.bot.state.dialogs.get(
            self.get_step_key(index), user=self.msg.user)

    def set_step_data(self, index, data):
        return self.msg.bot.state.dialogs.set(
            self.get_step_key(index), data, user=self.msg.user)

    def update_step_data(self, index, new_data):
        data = self.get_step_data(index)
        if data and isinstance(data, dict):
            data.update(new_data)
        return self.set_step_data(index, data)

    def get_step_key(self, index):
        return self.name + "_%s" % index

    def delete_steps_data(self):
        for i, action in enumerate(self.actions):
            self.msg.bot.state.dialogs.delete(
                self.get_step_key(i),
                user=self.msg.user)

    def get_help(self):
        step = self.get_current_step()
        return getattr(step[1][0], "__doc__", "No documentation")

    def get_current_step(self):
        for i, action in enumerate(self.actions):
            if self.get_step_data(i):
                continue
            else:
                return i, action

    def process(self):

        index, step = self.get_current_step()

        if index == 0:
            self.msg.reply("Started new dialog with name: *%s*,\n"
                           "help: %s" % (self.name, self.get_help()))

        params = self.extract_parameters(self.msg, step[1])
        result = step[0](self, self.msg, params)

        if result is True:
            self.delete_steps_data()
            self.msg.reply(
                "Dialog with name: *%s* was successfuly finished." % self.name)
        else:
            self.set_step_data(index, result)
            self.msg.bot.state.dialogs.set(
                self.name, self, user=self.msg.user)
            return True
