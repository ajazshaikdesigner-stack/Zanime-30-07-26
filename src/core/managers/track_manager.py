"""
Track Manager — Business logic for advanced timeline operations.

Supports:
  - Ripple Edit (inserts clip and shifts all subsequent clips)
  - Ripple Delete (deletes clip and closes the gap)
  - Slip Edit (adjusts clip in/out points without moving clip start/end on timeline)
  - Slide Edit (moves clip and adjusts adjacent clip lengths)
  - Snapping & Clip Lock checks
"""

import logging

from src.models.timeline_model import AdvancedTimelineModel, TimelineClip, TimelineTrack

logger = logging.getLogger(__name__)


class TrackManager:
    """Encapsulates editing algorithm logic for Advanced Production Timeline."""

    def __init__(self, timeline: AdvancedTimelineModel):
        self.timeline = timeline

    def ripple_insert(self, track_uuid: str, clip: TimelineClip) -> bool:
        """Insert clip at clip.start_frame, shifting all subsequent clips right by clip.duration."""
        track = self._get_track(track_uuid)
        if not track or track.is_locked:
            return False

        shift = clip.duration
        insert_point = clip.start_frame

        # Shift existing clips right
        for c in track.clips:
            if c.start_frame >= insert_point:
                c.start_frame += shift

        clip.track_id = track_uuid
        track.clips.append(clip)
        track.clips.sort(key=lambda c: c.start_frame)
        logger.info("TrackManager: Ripple inserted '%s' (+%d frames)", clip.name, shift)
        return True

    def ripple_delete(self, track_uuid: str, clip_uuid: str) -> bool:
        """Remove clip and shift all subsequent clips left to fill the gap."""
        track = self._get_track(track_uuid)
        if not track or track.is_locked:
            return False

        clip = next((c for c in track.clips if c.uuid == clip_uuid), None)
        if not clip or clip.is_locked:
            return False

        gap_start = clip.start_frame
        gap_size = clip.duration

        track.clips.remove(clip)

        for c in track.clips:
            if c.start_frame > gap_start:
                c.start_frame = max(gap_start, c.start_frame - gap_size)

        logger.info("TrackManager: Ripple deleted clip (closed %d frame gap)", gap_size)
        return True

    def slip_clip(self, track_uuid: str, clip_uuid: str, frame_delta: int) -> bool:
        """
        Slip edit: Shift source_in and source_out by frame_delta.
        Clip start_frame and duration on timeline remain unchanged.
        """
        track = self._get_track(track_uuid)
        if not track or track.is_locked:
            return False

        clip = next((c for c in track.clips if c.uuid == clip_uuid), None)
        if not clip or clip.is_locked:
            return False

        new_in = clip.source_in + frame_delta
        if new_in < 0:
            return False

        clip.source_in = new_in
        clip.source_out = clip.source_in + clip.duration
        logger.info("TrackManager: Slipped clip '%s' by %d frames", clip.name, frame_delta)
        return True

    def slide_clip(self, track_uuid: str, clip_uuid: str, frame_delta: int) -> bool:
        """
        Slide edit: Move clip on timeline by frame_delta.
        Adjust preceding clip duration and succeeding clip start_frame.
        """
        track = self._get_track(track_uuid)
        if not track or track.is_locked:
            return False

        track.clips.sort(key=lambda c: c.start_frame)
        idx = next((i for i, c in enumerate(track.clips) if c.uuid == clip_uuid), -1)
        if idx < 0:
            return False

        clip = track.clips[idx]
        if clip.is_locked:
            return False

        # Preceding clip
        if idx > 0:
            prev_clip = track.clips[idx - 1]
            if prev_clip.duration + frame_delta < 1:
                return False
            prev_clip.duration += frame_delta

        # Succeeding clip
        if idx < len(track.clips) - 1:
            next_clip = track.clips[idx + 1]
            next_clip.start_frame += frame_delta
            next_clip.duration = max(1, next_clip.duration - frame_delta)

        clip.start_frame += frame_delta
        logger.info("TrackManager: Slid clip '%s' by %d frames", clip.name, frame_delta)
        return True

    def _get_track(self, track_uuid: str) -> TimelineTrack | None:
        return next((t for t in self.timeline.tracks if t.uuid == track_uuid), None)
