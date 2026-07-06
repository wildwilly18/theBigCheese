"""Compatibility exports for refactored entity types."""

from entities.base_entity import BaseEntity
from entities.npc import NPC, NPCState
from entities.player import Player

# Backward-compatible aliases while call sites migrate.
Actor = NPC
ActorState = NPCState
