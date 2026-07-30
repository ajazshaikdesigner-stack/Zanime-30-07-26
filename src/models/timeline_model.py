"""
Data models for Advanced Production Timeline — Phase 4.

Includes:
  - TimelineMarker (frame, label, color, comment)
  - TimelineClip (name, track_id, start_frame, duration, source_in, source_out, color, is_locked)
  - TimelineTrack (id, name, track_type, color, is_muted, is_soloed, is_locked, clips, folder_id)
  - TrackFolder (id, name, is_collapsed, color)
  - AdvancedTimelineModel (fps, total_frames, playhead_frame, tracks, folders, markers, snap_to_grid)
"""

import uuid
from dataclasses import dataclass, field
from enum import Enum


class TrackType(Enum):
    VIDEO = "video"
    AUDIO = "audio"
    CAMERA = "camera"
    EFFECT = "effect"
    SUBTITLE = "subtitle"


class EditMode(Enum):
    OVERWRITE = "overwrite"
    INSERT_RIPPLE = "insert_ripple"
    SLIP = "slip"
    SLIDE = "slide"


@dataclass
class TimelineMarker:
    frame: int = 0
    label: str = "Marker"
    color: str = "#ffd43b"
    comment: str = ""
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class TimelineClip:
    name: str = "Clip"
    track_id: str = ""
    start_frame: int = 0
    duration: int = 48
    source_in: int = 0
    source_out: int = 48
    color: str = "#4a9aff"
    is_locked: bool = False
    is_selected: bool = False
    asset_path: str = ""
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def end_frame(self) -> int:
        return self.start_frame + self.duration


@dataclass
class TrackFolder:
    name: str = "Folder"
    is_collapsed: bool = False
    color: str = "#333344"
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class TimelineTrack:
    name: str = "Track 1"
    track_type: str = TrackType.VIDEO.value
    color: str = "#4a9aff"
    is_muted: bool = False
    is_soloed: bool = False
    is_locked: bool = False
    folder_id: str | None = None
    clips: list[TimelineClip] = field(default_factory=list)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class AdvancedTimelineModel:
    fps: int = 24
    total_frames: int = 480
    playhead_frame: int = 0
    edit_mode: str = EditMode.OVERWRITE.value
    snap_enabled: bool = True
    snap_tolerance: int = 5
    tracks: list[TimelineTrack] = field(default_factory=list)
    folders: list[TrackFolder] = field(default_factory=list)
    markers: list[TimelineMarker] = field(default_factory=list)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

    def add_track(self, name: str, track_type: str = TrackType.VIDEO.value) -> TimelineTrack:
        track = TimelineTrack(name=name, track_type=track_type)
        self.tracks.append(track)
        return track

    def add_marker(self, frame: int, label: str = "Marker", color: str = "#ffd43b") -> TimelineMarker:
        marker = TimelineMarker(frame=frame, label=label, color=color)
        self.markers.append(marker)
        self.markers.sort(key=lambda m: m.frame)
        return marker

    def find_snap_point(self, candidate_frame: int) -> int:
        """Return nearest snap frame within snap_tolerance (playhead, markers, clip edges)."""
        if not self.snap_enabled:
            return candidate_frame

        candidates = [self.playhead_frame]
        candidates.extend(m.frame for m in self.markers)
        for tr in self.tracks:
            for clip in tr.clips:
                candidates.append(clip.start_frame)
                candidates.append(clip.end_frame)

        best_frame = candidate_frame
        min_dist = self.snap_tolerance + 1

        for c in candidates:
            dist = abs(c - candidate_frame)
            if dist < min_dist:
                min_dist = dist
                best_frame = c

        return best_frame
