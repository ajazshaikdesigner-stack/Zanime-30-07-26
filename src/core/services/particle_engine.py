"""
Particle Engine — 2D/3D Physics Particle Simulation for Phase 4.

Presets:
  - Dust, Rain, Fire, Leaves, Magic, Snow, Spark, Smoke
"""

import math
import random
from dataclasses import dataclass, field
from enum import Enum


class ParticlePreset(Enum):
    DUST = "Dust"
    RAIN = "Rain"
    FIRE = "Fire"
    LEAVES = "Leaves"
    MAGIC = "Magic"
    SNOW = "Snow"
    SPARK = "Spark"
    SMOKE = "Smoke"


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    ax: float = 0.0
    ay: float = 0.0
    size: float = 4.0
    alpha: float = 1.0
    color: str = "#ffffff"
    lifespan: float = 2.0
    age: float = 0.0

    @property
    def is_dead(self) -> bool:
        return self.age >= self.lifespan


class ParticleEmitter:
    """Simulates particle physics & lifespan over time."""

    def __init__(self, preset: str = ParticlePreset.SNOW.value):
        self.preset = preset
        self.x = 0.0
        self.y = 0.0
        self.gravity = 9.8
        self.wind = 0.0
        self.emission_rate = 20  # particles per second
        self.particles: list[Particle] = []
        self._configure_preset()

    def _configure_preset(self):
        if self.preset == ParticlePreset.SNOW.value:
            self.gravity = 15.0
            self.wind = 5.0
            self.emission_rate = 30
        elif self.preset == ParticlePreset.RAIN.value:
            self.gravity = 300.0
            self.wind = -20.0
            self.emission_rate = 80
        elif self.preset == ParticlePreset.FIRE.value:
            self.gravity = -40.0
            self.wind = 2.0
            self.emission_rate = 50
        elif self.preset == ParticlePreset.DUST.value:
            self.gravity = 2.0
            self.wind = 1.0
            self.emission_rate = 15

    def emit(self, count: int = 1):
        for _ in range(count):
            if self.preset == ParticlePreset.FIRE.value:
                p = Particle(
                    x=self.x + random.uniform(-10, 10),
                    y=self.y,
                    vx=random.uniform(-15, 15),
                    vy=random.uniform(-80, -30),
                    size=random.uniform(6, 12),
                    color=random.choice(["#ff4500", "#ffa500", "#ff8c00", "#ffff00"]),
                    lifespan=random.uniform(0.8, 1.5),
                )
            elif self.preset == ParticlePreset.RAIN.value:
                p = Particle(
                    x=self.x + random.uniform(-400, 400),
                    y=self.y - 200,
                    vx=self.wind + random.uniform(-5, 5),
                    vy=random.uniform(250, 400),
                    size=2.0,
                    color="#74c0fc",
                    lifespan=1.2,
                )
            else:  # Snow / default
                p = Particle(
                    x=self.x + random.uniform(-400, 400),
                    y=self.y - 200,
                    vx=self.wind + random.uniform(-10, 10),
                    vy=random.uniform(20, 60),
                    size=random.uniform(3, 7),
                    color="#ffffff",
                    lifespan=4.0,
                )
            self.particles.append(p)

    def update(self, dt: float):
        """Advance physics state by dt seconds."""
        # Spawn new particles
        spawn_count = int(self.emission_rate * dt)
        if spawn_count > 0:
            self.emit(spawn_count)

        # Move & age existing particles
        alive = []
        for p in self.particles:
            p.age += dt
            if not p.is_dead:
                p.vx += (p.ax + self.wind) * dt
                p.vy += (p.ay + self.gravity) * dt
                p.x += p.vx * dt
                p.y += p.vy * dt
                p.alpha = max(0.0, 1.0 - (p.age / p.lifespan))
                alive.append(p)
        self.particles = alive
