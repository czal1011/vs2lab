import random
import logging
import time
import stablelog

# coordinator messages
from const3PC import VOTE_REQUEST, GLOBAL_COMMIT, GLOBAL_ABORT, PREPARE_COMMIT
# participant messages
from const3PC import VOTE_COMMIT, VOTE_ABORT, READY_COMMIT
# misc constants
from const3PC import TIMEOUT


class Coordinator:
    """
    Implements a two phase commit coordinator.
    - state written to stable log (but recovery is not considered)
    - simulates possible crash failure after vote request
    """

    def __init__(self, chan):
        self.channel = chan
        self.coordinator = self.channel.join('coordinator')
        self.participants = []  # list of all participants
        self.log = stablelog.create_log("coordinator-" + self.coordinator)
        self.stable_log = stablelog.create_log("coordinator-"
                                               + self.coordinator)
        self.logger = logging.getLogger("vs2lab.lab6.3pc.Coordinator")
        self.state = None

    def _enter_state(self, state):
        self.stable_log.info(state)  # Write to recoverable persistant log file
        self.logger.info("Coordinator {} entered state {}."
                         .format(self.coordinator, state))
        self.state = state

    def init(self):
        # * Start of Phase 1

        self.channel.bind(self.coordinator)
        self._enter_state('INIT')  # Start in INIT state.

        # Prepare participant information.
        self.participants = self.channel.subgroup('participant')

    def run(self):
        if random.random() > 3/4:  # simulate a crash
            return "Coordinator crashed in state INIT."

        # Request local votes from all participants
        self._enter_state('WAIT')
        self.channel.send_to(self.participants, VOTE_REQUEST)
        
        # * Start of Phase 2

        if random.random() > 2/3:  # simulate a crash
            return "Coordinator crashed in state WAIT."

        # Collect votes from all participants
        yet_to_receive = list(self.participants)
        while len(yet_to_receive) > 0:
            msg = self.channel.receive_from(self.participants, TIMEOUT)

            if (not msg) or (msg[1] == VOTE_ABORT):
                reason = "timeout" if not msg else "local_abort from " + msg[0]
                self._enter_state('ABORT')
                # Inform all participants about global abort
                self.channel.send_to(self.participants, GLOBAL_ABORT)
                return "Coordinator {} terminated in state ABORT. Reason: {}."\
                    .format(self.coordinator, reason)

            else:
                assert msg[1] == VOTE_COMMIT
                yet_to_receive.remove(msg[0])

        # all participants have locally committed
        self._enter_state('PRECOMMIT')
        self.channel.send_to(self.participants, PREPARE_COMMIT)

        # * Start of Phase 3
        # Collect votes from all participants

        if random.random() >2/3:  # simulate a crash
            return "Coordinator crashed in state PRECOMMIT."
        
        yet_to_receive = list(self.participants)
        while len(yet_to_receive) > 0:
            msg = self.channel.receive_from(self.participants, TIMEOUT)

            if (not msg):
                self._enter_state('COMMIT')
                # Inform all participants about global commit
                self.channel.send_to(self.participants, GLOBAL_COMMIT)
                return f"Coordinator {self.coordinator} terminated in state COMMIT. Not every participant could be reached."
            else:
                assert msg[1] == READY_COMMIT
                yet_to_receive.remove(msg[0])
        
        self._enter_state('COMMIT')
        
        # Inform all participants about global commit
        self.channel.send_to(self.participants, GLOBAL_COMMIT)

        return "Coordinator {} terminated in state COMMIT."\
            .format(self.coordinator)