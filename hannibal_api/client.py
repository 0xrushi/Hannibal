"""
High-level Python client for Hannibal Realtime API.

Provides typed functions for controlling Hannibal in a running game.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .transport import FileTransport


class HannibalClient:
    """
    High-level client for controlling Hannibal AI in real-time.

    Example:
        client = HannibalClient(player_id=1)
        client.select([186, 188])
        client.gather("wood.tree")
        client.build("house", mode="selected")
    """

    def __init__(
        self,
        player_id: int = 1,
        transport: Optional[FileTransport] = None,
        timeout: float = 5.0,
    ):
        """
        Initialize the client.

        Args:
            player_id: Which player's Hannibal bot to control (1-indexed)
            transport: Custom transport adapter (uses FileTransport if None)
            timeout: Default timeout for operations in seconds
        """
        self.player_id = player_id
        self.transport = transport or FileTransport(default_timeout=timeout)
        self.timeout = timeout

    def _execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a command and return the response.

        Args:
            action: Action name
            **kwargs: Action parameters

        Returns:
            Response result

        Raises:
            RuntimeError: If the command failed
        """
        request = {
            "action": action,
            "player_id": self.player_id,
            **kwargs,
        }

        response = self.transport.send_and_recv(request, timeout=self.timeout)

        if not response.get("ok"):
            error_msg = response.get("error", "Unknown error")
            raise RuntimeError(f"Command '{action}' failed: {error_msg}")

        return response.get("result", {})

    def select(self, entity_ids: List[int]) -> Dict[str, Any]:
        """
        Set current selection by entity IDs.

        Args:
            entity_ids: List of entity IDs to select

        Returns:
            Result with selected_ids (filtered to owned entities)
        """
        return self._execute("select", entity_ids=entity_ids)

    def move(self, entity_ids: List[int], x: float, z: float) -> Dict[str, Any]:
        """
        Move entities to a position.

        Args:
            entity_ids: List of entity IDs to move
            x: X coordinate
            z: Z coordinate

        Returns:
            Result with moved_ids and position
        """
        return self._execute("move", entity_ids=entity_ids, x=x, z=z)

    def gather(
        self,
        resource: str,
        targets: Optional[int] = None,
        near: str = "selection",
    ) -> Dict[str, Any]:
        """
        Order selected entities to gather a resource (improved with proximity search).

        Args:
            resource: Resource type (e.g., "wood.tree", "food.fruit", "stone.rock")
            targets: Number of resource targets to gather from (default: 1)
            near: Where to find resources:
                - "selection": Near first selected unit (default)
                - "cc": Near civic center

        Returns:
            Result with:
                - entity_ids: Selected gatherers
                - resource: Resource type gathered
                - targets: Resource entity IDs
                - nearest_distance: Distance to closest resource
        """
        params = {"resource": resource, "near": near}
        if targets is not None:
            params["targets"] = targets
        return self._execute("gather", **params)

    def gather_near_position(
        self, x: float, z: float, resource: str, radius: float = 100
    ) -> Dict[str, Any]:
        """
        Order selected entities to gather resources near a specific position.

        Args:
            x: X coordinate of search center
            z: Z coordinate of search center
            resource: Resource type (e.g., "wood.tree", "food.fruit", "stone.rock")
            radius: Search radius from position (default: 100)

        Returns:
            Result with:
                - entity_ids: Selected gatherers
                - resource: Resource type gathered
                - targets: Resource entity IDs
                - search_position: Center of search
                - search_radius: Radius used
                - resources_found: Total resources found in radius
                - nearest_distance: Distance to closest resource
        """
        return self._execute(
            "gather_near_position", x=x, z=z, resource=resource, radius=radius
        )

    def build(
        self,
        what: str,
        amount: int = 1,
        mode: str = "selected",
        x: Optional[float] = None,
        z: Optional[float] = None,
        angle: float = 0,
    ) -> Dict[str, Any]:
        """
        Build a structure.

        Args:
            what: Structure name (e.g., "house", "barracks")
            amount: Number to build
            mode: "selected" (use selected builders) or "economy" (let Hannibal manage)
            x: Optional X coordinate for building placement
            z: Optional Z coordinate for building placement
            angle: Building rotation angle in radians (default: 0)

        Returns:
            Result with template, builder_ids (if selected mode), position, and mode used
        """
        params = {"what": what, "amount": amount, "mode": mode, "angle": angle}
        if x is not None and z is not None:
            params["x"] = x
            params["z"] = z
        return self._execute("build", **params)

    def train(self, unit: str, amount: int = 1) -> Dict[str, Any]:
        """
        Train units.

        Args:
            unit: Unit type (e.g., "female.citizen", "infantry.spearman")
            amount: Number to train

        Returns:
            Result with unit and queued count
        """
        return self._execute("train", unit=unit, amount=amount)

    def research(self, tech: str) -> Dict[str, Any]:
        """
        Research a technology.

        Args:
            tech: Technology name (e.g., "phase_town")

        Returns:
            Result with tech and queued status
        """
        return self._execute("research", tech=tech)

    def get_state(self) -> Dict[str, Any]:
        """
        Get current player state.

        Returns:
            State dict with resources, population, phase, etc.
        """
        return self._execute("get_state")

    def list_entities(
        self,
        filter: Optional[Dict[str, Any]] = None,
        offset: int = 0,
        limit: int = 50,
        include_structures: bool = True,
    ) -> Dict[str, Any]:
        """
        List entities with enhanced filtering and pagination.

        Args:
            filter: Optional filter dict with options:
                - class (str): Filter by unit class (e.g., "Worker", "Soldier")
                - owner (int): Filter by owner player ID
                - position (dict): Filter by position {"x": float, "z": float, "radius": float}
                - min_health (float): Minimum health percentage (0-100)
            offset: Skip first N entities (for pagination)
            limit: Maximum entities to return (default: 50)
            include_structures: Include buildings in results (default: True)

        Returns:
            Result with:
                - entities: List of entity info dicts
                - count: Number of entities in this page
                - total: Total entities matching filter
                - offset: Current offset
                - limit: Current limit
                - has_more: Whether more entities exist
        """
        params = {"offset": offset, "limit": limit}

        if filter is None:
            filter = {}

        filter["include_structures"] = include_structures
        filter["offset"] = offset
        filter["limit"] = limit

        params["filter"] = filter
        return self._execute("list_entities", **params)

    def clear_stale_files(self):
        """Clear any stale command/response files before starting a session."""
        self.transport.clear_stale_files()

    # Combat Commands

    def attack(self, target_id: int, queued: bool = False) -> Dict[str, Any]:
        """
        Attack a specific target entity.

        Args:
            target_id: Entity ID of the target to attack
            queued: Whether to queue this command after current actions

        Returns:
            Result with attacker_ids, target_id, and queued status
        """
        return self._execute("attack", target_id=target_id, queued=queued)

    def attack_walk(
        self, x: float, z: float, target_classes: str = "Unit", queued: bool = False
    ) -> Dict[str, Any]:
        """
        Move and attack enemies encountered along the way.

        Args:
            x: X coordinate destination
            z: Z coordinate destination
            target_classes: Classes of entities to attack (default: "Unit")
            queued: Whether to queue this command after current actions

        Returns:
            Result with entity_ids, position, and target_classes
        """
        return self._execute(
            "attack_walk", x=x, z=z, target_classes=target_classes, queued=queued
        )

    def patrol(
        self, x: float, z: float, target_classes: str = "Unit", queued: bool = False
    ) -> Dict[str, Any]:
        """
        Patrol to position and back, attacking enemies encountered.

        Args:
            x: X coordinate destination
            z: Z coordinate destination
            target_classes: Classes of entities to attack (default: "Unit")
            queued: Whether to queue this command after current actions

        Returns:
            Result with entity_ids and position
        """
        return self._execute(
            "patrol", x=x, z=z, target_classes=target_classes, queued=queued
        )

    def set_stance(self, stance: str) -> Dict[str, Any]:
        """
        Set combat stance for selected units.

        Args:
            stance: Combat stance - one of:
                - "violent": Attack anything in range, chase far
                - "aggressive": Attack anything in range, chase nearby
                - "defensive": Attack when attacked, chase briefly
                - "passive": Never attack
                - "standground": Attack in range, never move

        Returns:
            Result with entity_ids and stance

        Raises:
            ValueError: If stance is not valid
        """
        valid = ["violent", "aggressive", "defensive", "passive", "standground"]
        if stance not in valid:
            raise ValueError(f"Invalid stance. Must be one of: {valid}")
        return self._execute("set_stance", stance=stance)

    def set_formation(self, formation: str) -> Dict[str, Any]:
        """
        Set unit formation for selected units.

        Args:
            formation: Formation name - one of:
                - "Scatter": Loose, spread out formation
                - "Box": Defensive square formation
                - "ColumnClosed": Tight column for marching
                - "LineClosed": Tight line formation
                - "ColumnOpen": Loose column
                - "LineOpen": Loose line
                - "Flank": Wide formation with flanks
                - "Skirmish": Loose skirmishing formation
                - "Wedge": Wedge/triangle formation
                - "Testudo": Roman turtle formation
                - "Phalanx": Greek phalanx formation
                - "Syntagma": Macedonian formation
                - "BattleLine": Standard battle line

        Returns:
            Result with entity_ids and formation
        """
        valid = [
            "Scatter",
            "Box",
            "ColumnClosed",
            "LineClosed",
            "ColumnOpen",
            "LineOpen",
            "Flank",
            "Skirmish",
            "Wedge",
            "Testudo",
            "Phalanx",
            "Syntagma",
            "BattleLine",
        ]
        if formation not in valid:
            raise ValueError(f"Invalid formation. Must be one of: {valid}")
        return self._execute("set_formation", formation=formation)

    def guard(self, target_id: int, queued: bool = False) -> Dict[str, Any]:
        """
        Guard another unit or structure.

        Args:
            target_id: Entity ID of unit/structure to guard
            queued: Whether to queue this command after current actions

        Returns:
            Result with guard_ids and target_id
        """
        return self._execute("guard", target_id=target_id, queued=queued)

    def stop(self, queued: bool = False) -> Dict[str, Any]:
        """
        Stop current action for selected units.

        Args:
            queued: Whether to queue this command after current actions

        Returns:
            Result with entity_ids
        """
        return self._execute("stop", queued=queued)

    # Unit Management Commands

    def garrison(self, target_id: int, queued: bool = False) -> Dict[str, Any]:
        """
        Garrison selected units into a building or ship.

        Args:
            target_id: Entity ID of building/ship to garrison into
            queued: Whether to queue this command after current actions

        Returns:
            Result with entity_ids, target_id, and queued status

        Example:
            # Garrison units in civic center for healing/protection
            client.select(soldier_ids)
            client.garrison(target_id=civic_center_id)

            # Garrison units on transport ship
            client.select(unit_ids)
            client.garrison(target_id=transport_ship_id)
        """
        return self._execute("garrison", target_id=target_id, queued=queued)

    def unload(
        self, garrison_holder_id: int, entity_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Unload specific units from a garrison holder (building or ship).

        Args:
            garrison_holder_id: Entity ID of the garrison holder
            entity_ids: Optional list of specific entity IDs to unload.
                       If None, unloads the first garrisoned unit.

        Returns:
            Result with garrison_holder_id and unloaded_ids

        Example:
            # Unload first unit
            client.unload(garrison_holder_id=building_id)

            # Unload specific units
            client.unload(garrison_holder_id=building_id, entity_ids=[100, 101])
        """
        params = {"garrison_holder_id": garrison_holder_id}
        if entity_ids is not None:
            params["entity_ids"] = entity_ids
        return self._execute("unload", **params)

    def unload_all(self, garrison_holder_id: int) -> Dict[str, Any]:
        """
        Unload all owned units from a garrison holder.

        Args:
            garrison_holder_id: Entity ID of the garrison holder

        Returns:
            Result with garrison_holder_id

        Example:
            # Unload all units from civic center
            client.unload_all(garrison_holder_id=civic_center_id)

            # Unload all units from transport ship
            client.unload_all(garrison_holder_id=transport_ship_id)
        """
        return self._execute("unload_all", garrison_holder_id=garrison_holder_id)

    def repair(
        self,
        target_id: int,
        autocontinue: bool = True,
        queued: bool = False,
    ) -> Dict[str, Any]:
        """
        Repair a damaged building or siege weapon.

        Args:
            target_id: Entity ID of building/siege to repair
            autocontinue: Whether to continue repairing automatically (default: True)
            queued: Whether to queue this command after current actions

        Returns:
            Result with repairer_ids, target_id, autocontinue, and queued status

        Example:
            # Select workers
            client.select(worker_ids)

            # Repair damaged building
            client.repair(target_id=damaged_building_id)

            # Repair and don't auto-continue after done
            client.repair(target_id=building_id, autocontinue=False)
        """
        return self._execute(
            "repair", target_id=target_id, autocontinue=autocontinue, queued=queued
        )

    def heal(self, target_id: int, queued: bool = False) -> Dict[str, Any]:
        """
        Move healer units to target for healing.

        Note: In 0 A.D., healing is automatic. Healer units (priests, etc.)
        automatically heal nearby wounded friendly units. This command moves
        healers to the target and guards them, allowing auto-healing.

        Args:
            target_id: Entity ID of wounded unit to heal
            queued: Whether to queue this command after current actions

        Returns:
            Result with healer_ids, target_id, and queued status

        Example:
            # Select healers (priests, etc.)
            healers = client.list_entities(filter={"class": "Healer"})
            client.select([h["id"] for h in healers["entities"][:2]])

            # Send to heal wounded soldier
            client.heal(target_id=wounded_soldier_id)
        """
        return self._execute("heal", target_id=target_id, queued=queued)

    def return_resources(
        self, dropsite_id: Optional[int] = None, queued: bool = False
    ) -> Dict[str, Any]:
        """
        Order selected gatherers to return resources to a dropsite.

        Args:
            dropsite_id: Optional entity ID of dropsite (civic center, storehouse, etc.)
                        If None, finds nearest dropsite automatically.
            queued: Whether to queue this command after current actions

        Returns:
            Result with entity_ids, dropsite_id, and queued status

        Example:
            # Select gatherers
            client.select(gatherer_ids)

            # Return to nearest dropsite
            client.return_resources()

            # Return to specific dropsite
            client.return_resources(dropsite_id=storehouse_id)
        """
        params = {"queued": queued}
        if dropsite_id is not None:
            params["dropsite_id"] = dropsite_id
        return self._execute("return_resources", **params)
