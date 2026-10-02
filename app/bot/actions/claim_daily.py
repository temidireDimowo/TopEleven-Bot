"""Claim daily rewards action."""

import time
from app.bot.actions.base import BotAction


class ClaimDailyAction(BotAction):

    name = "Claim Daily Rewards"

    def execute(self) -> bool:
        """
        Detect the daily reward indicator and claim it.
        Requires a 'daily_reward' template or YOLO class.
        """
        self._emit('log', level='info', message='Looking for daily reward...')

        reward_pt = self._find('daily_reward')
        if reward_pt is None:
            self._emit('log', level='warning', message='Daily reward not available (already claimed or not visible)')
            return False

        self._click(reward_pt)
        time.sleep(2)

        # Dismiss the reward popup
        close_pt = self._adaptive_wait(['close_ad', 'skip_ad'], timeout=10)
        if close_pt:
            self._click(close_pt)
            time.sleep(1)

        self._emit('log', level='success', message='Daily reward claimed!')
        return True
