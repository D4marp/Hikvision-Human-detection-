"""
Office Worker Activity & Productivity Analyzer
Detects sitting duration, posture, activity level, and effectiveness metrics
"""

import cv2
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import threading
import time


class OfficeAnalyzer:
    """Analyze office worker productivity and activity"""
    
    def __init__(self):
        self.workers = {}  # {person_id: worker_data}
        self.activity_history = defaultdict(list)
        self.sit_durations = defaultdict(lambda: {'start': None, 'total': 0, 'count': 0})
        self.posture_data = defaultdict(lambda: {'sitting': 0, 'standing': 0, 'bending': 0})
        self.activity_levels = defaultdict(lambda: {'idle': 0, 'active': 0, 'very_active': 0})
        self.last_position = defaultdict(lambda: None)
        self.position_stability = defaultdict(lambda: {'stable_frames': 0, 'total_frames': 0})
        
    def detect_sitting_duration(self, person_id, keypoints, confidence):
        """
        Detect if person is sitting and track duration
        keypoints: YOLO pose keypoints [x, y, conf] for each joint
        """
        if keypoints is None or len(keypoints) < 5:
            return {'status': 'unknown', 'duration': 0, 'risk': 'unknown'}
        
        # Extract key body points (assuming COCO keypoints format)
        # 5: left_hip, 6: right_hip, 11: left_knee, 12: right_knee
        
        try:
            # Check if hips and knees are visible
            if len(keypoints) >= 12:
                hip_y = np.mean([keypoints[5][1], keypoints[6][1]])  # Hip Y position
                knee_y = np.mean([keypoints[11][1], keypoints[12][1]])  # Knee Y position
                
                # If knee is lower than hip, likely sitting
                is_sitting = knee_y > hip_y
                
                if is_sitting:
                    if self.sit_durations[person_id]['start'] is None:
                        self.sit_durations[person_id]['start'] = datetime.now()
                    
                    current_duration = (datetime.now() - self.sit_durations[person_id]['start']).total_seconds()
                    
                    # Risk assessment
                    risk = 'normal'
                    if current_duration > 3600:  # More than 1 hour
                        risk = 'high'
                    elif current_duration > 1800:  # More than 30 minutes
                        risk = 'medium'
                    
                    return {
                        'status': 'sitting',
                        'duration': int(current_duration),
                        'duration_formatted': self._format_duration(current_duration),
                        'risk': risk,
                        'recommendation': self._get_sitting_recommendation(current_duration)
                    }
                else:
                    # Standing up - record previous sitting duration
                    if self.sit_durations[person_id]['start'] is not None:
                        sit_time = (datetime.now() - self.sit_durations[person_id]['start']).total_seconds()
                        self.sit_durations[person_id]['total'] += sit_time
                        self.sit_durations[person_id]['count'] += 1
                        self.sit_durations[person_id]['start'] = None
                    
                    return {
                        'status': 'standing',
                        'duration': 0,
                        'duration_formatted': '0s',
                        'risk': 'low',
                        'recommendation': 'Good! Maintaining activity'
                    }
        except:
            pass
        
        return {'status': 'unknown', 'duration': 0, 'risk': 'unknown'}
    
    def detect_posture(self, person_id, keypoints):
        """Detect body posture (sitting, standing, bending)"""
        if keypoints is None or len(keypoints) < 13:
            return 'unknown'
        
        try:
            # Head, shoulders, hips positions
            head_y = keypoints[0][1]
            shoulder_y = np.mean([keypoints[5][1], keypoints[6][1]])
            hip_y = np.mean([keypoints[11][1], keypoints[12][1]])
            
            # Calculate body angles
            shoulder_spread = abs(keypoints[5][0] - keypoints[6][0])
            
            # Posture classification
            if abs(head_y - shoulder_y) > 50 and shoulder_spread > 100:
                posture = 'sitting'
                self.posture_data[person_id]['sitting'] += 1
            elif abs(head_y - hip_y) > 200:
                posture = 'standing'
                self.posture_data[person_id]['standing'] += 1
            elif abs(head_y - hip_y) < 80:
                posture = 'bending'
                self.posture_data[person_id]['bending'] += 1
            else:
                posture = 'neutral'
                self.posture_data[person_id]['sitting'] += 1
            
            return posture
        except:
            return 'unknown'
    
    def detect_activity_level(self, person_id, keypoints, prev_keypoints=None):
        """
        Detect activity level: idle, active, very_active
        Based on movement between frames
        """
        if keypoints is None:
            return 'idle'
        
        if prev_keypoints is None:
            prev_keypoints = keypoints
        
        try:
            # Calculate movement magnitude
            movement = 0
            for i in range(min(len(keypoints), len(prev_keypoints))):
                if keypoints[i][2] > 0.5 and prev_keypoints[i][2] > 0.5:
                    dx = keypoints[i][0] - prev_keypoints[i][0]
                    dy = keypoints[i][1] - prev_keypoints[i][1]
                    movement += np.sqrt(dx**2 + dy**2)
            
            # Classify activity
            avg_movement = movement / max(len(keypoints), 1)
            
            if avg_movement < 5:
                activity = 'idle'
                self.activity_levels[person_id]['idle'] += 1
            elif avg_movement < 15:
                activity = 'active'
                self.activity_levels[person_id]['active'] += 1
            else:
                activity = 'very_active'
                self.activity_levels[person_id]['very_active'] += 1
            
            return activity
        except:
            return 'idle'
    
    def calculate_effectiveness_score(self, person_id):
        """
        Calculate employee effectiveness score (0-100)
        Based on:
        - Activity level (40%)
        - Posture breaks (30%)
        - Sitting duration (30%)
        """
        try:
            total_activity = self.activity_levels[person_id]['idle'] + \
                            self.activity_levels[person_id]['active'] + \
                            self.activity_levels[person_id]['very_active']
            
            if total_activity == 0:
                return 50  # Default score
            
            # Activity score (40%)
            active_ratio = (self.activity_levels[person_id]['active'] + 
                           self.activity_levels[person_id]['very_active']) / total_activity
            activity_score = active_ratio * 40
            
            # Posture variation score (30%)
            total_posture = self.posture_data[person_id]['sitting'] + \
                           self.posture_data[person_id]['standing'] + \
                           self.posture_data[person_id]['bending']
            
            if total_posture > 0:
                posture_variation = (self.posture_data[person_id]['standing'] + 
                                    self.posture_data[person_id]['bending']) / total_posture
                posture_score = posture_variation * 30
            else:
                posture_score = 15
            
            # Sitting duration score (30%)
            avg_sit_duration = 0
            if self.sit_durations[person_id]['count'] > 0:
                avg_sit_duration = self.sit_durations[person_id]['total'] / \
                                   self.sit_durations[person_id]['count']
            
            # Ideal: 20-30 minute sessions
            if avg_sit_duration == 0:
                sitting_score = 30
            elif avg_sit_duration <= 1800:  # 30 minutes
                sitting_score = 30
            elif avg_sit_duration <= 3600:  # 1 hour
                sitting_score = 20
            else:
                sitting_score = 10
            
            total_score = activity_score + posture_score + sitting_score
            return min(100, int(total_score))
        except:
            return 50
    
    def get_worker_stats(self, person_id):
        """Get comprehensive worker statistics"""
        sit_info = self.sit_durations[person_id]
        posture_info = self.posture_data[person_id]
        activity_info = self.activity_levels[person_id]
        
        total_activity = activity_info['idle'] + activity_info['active'] + activity_info['very_active']
        
        avg_sit_duration = 0
        if sit_info['count'] > 0:
            avg_sit_duration = sit_info['total'] / sit_info['count']
        
        active_percentage = 0
        if total_activity > 0:
            active_percentage = ((activity_info['active'] + activity_info['very_active']) / total_activity) * 100
        
        effectiveness_score = self.calculate_effectiveness_score(person_id)
        
        return {
            'person_id': person_id,
            'effectiveness_score': effectiveness_score,
            'effectiveness_grade': self._get_grade(effectiveness_score),
            'current_sitting_duration': self.sit_durations[person_id]['start'] is not None and
                                       int((datetime.now() - self.sit_durations[person_id]['start']).total_seconds()) or 0,
            'average_sit_duration': int(avg_sit_duration),
            'average_sit_duration_formatted': self._format_duration(avg_sit_duration),
            'total_sitting_time': int(sit_info['total']),
            'sitting_sessions': sit_info['count'],
            'activity_breakdown': {
                'idle_percentage': (activity_info['idle'] / total_activity * 100) if total_activity > 0 else 0,
                'active_percentage': (activity_info['active'] / total_activity * 100) if total_activity > 0 else 0,
                'very_active_percentage': (activity_info['very_active'] / total_activity * 100) if total_activity > 0 else 0,
            },
            'posture_breakdown': {
                'sitting_percentage': (posture_info['sitting'] / (sum(posture_info.values()) or 1)) * 100,
                'standing_percentage': (posture_info['standing'] / (sum(posture_info.values()) or 1)) * 100,
                'bending_percentage': (posture_info['bending'] / (sum(posture_info.values()) or 1)) * 100,
            },
            'recommendations': self._get_worker_recommendations(person_id, effectiveness_score)
        }
    
    def _get_sitting_recommendation(self, duration_seconds):
        """Get recommendation based on sitting duration"""
        if duration_seconds < 600:
            return "Continue working - good pace"
        elif duration_seconds < 1800:
            return "Normal sitting duration"
        elif duration_seconds < 3600:
            return "⚠️  Consider a break soon"
        else:
            return "🚨 Extended sitting - take a break!"
    
    def _get_worker_recommendations(self, person_id, score):
        """Get personalized recommendations"""
        recommendations = []
        
        activity_info = self.activity_levels[person_id]
        total_activity = sum(activity_info.values())
        
        if total_activity > 0:
            idle_ratio = activity_info['idle'] / total_activity
            if idle_ratio > 0.7:
                recommendations.append("📍 Low activity level - increase movement")
        
        posture_info = self.posture_data[person_id]
        total_posture = sum(posture_info.values())
        
        if total_posture > 0:
            standing_ratio = (posture_info['standing'] + posture_info['bending']) / total_posture
            if standing_ratio < 0.1:
                recommendations.append("🪑 Try standing or changing positions regularly")
        
        avg_sit = 0
        if self.sit_durations[person_id]['count'] > 0:
            avg_sit = self.sit_durations[person_id]['total'] / self.sit_durations[person_id]['count']
        
        if avg_sit > 3600:
            recommendations.append("⏱️  Take 5-10 minute breaks every hour")
        
        if score < 50:
            recommendations.append("💪 Increase overall activity level")
        
        return recommendations if recommendations else ["✅ Keep up the good work!"]
    
    def _format_duration(self, seconds):
        """Format seconds to readable duration"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def _get_grade(self, score):
        """Convert score to grade"""
        if score >= 90:
            return "A - Excellent"
        elif score >= 80:
            return "B - Good"
        elif score >= 70:
            return "C - Average"
        elif score >= 50:
            return "D - Below Average"
        else:
            return "F - Needs Improvement"
    
    def add_office_overlay(self, frame, detections, fps=30):
        """Add office analytics overlay to frame"""
        h, w = frame.shape[:2]
        
        # Semi-transparent overlay
        overlay = frame.copy()
        
        # Title
        cv2.putText(overlay, "OFFICE PRODUCTIVITY MONITOR", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(overlay, f"FPS: {fps:.1f}", (w - 150, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        # Worker info
        y_offset = 70
        for person_id, detection in detections.items():
            if 'effectiveness_score' in detection:
                stats = detection
                score = stats['effectiveness_score']
                grade = stats['effectiveness_grade']
                
                # Color based on score
                if score >= 80:
                    color = (0, 255, 0)  # Green
                elif score >= 60:
                    color = (0, 255, 255)  # Yellow
                else:
                    color = (0, 0, 255)  # Red
                
                # Worker card
                card_height = 120
                cv2.rectangle(overlay, (10, y_offset), (w - 10, y_offset + card_height), 
                             color, 2)
                
                y_offset += 25
                cv2.putText(overlay, f"Worker #{person_id}", (20, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
                
                y_offset += 25
                cv2.putText(overlay, f"Score: {score}/100 ({grade})", (20, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
                
                y_offset += 20
                cv2.putText(overlay, 
                           f"Sitting: {stats['average_sit_duration_formatted']} avg | " +
                           f"Current: {stats['current_sitting_duration']}s",
                           (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                y_offset += 20
                activity = stats['activity_breakdown']
                cv2.putText(overlay,
                           f"Activity: Active {activity['active_percentage']:.0f}% | " +
                           f"Very Active {activity['very_active_percentage']:.0f}%",
                           (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                y_offset += 35
        
        # Blend
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        return frame
