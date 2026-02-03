// @ts-nocheck
HANNIBAL = (function (H) {
    H.LIB.Rpc = function (context) {
        H.extend(this, {
            context: context,
            klass: "rpc",
            parent: context,
            name: context.name + ":rpc",
            // Current selection (for gather/build commands)
            selection: [],
            imports: [
                "id",
                "state",
                "effector",
                "economy",
                "resources",
                "villages",
            ],
        });
    };
    H.LIB.Rpc.prototype = H.mixin(H.LIB.Serializer.prototype, {
        constructor: H.LIB.Rpc,
        log: function () {
            this.deb();
            this.deb("   RPC: executor initialized");
        },
        tick: function (secs, tick) {
            // Output entity list on first tick if debug chat is enabled
            if (tick === 5 && this.checkDebug("cht")) {
                this.listAllEntities();
            }
            return 0;
        },
        listAllEntities: function () {
            var _this = this;
            // Output all owned entities to stdout for easy ID discovery
            var units = this.state.getOwnUnits().toEntityArray();
            var structures = this.state.getOwnStructures().toEntityArray();
            this.deb("   RPC: === ENTITY LIST ===");
            this.deb("   RPC: Units (%s):", units.length);
            units.slice(0, 30).forEach(function (ent) {
                var pos = ent.position();
                _this.deb("   RPC:   ID %s: %s at [%s, %s]", ent.id(), ent.templateName(), pos ? Math.round(pos[0]) : "?", pos ? Math.round(pos[1]) : "?");
            });
            this.deb("   RPC: Structures (%s):", structures.length);
            structures.slice(0, 10).forEach(function (ent) {
                var pos = ent.position();
                _this.deb("   RPC:   ID %s: %s at [%s, %s]", ent.id(), ent.templateName(), pos ? Math.round(pos[0]) : "?", pos ? Math.round(pos[1]) : "?");
            });
            this.deb("   RPC: === END ENTITY LIST ===");
        },
        // Callable methods for external use (via console or injection)
        move: function (entity_ids, x, z) {
            // Move entities to position
            if (!Array.isArray(entity_ids)) {
                entity_ids = [entity_ids];
            }
            var owned = this.filterOwnedEntities(entity_ids);
            if (!owned.length) {
                this.deb("   RPC: ERROR - No owned entities found in: %s", uneval(entity_ids));
                return { ok: false, error: "No owned entities found" };
            }
            this.effector.move(owned, [x, z]);
            this.deb("   RPC: Moved entities %s to [%s, %s]", uneval(owned), x, z);
            return {
                ok: true,
                result: {
                    moved_ids: owned,
                    position: { x: x, z: z }
                }
            };
        },
        select: function (entity_ids) {
            // Set current selection
            if (!Array.isArray(entity_ids)) {
                entity_ids = [entity_ids];
            }
            var owned = this.filterOwnedEntities(entity_ids);
            this.selection = owned;
            this.deb("   RPC: Selected entities: %s", uneval(owned));
            return {
                ok: true,
                result: { selected_ids: owned }
            };
        },
        gather: function (resource, targets, near) {
            // Order selected entities to gather a resource
            if (!this.selection || !this.selection.length) {
                return { ok: false, error: "No entities selected for gather command" };
            }
            near = near || "selection";
            this.deb("   RPC: Gather %s near %s with entities: %s", resource, near, uneval(this.selection));
            // Parse resource type
            var parts = resource.split(".");
            var resourceType = parts[0]; // e.g., "wood" from "wood.tree"
            var resourceSubtype = parts[1]; // e.g., "tree" from "wood.tree"
            // Find reference position for "near" calculation
            var refPosition = null;
            if (near === "selection" && this.selection.length > 0) {
                // Use first selected unit's position
                var firstUnit = this.state.getEntityById(this.selection[0]);
                if (firstUnit) {
                    var pos = firstUnit.position();
                    if (pos) {
                        refPosition = { x: pos[0], z: pos[1] };
                    }
                }
            }
            else if (near === "cc" && this.villages && this.villages.list.length > 0) {
                // Use civic center position
                var cc = this.villages.list[0].center;
                if (cc && cc.position) {
                    var pos = cc.position();
                    if (pos) {
                        refPosition = { x: pos[0], z: pos[1] };
                    }
                }
            }
            if (!refPosition) {
                return { ok: false, error: "Could not determine reference position for resource search" };
            }
            // Find resources of the specified type
            var resourceList = [];
            if (this.resources && this.resources[resourceType]) {
                // Handle both flat array and nested structure
                var resourceGroup = this.resources[resourceType];
                if (Array.isArray(resourceGroup)) {
                    // Flat array of resources
                    resourceList = resourceGroup;
                }
                else if (resourceSubtype && resourceGroup[resourceSubtype]) {
                    // Nested structure: resources[type][subtype]
                    var subGroup_1 = resourceGroup[resourceSubtype];
                    if (Array.isArray(subGroup_1)) {
                        resourceList = subGroup_1;
                    }
                    else {
                        // It's an object with IDs as keys
                        resourceList = Object.keys(subGroup_1).map(function (id) {
                            return subGroup_1[id];
                        });
                    }
                }
                else {
                    // Try to get all subtypes
                    resourceList = [];
                    for (var key in resourceGroup) {
                        if (resourceGroup.hasOwnProperty(key)) {
                            var subGroup = resourceGroup[key];
                            if (Array.isArray(subGroup)) {
                                resourceList = resourceList.concat(subGroup);
                            }
                            else if (typeof subGroup === 'object') {
                                for (var id in subGroup) {
                                    if (subGroup.hasOwnProperty(id)) {
                                        resourceList.push(subGroup[id]);
                                    }
                                }
                            }
                        }
                    }
                }
            }
            if (!resourceList || resourceList.length === 0) {
                return {
                    ok: false,
                    error: "No " + resource + " resources found on map"
                };
            }
            // Filter out consumed/invalid resources and convert to entities
            var validResources = [];
            for (var i = 0; i < resourceList.length; i++) {
                var res = resourceList[i];
                // Handle both resource objects and entity IDs
                var resId = res.id ? res.id : (typeof res === 'number' ? res : null);
                if (resId) {
                    var entity = this.state.getEntityById(resId);
                    if (entity) {
                        var pos = entity.position();
                        if (pos) {
                            validResources.push({
                                id: resId,
                                x: pos[0],
                                z: pos[1]
                            });
                        }
                    }
                }
            }
            if (validResources.length === 0) {
                return {
                    ok: false,
                    error: "No valid " + resource + " resources found (all may be depleted)"
                };
            }
            // Sort by distance to reference position
            var sortByDistance = function (a, b) {
                var da = (a.x - refPosition.x) * (a.x - refPosition.x) + (a.z - refPosition.z) * (a.z - refPosition.z);
                var db = (b.x - refPosition.x) * (b.x - refPosition.x) + (b.z - refPosition.z) * (b.z - refPosition.z);
                return da - db;
            };
            validResources.sort(sortByDistance);
            // Take closest resource(s)
            var numTargets = targets || 1;
            var targetIds = validResources.slice(0, numTargets).map(function (r) { return r.id; });
            // Execute gather via effector
            this.effector.gather(this.selection, targetIds);
            this.deb("   RPC: Gathering from %s nearest resources", targetIds.length);
            return {
                ok: true,
                result: {
                    entity_ids: this.selection,
                    resource: resource,
                    targets: targetIds,
                    nearest_distance: Math.sqrt((validResources[0].x - refPosition.x) * (validResources[0].x - refPosition.x) +
                        (validResources[0].z - refPosition.z) * (validResources[0].z - refPosition.z))
                }
            };
        },
        gatherNearPosition: function (x, z, resource, radius) {
            // Order selected entities to gather resources near a specific position
            if (!this.selection || !this.selection.length) {
                return { ok: false, error: "No entities selected for gather_near_position command" };
            }
            radius = radius || 100; // Default search radius
            var refPosition = { x: x, z: z };
            this.deb("   RPC: Gather %s near position [%s, %s] radius %s", resource, x, z, radius);
            // Parse resource type
            var parts = resource.split(".");
            var resourceType = parts[0];
            var resourceSubtype = parts[1];
            // Find resources of the specified type
            var resourceList = [];
            if (this.resources && this.resources[resourceType]) {
                var resourceGroup = this.resources[resourceType];
                if (Array.isArray(resourceGroup)) {
                    resourceList = resourceGroup;
                }
                else if (resourceSubtype && resourceGroup[resourceSubtype]) {
                    var subGroup_2 = resourceGroup[resourceSubtype];
                    if (Array.isArray(subGroup_2)) {
                        resourceList = subGroup_2;
                    }
                    else {
                        resourceList = Object.keys(subGroup_2).map(function (id) {
                            return subGroup_2[id];
                        });
                    }
                }
                else {
                    // Get all subtypes
                    resourceList = [];
                    for (var key in resourceGroup) {
                        if (resourceGroup.hasOwnProperty(key)) {
                            var subGroup = resourceGroup[key];
                            if (Array.isArray(subGroup)) {
                                resourceList = resourceList.concat(subGroup);
                            }
                            else if (typeof subGroup === 'object') {
                                for (var id in subGroup) {
                                    if (subGroup.hasOwnProperty(id)) {
                                        resourceList.push(subGroup[id]);
                                    }
                                }
                            }
                        }
                    }
                }
            }
            if (!resourceList || resourceList.length === 0) {
                return {
                    ok: false,
                    error: "No " + resource + " resources found on map"
                };
            }
            // Filter resources within radius and get valid entities
            var validResources = [];
            for (var i = 0; i < resourceList.length; i++) {
                var res = resourceList[i];
                var resId = res.id ? res.id : (typeof res === 'number' ? res : null);
                if (resId) {
                    var entity = this.state.getEntityById(resId);
                    if (entity) {
                        var pos = entity.position();
                        if (pos) {
                            var dx = pos[0] - refPosition.x;
                            var dz = pos[1] - refPosition.z;
                            var distance = Math.sqrt(dx * dx + dz * dz);
                            if (distance <= radius) {
                                validResources.push({
                                    id: resId,
                                    x: pos[0],
                                    z: pos[1],
                                    distance: distance
                                });
                            }
                        }
                    }
                }
            }
            if (validResources.length === 0) {
                return {
                    ok: false,
                    error: "No " + resource + " resources found within radius " + radius + " of position [" + x + ", " + z + "]"
                };
            }
            // Sort by distance
            validResources.sort(function (a, b) {
                return a.distance - b.distance;
            });
            // Use closest resource
            var targetIds = [validResources[0].id];
            // Execute gather via effector
            this.effector.gather(this.selection, targetIds);
            this.deb("   RPC: Found %s resources within radius, gathering from closest at distance %s", validResources.length, validResources[0].distance.toFixed(1));
            return {
                ok: true,
                result: {
                    entity_ids: this.selection,
                    resource: resource,
                    targets: targetIds,
                    search_position: refPosition,
                    search_radius: radius,
                    resources_found: validResources.length,
                    nearest_distance: validResources[0].distance
                }
            };
        },
        build: function (what, amount, mode, x, z, angle) {
            // Build a structure
            amount = amount || 1;
            mode = mode || "selected";
            angle = angle || 0;
            if (mode === "selected" && (!this.selection || !this.selection.length)) {
                // Fall back to economy mode
                this.deb("   RPC: Build - selection empty, falling back to economy");
                mode = "economy";
            }
            if (mode === "economy") {
                // Use economy system to build
                if (this.economy && this.economy.request) {
                    this.economy.request({
                        verb: "build",
                        what: what,
                        amount: amount
                    });
                    return {
                        ok: true,
                        result: {
                            template: what,
                            amount: amount,
                            mode: "economy",
                            fallback_triggered: !this.selection || !this.selection.length
                        }
                    };
                }
                else {
                    return { ok: false, error: "Economy system not available" };
                }
            }
            // Selected mode - use selected builders
            this.deb("   RPC: Build %s with selected builders: %s", what, uneval(this.selection));
            // Determine building position
            var position = null;
            if (x !== undefined && z !== undefined) {
                // User specified exact position
                position = [x, z, angle];
                this.deb("   RPC: Using custom position [%s, %s] angle %s", x, z, angle);
            }
            else {
                // Auto-find placement near village center
                if (this.villages && this.villages.list && this.villages.list.length > 0) {
                    var village = this.villages.list[0];
                    // Try to use placement logic if available
                    if (village.placement && typeof village.placement === 'function') {
                        // Call village placement method
                        var placement = village.placement(what);
                        if (placement && placement.position) {
                            position = [placement.position[0], placement.position[1], placement.angle || 0];
                            this.deb("   RPC: Using village placement logic");
                        }
                    }
                    // Fallback: place near center with improved spacing
                    if (!position && village.center && village.center.position) {
                        var centerPos = village.center.position();
                        if (centerPos) {
                            // Better placement: use a spiral pattern or random offset
                            // For now, use improved offset based on building count
                            var buildingCount = this.state.getOwnStructures().toEntityArray().length;
                            var offsetAngle = (buildingCount * 0.618) * 2 * Math.PI; // Golden angle for better distribution
                            var offsetDistance = 25 + (buildingCount % 4) * 10; // Varying distance
                            var offsetX = Math.cos(offsetAngle) * offsetDistance;
                            var offsetZ = Math.sin(offsetAngle) * offsetDistance;
                            position = [
                                centerPos[0] + offsetX,
                                centerPos[1] + offsetZ,
                                angle
                            ];
                            this.deb("   RPC: Using improved auto-placement offset [%s, %s]", offsetX, offsetZ);
                        }
                    }
                }
                if (!position) {
                    return { ok: false, error: "Could not find building placement (no village center found)" };
                }
            }
            // Execute build via effector
            this.effector.construct(this.selection, what, position);
            return {
                ok: true,
                result: {
                    builder_ids: this.selection,
                    template: what,
                    position: { x: position[0], z: position[1], angle: position[2] },
                    mode: "selected",
                    custom_position: (x !== undefined && z !== undefined)
                }
            };
        },
        train: function (unit, amount) {
            // Train units via economy system
            amount = amount || 1;
            if (!this.economy || !this.economy.request) {
                return { ok: false, error: "Economy system not available" };
            }
            this.deb("   RPC: Train %s x%s", unit, amount);
            this.economy.request({
                verb: "train",
                what: unit,
                amount: amount
            });
            return {
                ok: true,
                result: {
                    unit: unit,
                    queued: amount
                }
            };
        },
        research: function (tech) {
            // Research technology via economy system
            if (!this.economy || !this.economy.request) {
                return { ok: false, error: "Economy system not available" };
            }
            this.deb("   RPC: Research %s", tech);
            this.economy.request({
                verb: "research",
                what: tech
            });
            return {
                ok: true,
                result: {
                    tech: tech,
                    queued: true
                }
            };
        },
        getState: function () {
            // Get current player state
            var playerData = this.state.playerData;
            var resources = playerData.resourceCounts;
            return {
                ok: true,
                result: {
                    player_id: this.id,
                    resources: {
                        food: resources.food || 0,
                        wood: resources.wood || 0,
                        stone: resources.stone || 0,
                        metal: resources.metal || 0
                    },
                    population: playerData.popCount || 0,
                    population_cap: playerData.popLimit || 0,
                    population_max: playerData.popMax || 300,
                    phase: playerData.phase || "village",
                    current_selection: this.selection
                }
            };
        },
        listEntities: function (filter) {
            // List entities matching filter with enhanced options
            filter = filter || {};
            var offset = filter.offset || 0;
            var limit = filter.limit || 50;
            var includeStructures = filter.include_structures !== false; // Default true
            // Get entities (units and optionally structures)
            var entities = this.state.getOwnUnits().toEntityArray();
            if (includeStructures) {
                var structures = this.state.getOwnStructures().toEntityArray();
                entities = entities.concat(structures);
            }
            var state = this.state;
            // Apply filters
            entities = entities.filter(function (ent) {
                // Filter by class
                if (filter.class && !ent.hasClass(filter.class)) {
                    return false;
                }
                // Filter by owner
                if (filter.owner !== undefined && ent.owner() !== filter.owner) {
                    return false;
                }
                // Filter by position (within radius)
                if (filter.position) {
                    var pos = ent.position();
                    if (!pos)
                        return false;
                    var dx = pos[0] - filter.position.x;
                    var dz = pos[1] - filter.position.z;
                    var distance = Math.sqrt(dx * dx + dz * dz);
                    if (distance > filter.position.radius) {
                        return false;
                    }
                }
                // Filter by minimum health
                if (filter.min_health !== undefined) {
                    var entity = state.getEntityById(ent.id());
                    if (entity) {
                        // Try to get health if available
                        var hitpoints = entity.hitpoints ? entity.hitpoints() : null;
                        var maxHitpoints = entity.maxHitpoints ? entity.maxHitpoints() : null;
                        if (hitpoints !== null && maxHitpoints !== null && maxHitpoints > 0) {
                            var healthPercent = (hitpoints / maxHitpoints) * 100;
                            if (healthPercent < filter.min_health) {
                                return false;
                            }
                        }
                    }
                }
                return true;
            });
            // Get total count before pagination
            var totalCount = entities.length;
            // Apply pagination
            var paginatedEntities = entities.slice(offset, offset + limit);
            // Build result with enhanced entity info
            var result = [];
            paginatedEntities.forEach(function (ent) {
                var pos = ent.position();
                var entity = state.getEntityById(ent.id());
                var info = {
                    id: ent.id(),
                    template: ent.templateName(),
                    position: pos ? { x: pos[0], z: pos[1] } : null,
                    owner: ent.owner()
                };
                // Try to add additional info if available
                if (entity) {
                    // Health info
                    var hitpoints = entity.hitpoints ? entity.hitpoints() : null;
                    var maxHitpoints = entity.maxHitpoints ? entity.maxHitpoints() : null;
                    if (hitpoints !== null && maxHitpoints !== null) {
                        info.health = {
                            current: hitpoints,
                            max: maxHitpoints,
                            percent: maxHitpoints > 0 ? Math.round((hitpoints / maxHitpoints) * 100) : 0
                        };
                    }
                    // Stance (for military units)
                    var stance = entity.stance ? entity.stance() : null;
                    if (stance) {
                        info.stance = stance;
                    }
                    // Unit class info
                    var classes = [];
                    var classNames = ["Infantry", "Cavalry", "Ranged", "Melee", "Worker", "Support", "Soldier", "Structure", "Ship"];
                    for (var i = 0; i < classNames.length; i++) {
                        if (ent.hasClass(classNames[i])) {
                            classes.push(classNames[i]);
                        }
                    }
                    if (classes.length > 0) {
                        info.classes = classes;
                    }
                }
                result.push(info);
            });
            this.deb("   RPC: Listed %s entities (offset: %s, limit: %s, total: %s)", result.length, offset, limit, totalCount);
            return {
                ok: true,
                result: {
                    entities: result,
                    count: result.length,
                    total: totalCount,
                    offset: offset,
                    limit: limit,
                    has_more: (offset + limit) < totalCount
                }
            };
        },
        attack: function (target_id, queued) {
            if (queued === void 0) { queued = false; }
            // Attack specific target entity
            if (!this.selection || !this.selection.length) {
                return { ok: false, error: "No entities selected for attack command" };
            }
            var targetEntity = this.state.getEntityById(target_id);
            if (!targetEntity) {
                return { ok: false, error: "Target entity not found" };
            }
            this.deb("   RPC: Attack target %s with entities: %s", target_id, uneval(this.selection));
            // Use effector to execute attack command
            this.effector.execute({
                type: "attack",
                entities: this.selection,
                target: target_id,
                queued: queued,
                allowCapture: true
            });
            return {
                ok: true,
                result: {
                    attacker_ids: this.selection,
                    target_id: target_id,
                    queued: queued
                }
            };
        },
        attackWalk: function (x, z, target_classes, queued) {
            if (target_classes === void 0) { target_classes = "Unit"; }
            if (queued === void 0) { queued = false; }
            // Move and attack enemies encountered
            if (!this.selection || !this.selection.length) {
                return { ok: false, error: "No entities selected for attack-walk command" };
            }
            this.deb("   RPC: Attack-walk to [%s, %s] with entities: %s", x, z, uneval(this.selection));
            this.effector.execute({
                type: "attack-walk",
                entities: this.selection,
                x: x,
                z: z,
                targetClasses: { attack: [target_classes] },
                allowCapture: true,
                queued: queued
            });
            return {
                ok: true,
                result: {
                    entity_ids: this.selection,
                    position: { x: x, z: z },
                    target_classes: target_classes,
                    queued: queued
                }
            };
        },
        patrol: function (x, z, target_classes, queued) {
            if (target_classes === void 0) { target_classes = "Unit"; }
            if (queued === void 0) { queued = false; }
            // Patrol to position and back
            if (!this.selection || !this.selection.length) {
                return { ok: false, error: "No entities selected for patrol command" };
            }
            this.deb("   RPC: Patrol to [%s, %s] with entities: %s", x, z, uneval(this.selection));
            this.effector.execute({
                type: "patrol",
                entities: this.selection,
                x: x,
                z: z,
                targetClasses: { attack: [target_classes] },
                allowCapture: true,
                queued: queued
            });
            return {
                ok: true,
                result: {
                    entity_ids: this.selection,
                    position: { x: x, z: z },
                    target_classes: target_classes,
                    queued: queued
                }
            };
        },
        setStance: function (stance) {
            // Set combat stance for selected units
            var validStances = ["violent", "aggressive", "defensive", "passive", "standground"];
            if (validStances.indexOf(stance) === -1) {
                return { ok: false, error: "Invalid stance. Must be one of: " + validStances.join(", ") };
            }
            if (!this.selection || !this.selection.length) {
                return { ok: false, error: "No entities selected for stance command" };
            }
            this.deb("   RPC: Set stance '%s' for entities: %s", stance, uneval(this.selection));
            this.effector.stance(this.selection, stance);
            return {
                ok: true,
                result: {
                    entity_ids: this.selection,
                    stance: stance
                }
            };
        },
        setFormation: function (formation) {
            // Set unit formation
            var validFormations = ["Scatter", "Box", "ColumnClosed", "LineClosed", "ColumnOpen", "LineOpen", "Flank", "Skirmish", "Wedge", "Testudo", "Phalanx", "Syntagma", "BattleLine"];
            if (validFormations.indexOf(formation) === -1) {
                return { ok: false, error: "Invalid formation. Must be one of: " + validFormations.join(", ") };
            }
            if (!this.selection || !this.selection.length) {
                return { ok: false, error: "No entities selected for formation command" };
            }
            this.deb("   RPC: Set formation '%s' for entities: %s", formation, uneval(this.selection));
            this.effector.format(this.selection, formation);
            return {
                ok: true,
                result: {
                    entity_ids: this.selection,
                    formation: formation
                }
            };
        },
        guard: function (target_id, queued) {
            if (queued === void 0) { queued = false; }
            // Guard another unit
            if (!this.selection || !this.selection.length) {
                return { ok: false, error: "No entities selected for guard command" };
            }
            var targetEntity = this.state.getEntityById(target_id);
            if (!targetEntity) {
                return { ok: false, error: "Target entity not found" };
            }
            this.deb("   RPC: Guard target %s with entities: %s", target_id, uneval(this.selection));
            this.effector.execute({
                type: "guard",
                entities: this.selection,
                target: target_id,
                queued: queued
            });
            return {
                ok: true,
                result: {
                    guard_ids: this.selection,
                    target_id: target_id,
                    queued: queued
                }
            };
        },
        stop: function (queued) {
            if (queued === void 0) { queued = false; }
            // Stop current action
            if (!this.selection || !this.selection.length) {
                return { ok: false, error: "No entities selected for stop command" };
            }
            this.deb("   RPC: Stop entities: %s", uneval(this.selection));
            this.effector.execute({
                type: "stop",
                entities: this.selection,
                queued: queued
            });
            return {
                ok: true,
                result: {
                    entity_ids: this.selection,
                    queued: queued
                }
            };
        },
        garrison: function (target_id, queued) {
            if (queued === void 0) { queued = false; }
            // Garrison selected units into a building or ship
            if (!this.selection || !this.selection.length) {
                return { ok: false, error: "No entities selected for garrison command" };
            }
            var targetEntity = this.state.getEntityById(target_id);
            if (!targetEntity) {
                return { ok: false, error: "Target entity not found" };
            }
            this.deb("   RPC: Garrison entities %s into target %s", uneval(this.selection), target_id);
            // Execute garrison via effector
            this.effector.execute({
                type: "garrison",
                entities: this.selection,
                target: target_id,
                queued: queued
            });
            return {
                ok: true,
                result: {
                    entity_ids: this.selection,
                    target_id: target_id,
                    queued: queued
                }
            };
        },
        unload: function (garrison_holder_id, entity_ids) {
            // Unload specific units from garrison holder
            var holderEntity = this.state.getEntityById(garrison_holder_id);
            if (!holderEntity) {
                return { ok: false, error: "Garrison holder entity not found" };
            }
            // Get garrisoned entities if not specified
            var unloadIds = [];
            if (entity_ids && entity_ids.length > 0) {
                unloadIds = entity_ids;
            }
            else {
                // Unload all if no specific entities specified
                var garrisoned = holderEntity.garrisoned ? holderEntity.garrisoned() : null;
                if (garrisoned && garrisoned.length > 0) {
                    unloadIds = garrisoned.slice(0, 1); // Unload first one by default
                }
                else {
                    return { ok: false, error: "No entities garrisoned in holder" };
                }
            }
            this.deb("   RPC: Unload entities %s from garrison holder %s", uneval(unloadIds), garrison_holder_id);
            // Execute unload for each entity
            for (var i = 0; i < unloadIds.length; i++) {
                this.effector.execute({
                    type: "unload",
                    garrisonHolder: garrison_holder_id,
                    entities: [unloadIds[i]]
                });
            }
            return {
                ok: true,
                result: {
                    garrison_holder_id: garrison_holder_id,
                    unloaded_ids: unloadIds
                }
            };
        },
        unloadAll: function (garrison_holder_id) {
            // Unload all owned units from garrison holder
            var holderEntity = this.state.getEntityById(garrison_holder_id);
            if (!holderEntity) {
                return { ok: false, error: "Garrison holder entity not found" };
            }
            this.deb("   RPC: Unload all units from garrison holder %s", garrison_holder_id);
            // Execute unload-all command
            this.effector.execute({
                type: "unload-all-by-owner",
                garrisonHolders: [garrison_holder_id]
            });
            return {
                ok: true,
                result: {
                    garrison_holder_id: garrison_holder_id
                }
            };
        },
        repair: function (target_id, autocontinue, queued) {
            if (autocontinue === void 0) { autocontinue = true; }
            if (queued === void 0) { queued = false; }
            // Repair a building or siege weapon
            if (!this.selection || !this.selection.length) {
                return { ok: false, error: "No entities selected for repair command" };
            }
            var targetEntity = this.state.getEntityById(target_id);
            if (!targetEntity) {
                return { ok: false, error: "Target entity not found" };
            }
            this.deb("   RPC: Repair target %s with entities %s (autocontinue: %s)", target_id, uneval(this.selection), autocontinue);
            // Execute repair via effector
            this.effector.execute({
                type: "repair",
                entities: this.selection,
                target: target_id,
                autocontinue: autocontinue,
                queued: queued
            });
            return {
                ok: true,
                result: {
                    repairer_ids: this.selection,
                    target_id: target_id,
                    autocontinue: autocontinue,
                    queued: queued
                }
            };
        },
        heal: function (target_id, queued) {
            if (queued === void 0) { queued = false; }
            // Move healer units to target (they will auto-heal when in range)
            // Note: In 0 A.D., healing is automatic - healers heal nearby wounded allies
            if (!this.selection || !this.selection.length) {
                return { ok: false, error: "No entities selected for heal command" };
            }
            var targetEntity = this.state.getEntityById(target_id);
            if (!targetEntity) {
                return { ok: false, error: "Target entity not found" };
            }
            var targetPos = targetEntity.position();
            if (!targetPos) {
                return { ok: false, error: "Target has no position" };
            }
            this.deb("   RPC: Move healers %s to target %s for healing", uneval(this.selection), target_id);
            // Move healers near the target
            // They will automatically start healing when in range
            this.effector.execute({
                type: "move",
                entities: this.selection,
                x: targetPos[0],
                z: targetPos[1],
                queued: queued
            });
            // Also try to explicitly guard the target (healers will follow and heal)
            this.effector.execute({
                type: "guard",
                entities: this.selection,
                target: target_id,
                queued: true
            });
            return {
                ok: true,
                result: {
                    healer_ids: this.selection,
                    target_id: target_id,
                    queued: queued,
                    note: "Healers will automatically heal target when in range"
                }
            };
        },
        returnResources: function (dropsite_id, queued) {
            if (queued === void 0) { queued = false; }
            // Order selected gatherers to return resources to dropsite
            if (!this.selection || !this.selection.length) {
                return { ok: false, error: "No entities selected for return resources command" };
            }
            var targetId = dropsite_id;
            // If no dropsite specified, find nearest one
            if (!targetId) {
                var structures = this.state.getOwnStructures().toEntityArray();
                var nearestDropsite = null;
                var minDistance = Infinity;
                // Get first selected unit position as reference
                var firstUnit = this.state.getEntityById(this.selection[0]);
                if (!firstUnit) {
                    return { ok: false, error: "Selected unit not found" };
                }
                var unitPos = firstUnit.position();
                if (!unitPos) {
                    return { ok: false, error: "Selected unit has no position" };
                }
                var refPos = { x: unitPos[0], z: unitPos[1] };
                // Find nearest dropsite (civic center, storehouse, farmstead)
                for (var i = 0; i < structures.length; i++) {
                    var struct = structures[i];
                    if (struct.hasClass("DropsiteWood") || struct.hasClass("DropsiteStone") ||
                        struct.hasClass("DropsiteFood") || struct.hasClass("DropsiteMetal")) {
                        var pos = struct.position();
                        if (pos) {
                            var dx = pos[0] - refPos.x;
                            var dz = pos[1] - refPos.z;
                            var distance = Math.sqrt(dx * dx + dz * dz);
                            if (distance < minDistance) {
                                minDistance = distance;
                                nearestDropsite = struct;
                            }
                        }
                    }
                }
                if (!nearestDropsite) {
                    return { ok: false, error: "No dropsite found" };
                }
                targetId = nearestDropsite.id();
            }
            this.deb("   RPC: Return resources with entities %s to dropsite %s", uneval(this.selection), targetId);
            // Execute return resources command
            this.effector.execute({
                type: "returnresource",
                entities: this.selection,
                target: targetId,
                queued: queued
            });
            return {
                ok: true,
                result: {
                    entity_ids: this.selection,
                    dropsite_id: targetId,
                    queued: queued
                }
            };
        },
        filterOwnedEntities: function (entity_ids) {
            // Filter entity IDs to only owned + existing ones
            var state = this.state;
            var owned = [];
            entity_ids.forEach(function (id) {
                var ent = state.getEntityById(id);
                if (ent && ent.owner() === state.getPlayerID()) {
                    owned.push(id);
                }
            });
            return owned;
        }
    });
    return H;
}(HANNIBAL));
