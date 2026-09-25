"""
Retention Service.
Implements exponential decay modeling of audience retention curves,
R^2 goodness-of-fit gating (suppressing lambda if R^2 < 0.70),
intro hook drop-off analysis (0-30s), mid-video dip detection, and end-screen completion rate.
"""
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from scipy.optimize import curve_fit
from backend.app.config import settings

def exp_decay_model(t, r0, decay_lambda, c):
    """Exponential retention decay function: R(t) = R0 * exp(-lambda * t) + C"""
    return r0 * np.exp(-decay_lambda * t) + c

class RetentionService:
    @staticmethod
    def fit_retention_curve(points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fits exponential decay model to retention curve points.
        Evaluates R^2 goodness of fit.
        If R^2 < RETENTION_FIT_R2_MIN (0.70), suppresses lambda parameter.
        """
        if not points or len(points) < 5:
            return {
                "retention_decay_lambda": None,
                "retention_r2": None,
                "is_lambda_suppressed": True,
                "fit_status": "INSUFFICIENT_DATA",
                "fitted_curve": []
            }

        # Sort points by relative position (0.0 to 1.0)
        sorted_pts = sorted(points, key=lambda x: x.get("relative_position", 0.0))
        t_vals = np.array([p.get("relative_position", 0.0) for p in sorted_pts], dtype=float)
        r_vals = np.array([p.get("retention_percentage", 0.0) for p in sorted_pts], dtype=float)

        fitted_curve = []
        lambda_val = None
        r2_val = None
        is_suppressed = True
        status_msg = "OK"

        try:
            # Initial guess: r0 ~ initial drop, lambda ~ 1.5, c ~ tail retention
            p0 = [max(r_vals[0] - r_vals[-1], 10.0), 1.5, min(r_vals[-1], 40.0)]
            bounds = ([0.0, 0.001, 0.0], [150.0, 50.0, 100.0])
            
            popt, _ = curve_fit(exp_decay_model, t_vals, r_vals, p0=p0, bounds=bounds, maxfev=2000)
            r0_fit, lambda_fit, c_fit = popt

            # Generate fitted values
            pred_y = exp_decay_model(t_vals, r0_fit, lambda_fit, c_fit)
            
            # Compute R^2
            ss_res = np.sum((r_vals - pred_y) ** 2)
            ss_tot = np.sum((r_vals - np.mean(r_vals)) ** 2)
            r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
            r2_val = round(float(max(0.0, min(r2, 1.0))), 3)
            lambda_val = round(float(lambda_fit), 3)

            # Enforce Part 2.2 R^2 gating parameter
            if r2_val >= settings.RETENTION_FIT_R2_MIN:
                is_suppressed = False
                status_msg = "VALID_FIT"
            else:
                is_suppressed = True
                status_msg = "SUPPRESSED_DUE_TO_LOW_R2"

            fitted_curve = [
                {
                    "relative_position": round(float(t), 3),
                    "fitted_percentage": round(float(y), 2)
                }
                for t, y in zip(t_vals, pred_y)
            ]

        except Exception as e:
            status_msg = f"FIT_ERROR: {str(e)}"
            is_suppressed = True

        return {
            "retention_decay_lambda": lambda_val if not is_suppressed else None,
            "retention_r2": r2_val,
            "is_lambda_suppressed": is_suppressed,
            "fit_status": status_msg,
            "fitted_curve": fitted_curve
        }

    @staticmethod
    def analyze_retention_dynamics(
        points: List[Dict[str, Any]], 
        duration_sec: int
    ) -> Dict[str, Any]:
        """
        Identifies crucial retention milestones:
        - 0-30s intro hook drop-off
        - Mid-video dips count
        - Re-watch spikes count
        - End-screen completion rate (retention at 95% mark)
        """
        if not points or len(points) < 5:
            return {
                "intro_dropoff_30s": 0.0,
                "mid_video_dips_count": 0,
                "rewatch_spikes_count": 0,
                "end_screen_rate": 0.0,
                "hook_health": "UNKNOWN"
            }

        sorted_pts = sorted(points, key=lambda x: x.get("second_offset", 0))
        
        # 1. Intro drop-off: difference between t=0 (or first point) and t=30s
        first_pct = sorted_pts[0].get("retention_percentage", 100.0)
        
        # Find closest point to 30 seconds
        t30_point = min(sorted_pts, key=lambda p: abs(p.get("second_offset", 0) - 30))
        t30_pct = t30_point.get("retention_percentage", 70.0)
        intro_drop = round(max(0.0, first_pct - t30_pct), 2)

        # 2. Mid-video dips and re-watch spikes
        # Segment between 30s and 90% duration
        mid_dips = 0
        rewatch_spikes = 0
        
        for i in range(1, len(sorted_pts) - 1):
            curr_sec = sorted_pts[i].get("second_offset", 0)
            if 30 < curr_sec < (duration_sec * 0.9):
                prev_pct = sorted_pts[i-1].get("retention_percentage", 0.0)
                curr_pct = sorted_pts[i].get("retention_percentage", 0.0)
                diff = curr_pct - prev_pct
                
                if diff < -4.0:  # Sudden drop of > 4%
                    mid_dips += 1
                elif diff > 2.5:  # Spike of > 2.5% indicating re-watching
                    rewatch_spikes += 1

        # 3. End-screen rate (retention near 95% position)
        end_point = min(sorted_pts, key=lambda p: abs(p.get("relative_position", 0.0) - 0.95))
        end_rate = round(float(end_point.get("retention_percentage", 0.0)), 2)

        # Hook health assessment
        if intro_drop <= 25.0:
            hook_health = "EXCELLENT"
        elif intro_drop <= 35.0:
            hook_health = "AVERAGE"
        else:
            hook_health = "HIGH_DROPOFF"

        return {
            "intro_dropoff_30s": intro_drop,
            "mid_video_dips_count": mid_dips,
            "rewatch_spikes_count": rewatch_spikes,
            "end_screen_rate": end_rate,
            "hook_health": hook_health
        }
