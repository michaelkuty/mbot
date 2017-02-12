import logging

import dill as pickle
import io
from mbot.state import StateMachine
from mbot.utils.packages import install_package

LOG = logging.getLogger(__name__)


class Storage:

    """Base storage class
    """

    def __init__(self, bot, encrypt=True, *args, **kwargs):
        self.bot = bot
        self.encrypt = encrypt

    def encrypt_data(self, data):
        return self.bot.fernet.encrypt(data)

    def decrypt_data(self, data):
        return self.bot.fernet.decrypt(data)

    def save_state(self, state):
        """Save state"""

        with open(state.state_path, 'wb') as f:

            data = pickle.dumps(state, pickle.HIGHEST_PROTOCOL)

            if self.encrypt:
                data = self.encrypt_data(data)

            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

    def restore_state(self, path):
        """Returns loaded state"""

        try:
            with open(path, 'rb') as f:
                if self.encrypt:
                    state = pickle.loads(self.decrypt_data(pickle.load(f)))
                else:
                    state = pickle.load(f)

                LOG.debug("Restoring state successs")
        except Exception as e:
            LOG.debug("Restoring state from %s failed with %s" % (
                path, e))
            state = StateMachine(self.bot, state_path=path)
            LOG.debug("Successfully inicialized new state.")

        return state


class S3(Storage):

    """S3 storage class
    """

    def __init__(self, bucket_name, *args, **kwargs):
        self.bucket_name = bucket_name
        super().__init__(*args, **kwargs)

    @property
    def bucket(self):
        return self.get_bucket(self.bucket_name)

    def get_bucket(self, name):
        """Returns bucket by name
        """

        try:
            import boto3
        except ImportError:
            install_package("boto3")

        try:
            logging.getLogger('boto3').setLevel(logging.CRITICAL)
            logging.getLogger('botocore').setLevel(logging.CRITICAL)
            logging.getLogger('nose').setLevel(logging.CRITICAL)
        except:
            pass

        s3 = boto3.resource('s3')

        return s3.Bucket(name)

    def save_state(self, state):
        """Save state"""

        data = pickle.dumps(state, pickle.HIGHEST_PROTOCOL)

        if self.encrypt:
            data = self.encrypt_data(data)

        return self.bucket.put_object(Key=state.state_path,
                                      Body=data)

    def restore_state(self, path):
        """Returns loaded state"""

        tmp_file = io.BytesIO()

        self.bucket.download_fileobj(path, tmp_file)

        if self.encrypt:
            data = self.encrypt_data(tmp_file.getvalue())
        else:
            data = tmp_file.getvalue()

        state = pickle.loads(str(data, encoding="utf-8"))

        state.bot = self.bot

        return state
