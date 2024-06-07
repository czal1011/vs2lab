import random
import logging

# coordinator messages
from const2PC import VOTE_REQUEST, GLOBAL_COMMIT, GLOBAL_ABORT, PREPARE_COMMIT
# participant decissions
from const2PC import LOCAL_SUCCESS, LOCAL_ABORT, READY_COMMIT
# participant messages
from const2PC import VOTE_COMMIT, VOTE_ABORT, NEED_DECISION, VOTE_NEW_COORDINATOR
# misc constants
from const2PC import TIMEOUT

import stablelog


class Participant:
    """
    Implements a two phase commit participant.
    - state written to stable log (but recovery is not considered)
    - in case of coordinator crash, participants mutually synchronize states
    - system blocks if all participants vote commit and coordinator crashes
    - allows for partially synchronous behavior with fail-noisy crashes
    """

    def __init__(self, chan):
        self.channel = chan
        self.participant = self.channel.join('participant')
        self.stable_log = stablelog.create_log(
            "participant-" + self.participant)
        self.logger = logging.getLogger("vs2lab.lab6.2pc.Participant")
        self.coordinator = {}
        self.all_participants = {}
        self.state = 'NEW'

    @staticmethod
    def _do_work():
        # Simulate local activities that may succeed or not
        return LOCAL_ABORT if random.random() > 2/3 else LOCAL_SUCCESS

    def _enter_state(self, state):
        self.stable_log.info(state)  # Write to recoverable persistant log file
        self.logger.info("Participant {} entered state {}."
                         .format(self.participant, state))
        self.state = state

    def init(self):
        self.channel.bind(self.participant)
        self.coordinator = self.channel.subgroup('coordinator')
        self.all_participants = self.channel.subgroup('participant')
        self._enter_state('INIT')  # Start in local INIT state.

    def find_new_coordinator(self): # TODO muss implementiert werden (da wenn Koordinator keine Nachricht zurückgibt)
        active_participants = self.all_participants
        while(len(active_participants) > 0):
            new_coordinator = min(active_participants)
            self.channel.send_to(new_coordinator, NEW_COORDINATOR)
            ack = self.channel.receive_from(new_coordinator, TIMEOUT)
            if not ack:
                active_participants.remove(new_coordinator)
            else:
                self.channel.send_to(new_coordinator, CONFIRM_COORD)
                break
        self.coordinator = new_coordinator
        # TODO broadcast an alle participants: neuer Koordinator

    def run(self):
        # ! STATE 'INIT'

        # Wait for start of joint commit
        msg = self.channel.receive_from(self.coordinator, TIMEOUT)

        if not msg:  # Crashed coordinator - give up entirely
            # decide to locally abort (before doing anything)
            decision = LOCAL_ABORT

        else:  # Coordinator requested to vote, joint commit starts
            assert msg[1] == VOTE_REQUEST

            # Firstly, come to a local decision
            decision = self._do_work()  # proceed with local activities

            # If local decision is negative,
            # then vote for abort and quit directly
            if decision == LOCAL_ABORT:
                self.channel.send_to(self.coordinator, VOTE_ABORT)

            # If local decision is positive,
            # we are ready to proceed the joint commit
            else:
                assert decision == LOCAL_SUCCESS
                self._enter_state('READY')

                # ! STATE 'READY'

                # Notify coordinator about local commit vote
                self.channel.send_to(self.coordinator, READY_COMMIT)

                # Wait for coordinator to notify the final outcome
                msg = self.channel.receive_from(self.coordinator, TIMEOUT)

                if not msg:  # Crashed coordinator
                    # Start vote
                    find_new_coordinator()

                    if self.coordinator == self.proc: # Coordinator
                        

                    # Ask all processes for their decisions
                    self.channel.send_to(self.all_participants, NEED_DECISION)
                    while True:
                        msg = self.channel.receive_from_any()
                        # new coordinator?
                        if msg[1] == NEW_COORDINATOR:
                            self.coordinator = list(self.proc) # TODO does that work?
                            self._enter_state('ABORT')
                            self.channel.send_to(all_participants, GLOBAL_ABORT)
                        # If someone reports a final decision,
                        # we locally adjust to it
                        if msg[1] in [
                                PREPARE_COMMIT, GLOBAL_ABORT, LOCAL_ABORT]:
                            decision = msg[1]
                            break

                else:  # Coordinator came to a decision
                    decision = msg[1]

        # ! STATE 'PRECOMMIT' / 'ABORT'

        # Change local state based on the outcome of the joint commit protocol
        # Note: If the protocol has blocked due to coordinator crash,
        # we will never reach this point
        if decision == PREPARE_COMMIT:
            self._enter_state('PRECOMMIT')
            self.channel.receive_from(self.coordinator, TIMEOUT)
            if msg[1] == GLOBAL_COMMIT:
                # ! STATE 'COMMIT'
                self._enter_state('COMMIT')
        else:
            assert decision in [GLOBAL_ABORT, LOCAL_ABORT]
            self._enter_state('ABORT')

        

        # Help any other participant when coordinator crashed
        num_of_others = len(self.all_participants) - 1
        while num_of_others > 0:
            num_of_others -= 1
            msg = self.channel.receive_from(self.all_participants, TIMEOUT * 2)
            if msg and msg[1] == NEED_DECISION:
                self.channel.send_to({msg[0]}, decision)

        return "Participant {} terminated in state {} due to {}.".format(
            self.participant, self.state, decision)