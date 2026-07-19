from typing import Callable, Optional


def ease_out_cubic(t: float) -> float:

    return 1 - pow(1 - t, 3)


class WindowAnimator:

    def __init__(self, window, duration: float = 0.15, steps: int = 12):
        self.window = window
        self.duration = max(duration, 0.01)
        self.steps = max(steps, 1)
        self._interval_ms = int((self.duration * 1000) / self.steps)
        self._current_job = None

    def fade_in(self, on_complete: Optional[Callable] = None) -> None:

        self._cancel_running_job()
        self.window.attributes("-alpha", 0.0)
        self.window.deiconify()
        self._animate_step(0, self.steps, self._set_alpha, on_complete)

    def fade_out(self, on_complete: Optional[Callable] = None) -> None:
        self._cancel_running_job()

        def finalize():
            self.window.withdraw()
            if on_complete:
                on_complete()

        self._animate_step(0, self.steps, self._set_alpha, finalize, reverse=True)

    def _set_alpha(self, progress: float) -> None:
        try:
            self.window.attributes("-alpha", progress)
        except Exception:
            pass

    def _animate_step(
        self,
        current_step: int,
        total_steps: int,
        apply_fn: Callable[[float], None],
        on_complete: Optional[Callable],
        reverse: bool = False,
    ) -> None:
        raw_progress = current_step / total_steps
        eased = ease_out_cubic(raw_progress)
        value = (1 - eased) if reverse else eased
        apply_fn(value)

        if current_step >= total_steps:
            if on_complete:
                on_complete()
            self._current_job = None
            return

        self._current_job = self.window.after(
            self._interval_ms,
            lambda: self._animate_step(current_step + 1, total_steps, apply_fn, on_complete, reverse),
        )

    def _cancel_running_job(self) -> None:
        if self._current_job is not None:
            try:
                self.window.after_cancel(self._current_job)
            except Exception:
                pass
            self._current_job = None
