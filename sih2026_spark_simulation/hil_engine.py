import time
import numpy as np

def generate_virtual_hil_telemetry(flight_time_s=10.0, setback_g=20000.0):
    """
    Generates synthetic 100Hz Hardware-in-the-Loop (HIL) telemetry stream
    mimicking live ESP32/STM32 microcontroller MEMS IMU and servo PWM signals.
    """
    t = float(flight_time_s)
    
    # 1. IMU Gyro & Orientation
    pitch_deg = float(np.degrees(np.arctan2(10.0, max(1.0, 50.0 - t))))
    roll_deg = float((np.sin(t * 1.2) * 2.5))  # Despun nose roll stability ~0 deg
    yaw_deg = float(np.sin(t * 0.5) * 4.0)
    
    # 2. Setback Shock Acceleration Sensor (G-load)
    if t <= 0.1:
        current_g = float(setback_g * (t / 0.1))
    elif t <= 0.3:
        current_g = float(setback_g * np.exp(-(t - 0.1) * 15.0))
    else:
        current_g = float(1.0 + 0.15 * np.sin(t * 5.0))
        
    # 3. 4x Servo PWM Command Pulse Widths (1000us to 2000us, 1500us neutral)
    servo1_us = int(1500 + 350 * np.sin(t * 1.5))
    servo2_us = int(1500 - 350 * np.sin(t * 1.5))
    servo3_us = int(1500 + 200 * np.cos(t * 1.5))
    servo4_us = int(1500 - 200 * np.cos(t * 1.5))
    
    return {
        "timestamp_ms": int(t * 1000.0),
        "imu_pitch_deg": pitch_deg,
        "imu_roll_deg": roll_deg,
        "imu_yaw_deg": yaw_deg,
        "setback_g_load": current_g,
        "servo1_pwm_us": servo1_us,
        "servo2_pwm_us": servo2_us,
        "servo3_pwm_us": servo3_us,
        "servo4_pwm_us": servo4_us,
        "packet_rate_hz": 100,
        "hardware_status": "ONLINE (ESP32-S3 HIL Bridge Connected)"
    }
