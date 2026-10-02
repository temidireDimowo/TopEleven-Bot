"""Farm greens action — watches one ad to earn a green token."""

import time
from app.bot.actions.base import BotAction


class FarmGreensAction(BotAction):

    name = "Farm Greens"

    def execute(self) -> bool:
        """
        One green-farming cycle:
        1. Find token_pack icon → click
        2. Find watch_ads_general → click
        3. Adaptive wait for skip_ad / close_ad
        4. Click dismiss button
        Returns True if green was earned.
        """
        self._emit('log', level='info', message='Starting green farming cycle...')

        # Step 1: Find and click the token pack icon
        self._emit('log', level='info', message='Looking for token pack...')
        token_pt = self._find('token_pack')
        if token_pt is None:
            self._emit('log', level='warning', message='Token pack not found — cycle skipped')
            return False

        self._click(token_pt)
        if not self._interruptible_sleep(5):
            return False

        # Step 2: Find and click the Watch Ad button
        self._emit('log', level='info', message='Looking for watch ads button...')
        watch_pt = self._find('watch_ads_general')
        if watch_pt is None:
            self._emit('log', level='warning', message='Watch ads button not found — cycle skipped')
            return False

        self._click(watch_pt)
        if not self._interruptible_sleep(3):
            return False

        # Step 3: Adaptive wait — poll for dismiss button instead of blind 75s sleep
        self._emit('log', level='info', message='Watching ad — waiting for dismiss button...')
        dismiss_pt = self._adaptive_wait(['skip_ad', 'close_ad'])

        if dismiss_pt is None:
            # Timed out or stopped — try escape as last resort
            if self._should_stop():
                return False
            self._emit('log', level='warning', message='Ad dismiss timed out — pressing escape')
            self.platform.press_escape()
            return False

        # Step 4: Click dismiss
        self._click(dismiss_pt)
        time.sleep(1)
        self._emit('log', level='success', message='Ad dismissed — green earned!')

        # Check if a second ad plays
        if not self._should_stop():
            second_dismiss = self._adaptive_wait(['skip_ad', 'close_ad'], timeout=10)
            if second_dismiss:
                self._emit('log', level='info', message='Dismissing second ad...')
                self._click(second_dismiss)
                time.sleep(1)

        return True
