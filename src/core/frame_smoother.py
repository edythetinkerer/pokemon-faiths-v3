"""
Frame Time Smoother - Prevents frame time spikes and stuttering
"""

class FrameTimeSmoother:
    """Smooth frame times to prevent stuttering"""
    
    def __init__(self, max_dt: float = 0.05):
        """
        Args:
            max_dt: Maximum delta time (default 0.05 = 20 FPS minimum)
        """
        self.max_dt = max_dt
        self.dt_history = []
        self.history_size = 5
    
    def smooth_dt(self, dt: float) -> float:
        """
        Smooth delta time to prevent spikes
        
        Args:
            dt: Raw delta time from clock.tick()
        
        Returns:
            Smoothed delta time
        """
        # Cap maximum dt to prevent huge spikes
        dt = min(dt, self.max_dt)
        
        # Add to history
        self.dt_history.append(dt)
        if len(self.dt_history) > self.history_size:
            self.dt_history.pop(0)
        
        # Return average of recent frames
        return sum(self.dt_history) / len(self.dt_history)
