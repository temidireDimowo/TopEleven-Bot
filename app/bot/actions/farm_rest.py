"""Farm rest action — watches an ad to earn a rest token for a player."""

import time
from app.bot.actions.base import BotAction


class FarmRestAction(BotAction):

    name = "Farm Rest"

    def execute(self) -> bool:
        """
        One rest-farming cycle (token_pack pre-selected by user):
        1. Find watch_ads_general → click
        2. Adaptive wait for skip_ad / close_ad
        3. Click dismiss button
        """
        self._emit('log', level='info', message='Starting rest farming cycle...')

        # Step 1: Find watch ads button (token pack already open)
        if not self._interruptible_sleep(3):
            return False

        self._emit('log', level='info', message='Looking for watch ads button...')
        watch_pt = self._find('watch_ads_general')
        if watch_pt is None:
            self._emit('log', level='warning', message='Watch ads button not found — cycle skipped')
            return False

        self._click(watch_pt)
        if not self._interruptible_sleep(3):
            return False

        # Step 2: Wait for ad to complete
        self._emit('log', level='info', message='Watching ad — waiting for dismiss button...')
        dismiss_pt = self._adaptive_wait(['skip_ad', 'close_ad'])

        if dismiss_pt is None:
            if self._should_stop():
                return False
            self._emit('log', level='warning', message='Ad dismiss timed out — pressing escape')
            self.platform.press_escape()
            return False

        # Step 3: Dismiss
        self._click(dismiss_pt)
        time.sleep(1)
        self._emit('log', level='success', message='Ad dismissed — rest token earned!')

        # Check for second ad
        if not self._should_stop():
            second_dismiss = self._adaptive_wait(['skip_ad', 'close_ad'], timeout=10)
            if second_dismiss:
                self._emit('log', level='info', message='Dismissing second ad...')
                self._click(second_dismiss)

        return True
