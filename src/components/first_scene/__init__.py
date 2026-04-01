"""First scene specification — WorldSeed + PlayerCharacter → structured scene brief."""

from .builder import FirstSceneSpecBuilder
from .models import FirstSceneSpec, SceneHook, SceneLocation

__all__ = ["FirstSceneSpec", "SceneLocation", "SceneHook", "FirstSceneSpecBuilder"]
