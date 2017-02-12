

class Middleware:

    @property
    def code(self):
        """Returns name"""
        return self.__class__.__name__.lower()

    public = False
    groups = ['admin']
    permissions = []

    def skip_message(self, msg):
        """Returns Boolean
        Skips whole message from processing
        """
        return False

    def skip_middleware(self, msg):
        """Returns Boolean
        Skips middleware for this message
        """
        return False

    def pre_process(self, msg):
        """Called before processing"""
        return msg

    def process(self, msg):
        """Main method for message processing"""
        raise NotImplementedError

    def post_process(self, msg):
        """Called after process is done"""
        pass

    def check_permissions(self, msg):
        """Check permission and returns Boolean"""
        user = msg.bot.state.users.get(msg.user.lower())
        return user.has_permissions(self)

    @property
    def periodic_jobs(self):
        return []
